import os
import sys
import glob
import joblib
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

fol = "ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
preds_dir = os.path.join(fol, "retrain-preds")
scaler_dir = os.path.join(fol, "scaler")
inter_p = os.path.join(fol, "hasil-interpolasi", "data_cleaned_after_imputation.xlsx")

df_clean = pd.read_excel(inter_p, sheet_name="cleaned_data")
orig_min = float(df_clean['visitors'].min())
orig_max = float(df_clean['visitors'].max())

pred_files = glob.glob(os.path.join(preds_dir, "preds_*.csv"))
y_pred_den_dict = {}

for pf in pred_files:
    comp = os.path.splitext(os.path.basename(pf))[0].replace("preds_", "")
    dfp = pd.read_csv(pf)
    y_true_n = dfp['y_true'].values.astype(float)
    y_pred_n = dfp['y_pred'].values.astype(float)
    
    sf = os.path.join(scaler_dir, f"scaler_{comp}.pkl")
    if os.path.exists(sf):
        scaler = joblib.load(sf)
        y_pred_den = scaler.inverse_transform(y_pred_n.reshape(-1, 1)).ravel()
        y_true_den = scaler.inverse_transform(y_true_n.reshape(-1, 1)).ravel()
    else:
        y_pred_den, y_true_den = y_pred_n, y_true_n
    y_pred_den_dict[comp] = y_pred_den

test_len = len(list(y_pred_den_dict.values())[0])
test_dates = pd.to_datetime(df_clean['date'].iloc[-test_len:]).values
actual_test_signal = df_clean['visitors'].iloc[-test_len:].values.astype(float)

# 1. Denormalized reconstruction (skala asli pengunjung)
x_pred_den_final = np.sum([y_pred_den_dict[c] for c in y_pred_den_dict.keys()], axis=0)

# 2. Normalized reconstruction (skala 0-1)
x_pred_norm_final = (x_pred_den_final - orig_min) / (orig_max - orig_min + 1e-8)
x_pred_norm_final = np.clip(x_pred_norm_final, 0.0, 1.0)
x_true_norm_final = (actual_test_signal - orig_min) / (orig_max - orig_min + 1e-8)

mae_denorm = float(np.mean(np.abs(actual_test_signal - x_pred_den_final)))
mape_denorm = float(np.mean(np.abs((actual_test_signal - x_pred_den_final) / actual_test_signal))) * 100
mae_norm = float(np.mean(np.abs(x_true_norm_final - x_pred_norm_final)))
mape_norm = float(np.mean(np.abs((x_true_norm_final - x_pred_norm_final) / np.maximum(x_true_norm_final, 1e-8)))) * 100

print(f"Denorm Scale: MAE = {mae_denorm:.2f}, MAPE = {mape_denorm:.2f}%")
print(f"Norm Scale [0, 1]: MAE = {mae_norm:.4f}, MAPE = {mape_norm:.2f}%")
print(f"x_true_norm_final range: [{x_true_norm_final.min():.4f}, {x_true_norm_final.max():.4f}]")
print(f"x_pred_norm_final range: [{x_pred_norm_final.min():.4f}, {x_pred_norm_final.max():.4f}]")
print(f"actual_test_signal range: [{actual_test_signal.min():.0f}, {actual_test_signal.max():.0f}]")
print(f"x_pred_den_final range: [{x_pred_den_final.min():.0f}, {x_pred_den_final.max():.0f}]")
