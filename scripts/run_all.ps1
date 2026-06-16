# Quy trình bắt buộc: BIH phải chạy trước để tạo nghiệm nền đã lưu.
python src\run_bih.py --data data\raw --out results\BIH
python src\run_alns.py --data data\raw --out results\ALNS --bih_dir results\BIH --time_limit 90 --seed 2026
python src\run_tabu.py --data data\raw --out results\TABU --bih_dir results\BIH --time_limit 90 --seed 2026
python src\run_ortools.py --data data\raw --out results\ORTOOLS --bih_dir results\BIH --time_limit 90
python src\aggregate_compare.py --results results --out results\COMPARE
