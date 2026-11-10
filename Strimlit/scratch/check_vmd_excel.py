import sys, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

for p in ["VMD-GRU/Gunung geger/hasil-dekomposisi/vmd_hasil_lengkap.xlsx",
          "ICEEMDAN-VMD-GRU/Gunung geger/hasil-dekomposisi/vmd_hasil_lengkap.xlsx"]:
    print(f"\n=== {p} ===")
    xls = pd.ExcelFile(p)
    print("Sheets:", xls.sheet_names)
    for sh in xls.sheet_names:
        df = pd.read_excel(p, sheet_name=sh)
        print(f"Sheet '{sh}' shape: {df.shape}")
        for i in range(min(5, len(df))):
            print(f"  row {i}: {list(df.iloc[i].values)}")
