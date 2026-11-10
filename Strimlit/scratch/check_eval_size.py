import sys, os, json, gzip, base64
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from scratch.test_admin_loading import nb_am

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

bench_eval = {}
for m in nb_am.METODE:
    bench_eval[m] = {}
    for d in dests:
        folder = nb_am.cari_folder(m, d)
        h = nb_am.muat_hasil_folder(folder, d, m)
        # Keep evaluation fields
        sub_modes = {}
        for sm_name, sm_val in h.get("sub_mode_preds", {}).items():
            sub_modes[sm_name] = {
                "mae_norm": sm_val.get("mae_norm"),
                "rmse_norm": sm_val.get("rmse_norm"),
                "mape_norm": sm_val.get("mape_norm"),
                "mae_den": sm_val.get("mae_den"),
                "rmse_den": sm_val.get("rmse_den"),
                "mape_den": sm_val.get("mape_den"),
            }
        item = {
            "destinasi": d,
            "metode": m,
            "tgl_hist": h["tgl_hist"],
            "aktual_hist": h["aktual_hist"],
            "raw_hist": h.get("raw_hist", h["aktual_hist"]),
            "gap_log": h.get("gap_log", []),
            "split_idx": h["split_idx"],
            "tgl_uji": h["tgl_uji"],
            "aktual_uji": h["aktual_uji"],
            "prediksi_uji": h["prediksi_uji"],
            "mae": h["mae"],
            "rmse": h.get("rmse"),
            "mape": h["mape"],
            "mae_norm": h.get("mae_norm"),
            "rmse_norm": h.get("rmse_norm"),
            "mape_norm": h.get("mape_norm"),
            "tgl_fut": h["tgl_fut"],
            "prediksi_fut": h["prediksi_fut"],
            "sub_mode_preds": sub_modes,
            "n_komponen": h.get("n_komponen", 1),
            "loaded_from_folder": True,
        }
        bench_eval[m][d] = item

raw_json = json.dumps(bench_eval)
compressed = gzip.compress(raw_json.encode('utf-8'))
b64 = base64.b64encode(compressed).decode('ascii')

print(f"Raw JSON size: {len(raw_json)} bytes ({len(raw_json)/1024:.1f} KB)")
print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
print(f"Base64 string length: {len(b64)} chars ({len(b64)/1024:.1f} KB)")
