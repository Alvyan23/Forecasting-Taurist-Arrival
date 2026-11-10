import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("scratch/test_new_admin"))

import importlib.util
spec = importlib.util.spec_from_file_location("test_am", "scratch/test_new_admin/admin_methods.py")
test_am = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_am)

print("Loaded test_am successfully!")
print("BENCHMARKS_ADMIN keys:", list(test_am.BENCHMARKS_ADMIN.keys()))

# Test jalankan_metode with NO folder found (simulate Google Colab)
# temporarily patch cari_folder to return None
orig_cari = test_am.cari_folder
test_am.cari_folder = lambda m, d: None

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

for m in test_am.METODE:
    print(f"\nTesting method without folder: {m}")
    for d in dests:
        res = test_am.jalankan_metode(d, None, m)
        print(f"  {d:25s} -> Loaded: {res.get('loaded_from_folder')}, MAE: {res.get('mae'):.2f}, MAPE: {res.get('mape'):.2f}%, Points: {len(res.get('prediksi_uji'))}")
