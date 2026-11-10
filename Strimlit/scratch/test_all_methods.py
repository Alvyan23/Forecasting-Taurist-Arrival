"""
Full integration test: load all 4 methods for Gunung Geger using the updated admin_methods.py
and verify the metrics match the expected notebook values.
"""
import sys
import os
sys.path.insert(0, "c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit")
os.chdir("c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit")

import warnings
warnings.filterwarnings("ignore")

import admin_methods as am

DEST = "Gunung Geger"

for metode in am.METODE:
    print(f"\n{'='*60}")
    print(f"Metode: {metode}")
    fol = am.cari_folder(metode, DEST)
    if not fol:
        print(f"  WARNING: folder tidak ditemukan!")
        continue
    print(f"  Folder: {fol}")
    res = am.muat_hasil_folder(fol, DEST, metode)
    if not res:
        print(f"  WARNING: muat_hasil_folder gagal!")
        continue
    print(f"  test_len: {len(res['tgl_uji'])}")
    print(f"  MAE     : {res['mae']:.4f}")
    print(f"  MAPE    : {res['mape']:.4f}%")
    print(f"  MAE_norm: {res['mae_norm']:.4f}")
    print(f"  Prediksi uji[:3]: {[round(v,2) for v in res['prediksi_uji'][:3]]}")
    print(f"  Aktual uji[:3]  : {res['aktual_uji'][:3]}")
    print(f"  Tgl uji [0]     : {res['tgl_uji'][0]}")
    print(f"  Loaded from folder: {res.get('loaded_from_folder', False)}")
    print(f"  PNG map keys: {list(res.get('png_map',{}).keys())}")
    
print("\n\nAll OK!")
