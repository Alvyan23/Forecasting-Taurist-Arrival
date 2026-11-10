import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# =========================================================
# 1. PERSIAPAN DIREKTORI
# =========================================================
os.makedirs('scaler', exist_ok=True)
os.makedirs('hasil-normalisasi', exist_ok=True)
os.makedirs('output_hasil/grafik', exist_ok=True)

# =========================================================
# 2. MEMBACA / MENYIAPKAN DATA KOMPONEN HYBRID
# =========================================================
# Menggunakan df_imfs_numeric bila tersedia di memori,
# jika tidak maka dibaca dari file imfs.csv hasil dekomposisi.
if 'df_imfs_numeric' in globals():
  data_to_normalize = df_imfs_numeric.copy()
else:
  data_to_normalize = pd.read_csv('hasil-dekomposisi/imfs.csv')

# ─── [PERBAIKAN] Menyiapkan kolom tanggal secara konsisten ─────
# Sebelumnya variabel `imfs` (dengan kolom 'date') dipakai langsung
# di script visualisasi tanpa dijamin selalu tersedia/konsisten.
# Di sini kita bangun ulang secara eksplisit agar tidak error.
if 'data_clean' in globals() and 'date' in data_clean.columns:
  tanggal = pd.to_datetime(data_clean['date']).reset_index(drop=True)
elif 'imfs' in globals() and 'date' in imfs.columns:
  tanggal = pd.to_datetime(imfs['date']).reset_index(drop=True)
else:
  # Fallback: index biasa jika kolom tanggal benar-benar tidak ada
  tanggal = pd.Series(range(len(data_to_normalize)), name='date')

data_to_normalize = data_to_normalize.reset_index(drop=True)

# DataFrame untuk menampung hasil normalisasi seluruh sub-komponen
normalized_imfs = pd.DataFrame()

# ─── [TAMBAHAN] Menyimpan ringkasan min/max tiap kolom untuk ────
#     keperluan perhitungan manual & rekap Excel nantinya
minmax_summary = []

print('=' * 65)
print('⚙️ PROSES NORMALISASI MINMAXSCALER SUB-KOMPONEN HYBRID')
print('=' * 65)

# =========================================================
# 3. NORMALISASI SETIAP SUB-KOMPONEN & SIMPAN SCALER
# =========================================================
for column in data_to_normalize.columns:
  scaler = MinMaxScaler(feature_range=(0, 1))

  # Reshape data 1D ke 2D array (syarat input sklearn)
  data = data_to_normalize[column].values.reshape(-1, 1)
  normalized_data = scaler.fit_transform(data)
  normalized_imfs[column] = normalized_data.flatten()

  # Simpan objek scaler masing-masing sub-komponen
  scaler_filename = f'scaler/scaler_{column}.pkl'
  joblib.dump(scaler, scaler_filename)

  # Simpan ringkasan min & max (dipakai untuk rumus manual)
  x_min = float(scaler.data_min_[0])
  x_max = float(scaler.data_max_[0])
  minmax_summary.append({
      'Komponen': column,
      'x_min': x_min,
      'x_max': x_max,
      'Range (x_max - x_min)': x_max - x_min,
  })

  print(f'✅ Scaler berhasil disimpan: {scaler_filename}')

# =========================================================
# 4. SIMPAN HASIL NORMALISASI (DATASET MURNI & DENGAN TANGGAL)
# =========================================================
normalized_imfs.to_csv('hasil-normalisasi/normalized_imfs.csv', index=False)
normalized_imfs.to_pickle('hasil-normalisasi/normalized_imfs.pkl')

normalized_imfs_with_date = normalized_imfs.copy()
normalized_imfs_with_date['date'] = tanggal.values
normalized_imfs_with_date.to_csv(
    'hasil-normalisasi/normalized_imfs_with_date.csv', index=False
)

print('\n💾 Hasil normalisasi berhasil disimpan:')
print('   - hasil-normalisasi/normalized_imfs.csv')
print('   - hasil-normalisasi/normalized_imfs.pkl')
print('   - hasil-normalisasi/normalized_imfs_with_date.csv')


# =========================================================
# 5. VISUALISASI SEBELUM VS SESUDAH NORMALISASI
# =========================================================
n_cols = len(data_to_normalize.columns)
sns.set_theme(style='whitegrid')

fig, axes = plt.subplots(n_cols, 2, figsize=(14, 2.2 * n_cols), sharex=True)

# ─── [PERBAIKAN] jika hanya 1 komponen, axes tidak 2D — dipaksa jadi 2D ──
if n_cols == 1:
  axes = np.array([axes])

fig.suptitle(
    'Perbandingan Sub-Komponen Sebelum dan Sesudah Normalisasi (Min-Max 0–1)',
    fontsize=14,
    fontweight='bold',
    y=0.995,
)

for i, col in enumerate(data_to_normalize.columns):
  # Grafik Kiri: Sebelum Normalisasi (Skala Asli)
  axes[i, 0].plot(tanggal, data_to_normalize[col], color='#1f77b4', linewidth=1.2)
  axes[i, 0].set_ylabel(col, fontsize=9, fontweight='bold')
  axes[i, 0].grid(True, linestyle=':', alpha=0.5)

  # Grafik Kanan: Sesudah Normalisasi (Skala 0 sampai 1)
  axes[i, 1].plot(tanggal, normalized_imfs[col], color='#ff7f0e', linewidth=1.2)
  axes[i, 1].set_ylim(-0.05, 1.05)
  axes[i, 1].grid(True, linestyle=':', alpha=0.5)

  if i == 0:
    axes[i, 0].set_title('Sebelum Normalisasi (Skala Asli)', fontsize=11, fontweight='bold', pad=8)
    axes[i, 1].set_title('Sesudah Normalisasi (Skala 0–1)', fontsize=11, fontweight='bold', pad=8)

axes[-1, 0].set_xlabel('Tanggal', fontsize=10)
axes[-1, 1].set_xlabel('Tanggal', fontsize=10)

plt.tight_layout()
plt.savefig(
    'output_hasil/grafik/05_normalization_comparison.png',
    dpi=150,
    bbox_inches='tight',
)
plt.show()
print('💾 Grafik disimpan: output_hasil/grafik/05_normalization_comparison.png')


# =========================================================================
# =========================================================================
#   6. EKSPOR EXCEL: RINGKASAN SCALER, DATA HASIL, & PERHITUNGAN MANUAL
# =========================================================================
# =========================================================================
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

header_fill = PatternFill('solid', start_color='1F4E79', fgColor='1F4E79')
alt_fill = PatternFill('solid', start_color='D6E4F0', fgColor='D6E4F0')
note_fill = PatternFill('solid', start_color='FFF2CC', fgColor='FFF2CC')
best_fill = PatternFill('solid', start_color='C6EFCE', fgColor='C6EFCE')
header_font = Font(bold=True, color='FFFFFF', name='Arial', size=11)
data_font = Font(name='Arial', size=10)
note_font = Font(name='Arial', size=10, italic=True)
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin'),
)


def title_block(ws, r, text, span=7, size=13, height=22):
  ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=span)
  c = ws.cell(row=r, column=1, value=text)
  c.font = Font(bold=True, color='FFFFFF', name='Arial', size=size)
  c.fill = header_fill
  c.alignment = center
  ws.row_dimensions[r].height = height
  return r + 1


def note_block(ws, r, text, span=7, height=32):
  ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=span)
  c = ws.cell(row=r, column=1, value=text)
  c.font = note_font
  c.fill = note_fill
  c.alignment = left_wrap
  ws.row_dimensions[r].height = height
  return r + 1


def table_header(ws, r, headers):
  for ci, h in enumerate(headers, start=1):
    c = ws.cell(row=r, column=ci, value=h)
    c.font = header_font
    c.fill = header_fill
    c.alignment = center
    c.border = thin_border
  return r + 1


def table_row(ws, r, values, alt=False, highlight=False):
  fill = best_fill if highlight else (alt_fill if alt else PatternFill())
  for ci, v in enumerate(values, start=1):
    c = ws.cell(row=r, column=ci, value=v)
    c.font = data_font
    c.fill = fill
    c.alignment = center
    c.border = thin_border
  return r + 1


wb = openpyxl.Workbook()

# ------------------------------------------------------------------
# SHEET 1: Ringkasan Min-Max per Komponen (dasar rumus normalisasi)
# ------------------------------------------------------------------
ws1 = wb.active
ws1.title = 'Ringkasan_MinMax'
r = 1
r = title_block(ws1, r, 'Ringkasan Nilai Min & Max per Sub-Komponen (Dasar Normalisasi Min-Max)', span=4)
r = note_block(
    ws1, r,
    'Nilai x_min dan x_max diambil langsung dari MinMaxScaler.data_min_ dan data_max_ '
    'masing-masing sub-komponen, dengan feature_range = (0, 1).',
    span=4,
)
r += 1
r = table_header(ws1, r, ['Komponen', 'x_min', 'x_max', 'Range (x_max - x_min)'])
for i, row in enumerate(minmax_summary):
  r = table_row(
      ws1, r,
      [row['Komponen'], round(row['x_min'], 6), round(row['x_max'], 6), round(row['Range (x_max - x_min)'], 6)],
      alt=(i % 2 == 0),
  )
for i, w in enumerate([26, 20, 20, 24], start=1):
  ws1.column_dimensions[get_column_letter(i)].width = w

# ------------------------------------------------------------------
# SHEET 2: Data Hasil Normalisasi Lengkap (seluruh komponen)
# ------------------------------------------------------------------
ws2 = wb.create_sheet('Data_Normalisasi')
r = 1
n_cols_ws2 = len(normalized_imfs.columns) + 1
r = title_block(ws2, r, 'Hasil Normalisasi Min-Max (Skala 0–1) — Seluruh Sub-Komponen', span=min(n_cols_ws2, 12))
r += 1
headers2 = ['Tanggal'] + list(normalized_imfs.columns)
r = table_header(ws2, r, headers2)
tanggal_str = pd.to_datetime(tanggal).dt.strftime('%Y-%m-%d').values if np.issubdtype(pd.Series(tanggal).dtype, np.datetime64) else [str(t)[:10] for t in tanggal]
for i in range(len(normalized_imfs)):
  row_vals = [tanggal_str[i]] + [round(float(normalized_imfs.iloc[i, c]), 6) for c in range(len(normalized_imfs.columns))]
  r = table_row(ws2, r, row_vals, alt=(i % 2 == 0))
for i in range(1, n_cols_ws2 + 1):
  ws2.column_dimensions[get_column_letter(i)].width = 16

# ------------------------------------------------------------------
# SHEET 3: Perhitungan Manual Rumus Normalisasi Min-Max
# ------------------------------------------------------------------
ws3 = wb.create_sheet('Perhitungan_Manual')
r = 1
r = title_block(ws3, r, 'PERHITUNGAN MANUAL NORMALISASI MIN-MAX (SKALA 0–1)', span=7, size=14)
r = note_block(
    ws3, r,
    'Rumus: x_norm = (x - x_min) / (x_max - x_min). '
    'Ilustrasi ditampilkan untuk 2 komponen contoh (kolom pertama & kedua) sebanyak 10 data pertama, '
    'lalu diverifikasi terhadap hasil MinMaxScaler (sklearn) untuk memastikan kesesuaian.',
    span=7, height=44,
)
r += 1

contoh_kolom = list(data_to_normalize.columns)[: min(2, len(data_to_normalize.columns))]
n_preview = min(10, len(data_to_normalize))

for kolom in contoh_kolom:
  x_min_k = data_to_normalize[kolom].min()
  x_max_k = data_to_normalize[kolom].max()

  r = title_block(ws3, r, f'Komponen: {kolom}  (x_min = {x_min_k:.6f} ; x_max = {x_max_k:.6f})', span=7, size=12)
  r = table_header(ws3, r, ['g (Titik ke-)', 'x (nilai asli)', 'x - x_min', 'x_max - x_min', 'x_norm = (x-x_min)/(x_max-x_min)', 'x_norm (sklearn)', 'Selisih'])

  for i in range(n_preview):
    x_val = data_to_normalize[kolom].iloc[i]
    x_norm_manual = (x_val - x_min_k) / (x_max_k - x_min_k)
    x_norm_sklearn = normalized_imfs[kolom].iloc[i]
    r = table_row(
        ws3, r,
        [
            i + 1, round(float(x_val), 4), round(float(x_val - x_min_k), 4),
            round(float(x_max_k - x_min_k), 4), round(float(x_norm_manual), 6),
            round(float(x_norm_sklearn), 6), round(float(x_norm_manual - x_norm_sklearn), 8),
        ],
        alt=(i % 2 == 0),
    )

  cocok = 'COCOK ✅' if abs((data_to_normalize[kolom] - x_min_k) / (x_max_k - x_min_k) - normalized_imfs[kolom]).max() < 1e-9 else 'TIDAK COCOK ❌'
  r = note_block(
      ws3, r,
      f'Verifikasi (seluruh {len(data_to_normalize)} data pada komponen {kolom}): '
      f'perhitungan manual vs hasil MinMaxScaler → {cocok}',
      span=7, height=22,
  )
  r += 1

for i in range(1, 8):
  ws3.column_dimensions[get_column_letter(i)].width = 22

# ─── SIMPAN FILE EXCEL ──────────────────────────────────────────────
xlsx_path_norm = 'hasil-normalisasi/normalisasi_hasil_lengkap.xlsx'
wb.save(xlsx_path_norm)
print(f'\n💾 Excel lengkap normalisasi disimpan: {xlsx_path_norm}')
print('   Sheet: Ringkasan_MinMax, Data_Normalisasi, Perhitungan_Manual')