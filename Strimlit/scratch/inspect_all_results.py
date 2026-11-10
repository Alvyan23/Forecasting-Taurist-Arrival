import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import json

# Let's inspect what muat_hasil_folder returns for each method
from scratch.test_admin_loading import nb_am

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

all_data = {}
for m in nb_am.METODE:
    all_data[m] = {}
    for d in dests:
        folder = nb_am.cari_folder(m, d)
        h = nb_am.muat_hasil_folder(folder, d, m)
        print(f"[{m}] [{d}] keys: {list(h.keys())}")
        print(f"    mae: {h.get('mae')}, rmse: {h.get('rmse')}, mape: {h.get('mape')}")
        print(f"    tgl_uji: len {len(h.get('tgl_uji', []))}, pred_uji: len {len(h.get('prediksi_uji', []))}")
        print(f"    tgl_fut: len {len(h.get('tgl_fut', []))}, pred_fut: len {len(h.get('prediksi_fut', []))}")
        print(f"    comps: {list(h.get('comps', {}).keys())}")
