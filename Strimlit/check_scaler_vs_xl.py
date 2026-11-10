import os
import joblib
import pandas as pd
import numpy as np

folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
sc = joblib.load(os.path.join(folder, "scaler/scaler_IMF_1_VMD_1.pkl"))
print("scaler min_:", sc.min_, "data_min_:", sc.data_min_, "data_max_:", sc.data_max_, "data_range_:", sc.data_range_)

norm_xl = os.path.join(folder, "hasil-normalisasi", "normalisasi_hasil_lengkap.xlsx")
df_mm = pd.read_excel(norm_xl, sheet_name="Ringkasan_MinMax", header=2)
print(df_mm.head(5))
