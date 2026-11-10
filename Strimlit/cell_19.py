import os
import joblib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from sklearn.metrics import mean_absolute_error, mean_squared_error


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def safe_mape(y_true, y_pred, eps=1e-8):
  """Menghitung Mean Absolute Percentage Error (MAPE) secara aman."""
  y_true = np.asarray(y_true).reshape(-1)
  y_pred = np.asarray(y_pred).reshape(-1)
  denom = np.maximum(np.abs(y_true), eps)
  return float(np.mean(np.abs((y_true - y_pred) / denom)))


def inverse_1d(scaler, arr_1d):
  """Melakukan inverse transform (denormalisasi) pada array 1D."""
  arr_1d = np.asarray(arr_1d).reshape(-1, 1)
  return scaler.inverse_transform(arr_1d).reshape(-1)


# =========================================================
# SETUP DATA TEST & LOKASI FILE
# =========================================================
preds_dir = 'retrain-preds'
scaler_dir = 'scaler'

print('=' * 75)
print('📊 EVALUASI PREDIKSI REKONSTRUKSI DALAM SKALA ASLI (DENORMALIZED)')
print('=' * 75)

# Mengambil seluruh sub-komponen dari hasil tuning/retrain
components = list(best_params.keys())

# Menentukan panjang data test set berdasarkan salah satu file hasil prediksi
sample_comp = components[0]
sample_preds = pd.read_csv(os.path.join(preds_dir, f'preds_{sample_comp}.csv'))
test_len = len(sample_preds)

# Mengambil tanggal dan jumlah pengunjung asli untuk test set
test_dates = data_clean['date'].iloc[-test_len:].values
actual_test_signal = (
    data_clean['visitors'].iloc[-test_len:].values.astype(float)
)

# =========================================================
# 1) EVALUASI & DENORMALISASI PER SUB-MODE
# =========================================================
y_pred_den_dict = {}
imf_metrics_rows = []

print('\n🔍 Evaluasi Prediksi Per Sub-Mode (Skala Asli Sub-Komponen):')

for comp in components:
  pred_path = os.path.join(preds_dir, f'preds_{comp}.csv')
  scaler_path = os.path.join(scaler_dir, f'scaler_{comp}.pkl')

  if not os.path.exists(pred_path):
    print(f'⚠️ File {pred_path} tidak ditemukan, skip...')
    continue

  dfp = pd.read_csv(pred_path)
  y_true_norm = dfp['y_true'].values.astype(float)
  y_pred_norm = dfp['y_pred'].values.astype(float)

  # Denormalisasi nilai prediksi & aktual milik sub-mode ini
  if os.path.exists(scaler_path):
    scaler = joblib.load(scaler_path)
    y_true_den = inverse_1d(scaler, y_true_norm)
    y_pred_den = inverse_1d(scaler, y_pred_norm)
  else:
    y_true_den, y_pred_den = y_true_norm, y_pred_norm

  # Simpan hasil denormalisasi prediksi ke dictionary
  y_pred_den_dict[comp] = y_pred_den

  # Hitung metrik evaluasi sub-mode dalam skala asli
  imf_mae = float(mean_absolute_error(y_true_den, y_pred_den))
  imf_rmse = float(np.sqrt(mean_squared_error(y_true_den, y_pred_den)))
  imf_mape = safe_mape(y_true_den, y_pred_den) * 100.0

  imf_metrics_rows.append({
      'Sub-Component': comp,
      'MAE (Denorm)': imf_mae,
      'RMSE (Denorm)': imf_rmse,
      'MAPE (Denorm) %': imf_mape,
  })

  # Tabel perbandingan individual sub-mode
  df_imf_comp = pd.DataFrame({
      'Date': pd.to_datetime(test_dates),
      'Actual_IMF': y_true_den,
      'Predicted_IMF': y_pred_den,
  })
  df_imf_comp['Abs_Error'] = np.abs(
      df_imf_comp['Actual_IMF'] - df_imf_comp['Predicted_IMF']
  )

  # Visualisasi Individual Sub-Mode
  plt.figure(figsize=(11, 3.5))
  plt.plot(
      test_dates,
      y_true_den,
      label='Actual (Denorm)',
      color='#1f77b4',
      linewidth=1.8,
  )
  plt.plot(
      test_dates,
      y_pred_den,
      label='Predicted (Denorm)',
      color='#ff7f0e',
      linestyle='--',
      linewidth=1.5,
  )
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
  plt.title(
      f'{comp} | Actual vs Predicted (Skala Asli)\nMAE = {imf_mae:.4f} | MAPE ='
      f' {imf_mape:.2f}%',
      fontsize=10,
      fontweight='bold',
  )
  plt.ylabel('Nilai')
  plt.legend(loc='upper right')
  plt.grid(True, linestyle=':', alpha=0.5)
  plt.tight_layout()
  plt.show()

# Ringkasan metrik seluruh sub-mode
imf_metrics_df = pd.DataFrame(imf_metrics_rows)
print('\n📋 RINGKASAN METRIK EVALUASI PER SUB-MODE:')
display(imf_metrics_df)

# =========================================================
# 2) REKONSTRUKSI PREDIKSI TOTAL (JUMLAH PENGUNJUNG ASLI)
# =========================================================
# Penjumlahan seluruh hasil denormalisasi sub-mode VMD + Residu ICEEMDAN
x_pred_den_final = np.sum(
    [y_pred_den_dict[c] for c in y_pred_den_dict.keys()], axis=0
)

# Hitung metrik evaluasi akhir (Sinyal Asli Total Pengunjung)
final_mae = float(mean_absolute_error(actual_test_signal, x_pred_den_final))
final_rmse = float(
    np.sqrt(mean_squared_error(actual_test_signal, x_pred_den_final))
)
final_mape = safe_mape(actual_test_signal, x_pred_den_final) * 100.0

# Tabel Hasil Rekonstruksi
df_recon = pd.DataFrame({
    'Date': pd.to_datetime(test_dates),
    'Actual': actual_test_signal.astype(float),
    'Predicted': x_pred_den_final.astype(float),
})
df_recon['Abs_Error'] = np.abs(df_recon['Actual'] - df_recon['Predicted'])

print('\n' + '=' * 75)
print('📋 TABEL AKTUAL vs PREDIKSI REKONSTRUKSI (SKALA ASLI PENGUNJUNG)')
print('=' * 75)
display(df_recon)

print('\n✅ HASIL EVALUASI AKHIR REKONSTRUKSI (SKALA ASLI):')
print(f'   MAE  : {final_mae:.2f}')
print(f'   RMSE : {final_rmse:.2f}')
print(f'   MAPE : {final_mape:.2f}%')

# =========================================================
# 3) VISUALISASI REKONSTRUKSI AKHIR
# =========================================================
plt.figure(figsize=(14, 6))
plt.plot(
    test_dates,
    actual_test_signal,
    label='Sinyal Aktual (Jumlah Pengunjung)',
    color='#1f77b4',
    linewidth=2.2,
    marker='o',
)
plt.plot(
    test_dates,
    x_pred_den_final,
    label='Prediksi Rekonstruksi (Hybrid I-CEEMDAN - VMD - GRU)',
    color='#ff7f0e',
    linestyle='--',
    linewidth=1.8,
    marker='x',
)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.gcf().autofmt_xdate()

plt.title(
    'Perbandingan Sinyal Aktual vs Hasil Prediksi Rekonstruksi (Skala'
    ' Asli)\n'
    f'MAE = {final_mae:.2f} | RMSE = {final_rmse:.2f} | MAPE ='
    f' {final_mape:.2f}%',
    fontsize=13,
    fontweight='bold',
    pad=12,
)
plt.xlabel('Periode / Tanggal', fontsize=11)
plt.ylabel('Jumlah Pengunjung', fontsize=11)
plt.legend(loc='upper right', frameon=True)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

# Simpan Grafik Evaluasi Final Rekonstruksi Skala Asli
os.makedirs('output_hasil/grafik', exist_ok=True)
output_chart_path = (
    'output_hasil/grafik/07_final_reconstruction_prediction_original_scale.png'
)
plt.savefig(output_chart_path, dpi=150, bbox_inches='tight')
plt.show()

print(f'\n💾 Grafik hasil rekonstruksi skala asli disimpan di: {output_chart_path}')