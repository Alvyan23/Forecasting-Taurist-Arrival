import sys
import os
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

import admin_methods as am

folder = am.cari_folder("Hybrid ICEEMDAN-VMD-GRU", "Makam Syaikhona Kholil")
print("Found folder:", folder)
h = am.muat_hasil_folder(folder, "Makam Syaikhona Kholil", "Hybrid ICEEMDAN-VMD-GRU")

print("Keys in h:", list(h.keys()))
print(f"MAE: {h['mae']:.2f}")
print(f"MAPE: {h['mape']:.2f}%")
print(f"Test dates: {h['tgl_uji'][0]} to {h['tgl_uji'][-1]} ({len(h['tgl_uji'])} points)")
print(f"Aktual uji sample: {h['aktual_uji'][:3]}")
print(f"Prediksi uji sample: {h['prediksi_uji'][:3]}")
print(f"Sub-modes count: {len(h.get('sub_mode_preds', {}))}")
print(f"PNGs found: {list(h.get('png_map', {}).keys())}")
