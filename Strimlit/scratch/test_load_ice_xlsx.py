import os, re, pandas as pd

def load_ice_xlsx(folder):
    ice = {}
    ice_xlsx = os.path.join(folder, "output_hasil", "iceemdan_decomposition.xlsx")
    if os.path.exists(ice_xlsx):
        df_ice = pd.read_excel(ice_xlsx, header=None)
        for idx, row in df_ice.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if "imf_1" in row_str:
                df_ice.columns = [str(x).strip() for x in row.values]
                df_ice_data = df_ice.iloc[idx+1:].dropna(how="all")
                for c in df_ice_data.columns:
                    if re.match(r"^IMF_\d+$", c) or "residue" in c.lower():
                        ice[c] = pd.to_numeric(df_ice_data[c], errors="coerce").fillna(0).astype(float).tolist()
                break
    return ice

for fol in ["ICEEMDAN-VMD-GRU/Gunung geger", "ICEEMDAN-GRU/Gunung Geger"]:
    res = load_ice_xlsx(fol)
    print(f"\nFolder: {fol}")
    print("Keys found:", list(res.keys()))
    for k in res:
        print(f"  {k}: len {len(res[k])}, min {min(res[k]):.2f}, max {max(res[k]):.2f}")
