
from __future__ import annotations
import csv, json, math, random, time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Optional

@dataclass
class Customer:
    idx: int
    x: float
    y: float
    demand: int
    ready: float
    due: float
    service: float

@dataclass
class Instance:
    name: str
    vehicle_number: int
    capacity: int
    customers: List[Customer]
    dist: List[List[float]]

def read_homberger(path: Path) -> Instance:
    lines = path.read_text(encoding='latin1').splitlines()
    name = lines[0].strip() or path.stem
    vehicle_number, capacity = None, None
    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            vehicle_number, capacity = int(parts[0]), int(parts[1])
            break
    if capacity is None:
        raise ValueError(f'Không đọc được số xe/tải trọng trong {path}')
    start = None
    for i, line in enumerate(lines):
        if line.strip().upper().startswith('CUST NO'):
            start = i + 1
            break
    customers=[]
    for line in lines[start:]:
        p=line.split()
        if len(p) >= 7 and p[0].lstrip('-').isdigit():
            customers.append(Customer(int(p[0]), float(p[1]), float(p[2]), int(float(p[3])), float(p[4]), float(p[5]), float(p[6])))
    customers.sort(key=lambda c: c.idx)
    n=len(customers)
    dist=[[0.0]*n for _ in range(n)]
    for i,a in enumerate(customers):
        for j,b in enumerate(customers):
            dist[i][j]=math.hypot(a.x-b.x, a.y-b.y)
    return Instance(name=name, vehicle_number=vehicle_number, capacity=capacity, customers=customers, dist=dist)

def list_instance_files(data_dir: Path, instance: Optional[str]=None) -> List[Path]:
    if instance:
        p=data_dir/instance
        if not p.exists():
            p=data_dir/(instance if instance.lower().endswith('.txt') else instance + '.TXT')
        return [p]
    return sorted(data_dir.glob('*.TXT')) + sorted(data_dir.glob('*.txt'))

def route_stats(inst: Instance, route: List[int]) -> Tuple[bool, float, float, int]:
    # route không chứa depot; khách hàng dùng chỉ số 1..n-1 theo file Homberger
    load=0
    time_now=0.0
    dist_total=0.0
    prev=0
    for node in route:
        c=inst.customers[node]
        travel=inst.dist[prev][node]
        arrive=time_now+travel
        start=max(arrive, c.ready)
        if start > c.due + 1e-9:
            return False, dist_total+travel, start, load+c.demand
        time_now=start+c.service
        dist_total += travel
        load += c.demand
        if load > inst.capacity:
            return False, dist_total, time_now, load
        prev=node
    depot=inst.customers[0]
    dist_total += inst.dist[prev][0]
    arrive_depot=time_now + inst.dist[prev][0]
    feasible = arrive_depot <= depot.due + 1e-9 and load <= inst.capacity
    return feasible, dist_total, arrive_depot, load

def solution_stats(inst: Instance, routes: List[List[int]]) -> Dict:
    clean=[r for r in routes if r]
    feasible=True
    total_dist=0.0
    loads=[]
    for r in clean:
        ok,d,t,l=route_stats(inst,r)
        feasible = feasible and ok
        total_dist += d
        loads.append(l)
    seen=[x for r in clean for x in r]
    feasible = feasible and sorted(seen)==list(range(1,len(inst.customers)))
    return {
        'vehicles': len(clean),
        'distance': round(total_dist, 4),
        'feasible': bool(feasible),
        'max_load': max(loads) if loads else 0,
        'served': len(seen),
        'customers': len(inst.customers)-1,
    }

def objective_tuple(inst: Instance, routes: List[List[int]]) -> Tuple[int,float]:
    st=solution_stats(inst,routes)
    penalty=0 if st['feasible'] else 10**9
    return (st['vehicles']+penalty, st['distance']+penalty)

def can_insert(inst: Instance, route: List[int], node: int, pos: int) -> Tuple[bool, float]:
    old_ok, old_d, *_ = route_stats(inst, route)
    new=route[:pos]+[node]+route[pos:]
    ok, new_d, *_ = route_stats(inst, new)
    return ok, new_d - old_d

def best_insert_position(inst: Instance, routes: List[List[int]], node: int):
    best=None
    for ri,r in enumerate(routes):
        for pos in range(len(r)+1):
            ok, inc=can_insert(inst,r,node,pos)
            if ok and (best is None or inc < best[0]):
                best=(inc,ri,pos)
    return best

def bih_solution(inst: Instance, policy: str='earliest_due') -> List[List[int]]:
    nodes=list(range(1,len(inst.customers)))
    if policy=='earliest_due':
        nodes.sort(key=lambda i:(inst.customers[i].due, inst.customers[i].ready))
    elif policy=='earliest_ready':
        nodes.sort(key=lambda i:(inst.customers[i].ready, inst.customers[i].due))
    elif policy=='largest_demand':
        nodes.sort(key=lambda i:(-inst.customers[i].demand, inst.customers[i].due))
    elif policy=='farthest':
        nodes.sort(key=lambda i:(-inst.dist[0][i], inst.customers[i].due))
    routes=[]
    for node in nodes:
        best=best_insert_position(inst,routes,node)
        if best is None:
            routes.append([node])
        else:
            _,ri,pos=best
            routes[ri].insert(pos,node)
    return routes

def best_bih(inst: Instance) -> List[List[int]]:
    policies=['earliest_due','earliest_ready','largest_demand','farthest']
    sols=[bih_solution(inst,p) for p in policies]
    return min(sols, key=lambda r: objective_tuple(inst,r))

def write_solution(out_dir: Path, algorithm: str, inst: Instance, routes: List[List[int]], runtime: float, seed: Optional[int]=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    st=solution_stats(inst,routes)
    row={
        'instance': inst.name,
        'family': inst.name.split('_')[0].upper(),
        'algorithm': algorithm,
        'vehicles': st['vehicles'],
        'distance': st['distance'],
        'runtime': round(runtime,4),
        'feasible': st['feasible'],
        'served': st['served'],
        'customers': st['customers'],
        'seed': '' if seed is None else seed,
    }
    json_path=out_dir/f'{inst.name}_{algorithm}.json'
    json_path.write_text(json.dumps({'summary': row, 'routes': routes}, ensure_ascii=False, indent=2), encoding='utf-8')
    csv_path=out_dir/f'{algorithm}_summary.csv'
    exists=csv_path.exists()
    with csv_path.open('a', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists: w.writeheader()
        w.writerow(row)
    return row

def remove_empty(routes):
    return [r for r in routes if r]

def clone_routes(routes):
    return [list(r) for r in routes]

def all_customers(routes):
    return [n for r in routes for n in r]

def greedy_repair(inst: Instance, routes: List[List[int]], removed: List[int], rng: random.Random):
    rng.shuffle(removed)
    for node in removed:
        best=best_insert_position(inst,routes,node)
        if best is None:
            routes.append([node])
        else:
            _,ri,pos=best
            routes[ri].insert(pos,node)
    return remove_empty(routes)

def random_destroy(routes: List[List[int]], q: int, rng: random.Random):
    routes=clone_routes(routes)
    nodes=all_customers(routes)
    q=min(q,len(nodes))
    removed=set(rng.sample(nodes,q)) if q>0 else set()
    new=[]
    for r in routes:
        new.append([x for x in r if x not in removed])
    return remove_empty(new), list(removed)

def worst_destroy(inst: Instance, routes: List[List[int]], q: int, rng: random.Random):
    contrib=[]
    for ri,r in enumerate(routes):
        for pi,node in enumerate(r):
            prev=0 if pi==0 else r[pi-1]
            nxt=0 if pi==len(r)-1 else r[pi+1]
            saving=inst.dist[prev][node]+inst.dist[node][nxt]-inst.dist[prev][nxt]
            contrib.append((saving,node))
    contrib.sort(reverse=True)
    removed={node for _,node in contrib[:q]}
    new=[[x for x in r if x not in removed] for r in routes]
    return remove_empty(new), list(removed)

def relocate_neighbor(inst: Instance, routes: List[List[int]], rng: random.Random):
    nr=clone_routes(routes)
    nonempty=[i for i,r in enumerate(nr) if r]
    if not nonempty: return nr
    a=rng.choice(nonempty)
    pos=rng.randrange(len(nr[a]))
    node=nr[a].pop(pos)
    best=best_insert_position(inst,nr,node)
    if best is None:
        nr[a].insert(pos,node)
    else:
        _,ri,p=best
        nr[ri].insert(p,node)
    return remove_empty(nr)

def swap_neighbor(inst: Instance, routes: List[List[int]], rng: random.Random):
    nr=clone_routes(routes)
    flat=[(ri,pi) for ri,r in enumerate(nr) for pi,_ in enumerate(r)]
    if len(flat)<2: return nr
    (r1,p1),(r2,p2)=rng.sample(flat,2)
    nr[r1][p1],nr[r2][p2]=nr[r2][p2],nr[r1][p1]
    if solution_stats(inst,nr)['feasible']:
        return remove_empty(nr)
    return routes

def try_merge_routes(inst: Instance, routes: List[List[int]], max_pairs: int=500):
    routes=remove_empty(clone_routes(routes))
    improved=True; checked=0
    while improved and checked<max_pairs:
        improved=False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i==j or not routes[i] or not routes[j]: continue
                cand=routes[i]+routes[j]
                checked += 1
                if route_stats(inst,cand)[0]:
                    routes[i]=cand; routes[j]=[]; routes=remove_empty(routes); improved=True; break
            if improved or checked>=max_pairs: break
    return remove_empty(routes)

def load_bih_baseline(bih_dir: Path, inst: Instance) -> List[List[int]]:
    """Đọc nghiệm nền BIH đã được tạo bởi run_bih.py.

    Hàm này cố ý KHÔNG tự tạo BIH. Nếu thiếu file BIH, các thuật toán
    cải tiến phải dừng để bảo đảm quy trình thực nghiệm luôn bắt đầu từ
    cùng một nghiệm nền đã lưu.
    """
    bih_dir = Path(bih_dir)
    json_path = bih_dir / f'{inst.name}_BIH.json'
    if not json_path.exists():
        raise FileNotFoundError(
            f'Thiếu nghiệm nền BIH cho instance {inst.name}: {json_path}\n'
            f'Hãy chạy trước: python src\\run_bih.py --data data\\raw --out {bih_dir}'
        )
    data = json.loads(json_path.read_text(encoding='utf-8'))
    routes = data.get('routes')
    if not isinstance(routes, list) or not routes:
        raise ValueError(f'File nghiệm nền BIH không hợp lệ: {json_path}')
    st = solution_stats(inst, routes)
    if not st['feasible']:
        raise ValueError(f'Nghiệm nền BIH trong {json_path} không khả thi.')
    return routes

def require_bih_summary(results_dir: Path, required_instances: Optional[List[str]] = None) -> Path:
    """Kiểm tra bắt buộc phải có BIH_summary.csv trước khi tổng hợp."""
    results_dir = Path(results_dir)
    csv_path = results_dir / 'BIH' / 'BIH_summary.csv'
    if not csv_path.exists():
        raise FileNotFoundError(
            f'Thiếu file {csv_path}. Hãy chạy BIH trước khi chạy tổng hợp:\n'
            f'python src\\run_bih.py --data data\\raw --out results\\BIH'
        )
    if required_instances:
        with csv_path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            have = {row.get('instance') for row in reader}
        missing = sorted(set(required_instances) - have)
        if missing:
            raise FileNotFoundError(
                'BIH_summary.csv còn thiếu các instance: ' + ', '.join(missing[:10]) +
                (' ...' if len(missing) > 10 else '')
            )
    return csv_path
