
from pathlib import Path
import argparse, random, time
from collections import deque
from vrptw_core import read_homberger, list_instance_files, best_bih, clone_routes, objective_tuple, solution_stats, relocate_neighbor, swap_neighbor, try_merge_routes, write_solution

def tabu_search(inst, time_limit=90, seed=2026, tenure=80, candidates=80):
    rng=random.Random(seed)
    current=try_merge_routes(inst,best_bih(inst))
    best=clone_routes(current)
    tabu=deque(maxlen=tenure)
    start=time.time(); it=0
    while time.time()-start < time_limit:
        it += 1
        best_cand=None; best_move=None; best_obj=None
        for _ in range(candidates):
            op='relocate' if rng.random()<0.7 else 'swap'
            cand = relocate_neighbor(inst,current,rng) if op=='relocate' else swap_neighbor(inst,current,rng)
            if not solution_stats(inst,cand)['feasible']:
                continue
            move=(op, tuple(sorted([len(r) for r in cand])))
            obj=objective_tuple(inst,cand)
            aspiration = obj < objective_tuple(inst,best)
            if move in tabu and not aspiration:
                continue
            if best_cand is None or obj < best_obj:
                best_cand, best_move, best_obj = cand, move, obj
        if best_cand is None:
            current=relocate_neighbor(inst,current,rng)
            continue
        current=clone_routes(best_cand)
        tabu.append(best_move)
        if objective_tuple(inst,current) < objective_tuple(inst,best):
            best=clone_routes(current)
        if it % 30 == 0:
            merged=try_merge_routes(inst,best,max_pairs=200)
            if objective_tuple(inst,merged)<objective_tuple(inst,best): best=merged
    return best

def main():
    p=argparse.ArgumentParser(description='Run Tabu Search for Homberger VRPTW')
    p.add_argument('--data', default='data/raw')
    p.add_argument('--out', default='results/TABU')
    p.add_argument('--instance', default=None)
    p.add_argument('--time_limit', type=float, default=90)
    p.add_argument('--seed', type=int, default=2026)
    p.add_argument('--tenure', type=int, default=80)
    p.add_argument('--candidates', type=int, default=80)
    args=p.parse_args()
    out=Path(args.out); csv=out/'TABU_summary.csv'
    if csv.exists(): csv.unlink()
    for fp in list_instance_files(Path(args.data), args.instance):
        inst=read_homberger(fp); t=time.time()
        routes=tabu_search(inst,args.time_limit,args.seed,args.tenure,args.candidates)
        row=write_solution(out,'TABU',inst,routes,time.time()-t,args.seed)
        print(row)
if __name__=='__main__': main()
