import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

def baca_sheet_vmd(p, sheet):
    df = pd.read_excel(p, sheet_name=sheet, header=None)
    for idx, row in df.iterrows():
        first_val = str(row.values[0]).strip().lower()
        if "sinyal" in first_val or "imf" in first_val or "k" in first_val:
            header = [str(c).strip() for c in row.values]
            data = df.iloc[idx+1:].copy()
            data.columns = header
            return data.dropna(how="all").reset_index(drop=True)
    return df

for m in ["VMD-GRU", "ICEEMDAN-VMD-GRU"]:
    fol = os.path.join(m, "Gunung geger")
    p = os.path.join(fol, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    df_opt = baca_sheet_vmd(p, "Parameter_Optimal")
    print(f"\n=== {m} Clean Parameter_Optimal ===")
    print(df_opt)
    df_cand = baca_sheet_vmd(p, "Pencarian_Parameter")
    print(f"\n=== {m} Clean Candidates (top 3) ===")
    print(df_cand.head(3))
