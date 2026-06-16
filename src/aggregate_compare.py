
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from vrptw_core import require_bih_summary

def main():
    p=argparse.ArgumentParser(description='Aggregate and compare ALNS, Tabu, ORTools results')
    p.add_argument('--results', default='results')
    p.add_argument('--out', default='results/COMPARE')
    args=p.parse_args()
    results=Path(args.results); out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    # Bắt buộc phải có BIH_summary.csv để BIH là nghiệm nền trong mọi bảng so sánh.
    require_bih_summary(results)
    files=list(results.glob('*/*_summary.csv'))
    if not files:
        raise SystemExit('Không thấy file *_summary.csv trong results. Hãy chạy thuật toán trước.')
    dfs=[]
    for f in files:
        try: dfs.append(pd.read_csv(f))
        except Exception as e: print('Bỏ qua',f,e)
    df=pd.concat(dfs, ignore_index=True)
    df=df[df['algorithm'].isin(['BIH','ALNS','TABU','ORTOOLS'])].copy()
    if 'BIH' not in set(df['algorithm']):
        raise SystemExit('Bảng tổng hợp bắt buộc phải có BIH. Hãy chạy run_bih.py trước.')
    df.to_csv(out/'all_results.csv', index=False, encoding='utf-8-sig')
    summary=df.groupby('algorithm').agg(
        instances=('instance','count'),
        feasible_rate=('feasible','mean'),
        avg_vehicles=('vehicles','mean'),
        avg_distance=('distance','mean'),
        avg_runtime=('runtime','mean')
    ).reset_index()
    summary.to_csv(out/'summary_by_algorithm.csv', index=False, encoding='utf-8-sig')
    fam=df.groupby(['family','algorithm']).agg(
        instances=('instance','count'),
        avg_vehicles=('vehicles','mean'),
        avg_distance=('distance','mean'),
        avg_runtime=('runtime','mean')
    ).reset_index()
    fam.to_csv(out/'summary_by_family_algorithm.csv', index=False, encoding='utf-8-sig')
    pivot=df.pivot_table(index='instance', columns='algorithm', values='vehicles', aggfunc='min')
    pivot.plot(kind='bar', figsize=(16,5))
    plt.ylabel('Số xe')
    plt.title('So sánh số xe theo instance')
    plt.tight_layout(); plt.savefig(out/'vehicle_compare.png', dpi=200); plt.close()
    pivot=df.pivot_table(index='instance', columns='algorithm', values='distance', aggfunc='min')
    pivot.plot(kind='bar', figsize=(16,5))
    plt.ylabel('Tổng quãng đường')
    plt.title('So sánh quãng đường theo instance')
    plt.tight_layout(); plt.savefig(out/'distance_compare.png', dpi=200); plt.close()
    fp=fam.pivot(index='family', columns='algorithm', values='avg_distance')
    fp.plot(kind='bar', figsize=(10,5))
    plt.ylabel('Quãng đường trung bình')
    plt.title('So sánh quãng đường trung bình theo nhóm dữ liệu')
    plt.tight_layout(); plt.savefig(out/'family_distance_compare.png', dpi=200); plt.close()
    print('\nSUMMARY BY ALGORITHM')
    print(summary.to_string(index=False))
    print('\nĐã lưu kết quả vào:', out)
if __name__=='__main__':
    try:
        main()
    except FileNotFoundError as e:
        raise SystemExit(str(e))
