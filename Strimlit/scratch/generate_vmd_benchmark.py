import sys, os, json, gzip, base64, re, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

import admin_methods as am
from scratch.test_vmd_all_builder import muat_vmd_all_dari_folder

def _nn(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

def load_ice_xlsx(folder):
    ice = {}
    ice_xlsx = os.path.join(folder, "output_hasil", "iceemdan_decomposition.xlsx")
    if os.path.exists(ice_xlsx):
        try:
            df_ice = pd.read_excel(ice_xlsx, header=None)
            for idx, row in df_ice.iterrows():
                row_str = [str(x).strip().lower() for x in row.values]
                if "imf_1" in row_str:
                    df_ice.columns = [str(x).strip() for x in row.values]
                    df_ice_data = df_ice.iloc[idx + 1:].dropna(how="all")
                    for c in df_ice_data.columns:
                        if re.match(r"^IMF_\d+$", c) or "residue" in c.lower():
                            ice[c] = pd.to_numeric(df_ice_data[c], errors="coerce").fillna(0).astype(float).tolist()
                    break
        except Exception:
            pass
    return ice

bench_all = {}
for m in am.METODE:
    m_key = _nn(m)
    bench_all[m_key] = {}
    for d in dests:
        d_key = _nn(d)
        fol = am.cari_folder(m, d)
        h = am.muat_hasil_folder(fol, d, m)
        sub_modes = {}
        for sm_name, sm_val in h.get("sub_mode_preds", {}).items():
            sub_modes[sm_name] = {
                "mae_norm": float(sm_val.get("mae_norm", 0.0)),
                "rmse_norm": float(sm_val.get("rmse_norm", 0.0)),
                "mape_norm": float(sm_val.get("mape_norm", 0.0)),
                "mae_den": float(sm_val.get("mae_den", 0.0)),
                "rmse_den": float(sm_val.get("rmse_den", 0.0)),
                "mape_den": float(sm_val.get("mape_den", 0.0)),
            }
        item = {
            "destinasi": d,
            "metode": m,
            "tgl_hist": list(h["tgl_hist"]),
            "aktual_hist": [round(float(x), 4) for x in h["aktual_hist"]],
            "raw_hist": [round(float(x), 4) for x in h.get("raw_hist", h["aktual_hist"])],
            "gap_log": h.get("gap_log", []),
            "split_idx": int(h["split_idx"]),
            "tgl_uji": list(h["tgl_uji"]),
            "aktual_uji": [round(float(x), 4) for x in h["aktual_uji"]],
            "prediksi_uji": [round(float(x), 4) for x in h["prediksi_uji"]],
            "mae": float(h["mae"]),
            "rmse": float(h["rmse"]) if h.get("rmse") is not None else None,
            "mape": float(h["mape"]),
            "mae_norm": float(h["mae_norm"]) if h.get("mae_norm") is not None else None,
            "rmse_norm": float(h["rmse_norm"]) if h.get("rmse_norm") is not None else None,
            "mape_norm": float(h["mape_norm"]) if h.get("mape_norm") is not None else None,
            "tgl_fut": list(h["tgl_fut"]),
            "prediksi_fut": [float(x) for x in h["prediksi_fut"]],
            "sub_mode_preds": sub_modes,
            "n_komponen": int(h.get("n_komponen", 1)),
            "loaded_from_folder": True,
        }

        # Comps
        if "comps" in h and h["comps"]:
            item["comps"] = {k: [round(float(x), 4) for x in v] for k, v in h["comps"].items()}

        # Ice data
        ice = load_ice_xlsx(fol)
        if not ice and "ice_data" in h and h["ice_data"]:
            ice = h["ice_data"]
        if not ice and m == "Hybrid ICEEMDAN-GRU" and "comps" in h:
            ice = h["comps"]
        if ice:
            item["ice_data"] = {k: [round(float(x), 4) for x in v] for k, v in ice.items()}

        # VMD candidates & best
        if "VMD" in m:
            v_all = muat_vmd_all_dari_folder(fol, m, h)
            if v_all:
                item["vmd_search_data"] = {
                    name: {
                        "candidates": r["candidates"],
                        "best": r["best"]
                    } for name, r in v_all.items()
                }

        bench_all[m_key][d_key] = item

raw_json = json.dumps(bench_all)
compressed = gzip.compress(raw_json.encode('utf-8'))
b64 = base64.b64encode(compressed).decode('ascii')

print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
print(f"Base64 length: {len(b64)} chars ({len(b64)/1024:.1f} KB)")

with open("scratch/benchmarks_admin_vmd_b64.txt", "w", encoding="utf-8") as f:
    f.write(b64)
print("Saved to scratch/benchmarks_admin_vmd_b64.txt successfully!")
