import sys, os, re, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

def muat_vmd_all_dari_folder(folder, metode, h):
    p = os.path.join(folder, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    if not os.path.exists(p):
        return None
    try:
        df_c_raw = pd.read_excel(p, sheet_name="Pencarian_Parameter", header=None)
        h_idx = -1
        for idx, row in df_c_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if "k" in row_str and "alpha" in row_str:
                h_idx = idx
                break
        if h_idx == -1: return None
        df_c = df_c_raw.iloc[h_idx+1:].dropna(how="all").copy()
        df_c.columns = [str(x).strip() for x in df_c_raw.iloc[h_idx].values]

        df_b_raw = pd.read_excel(p, sheet_name="Parameter_Optimal", header=None)
        b_idx = -1
        for idx, row in df_b_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if any("k optimal" in x or "k_optimal" in x for x in row_str):
                b_idx = idx
                break
        if b_idx == -1: return None
        df_b = df_b_raw.iloc[b_idx+1:].dropna(how="all").copy()
        df_b.columns = [str(x).strip() for x in df_b_raw.iloc[b_idx].values]

        first_c = df_c.columns[0]
        first_b = df_b.columns[0]

        vmd_all = {}
        if metode == "Hybrid VMD-GRU":
            signal_name = "Visitors"
            cands = []
            for _, r in df_c.iterrows():
                cands.append({
                    "K": int(r["K"]), "alpha": int(r["Alpha"]),
                    "Corr": float(r["Korelasi Antar-Mode"]),
                    "ELC": float(r["ELC (Error Rekonstruksi)"]),
                    "BW": float(r["Bandwidth Rata-rata"]),
                })
            r_b = df_b.iloc[0]
            best = {
                "K": int(r_b["K Optimal"]), "alpha": int(r_b["Alpha Optimal"]),
                "Corr": float(r_b["Korelasi"]), "ELC": float(r_b["ELC"]),
                "BW": float(r_b["Bandwidth"]),
            }
            vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith("VMD_")],
                              key=lambda x: int(x.split("_")[1]) if x.split("_")[1].isdigit() else 0)
            modes = np.array([h["comps"][k] for k in vmd_keys], dtype=float) if vmd_keys else np.zeros((best["K"], len(h["aktual_hist"])))
            vmd_all[signal_name] = {"candidates": cands, "best": best, "modes": modes}

        elif metode == "Hybrid ICEEMDAN-VMD-GRU":
            for _, r_b in df_b.iterrows():
                imf_name = str(r_b[first_b]).strip()
                sub_c = df_c[df_c[first_c].astype(str).str.strip() == imf_name]
                cands = []
                for _, r in sub_c.iterrows():
                    cands.append({
                        "K": int(r["K"]), "alpha": int(r["Alpha"]),
                        "Corr": float(r["Korelasi Antar-Mode"]),
                        "ELC": float(r["ELC (Error Rekonstruksi)"]),
                        "BW": float(r["Bandwidth Rata-rata"]),
                    })
                best = {
                    "K": int(r_b["K Optimal"]), "alpha": int(r_b["Alpha Optimal"]),
                    "Corr": float(r_b["Korelasi"]), "ELC": float(r_b["ELC"]),
                    "BW": float(r_b["Bandwidth"]),
                }
                prefix = f"{imf_name}_VMD_"
                vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith(prefix)],
                                  key=lambda x: int(x.split("_VMD_")[1]) if x.split("_VMD_")[1].isdigit() else 0)
                modes = np.array([h["comps"][k] for k in vmd_keys], dtype=float) if vmd_keys else np.zeros((best["K"], len(h["aktual_hist"])))
                vmd_all[imf_name] = {"candidates": cands, "best": best, "modes": modes}

        return vmd_all
    except Exception as e:
        print("Error parsing vmd_all:", e)
        return None

import admin_methods as am
dest = "Gunung geger"
for m in ["Hybrid VMD-GRU", "Hybrid ICEEMDAN-VMD-GRU"]:
    fol = am.cari_folder(m, dest)
    h = am.muat_hasil_folder(fol, dest, m)
    vmd_all = muat_vmd_all_dari_folder(fol, m, h)
    print(f"\n=== {m} ===")
    if vmd_all:
        for name, r in vmd_all.items():
            print(f"  {name}: {len(r['candidates'])} candidates, best: K={r['best']['K']}, alpha={r['best']['alpha']}, BW={r['best']['BW']:.5f}, modes shape: {r['modes'].shape}")
    else:
        print("  Failed to load vmd_all!")
