import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

for m in ['ICEEMDAN-VMD-GRU', 'ICEEMDAN-GRU', 'VMD-GRU', 'GRU']:
    p = os.path.join(m, "Gunung geger")
    if not os.path.exists(p):
        p = os.path.join(m, "Gunung Geger")
    fn = os.path.join(p, "hasil-normalisasi", "normalisasi_hasil_lengkap.xlsx")
    if os.path.exists(fn):
        print(f"\n=== {m} normalisasi_hasil_lengkap.xlsx ===")
        xls = pd.ExcelFile(fn)
        print("Sheets:", xls.sheet_names)
        df = pd.read_excel(fn, sheet_name=xls.sheet_names[0])
        print("Shape:", df.shape)
        for i in range(min(5, len(df))):
            print(f"  row {i}: {list(df.iloc[i].values)}")
