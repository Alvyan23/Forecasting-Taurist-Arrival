import sys
import os
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
# Let's run exact cell 18 and 19 logic
preds_dir = os.path.join(folder, "retrain-preds")
scaler_dir = os.path.join(folder, "scaler")

df_raw = pd.read_excel(os.path.join(folder, "hasil-interpolasi/data_cleaned_after_imputation.xlsx"))
print("df_raw columns:", df_raw.columns.tolist())
orig_min = float(df_raw['visitors'].min())
orig_max = float(df_raw['visitors'].max())
print(f"orig_min: {orig_min}, orig_max: {orig_max}")

df_norm = df_raw.copy()
df_norm['visitors_norm'] = (df_raw['visitors'] - orig_min) / (orig_max - orig_min + 1e-8)

sample_preds = pd.read_csv(os.path.join(preds_dir, 'preds_IMF_1_VMD_1.csv'))
test_len = len(sample_preds)
print("test_len:", test_len)

test_dates = df_norm['date'].iloc[-test_len:].values
actual_test_signal = df_raw['visitors'].iloc[-test_len:].values
actual_test_signal_norm = df_norm['visitors_norm'].iloc[-test_len:].values

# Sum reconstructed predictions
pred_files = [f for f in os.listdir(preds_dir) if f.startswith('preds_') and f.endswith('.csv')]
import joblib

y_pred_den_dict = {}
for pf in pred_files:
    comp = pf.replace('preds_', '').replace('.csv', '')
    dfp = pd.read_csv(os.path.join(preds_dir, pf))
    yp = dfp['y_pred'].values.reshape(-1, 1)
    sc_path = os.path.join(scaler_dir, f"scaler_{comp}.pkl")
    if os.path.exists(sc_path):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scaler = joblib.load(sc_path)
            y_pred_den_dict[comp] = scaler.inverse_transform(yp).ravel()
    else:
        y_pred_den_dict[comp] = yp.ravel()

x_pred_recon = np.sum([y_pred_den_dict[c] for c in y_pred_den_dict.keys()], axis=0)
x_pred_norm_final = (x_pred_recon - orig_min) / (orig_max - orig_min + 1e-8)
x_pred_norm_final = np.clip(x_pred_norm_final, 0.0, 1.0)

mae_norm = np.mean(np.abs(actual_test_signal_norm - x_pred_norm_final))
mape_norm = np.mean(np.abs((actual_test_signal_norm - x_pred_norm_final) / actual_test_signal_norm)) * 100

mae_asli = np.mean(np.abs(actual_test_signal - x_pred_recon))
rmse_asli = np.sqrt(np.mean((actual_test_signal - x_pred_recon)**2))
mape_asli = np.mean(np.abs((actual_test_signal - x_pred_recon) / actual_test_signal)) * 100

print(f"Norm Scale: MAE={mae_norm:.4f}, MAPE={mape_norm:.2f}%")
print(f"Asli Scale: MAE={mae_asli:.2f}, RMSE={rmse_asli:.2f}, MAPE={mape_asli:.2f}%")

print("\nSample values:")
for i in range(5):
    d_str = str(test_dates[i])[:10]
    print(f"Date {d_str}: Act_Norm={actual_test_signal_norm[i]:.4f}, Pred_Norm={x_pred_norm_final[i]:.4f} | Act_Asli={actual_test_signal[i]:,.0f}, Pred_Asli={x_pred_recon[i]:,.0f}")
