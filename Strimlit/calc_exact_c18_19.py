import sys
import os
import json
import pandas as pd
import numpy as np
import joblib
import warnings

warnings.simplefilter("ignore")
folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
with open(os.path.join(folder, "best-parameter-gru/best_gru_params_per_mode.json")) as f:
    best_params = json.load(f)

preds_dir = os.path.join(folder, "retrain-preds")
scaler_dir = os.path.join(folder, "scaler")
df_raw = pd.read_excel(os.path.join(folder, "hasil-interpolasi/data_cleaned_after_imputation.xlsx"))

orig_min = float(df_raw['visitors'].min())
orig_max = float(df_raw['visitors'].max())
df_norm = df_raw.copy()
df_norm['visitors_norm'] = (df_raw['visitors'] - orig_min) / (orig_max - orig_min + 1e-8)

components = list(best_params.keys())
sample_comp = components[0]
sample_preds = pd.read_csv(os.path.join(preds_dir, f'preds_{sample_comp}.csv'))
test_len = len(sample_preds)

test_dates = df_norm['date'].iloc[-test_len:].values
actual_test_signal = df_raw['visitors'].iloc[-test_len:].values.astype(float)
actual_test_signal_norm = df_norm['visitors_norm'].iloc[-test_len:].values.astype(float)

y_pred_den_dict = {}
for comp in components:
    dfp = pd.read_csv(os.path.join(preds_dir, f'preds_{comp}.csv'))
    yp = dfp['y_pred'].values.reshape(-1, 1)
    sc = joblib.load(os.path.join(scaler_dir, f'scaler_{comp}.pkl'))
    y_pred_den_dict[comp] = sc.inverse_transform(yp).ravel()

x_pred_recon = np.sum([y_pred_den_dict[c] for c in components], axis=0)
x_pred_norm_final = (x_pred_recon - orig_min) / (orig_max - orig_min + 1e-8)
x_pred_norm_final = np.clip(x_pred_norm_final, 0.0, 1.0)

from sklearn.metrics import mean_absolute_error, mean_squared_error
def safe_mape(y_true, y_pred):
    return float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8)))) * 100

print("Norm MAE:", mean_absolute_error(actual_test_signal_norm, x_pred_norm_final))
print("Norm RMSE:", np.sqrt(mean_squared_error(actual_test_signal_norm, x_pred_norm_final)))
print("Norm MAPE:", safe_mape(actual_test_signal_norm, x_pred_norm_final))

print("Asli MAE:", mean_absolute_error(actual_test_signal, x_pred_recon))
print("Asli RMSE:", np.sqrt(mean_squared_error(actual_test_signal, x_pred_recon)))
print("Asli MAPE:", safe_mape(actual_test_signal, x_pred_recon))
