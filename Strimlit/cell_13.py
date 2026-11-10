import os
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_absolute_error

# ─── 1. Membaca Hasil Dekomposisi & Data Preprocessing ─────────
# Membaca hasil sub-komponen hybrid yang sudah disimpan
imfs_df = pd.read_csv('hasil-dekomposisi/imfs.csv')

# Rekonstruksi sinyal (penjumlahan seluruh sub-komponen VMD + Residu ICEEMDAN)
reconstructed_signal = imfs_df.sum(axis=1)

# Sinyal asli dan tanggal dari data preprocessing (data_clean)
original_signal = data_clean['visitors'].values
dates = data_clean['date']

# ─── 2. Evaluasi Rekonstruksi (MAE) ───────────────────────────
mae = mean_absolute_error(original_signal, reconstructed_signal)

print('=' * 65)
print('📊 EVALUASI REKONSTRUKSI HYBRID I-CEEMDAN - VMD')
print('=' * 65)
print(f'Mean Absolute Error (MAE): {mae:.6f}')

# ─── 3. Visualisasi Sinyal Asli vs Rekonstruksi ────────────────
plt.figure(figsize=(14, 6))

# Plot Sinyal Asli (Interpolasi)
plt.plot(
    dates,
    original_signal,
    label='Sinyal Asli (Interpolasi)',
    color='black',
    linewidth=1.8,
)

# Plot Sinyal Rekonstruksi (Sum of Hybrid Components)
plt.plot(
    dates,
    reconstructed_signal,
    label='Sinyal Rekonstruksi (Hybrid I-CEEMDAN - VMD)',
    color='red',
    linestyle='--',
    linewidth=1.5,
    alpha=0.85,
)

plt.title(
    f'Perbandingan Sinyal Asli dan Hasil Rekonstruksi Hybrid I-CEEMDAN - VMD\n(MAE = {mae:.6f})',
    fontsize=13,
    fontweight='bold',
    pad=12,
)
plt.xlabel('Tanggal', fontsize=11)
plt.ylabel('Jumlah Pengunjung', fontsize=11)
plt.legend(loc='upper right', frameon=True)
plt.grid(True, alpha=0.3)

plt.tight_layout()

# Simpan Grafik Evaluasi Rekonstruksi
os.makedirs('output_hasil/grafik', exist_ok=True)
plt.savefig(
    'output_hasil/grafik/04_reconstruction_hybrid_iceemdan_vmd.png',
    dpi=150,
    bbox_inches='tight',
)
plt.show()

print(
    '💾 Grafik disimpan:'
    ' output_hasil/grafik/04_reconstruction_hybrid_iceemdan_vmd.png'
)