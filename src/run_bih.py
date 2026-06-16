
from pathlib import Path
import argparse, time, sys
from vrptw_core import read_homberger, list_instance_files, best_bih, try_merge_routes, write_solution

def main():
    p=argparse.ArgumentParser(description='Run BIH baseline for Homberger VRPTW')
    p.add_argument('--data', default='data/raw')
    p.add_argument('--out', default='results/BIH')
    p.add_argument('--instance', default=None)
    args=p.parse_args()
    out=Path(args.out); csv=out/'BIH_summary.csv'
    if csv.exists(): csv.unlink()
    for fp in list_instance_files(Path(args.data), args.instance):
        t=time.time(); inst=read_homberger(fp)
        routes=best_bih(inst)
        routes=try_merge_routes(inst,routes)
        row=write_solution(out,'BIH',inst,routes,time.time()-t)
        print(row)
if __name__=='__main__': main()
