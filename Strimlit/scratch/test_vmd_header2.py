import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

for m in ["VMD-GRU", "ICEEMDAN-VMD-GRU"]:
    fol = os.path.join(m, "Gunung geger")
    p = os.path.join(fol, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    df_opt = pd.read_excel(p, sheet_name="Parameter_Optimal", header=2)
    print(f"\n=== {m} Parameter_Optimal ===")
    print(df_opt)
