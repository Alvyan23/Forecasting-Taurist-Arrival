import sys
import os
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

import admin_methods as am

folder = am.cari_folder("Hybrid ICEEMDAN-VMD-GRU", "Makam Syaikhona Kholil")
h = am.muat_hasil_folder(folder, "Makam Syaikhona Kholil", "Hybrid ICEEMDAN-VMD-GRU")

print("Testing figures:")
f_int = am.fig_interpolasi(h)
print("  fig_interpolasi:", type(f_int))

f_ice = am.fig_iceemdan(h)
print("  fig_iceemdan:", type(f_ice))

f_vmd = am.fig_vmd(h)
print("  fig_vmd:", type(f_vmd))

comps = list(h.get("comps", {}).keys())
f_norm = am.fig_normalisasi(h, comps[0] if comps else None)
print("  fig_normalisasi:", type(f_norm))

f_den_tot = am.fig_denormalisasi(h, None)
print("  fig_denormalisasi (total):", type(f_den_tot))

f_den_sub = am.fig_denormalisasi(h, list(h.get("sub_mode_preds", {}).keys())[0])
print("  fig_denormalisasi (sub):", type(f_den_sub))

f_akt = am.fig_aktual_prediksi(h)
print("  fig_aktual_prediksi:", type(f_akt))

f_fut = am.fig_masa_depan(h)
print("  fig_masa_depan:", type(f_fut))

print("All figure generators executed successfully!")
