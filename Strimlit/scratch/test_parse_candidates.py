import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

def parse_vmd_candidates(folder):
    p = os.path.join(folder, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    if not os.path.exists(p):
        return None
    try:
        xls = pd.ExcelFile(p)
        df_cand_raw = pd.read_excel(p, sheet_name="Pencarian_Parameter", header=None)
        # find header row
        h_idx = -1
        for idx, row in df_cand_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if "k" in row_str and "alpha" in row_str:
                h_idx = idx
                break
        if h_idx == -1:
            return None
        df_c = df_cand_raw.iloc[h_idx+1:].copy()
        df_c.columns = [str(x).strip() for x in df_cand_raw.iloc[h_idx].values]
        df_c = df_c.dropna(how="all")
        
        # parse best table
        df_best_raw = pd.read_excel(p, sheet_name="Parameter_Optimal", header=None)
        b_idx = -1
        for idx, row in df_best_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if any("k optimal" in x or "k_optimal" in x for x in row_str):
                b_idx = idx
                break
        df_b = df_best_raw.iloc[b_idx+1:].copy()
        df_b.columns = [str(x).strip() for x in df_best_raw.iloc[b_idx].values]
        df_b = df_b.dropna(how="all")
        
        return df_c, df_b
    except Exception as e:
        print("Error parsing:", e)
        return None

for m in ["VMD-GRU", "ICEEMDAN-VMD-GRU"]:
    fol = os.path.join(m, "Gunung geger")
    res = parse_vmd_candidates(fol)
    if res:
        df_c, df_b = res
        print(f"\n=== {m} ===")
        print("Candidates columns:", list(df_c.columns))
        print("Candidates count:", len(df_c))
        print("Sample candidate:", df_c.iloc[0].to_dict())
        print("Best columns:", list(df_b.columns))
        print("Best count:", len(df_b))
        print("Sample best:", df_b.iloc[0].to_dict())
