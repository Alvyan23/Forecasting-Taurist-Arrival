import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import admin_methods as am

def get_cands_and_best_for_imf(df_c, df_b, signal_name):
    # filter df_c by signal_name if column 0 exists
    first_col_c = df_c.columns[0]
    if signal_name:
        sub_c = df_c[df_c[first_col_c].astype(str) == signal_name]
    else:
        sub_c = df_c
        
    cands = []
    for _, r in sub_c.iterrows():
        cands.append({
            "K": int(r["K"]),
            "alpha": int(r["Alpha"]),
            "BW": float(r["Bandwidth Rata-rata"]),
            "ELC": float(r["ELC (Error Rekonstruksi)"]),
            "Corr": float(r["Korelasi Antar-Mode"]),
        })
        
    first_col_b = df_b.columns[0]
    if signal_name:
        sub_b = df_b[df_b[first_col_b].astype(str) == signal_name]
    else:
        sub_b = df_b
    r_b = sub_b.iloc[0]
    best = {
        "K": int(r_b["K Optimal"]),
        "alpha": int(r_b["Alpha Optimal"]),
        "BW": float(r_b["Bandwidth"]),
        "ELC": float(r_b["ELC"]),
        "Corr": float(r_b["Korelasi"]),
    }
    return cands, best

from scratch.test_parse_candidates import parse_vmd_candidates

for m in ["VMD-GRU", "ICEEMDAN-VMD-GRU"]:
    fol = os.path.join(m, "Gunung geger")
    df_c, df_b = parse_vmd_candidates(fol)
    print(f"\n=== {m} ===")
    if m == "VMD-GRU":
        cands, best = get_cands_and_best_for_imf(df_c, df_b, "Visitors")
        fig = am.fig_vmd_search(cands, best)
        print("VMD-GRU fig_vmd_search created successfully! Trace count:", len(fig.data))
        print("Best:", best)
    else:
        for imf in ["IMF_1", "IMF_2", "IMF_3", "IMF_4"]:
            cands, best = get_cands_and_best_for_imf(df_c, df_b, imf)
            fig = am.fig_vmd_search(cands, best)
            print(f"ICEEMDAN-VMD-GRU {imf} fig_vmd_search created! Trace count: {len(fig.data)}, Best: {best}")
