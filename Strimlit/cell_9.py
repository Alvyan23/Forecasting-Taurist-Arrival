import os
import subprocess
import sys

# ─── Automatic Installation for EMD-signal, scikit-learn & joblib ─────
try:
  from PyEMD import EMD
  import joblib
except ModuleNotFoundError:
  print('📦 Installing EMD-signal, scikit-learn and joblib...')
  subprocess.check_call(
      [sys.executable, '-m', 'pip', 'install', 'EMD-signal', 'scikit-learn', 'joblib']
  )
  from PyEMD import EMD
  import joblib

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
import seaborn as sns
from joblib import Parallel, delayed
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sklearn.metrics import mean_absolute_error

print('=' * 65)
print('🔧 DEKOMPOSISI I-CEEMDAN (Colominas et al., 2014)')
print('   Parameter: trials=100, epsilon0=0.2, seed=42')
print('   → SEMUA IMF + Residue digunakan (tanpa filter korelasi)')
print('=' * 65)


# ══════════════════════════════════════════════════════════════
# ICEEMDAN asli (Pers. 1-8 artikel) — BAGIAN YANG DIPERBAIKI
# ══════════════════════════════════════════════════════════════
def _n_extrema(x):
  d = np.diff(x)
  return int(np.sum(d[:-1] * d[1:] < 0))


def _local_mean(z):
  """M(z) = z - IMF1(z): rata-rata lokal via EMD."""
  imfs = EMD().emd(z, max_imf=1)
  if len(imfs) < 2:
    return z.copy()
  return z - imfs[0]


def _noise_imfs(n, seed, kmax):
  """EMD satu realisasi white noise -> E_1..E_kmax (dinormalisasi std=1)."""
  w = np.random.default_rng(seed).standard_normal(n)
  imfs = EMD().emd(w)
  out = np.zeros((kmax, n))
  for k in range(min(kmax, len(imfs))):
    s = imfs[k].std()
    if s > 0:
      out[k] = imfs[k] / s
  return out


def _trial_mean(r, noise_k, beta):
  return _local_mean(r + beta * noise_k)


def iceemdan(x, trials=100, epsilon0=0.2, max_imf=15, seed=42, n_jobs=-1):
  """
  ICEEMDAN sesuai Pers. (1)-(8):
    R1 = <M(x + b0*E1(w_i))>,             F1 = x - R1
    Rk = <M(R_{k-1} + b_{k-1}*Ek(w_i))>,  Fk = R_{k-1} - Rk
  b = epsilon0 * std(sinyal/residu). Return (n_imf+1, N); baris terakhir = residu.
  """
  x = np.asarray(x, dtype=float)
  n = len(x)
  ss = np.random.SeedSequence(seed).spawn(trials)
  seeds = [int(s.generate_state(1)[0]) for s in ss]

  noise = Parallel(n_jobs=n_jobs)(
      delayed(_noise_imfs)(n, sd, max_imf + 1) for sd in seeds
  )

  modes = []
  r_prev = x.copy()
  for k in range(1, max_imf + 1):
    beta = epsilon0 * np.std(r_prev)
    means = Parallel(n_jobs=n_jobs)(
        delayed(_trial_mean)(r_prev, noise[i][k - 1], beta)
        for i in range(trials)
    )
    r_k = np.mean(means, axis=0)
    modes.append(r_prev - r_k)          # F_k = R_{k-1} - R_k
    r_prev = r_k
    if _n_extrema(r_prev) < 3:          # residu monoton -> selesai
      break
  modes.append(r_prev)                  # residu R_n
  return np.array(modes)


# ─── 1. Parameter I-CEEMDAN ───────────────────────────────────
ICEEMDAN_TRIALS = 100
ICEEMDAN_EPSILON = 0.2   # epsilon0 (β0 = epsilon0 * std), standar Colominas
ICEEMDAN_SEED = 42

# Ambil data input (Sinyal yang digunakan)
signal_original = data_clean['visitors'].values
dates = data_clean['date']

print('⏳ Menjalankan I-CEEMDAN... (beberapa saat)')
IMFs_all = iceemdan(
    signal_original,
    trials=ICEEMDAN_TRIALS,
    epsilon0=ICEEMDAN_EPSILON,
    seed=ICEEMDAN_SEED,
)

# Pemisahan IMF dan Residue
iceemdan_imfs = IMFs_all[:-1]  # Seluruh IMF
iceemdan_residue = IMFs_all[-1]  # Komponen terakhir sebagai Residue
n_iceemdan_imf = len(iceemdan_imfs)
n_total = len(IMFs_all)

print(f'✅ I-CEEMDAN selesai: {n_total} komponen ({n_iceemdan_imf} IMF + 1 Residue)')

# ══════════════════════════════════════════════════════════════
# SELANJUTNYA: KODE ASLI ANDA (tidak diubah)
# ══════════════════════════════════════════════════════════════

# ─── 2. Evaluasi Rekonstruksi (MAE) ───────────────────────────
reconstructed_iceemdan = iceemdan_imfs.sum(axis=0) + iceemdan_residue
mae_iceemdan = mean_absolute_error(signal_original, reconstructed_iceemdan)
print(f'MAE rekonstruksi ICEEMDAN: {mae_iceemdan:.6f}')

# ─── 3. Visualisasi Sinyal & IMF ──────────────────────────────
fig, axes = plt.subplots(
    n_iceemdan_imf + 2, 1, figsize=(12, 2 * (n_iceemdan_imf + 2)), sharex=True
)

# Sinyal Asli
axes[0].plot(dates, signal_original, color='black', linewidth=1.5)
axes[0].set_title('Sinyal Asli (Hasil Interpolasi)')
axes[0].grid(True, alpha=0.3)

# Plot tiap IMF
colors_ice = sns.color_palette('husl', n_iceemdan_imf)
for i in range(n_iceemdan_imf):
  axes[i + 1].plot(
      dates, iceemdan_imfs[i], color=colors_ice[i], linewidth=1.2
  )
  axes[i + 1].set_ylabel(f'IMF-{i + 1}')
  axes[i + 1].grid(True, alpha=0.3)

# Plot Residue
axes[-1].plot(dates, iceemdan_residue, color='darkred', linewidth=1.2)
axes[-1].set_ylabel('Residu')
axes[-1].set_xlabel('Tanggal')
axes[-1].grid(True, alpha=0.3)

plt.tight_layout()

# Simpan Grafik
os.makedirs('output_hasil/grafik', exist_ok=True)
plt.savefig(
    'output_hasil/grafik/03_iceemdan_decomposition.png',
    dpi=150,
    bbox_inches='tight',
)
plt.show()
print('💾 Grafik disimpan: output_hasil/grafik/03_iceemdan_decomposition.png')

# ─── 4. Tabel Korelasi Informatif (DITAMPILKAN DI TERMINAL) ───
labels = [f'IMF_{i+1}' for i in range(n_iceemdan_imf)] + ['Residue']

print('\n📋 Tabel Korelasi IMF dengan Data Asli:')
print('   (Semua komponen DIGUNAKAN — korelasi hanya informatif)')
print('-' * 55)

corr_results = []
for i, (comp, label) in enumerate(zip(IMFs_all, labels)):
  corr = np.corrcoef(signal_original, comp)[0, 1]
  corr_results.append({
      'Komponen': label,
      'Korelasi': round(corr, 6),
      'Abs_Korelasi': round(abs(corr), 6),
  })
  print(f'   {label:<10}: korelasi = {corr:+.6f}   ✅ DIGUNAKAN')

df_corr = pd.DataFrame(corr_results)
print(f'\n   → Total komponen digunakan: {n_total} ({labels})')

# ─── 5. Simpan Hasil ke Excel Multi-Sheet ──────────────────────
xlsx_path = 'output_hasil/iceemdan_decomposition.xlsx'
wb = openpyxl.Workbook()

header_fill = PatternFill('solid', start_color='1F4E79', fgColor='1F4E79')
alt_fill = PatternFill('solid', start_color='D6E4F0', fgColor='D6E4F0')
header_font = Font(bold=True, color='FFFFFF', name='Arial', size=11)
data_font = Font(name='Arial', size=10)
center_align = Alignment(horizontal='center', vertical='center')
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin'),
)
pos_fill = PatternFill('solid', start_color='C6EFCE', fgColor='C6EFCE')
neg_fill = PatternFill('solid', start_color='FFEB9C', fgColor='FFEB9C')

# Sheet 1: Data & IMF
ws_imf = wb.active
ws_imf.title = 'IMF_Components'

ws_imf.merge_cells('A1:' + get_column_letter(n_total + 2) + '1')
title_cell = ws_imf['A1']
title_cell.value = (
    'I-CEEMDAN Decomposition — Semua Komponen (IMF + Residue)'
)
title_cell.font = Font(bold=True, color='FFFFFF', name='Arial', size=13)
title_cell.fill = header_fill
title_cell.alignment = center_align
ws_imf.row_dimensions[1].height = 30

header_row = ['Tanggal', 'Sinyal_Asli'] + labels
for col_idx, h in enumerate(header_row, start=1):
  cell = ws_imf.cell(row=2, column=col_idx, value=h)
  cell.font = header_font
  cell.fill = header_fill
  cell.alignment = center_align
  cell.border = thin_border
  ws_imf.column_dimensions[get_column_letter(col_idx)].width = 18

for row_idx, (d_val, orig) in enumerate(
    zip(dates, signal_original), start=1
):
  fill = alt_fill if row_idx % 2 == 0 else PatternFill()
  row_data = [
      str(d_val)[:10],
      round(float(orig), 4),
  ] + [round(float(comp[row_idx - 1]), 6) for comp in IMFs_all]
  for col_idx, val in enumerate(row_data, start=1):
    cell = ws_imf.cell(row=row_idx + 2, column=col_idx, value=val)
    cell.font = data_font
    cell.fill = fill
    cell.border = thin_border
    cell.alignment = center_align

# Sheet 2: Korelasi
ws_corr = wb.create_sheet('Korelasi')
ws_corr.merge_cells('A1:D1')
tc = ws_corr['A1']
tc.value = (
    'Tabel Korelasi IMF dengan Data Asli (Informatif — Semua Komponen'
    ' Digunakan)'
)
tc.font = Font(bold=True, color='FFFFFF', name='Arial', size=12)
tc.fill = header_fill
tc.alignment = center_align

corr_headers = ['Komponen', 'Korelasi', '|Korelasi|', 'Status']
for col_idx, h in enumerate(corr_headers, start=1):
  cell = ws_corr.cell(row=2, column=col_idx, value=h)
  cell.font = header_font
  cell.fill = header_fill
  cell.alignment = center_align
  cell.border = thin_border

for row_idx, r in enumerate(corr_results, start=3):
  row_data = [
      r['Komponen'],
      r['Korelasi'],
      r['Abs_Korelasi'],
      'Digunakan ✅',
  ]
  row_fill = pos_fill if r['Korelasi'] >= 0 else neg_fill
  for col_idx, val in enumerate(row_data, start=1):
    cell = ws_corr.cell(row=row_idx, column=col_idx, value=val)
    cell.font = data_font
    cell.fill = row_fill
    cell.border = thin_border
    cell.alignment = center_align

# Sheet 3: Ringkasan
ws_info = wb.create_sheet('Ringkasan')
ws_info.merge_cells('A1:B1')
ri = ws_info['A1']
ri.value = 'Ringkasan Parameter I-CEEMDAN'
ri.font = Font(bold=True, color='FFFFFF', name='Arial', size=12)
ri.fill = header_fill
ri.alignment = center_align

summary_data = [
    ('Parameter', 'Nilai'),
    ('Trials', ICEEMDAN_TRIALS),
    ('Epsilon0 (β0 = epsilon0 × std)', ICEEMDAN_EPSILON),
    ('Seed', ICEEMDAN_SEED),
    ('Noise Kind', 'normal'),
    ('Algoritma', 'ICEEMDAN (Colominas et al., 2014)'),
    ('Total Komponen', n_total),
    ('Komponen IMF', n_iceemdan_imf),
    ('Residue', 1),
    ('Filter Korelasi/Entropy', 'TIDAK — Semua komponen digunakan'),
    ('MAE Rekonstruksi', round(mae_iceemdan, 6)),
]

for row_idx, (k, v) in enumerate(summary_data, start=2):
  is_header = row_idx == 2
  for col_idx, val in enumerate([k, v], start=1):
    cell = ws_info.cell(row=row_idx, column=col_idx, value=val)
    cell.font = header_font if is_header else data_font
    cell.fill = (
        header_fill
        if is_header
        else (alt_fill if row_idx % 2 == 0 else PatternFill())
    )
    cell.border = thin_border
    cell.alignment = center_align
ws_info.column_dimensions['A'].width = 32
ws_info.column_dimensions['B'].width = 40

# ─── 6. Sheet Perhitungan Manual (Rekonstruksi & Korelasi) ─────
ws_manual = wb.create_sheet('Perhitungan_Manual')

# --- Bagian A: Perhitungan Manual Rekonstruksi (Verifikasi MAE) ---
ws_manual.merge_cells('A1:G1')
title_manual = ws_manual['A1']
title_manual.value = 'A. Perhitungan Manual Rekonstruksi Sinyal (Verifikasi MAE)'
title_manual.font = Font(bold=True, color='FFFFFF', name='Arial', size=13)
title_manual.fill = header_fill
title_manual.alignment = center_align
ws_manual.row_dimensions[1].height = 28

manual_headers = [
    'Tanggal', 'Sinyal_Asli (x)', 'Jumlah_IMF (ΣIMF)', 'Residu (r)',
    'Rekonstruksi (ΣIMF+r)', 'Selisih (x - Rekon)', '|Error|'
]
for col_idx, h in enumerate(manual_headers, start=1):
  cell = ws_manual.cell(row=2, column=col_idx, value=h)
  cell.font = header_font
  cell.fill = header_fill
  cell.alignment = center_align
  cell.border = thin_border
  ws_manual.column_dimensions[get_column_letter(col_idx)].width = 20

jumlah_imf_manual = iceemdan_imfs.sum(axis=0)
selisih_manual = signal_original - reconstructed_iceemdan
error_abs_manual = np.abs(selisih_manual)

for row_idx in range(len(signal_original)):
  fill = alt_fill if row_idx % 2 == 0 else PatternFill()
  tgl_val = (
      dates.iloc[row_idx] if hasattr(dates, 'iloc') else dates[row_idx]
  )
  row_data = [
      str(tgl_val)[:10],
      round(float(signal_original[row_idx]), 4),
      round(float(jumlah_imf_manual[row_idx]), 6),
      round(float(iceemdan_residue[row_idx]), 6),
      round(float(reconstructed_iceemdan[row_idx]), 6),
      round(float(selisih_manual[row_idx]), 6),
      round(float(error_abs_manual[row_idx]), 6),
  ]
  for col_idx, val in enumerate(row_data, start=1):
    cell = ws_manual.cell(row=row_idx + 3, column=col_idx, value=val)
    cell.font = data_font
    cell.fill = fill
    cell.border = thin_border
    cell.alignment = center_align

# Baris total & MAE manual
row_total = len(signal_original) + 3
ws_manual.cell(row=row_total, column=1, value='Σ (Total)').font = Font(
    bold=True, name='Arial', size=10
)
ws_manual.cell(
    row=row_total, column=7, value=round(float(error_abs_manual.sum()), 6)
).font = Font(bold=True, name='Arial', size=10)
for c in range(1, 8):
  ws_manual.cell(row=row_total, column=c).border = thin_border
  ws_manual.cell(row=row_total, column=c).fill = (
      header_fill if c in (1, 7) else PatternFill()
  )

row_mae = row_total + 1
ws_manual.cell(
    row=row_mae, column=1, value='MAE Manual = Σ|Error| / n'
).font = Font(bold=True, name='Arial', size=10)
mae_manual_value = error_abs_manual.sum() / len(signal_original)
ws_manual.cell(
    row=row_mae, column=7, value=round(float(mae_manual_value), 6)
).font = Font(bold=True, name='Arial', size=10)
ws_manual.cell(row=row_mae, column=7).fill = (
    pos_fill if abs(mae_manual_value - mae_iceemdan) < 1e-9 else neg_fill
)

row_check = row_mae + 1
ws_manual.cell(
    row=row_check,
    column=1,
    value=(
        f'Verifikasi: MAE Manual ({mae_manual_value:.6f}) vs MAE sklearn '
        f'({mae_iceemdan:.6f}) → '
        f'{"COCOK ✅" if abs(mae_manual_value - mae_iceemdan) < 1e-6 else "TIDAK COCOK ❌"}'
    ),
)
ws_manual.merge_cells(f'A{row_check}:G{row_check}')

# --- Bagian B: Contoh Perhitungan Manual Korelasi (Pearson) IMF_1 ---
start_row_b = row_check + 3
ws_manual.merge_cells(f'A{start_row_b}:G{start_row_b}')
title_b = ws_manual.cell(row=start_row_b, column=1)
title_b.value = (
    'B. Contoh Perhitungan Manual Korelasi Pearson (IMF_1) — 10 Data Pertama'
)
title_b.font = Font(bold=True, color='FFFFFF', name='Arial', size=13)
title_b.fill = header_fill
title_b.alignment = center_align

header_row_b = start_row_b + 1
corr_manual_headers = [
    'Tanggal', 'x (Sinyal)', 'y (IMF_1)', 'x - x̄', 'y - ȳ',
    '(x-x̄)(y-ȳ)', '(x-x̄)²'
]
for col_idx, h in enumerate(corr_manual_headers, start=1):
  cell = ws_manual.cell(row=header_row_b, column=col_idx, value=h)
  cell.font = header_font
  cell.fill = header_fill
  cell.alignment = center_align
  cell.border = thin_border

x_signal = signal_original
y_imf1 = iceemdan_imfs[0]
x_mean = x_signal.mean()
y_mean = y_imf1.mean()

n_preview = min(10, len(x_signal))
for i in range(n_preview):
  dx = x_signal[i] - x_mean
  dy = y_imf1[i] - y_mean
  fill = alt_fill if i % 2 == 0 else PatternFill()
  tgl_val_b = dates.iloc[i] if hasattr(dates, 'iloc') else dates[i]
  row_vals = [
      str(tgl_val_b)[:10],
      round(float(x_signal[i]), 4),
      round(float(y_imf1[i]), 6),
      round(float(dx), 6),
      round(float(dy), 6),
      round(float(dx * dy), 6),
      round(float(dx ** 2), 6),
  ]
  for col_idx, val in enumerate(row_vals, start=1):
    cell = ws_manual.cell(
        row=header_row_b + 1 + i, column=col_idx, value=val
    )
    cell.font = data_font
    cell.fill = fill
    cell.border = thin_border
    cell.alignment = center_align

# Total (seluruh data, bukan hanya 10 preview) untuk formula korelasi penuh
dx_full = x_signal - x_mean
dy_full = y_imf1 - y_mean
sum_xy = (dx_full * dy_full).sum()
sum_x2 = (dx_full ** 2).sum()
sum_y2 = (dy_full ** 2).sum()
corr_manual = sum_xy / np.sqrt(sum_x2 * sum_y2)

row_total_b = header_row_b + n_preview + 1
ws_manual.cell(
    row=row_total_b,
    column=1,
    value=f'Σ (seluruh n={len(x_signal)} data, tidak hanya preview)',
).font = Font(bold=True, name='Arial', size=10)
ws_manual.cell(
    row=row_total_b, column=6, value=round(float(sum_xy), 6)
).font = Font(bold=True, name='Arial', size=10)
ws_manual.cell(
    row=row_total_b, column=7, value=round(float(sum_x2), 6)
).font = Font(bold=True, name='Arial', size=10)

row_formula = row_total_b + 1
ws_manual.merge_cells(f'A{row_formula}:G{row_formula}')
formula_cell = ws_manual.cell(row=row_formula, column=1)
formula_cell.value = (
    f'r = Σ(x-x̄)(y-ȳ) / √[Σ(x-x̄)² · Σ(y-ȳ)²] = {sum_xy:.6f} / '
    f'√[{sum_x2:.6f} × {sum_y2:.6f}] = {corr_manual:.6f}'
)
formula_cell.font = Font(bold=True, name='Arial', size=10)

row_check_b = row_formula + 1
corr_numpy = np.corrcoef(x_signal, y_imf1)[0, 1]
ws_manual.merge_cells(f'A{row_check_b}:G{row_check_b}')
check_cell_b = ws_manual.cell(row=row_check_b, column=1)
check_cell_b.value = (
    f'Verifikasi: r Manual ({corr_manual:.6f}) vs r numpy.corrcoef '
    f'({corr_numpy:.6f}) → '
    f'{"COCOK ✅" if abs(corr_manual - corr_numpy) < 1e-6 else "TIDAK COCOK ❌"}'
)

for col_idx in range(1, 8):
  ws_manual.column_dimensions[get_column_letter(col_idx)].width = 20

print('💾 Sheet "Perhitungan_Manual" berhasil ditambahkan (rekonstruksi MAE + korelasi Pearson).')

wb.save(xlsx_path)
print(f'\n💾 Excel disimpan: {xlsx_path}')
print('   Sheet: IMF_Components, Korelasi, Ringkasan, Perhitungan_Manual')
