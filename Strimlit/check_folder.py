import sys
import os
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
print("Files in folder:")
for f in os.listdir(folder):
    print(" -", f)

if os.path.exists(os.path.join(folder, "data_cleaned_after_imputation.xlsx")):
    df = pd.read_excel(os.path.join(folder, "data_cleaned_after_imputation.xlsx"))
    print("\ndata_cleaned_after_imputation columns:", df.columns.tolist(), "shape:", df.shape)
    print(df.head(3))
