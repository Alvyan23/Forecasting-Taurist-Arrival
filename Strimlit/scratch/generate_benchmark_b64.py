import sys, os, json, gzip, base64, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from scratch.test_admin_loading import nb_am

def _nn(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

bench_eval = {}
for m in nb_am.METODE:
    m_key = _nn(m)
    bench_eval[m_key] = {}
    for d in dests:
        d_key = _nn(d)
        folder = nb_am.cari_folder(m, d)
        h = nb_am.muat_hasil_folder(folder, d, m)
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
            "aktual_hist": [float(x) for x in h["aktual_hist"]],
            "raw_hist": [float(x) for x in h.get("raw_hist", h["aktual_hist"])],
            "gap_log": h.get("gap_log", []),
            "split_idx": int(h["split_idx"]),
            "tgl_uji": list(h["tgl_uji"]),
            "aktual_uji": [float(x) for x in h["aktual_uji"]],
            "prediksi_uji": [float(x) for x in h["prediksi_uji"]],
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
        if m == "Hybrid ICEEMDAN-VMD-GRU":
            if "ice_data" in h and h["ice_data"]:
                item["ice_data"] = {k: [round(float(x), 4) for x in v] for k, v in h["ice_data"].items()}
            if "comps" in h and h["comps"]:
                item["comps"] = {k: [round(float(x), 4) for x in v] for k, v in h["comps"].items()}

        bench_eval[m_key][d_key] = item

raw_json = json.dumps(bench_eval)
compressed = gzip.compress(raw_json.encode('utf-8'))
b64 = base64.b64encode(compressed).decode('ascii')

print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
print(f"Base64 length: {len(b64)} chars ({len(b64)/1024:.1f} KB)")

with open("scratch/benchmarks_admin_b64.txt", "w", encoding="utf-8") as f:
    f.write(b64)
