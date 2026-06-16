# Homberger 1000 VRPTW - BIH, ALNS, Tabu, OR-Tools

Dự án này dùng bộ dữ liệu Homberger 1000 khách hàng để chạy các thuật toán VRPTW:

- `BIH`: Best Insertion Heuristic, dùng làm nghiệm nền.
- `ALNS`: Adaptive Large Neighborhood Search, chạy độc lập nhưng có thể khởi tạo từ BIH.
- `Tabu`: Tabu Search, chạy độc lập nhưng có thể khởi tạo từ BIH.
- `ORTools`: CP-VRPTW của Google OR-Tools để làm nghiệm tham chiếu.
- `aggregate_compare.py`: tổng hợp và so sánh kết quả ALNS, Tabu, ORTools.

## 1. Tạo thư mục Git trên Windows

```powershell
cd C:\
mkdir Homberger1000_VRPTW
cd Homberger1000_VRPTW
git init
```

Sau đó chép toàn bộ nội dung thư mục này vào `C:\Homberger1000_VRPTW`.

## 2. Cài môi trường Python

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Nếu chưa cài OR-Tools được thì vẫn chạy được BIH, ALNS, Tabu. Riêng `run_ortools.py` cần thư viện `ortools`.

## 3. Cấu trúc thư mục

```text
Homberger1000_VRPTW/
├── data/
│   ├── homberger_1000_customer_instances.zip
│   └── raw/*.TXT
├── src/
│   ├── vrptw_core.py
│   ├── run_bih.py
│   ├── run_alns.py
│   ├── run_tabu.py
│   ├── run_ortools.py
│   └── aggregate_compare.py
├── scripts/
│   ├── run_bih.ps1
│   ├── run_alns.ps1
│   ├── run_tabu.ps1
│   ├── run_ortools.ps1
│   └── run_compare.ps1
├── results/
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Chạy từng thuật toán

Chạy thử 1 instance:

```powershell
python src\run_bih.py --data data\raw --out results\BIH --instance C1_10_1.TXT
python src\run_alns.py --data data\raw --out results\ALNS --instance C1_10_1.TXT --time_limit 90 --seed 2026
python src\run_tabu.py --data data\raw --out results\TABU --instance C1_10_1.TXT --time_limit 90 --seed 2026
python src\run_ortools.py --data data\raw --out results\ORTOOLS --instance C1_10_1.TXT --time_limit 90
```

Chạy toàn bộ 60 instance:

```powershell
python src\run_bih.py --data data\raw --out results\BIH
python src\run_alns.py --data data\raw --out results\ALNS --time_limit 90 --seed 2026
python src\run_tabu.py --data data\raw --out results\TABU --time_limit 90 --seed 2026
python src\run_ortools.py --data data\raw --out results\ORTOOLS --time_limit 90
```

## 5. Tổng hợp và so sánh

```powershell
python src\aggregate_compare.py --results results --out results\COMPARE
```

Kết quả chính:

- `results/COMPARE/all_results.csv`
- `results/COMPARE/summary_by_algorithm.csv`
- `results/COMPARE/summary_by_family_algorithm.csv`
- `results/COMPARE/vehicle_compare.png`
- `results/COMPARE/distance_compare.png`
- `results/COMPARE/family_distance_compare.png`

## 6. Đẩy lên GitHub

```powershell
git add .
git commit -m "Add Homberger1000 VRPTW experiments with BIH ALNS Tabu ORTools"
git branch -M main
git remote add origin https://github.com/<tai-khoan>/<ten-repo>.git
git push -u origin main
```

Nếu đã có remote rồi:

```powershell
git remote -v
git push
```

## 7. Ghi chú công bằng thực nghiệm

Để so sánh công bằng:

- Cùng bộ dữ liệu Homberger 1000.
- Cùng thời gian chạy, ví dụ 90 giây/instance/thuật toán.
- Cùng seed cho ALNS và Tabu, ví dụ 2026.
- Cùng hàm mục tiêu: ưu tiên số xe trước, sau đó tổng quãng đường.
- OR-Tools dùng `PATH_CHEAPEST_ARC` + `GUIDED_LOCAL_SEARCH` trong cùng giới hạn thời gian.

Khuyến nghị bài báo: chạy nhiều seed, ví dụ `2026..2055`, rồi báo cáo Best/Average/Std.
