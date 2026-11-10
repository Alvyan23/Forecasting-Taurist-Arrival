import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# test on all destinations for Hybrid ICEEMDAN-VMD-GRU
dests = [
    "Makam Syaikhona Kholil",
    "Kolla Langgundi",
    "Makam Sunan Cendana",
    "Makam Air Mata Ibu",
    "Gunung Geger"
]

for d in dests:
    p = os.path.join("ICEEMDAN-VMD-GRU", d)
    if not os.path.exists(p):
        for s in os.listdir("ICEEMDAN-VMD-GRU"):
            if s.lower() == d.lower():
                p = os.path.join("ICEEMDAN-VMD-GRU", s); break
    
    inter_p = os.path.join(p, "hasil-interpolasi", "data_cleaned_after_imputation.xlsx")
    assert os.path.exists(inter_p), f"Missing inter in {d}"
    
    df_clean = pd.read_excel(inter_p, sheet_name="cleaned_data")
    orig_min = float(df_clean['visitors'].min())
    orig_max = float(df_clean['visitors'].max())
    
    fut_p = os.path.join(p, "hasil-prediksi-future", "future_predictions_12_months.csv")
    assert os.path.exists(fut_p), f"Missing fut in {d}"
    
    png_dir = os.path.join(p, "output_hasil", "grafik")
    pngs = os.listdir(png_dir) if os.path.exists(png_dir) else []
    
    print(f"[{d}]: min={orig_min}, max={orig_max}, PNGs={len(pngs)}")

print("\nAll 5 destination folders validated successfully!")
