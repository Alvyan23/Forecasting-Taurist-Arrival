import os
import joblib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==================================================
# Helper 1: Safe MAPE (0–100%)
# ==================================================
def safe_mape(y_true, y_pred, eps=1e-8):
  y_true = np.asarray(y_true).reshape(-1)
  y_pred = np.asarray(y_pred).reshape(-1)
  denom = np.maximum(np.abs(y_true), eps)
  return float(np.mean(np.abs((y_true - y_pred) / denom)))


# ==================================================
# PATH & SETUP LOKASI FILE
# ==================================================
preds_dir = 'retrain-preds'
scaler_dir = 'scaler'

print('=' * 75)
print('📊 EVALUASI DENORMALISASI & REKONSTRUKSI PREDIKSI HYBRID I-CEEMDAN-VMD')
print('=' * 75)

# ==================================================
# 1) PENYIAPAN DATA AKTUAL & SIGNAL ASLI
# ==================================================
# Memastikan data_clean atau file Excel dapat diakses
if 'data_clean' in globals():
  df_raw = data_clean.copy()
else:
  import glob

  files = glob.glob('*.xlsx')
  df_raw = pd.read_excel(files[0])
  df_raw['Tahun'] = df_raw['Tahun'].ffill().astype(int)
  bulan_map = {
      'Januari': 'January',
      'Februari': 'February',
      'Maret': 'March',
      'April': 'April',
      'Mei': 'May',
      'Juni': 'June',
      'Juli': 'July',
      'Agustus': 'August',
      'September': 'September',
      'Oktober': 'October',
      'November': 'November',
      'Desember': 'December',
  }
  date_str = (
      df_raw['Bulan'].astype(str).str.strip().replace(bulan_map, regex=True)
      + ' '
      + df_raw['Tahun'].astype(str)
  )
  df_raw['date'] = pd.to_datetime(date_str, format='%B %Y')
  df_raw['visitors'] = df_raw['Pengunjung']

# Ambil min dan max asli dari sinyal sebelum normalisasi
orig_min = float(df_raw['visitors'].min())
orig_max = float(df_raw['visitors'].max())

# Normalized signal aktual 0–1
df_norm = df_raw.copy()
df_norm['visitors_norm'] = (df_raw['visitors'] - orig_min) / (
    orig_max - orig_min + 1e-8
)

# ==================================================
# 2) PANJANG TEST SET & PENYELARASAN DATES
# ==================================================
# Ambil komponen dari best_params
components = list(best_params.keys())
sample_comp = components[0]
sample_preds = pd.read_csv(os.path.join(preds_dir, f'preds_{sample_comp}.csv'))
test_len = len(sample_preds)

# Ambil tanggal dan nilai aktual normalisasi khusus test set
test_dates = df_norm['date'].iloc[-test_len:].values
actual_test_signal_norm = (
    df_norm['visitors_norm'].iloc[-test_len:].values.astype(float)
)

# ==================================================
# 3) LOOP EVALUASI PER SUB-MODE / KOMPONEN (NORMALIZED)
# ==================================================
y_pred_den_dict = {}
imf_metrics_rows = []

print('\n🔍 Evaluasi Prediksi Per Sub-Mode / Komponen:')

for comp in components:
  pred_file = os.path.join(preds_dir, f'preds_{comp}.csv')
  if not os.path.exists(pred_file):
    print(f'⚠️ Warning: File {pred_file} tidak ditemukan. Skip...')
    continue

  dfp = pd.read_csv(pred_file)
  y_true_norm = dfp['y_true'].values.astype(float)
  y_pred_norm = dfp['y_pred'].values.astype(float)

  # Inverse transform / denormalisasi ke skala asli sub-mode
  scaler_file = os.path.join(scaler_dir, f'scaler_{comp}.pkl')
  if os.path.exists(scaler_file):
    scaler = joblib.load(scaler_file)
    y_pred_den_dict[comp] = scaler.inverse_transform(
        y_pred_norm.reshape(-1, 1)
    ).ravel()
  else:
    y_pred_den_dict[comp] = y_pred_norm

  # Metrik performa per sub-mode (Normalized 0–1)
  imf_mae = mean_absolute_error(y_true_norm, y_pred_norm)
  imf_rmse = float(np.sqrt(mean_squared_error(y_true_norm, y_pred_norm)))
  imf_mape = safe_mape(y_true_norm, y_pred_norm) * 100

  imf_metrics_rows.append({
      'Sub-Component': comp,
      'MAE (Norm)': imf_mae,
      'RMSE (Norm)': imf_rmse,
      'MAPE (Norm) %': imf_mape,
  })

  # Visualisasi Per Sub-Mode
  plt.figure(figsize=(10, 3.2))
  plt.plot(
      test_dates,
      y_true_norm,
      label='Actual (Norm)',
      color='#1f77b4',
      linewidth=1.8,
  )
  plt.plot(
      test_dates,
      y_pred_norm,
      label='Predicted (Norm)',
      color='#ff7f0e',
      linestyle='--',
      linewidth=1.5,
  )
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
  plt.title(
      f'{comp} | Actual vs Predicted (Normalized 0–1)\nMAE = {imf_mae:.4f} |'
      f' MAPE = {imf_mape:.2f}%',
      fontsize=10,
      fontweight='bold',
  )
  plt.ylabel('Value (0–1)')
  plt.legend(loc='upper right')
  plt.grid(True, linestyle=':', alpha=0.5)
  plt.tight_layout()
  plt.show()

# Tabel Ringkasan Metrik Per Sub-Mode
imf_metrics_df = pd.DataFrame(imf_metrics_rows)
print('\n📋 Metrik Evaluasi Prediksi Per Sub-Mode / Komponen:')
display(imf_metrics_df)

# ==================================================
# 4) REKONSTRUKSI SINYAL PREDIKSI (SKALA ASLI -> NORMALIZED)
# ==================================================
# Sum of all predicted sub-modes in original scale
x_pred_recon = np.sum(
    [y_pred_den_dict[c] for c in y_pred_den_dict.keys()], axis=0
)

# Normalisasi hasil rekonstruksi prediksi ke skala 0–1 menggunakan min-max asli
x_pred_norm_final = (x_pred_recon - orig_min) / (orig_max - orig_min + 1e-8)
x_pred_norm_final = np.clip(x_pred_norm_final, 0.0, 1.0)

x_true_norm_final = actual_test_signal_norm

# ==================================================
# 5) METRIK FINAL HASIL REKONSTRUKSI
# ==================================================
final_mae_norm = mean_absolute_error(x_true_norm_final, x_pred_norm_final)
final_rmse_norm = float(
    np.sqrt(mean_squared_error(x_true_norm_final, x_pred_norm_final))
)
final_mape_norm = safe_mape(x_true_norm_final, x_pred_norm_final) * 100

df_recon_norm = pd.DataFrame({
    'Date': [str(d)[:10] for d in test_dates],
    'Actual_Signal_Norm': x_true_norm_final,
    'Predicted_Signal_Norm': x_pred_norm_final,
})
df_recon_norm['Abs_Error'] = np.abs(
    df_recon_norm['Actual_Signal_Norm'] - df_recon_norm['Predicted_Signal_Norm']
)

print('\n' + '=' * 75)
print('📋 TABEL AKTUAL vs PREDIKSI REKONSTRUKSI (NORMALIZED 0–1)')
print('=' * 75)
display(df_recon_norm)

print('\n✅ EVALUASI AKHIR SINYAL REKONSTRUKSI (NORMALIZED 0–1):')
print(f'   MAE  : {final_mae_norm:.4f}')
print(f'   RMSE : {final_rmse_norm:.4f}')
print(f'   MAPE : {final_mape_norm:.2f}%')

# ==================================================
# 6) VISUALISASI REKONSTRUKSI AKHIR
# ==================================================
plt.figure(figsize=(13, 5))
plt.plot(
    test_dates,
    x_true_norm_final,
    label='Actual Signal (Norm)',
    color='#1f77b4',
    linewidth=2.2,
    marker='o',
)
plt.plot(
    test_dates,
    x_pred_norm_final,
    label='Predicted Reconstruction (Norm)',
    color='#ff7f0e',
    linestyle='--',
    linewidth=1.8,
    marker='x',
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.title(
    'Perbandingan Sinyal Rekonstruksi Prediksi vs Sinyal Aktual (Normalized'
    ' 0–1)\n'
    f'MAE = {final_mae_norm:.4f} | RMSE = {final_rmse_norm:.4f} | MAPE ='
    f' {final_mape_norm:.2f}%',
    fontsize=12,
    fontweight='bold',
    pad=10,
)
plt.xlabel('Tanggal', fontsize=11)
plt.ylabel('Value (0–1)', fontsize=11)
plt.legend(loc='upper right', frameon=True)
plt.grid(True, linestyle=':', alpha=0.5)
plt.tight_layout()

# Simpan Grafik Evaluasi Final Rekonstruksi
os.makedirs('output_hasil/grafik', exist_ok=True)
plt.savefig(
    'output_hasil/grafik/06_final_reconstruction_prediction_norm.png',
    dpi=150,
    bbox_inches='tight',
)
plt.show()

print(
    '💾 Grafik disimpan:'
    ' output_hasil/grafik/06_final_reconstruction_prediction_norm.png'
)