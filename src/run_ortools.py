
from pathlib import Path
import argparse, time
from vrptw_core import read_homberger, list_instance_files, write_solution

def solve_ortools(inst, time_limit=90):
    try:
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    except Exception as e:
        raise RuntimeError('Chưa cài ortools. Chạy: pip install ortools') from e
    n=len(inst.customers)
    depot=0
    manager=pywrapcp.RoutingIndexManager(n, inst.vehicle_number, depot)
    routing=pywrapcp.RoutingModel(manager)
    scale=1000
    def dist_cb(from_index, to_index):
        i=manager.IndexToNode(from_index); j=manager.IndexToNode(to_index)
        return int(round(inst.dist[i][j]*scale))
    transit=routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)
    def demand_cb(from_index):
        return inst.customers[manager.IndexToNode(from_index)].demand
    demand_i=routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand_i, 0, [inst.capacity]*inst.vehicle_number, True, 'Capacity')
    def time_cb(from_index,to_index):
        i=manager.IndexToNode(from_index); j=manager.IndexToNode(to_index)
        return int(round(inst.dist[i][j] + inst.customers[i].service))
    time_i=routing.RegisterTransitCallback(time_cb)
    horizon=int(max(c.due for c in inst.customers)+10000)
    routing.AddDimension(time_i, horizon, horizon, False, 'Time')
    time_dim=routing.GetDimensionOrDie('Time')
    for node,c in enumerate(inst.customers):
        idx=manager.NodeToIndex(node)
        time_dim.CumulVar(idx).SetRange(int(c.ready), int(c.due))
    for v in range(inst.vehicle_number):
        time_dim.CumulVar(routing.Start(v)).SetRange(int(inst.customers[0].ready), int(inst.customers[0].due))
    params=pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy=routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic=routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds=int(time_limit)
    params.log_search=False
    sol=routing.SolveWithParameters(params)
    if sol is None:
        return []
    routes=[]
    for v in range(inst.vehicle_number):
        idx=routing.Start(v); route=[]
        while not routing.IsEnd(idx):
            node=manager.IndexToNode(idx)
            if node!=0: route.append(node)
            idx=sol.Value(routing.NextVar(idx))
        if route: routes.append(route)
    return routes

def main():
    p=argparse.ArgumentParser(description='Run Google OR-Tools for Homberger VRPTW')
    p.add_argument('--data', default='data/raw')
    p.add_argument('--out', default='results/ORTOOLS')
    p.add_argument('--instance', default=None)
    p.add_argument('--time_limit', type=float, default=90)
    args=p.parse_args()
    out=Path(args.out); csv=out/'ORTOOLS_summary.csv'
    if csv.exists(): csv.unlink()
    for fp in list_instance_files(Path(args.data), args.instance):
        inst=read_homberger(fp); t=time.time()
        routes=solve_ortools(inst,args.time_limit)
        row=write_solution(out,'ORTOOLS',inst,routes,time.time()-t)
        print(row)
if __name__=='__main__': main()
