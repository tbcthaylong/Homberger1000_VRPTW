# Homberger 1000 VRPTW - BIH, ALNS, Tabu, OR-Tools

Dự án này dùng bộ dữ liệu Homberger 1000 khách hàng để chạy các thuật toán VRPTW.

Điểm quan trọng của phiên bản này: **BIH là nghiệm nền bắt buộc**. Các chương trình `ALNS`, `Tabu`, `OR-Tools` và chương trình tổng hợp đều kiểm tra sự tồn tại của nghiệm nền BIH đã lưu trong `results/BIH`. Nếu chưa chạy `run_bih.py`, chương trình sẽ dừng và báo lỗi.

## 1. Cấu trúc thư mục

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
│   ├── run_compare.ps1
│   └── run_all.ps1
├── results/
├── requirements.txt
├── .gitignore
└── README.md
```

## 2. Cài môi trường

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install ortools
```

Nếu chưa cài được `ortools`, vẫn chạy được `BIH`, `ALNS`, `Tabu`. Riêng `run_ortools.py` cần thư viện `ortools`.

## 3. Thứ tự chạy bắt buộc

### Bước 1 - Chạy BIH để tạo nghiệm nền

```powershell
python src\run_bih.py --data data\raw --out results\BIH
```

Lệnh này tạo:

```text
results/BIH/BIH_summary.csv
results/BIH/<instance>_BIH.json
```

Các file JSON này là nghiệm nền bắt buộc cho từng instance.

### Bước 2 - Chạy ALNS từ nghiệm nền BIH

```powershell
python src\run_alns.py --data data\raw --out results\ALNS --bih_dir results\BIH --time_limit 90 --seed 2026
```

Nếu thiếu nghiệm nền BIH, chương trình sẽ báo lỗi và dừng.

### Bước 3 - Chạy Tabu từ nghiệm nền BIH

```powershell
python src\run_tabu.py --data data\raw --out results\TABU --bih_dir results\BIH --time_limit 90 --seed 2026
```

Nếu thiếu nghiệm nền BIH, chương trình sẽ báo lỗi và dừng.

### Bước 4 - Chạy OR-Tools, có kiểm tra mốc BIH

```powershell
python src\run_ortools.py --data data\raw --out results\ORTOOLS --bih_dir results\BIH --time_limit 90
```

OR-Tools không dùng BIH để khởi tạo, nhưng vẫn bắt buộc có BIH để bảo đảm bảng so sánh luôn có nghiệm nền.

### Bước 5 - Tổng hợp và so sánh

```powershell
python src\aggregate_compare.py --results results --out results\COMPARE
```

Chương trình tổng hợp cũng bắt buộc có:

```text
results/BIH/BIH_summary.csv
```

## 4. Chạy nhanh một instance để kiểm tra

```powershell
python src\run_bih.py --data data\raw --out results\BIH --instance C1_10_1.TXT
python src\run_alns.py --data data\raw --out results\ALNS --bih_dir results\BIH --instance C1_10_1.TXT --time_limit 10 --seed 2026
python src\run_tabu.py --data data\raw --out results\TABU --bih_dir results\BIH --instance C1_10_1.TXT --time_limit 10 --seed 2026
python src\run_ortools.py --data data\raw --out results\ORTOOLS --bih_dir results\BIH --instance C1_10_1.TXT --time_limit 10
python src\aggregate_compare.py --results results --out results\COMPARE
```

## 5. Chạy toàn bộ bằng PowerShell script

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_all.ps1
```

Hoặc chạy từng script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_bih.ps1
powershell -ExecutionPolicy Bypass -File scripts\run_alns.ps1
powershell -ExecutionPolicy Bypass -File scripts\run_tabu.ps1
powershell -ExecutionPolicy Bypass -File scripts\run_ortools.ps1
powershell -ExecutionPolicy Bypass -File scripts\run_compare.ps1
```

## 6. Kết quả đầu ra

```text
results/BIH/BIH_summary.csv
results/ALNS/ALNS_summary.csv
results/TABU/TABU_summary.csv
results/ORTOOLS/ORTOOLS_summary.csv
results/COMPARE/all_results.csv
results/COMPARE/summary_by_algorithm.csv
results/COMPARE/summary_by_family_algorithm.csv
results/COMPARE/vehicle_compare.png
results/COMPARE/distance_compare.png
results/COMPARE/family_distance_compare.png
```

## 7. Ghi chú công bằng thực nghiệm

- BIH tạo một nghiệm nền duy nhất cho từng instance.
- ALNS và Tabu đều đọc cùng nghiệm nền BIH đã lưu.
- OR-Tools không dùng BIH để khởi tạo nhưng vẫn được so sánh với cùng mốc BIH.
- Cùng bộ dữ liệu Homberger 1000.
- Cùng giới hạn thời gian, ví dụ 90 giây/instance/thuật toán.
- Cùng hàm mục tiêu: ưu tiên số xe trước, sau đó tổng quãng đường.
- Khuyến nghị bài báo: chạy nhiều seed, ví dụ `2026..2055`, rồi báo cáo Best/Average/Std.

## 8. Đẩy lên GitHub

```powershell
git add .
git commit -m "Require BIH baseline before ALNS Tabu ORTools comparison"
git push
```
