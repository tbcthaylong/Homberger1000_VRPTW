
from pathlib import Path
import argparse, math, random, time
from vrptw_core import read_homberger, list_instance_files, load_bih_baseline, clone_routes, objective_tuple, solution_stats, random_destroy, worst_destroy, greedy_repair, try_merge_routes, write_solution

def alns(inst, bih_dir, time_limit=90, seed=2026):
    rng=random.Random(seed)
    # Bắt buộc đọc nghiệm nền BIH đã lưu; không tự tạo BIH tại đây.
    current=try_merge_routes(inst, load_bih_baseline(Path(bih_dir), inst))
    best=clone_routes(current)
    start=time.time(); it=0
    destroy_ops=['random','worst']
    weights={op:1.0 for op in destroy_ops}
    temp=max(1.0, objective_tuple(inst,current)[1]*0.05)
    while time.time()-start < time_limit:
        it+=1
        ops=list(weights)
        op=rng.choices(ops, weights=[weights[o] for o in ops], k=1)[0]
        q=max(5, int(0.02*(len(inst.customers)-1)))
        q=rng.randint(max(2,q//2), max(3, q*2))
        if op=='random': partial, removed=random_destroy(current,q,rng)
        else: partial, removed=worst_destroy(inst,current,q,rng)
        cand=greedy_repair(inst, partial, removed, rng)
        if it % 25 == 0:
            cand=try_merge_routes(inst,cand, max_pairs=200)
        cobj=objective_tuple(inst,current); nobj=objective_tuple(inst,cand); bobj=objective_tuple(inst,best)
        accept = nobj < cobj
        if not accept:
            delta=(nobj[0]-cobj[0])*1000000 + (nobj[1]-cobj[1])
            accept = rng.random() < math.exp(-max(0,delta)/max(1e-9,temp))
        if accept:
            current=clone_routes(cand)
            weights[op]+=0.05
        if nobj < bobj and solution_stats(inst,cand)['feasible']:
            best=clone_routes(cand)
            weights[op]+=0.25
        temp *= 0.999
    return best

def main():
    p=argparse.ArgumentParser(description='Run ALNS for Homberger VRPTW')
    p.add_argument('--data', default='data/raw')
    p.add_argument('--out', default='results/ALNS')
    p.add_argument('--bih_dir', default='results/BIH', help='Thư mục chứa nghiệm nền BIH đã tạo bởi run_bih.py')
    p.add_argument('--instance', default=None)
    p.add_argument('--time_limit', type=float, default=90)
    p.add_argument('--seed', type=int, default=2026)
    args=p.parse_args()
    out=Path(args.out); csv=out/'ALNS_summary.csv'
    if csv.exists(): csv.unlink()
    for fp in list_instance_files(Path(args.data), args.instance):
        inst=read_homberger(fp); t=time.time()
        routes=alns(inst,args.bih_dir,args.time_limit,args.seed)
        row=write_solution(out,'ALNS',inst,routes,time.time()-t,args.seed)
        print(row)
if __name__=='__main__':
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        raise SystemExit(str(e))
