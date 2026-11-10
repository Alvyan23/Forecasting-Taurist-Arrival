import sys
import os
import json
import pandas as pd
import numpy as np
import warnings

sys.stdout.reconfigure(encoding='utf-8')
warnings.simplefilter("ignore")

base = "./ICEEMDAN-VMD-GRU"
dests = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

for dest in dests:
    folder = os.path.join(base, dest)
    imf_p = os.path.join(folder, "hasil-interpolasi/data_cleaned_after_imputation.xlsx")
    if not os.path.exists(imf_p):
        continue
    df_raw = pd.read_excel(imf_p)
    orig_min = float(df_raw['visitors'].min())
    orig_max = float(df_raw['visitors'].max())
    
    preds_dir = os.path.join(folder, "retrain-preds")
    scaler_dir = os.path.join(folder, "scaler")
    
    pfiles = [f for f in os.listdir(preds_dir) if f.startswith('preds_') and f.endswith('.csv')]
    sample_df = pd.read_csv(os.path.join(preds_dir, pfiles[0]))
    test_len = len(sample_df)
    
    akt_uji = df_raw['visitors'].iloc[-test_len:].values.astype(float)
    akt_uji_norm = (akt_uji - orig_min) / (orig_max - orig_min + 1e-8)
    
    # Let's test min_max_summary denorm vs joblib scaler denorm
    norm_xl = os.path.join(folder, "hasil-normalisasi", "normalisasi_hasil_lengkap.xlsx")
    mm_map = {}
    if os.path.exists(norm_xl):
        try:
            df_mm = pd.read_excel(norm_xl, sheet_name="Ringkasan_MinMax", header=2).dropna(subset=['Sub-Komponen'])
            for _, r in df_mm.iterrows():
                mm_map[str(r['Sub-Komponen'])] = {'min': float(r['Min']), 'max': float(r['Max']), 'range': float(r['Range'])}
        except Exception as e:
            pass
            
    y_preds_den = []
    for pf in pfiles:
        cname = pf.replace('preds_', '').replace('.csv', '')
        dfp = pd.read_csv(os.path.join(preds_dir, pf))
        yp_norm = dfp['y_pred'].values.astype(float)
        if cname in mm_map and mm_map[cname]['range'] > 0:
            yp_den = yp_norm * mm_map[cname]['range'] + mm_map[cname]['min']
        else:
            yp_den = yp_norm
        y_preds_den.append(yp_den)
        
    pred_uji = np.sum(y_preds_den, axis=0)
    pred_norm = np.clip((pred_uji - orig_min) / (orig_max - orig_min + 1e-8), 0.0, 1.0)
    
    mae_norm = np.mean(np.abs(akt_uji_norm - pred_norm))
    mape_norm = np.mean(np.abs((akt_uji_norm - pred_norm) / np.maximum(np.abs(akt_uji_norm), 1e-8))) * 100
    
    mae_asli = np.mean(np.abs(akt_uji - pred_uji))
    mape_asli = np.mean(np.abs((akt_uji - pred_uji) / np.maximum(np.abs(akt_uji), 1e-8))) * 100
    
    print(f"Dest: {dest}")
    print(f"  Test len: {test_len}")
    print(f"  Norm: MAE={mae_norm:.4f}, MAPE={mape_norm:.2f}%")
    print(f"  Asli: MAE={mae_asli:,.2f}, MAPE={mape_asli:.2f}%")
