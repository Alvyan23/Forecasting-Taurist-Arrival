import os
import subprocess
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

# ─── Install vmdpy jika belum ada ──────────────────────────────
try:
  from vmdpy import VMD
except ModuleNotFoundError:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'vmdpy'])
  from vmdpy import VMD


# =========================================================
# FUNGSI METRIK EVALUASI VMD
# =========================================================
def get_vmd_metrics(f, u):
  K = u.shape[0]

  # 1. Korelasi antar mode (indikasi mode mixing)
  correlations = []
  for i in range(K - 1):
    corr, _ = pearsonr(u[i], u[i + 1])
    correlations.append(abs(corr))
  mean_corr = np.mean(correlations) if correlations else 0

  # 2. Error rekonstruksi (energy loss / ELC)
  reconstructed_signal = np.sum(u, axis=0)
  res = f - reconstructed_signal
  elc = np.sum(res**2) / np.sum(f**2)

  # 3. Bandwidth rata-rata tiap mode
  mode_bandwidths = []
  for i in range(K):
    mode_fft = np.fft.fft(u[i])
    psd = np.abs(mode_fft) ** 2
    freqs = np.fft.fftfreq(len(u[i]))

    pos_idx = freqs >= 0
    psd_pos = psd[pos_idx]
    freqs_pos = freqs[pos_idx]

    if np.sum(psd_pos) > 0:
      mean_f = np.sum(freqs_pos * psd_pos) / np.sum(psd_pos)
      var_f = np.sum(((freqs_pos - mean_f) ** 2) * psd_pos) / np.sum(psd_pos)
      mode_bandwidths.append(var_f)
    else:
      mode_bandwidths.append(0)

  mean_bw = np.mean(mode_bandwidths)

  return mean_corr, elc, mean_bw


# =========================================================
# PARAMETER DASAR VMD
# =========================================================
tau = 0.0
DC = 0
init = 1
tol = 1e-7

# Range pencarian diperkecil hingga K=12 dan Alpha hingga 2000
K_range = range(2, 13)  # K dari 2 sampai 12
alpha_range = range(100, 2100, 100)  # Alpha dari 100 sampai 2000
corr_threshold = 1.2

# Tempat menyimpan semua hasil komponen VMD per IMF
all_vmd_components = {}
vmd_summary_params = []

# ─── [TAMBAHAN] Tempat menyimpan SELURUH kandidat (K, Alpha) yang diuji,
#     dari semua IMF, untuk direkap lengkap ke Excel nantinya ──────────
all_candidates_records = []

print('=' * 65)
print('🚀 PROSES FINE-TUNING VMD (PERKECIL RANGE K <= 12 & ALPHA <= 2000)')
print('=' * 65)

# =========================================================
# LOOP PENCARIAN PARAMETER & DEKOMPOSISI PER IMF
# =========================================================
for imf_idx, imf_signal in enumerate(iceemdan_imfs):
  imf_name = f'IMF_{imf_idx + 1}'
  f = imf_signal

  print(f'\n--- Memulai Fine-tuning VMD untuk {imf_name} ---')

  candidates = []

  for K in K_range:
    prev_corr = 999
    best_alpha_for_k = None
    best_metrics_for_k = None

    for alpha in alpha_range:
      u, u_hat, omega = VMD(f, alpha, tau, K, DC, init, tol)

      corr, elc, bw = get_vmd_metrics(f, u)

      if alpha > 100 and corr > (prev_corr * corr_threshold):
        break

      best_alpha_for_k = alpha
      best_metrics_for_k = (corr, elc, bw)
      prev_corr = corr

    if best_alpha_for_k is not None:
      candidates.append({
          'K': K,
          'alpha': best_alpha_for_k,
          'Corr': best_metrics_for_k[0],
          'ELC': best_metrics_for_k[1],
          'BW': best_metrics_for_k[2],
      })
      # ─── [TAMBAHAN] tandai kandidat ini dengan asal IMF-nya ─────
      candidates[-1]['IMF_Origin'] = imf_name

      corr_k, elc_k, bw_k = best_metrics_for_k

      print(
          f'Candidate K={K} | Alpha={best_alpha_for_k} | '
          f'Corr={corr_k:.5f} | ELC={elc_k:.5f} | BW={bw_k:.5f}'
      )

  # Filter kandidat dengan ELC yang wajar
  filtered_candidates = [c for c in candidates if c['ELC'] < 0.01]

  if not filtered_candidates:
    print('Tidak ada kandidat ELC < 0.01, ambil terbaik dari seluruh list.')
    filtered_candidates = candidates

  # SELEKSI HIERARKIS:
  # 1. Bandwidth (BW) dibulatkan ke 5 desimal.
  # 2. ELC terkecil.
  # 3. Korelasi (Corr) terkecil.
  best_vmd_params = min(
      filtered_candidates,
      key=lambda x: (round(x['BW'], 5), x['ELC'], x['Corr']),
  )

  print(f'\nHASIL OPTIMAL VMD UNTUK {imf_name}:')
  print(f"K       : {best_vmd_params['K']}")
  print(f"Alpha   : {best_vmd_params['alpha']}")
  print(f"Corr    : {best_vmd_params['Corr']:.5f}")
  print(f"ELC     : {best_vmd_params['ELC']:.5f}")
  print(f"BW      : {best_vmd_params['BW']:.5f}")

  # Simpan ringkasan parameter
  vmd_summary_params.append({
      'IMF_Origin': imf_name,
      'K': best_vmd_params['K'],
      'Alpha': best_vmd_params['alpha'],
      'Corr': best_vmd_params['Corr'],
      'ELC': best_vmd_params['ELC'],
      'BW': best_vmd_params['BW'],
  })

  # ─── [TAMBAHAN] gabungkan seluruh kandidat IMF ini ke rekap global ──
  all_candidates_records.extend(candidates)

  # Dekomposisi final untuk IMF ini menggunakan parameter terbaiknya
  u_optimal, u_hat_optimal, omega_optimal = VMD(
      f, best_vmd_params['alpha'], tau, best_vmd_params['K'], DC, init, tol
  )

  # Simpan hasil mode VMD untuk IMF ini
  for k_sub in range(best_vmd_params['K']):
    all_vmd_components[f'{imf_name}_VMD_{k_sub + 1}'] = u_optimal[k_sub]

  # =========================
  # VISUALISASI PENCARIAN PARAMETER UNTUK IMF INI
  # =========================
  df_search = pd.DataFrame(candidates)
  best_k = best_vmd_params['K']

  sns.set_theme(style='whitegrid')
  fig, axes = plt.subplots(1, 3, figsize=(18, 5))

  fig.suptitle(
      f'Visualisasi Pencarian Parameter VMD ({imf_name})\nOptimal: K={best_k},'
      f' Alpha={best_vmd_params["alpha"]}',
      fontsize=16,
      fontweight='bold',
      y=1.05,
  )

  k_min = df_search['K'].min()
  k_max = df_search['K'].max()

  # BW
  sns.lineplot(data=df_search, x='K', y='BW', marker='o', ax=axes[0])
  axes[0].set_title('Mean Bandwidth')
  axes[0].axvline(best_k, color='red', linestyle='--')
  axes[0].scatter(best_k, best_vmd_params['BW'], color='red', s=100)

  # ELC
  sns.lineplot(data=df_search, x='K', y='ELC', marker='s', ax=axes[1])
  axes[1].set_title('Energy Loss (ELC)')
  axes[1].axhline(0.01, color='orange', linestyle='--')
  axes[1].axvline(best_k, color='red', linestyle='--')

  # Corr
  sns.lineplot(data=df_search, x='K', y='Corr', marker='D', ax=axes[2])
  axes[2].set_title('Mean Correlation')
  axes[2].axvline(best_k, color='red', linestyle='--')

  for ax in axes:
    ax.set_xticks(range(k_min, k_max + 1, 1))
    ax.tick_params(axis='x', rotation=45)

  plt.tight_layout()
  plt.show()

  # =========================
  # VISUALISASI HASIL DEKOMPOSISI IMF INI
  # =========================
  print(f'Plot hasil dekomposisi VMD untuk {imf_name} (K={best_k})')

  n_imfs = best_k
  fig, axes = plt.subplots(
      n_imfs + 1, 1, figsize=(12, 2 * (n_imfs + 1)), sharex=True
  )

  # Sinyal IMF awal
  axes[0].plot(data_clean['date'], f, color='black', linewidth=1.5)
  axes[0].set_title(f'Sinyal Input ({imf_name})')
  axes[0].grid(True, alpha=0.3)

  colors = sns.color_palette('husl', n_imfs)
  for i in range(n_imfs):
    axes[i + 1].plot(
        data_clean['date'], u_optimal[i], color=colors[i], linewidth=1.2
    )
    axes[i + 1].set_ylabel(f'Mode {i+1}')
    axes[i + 1].grid(True, alpha=0.3)

  axes[-1].set_xlabel('Date')
  plt.tight_layout()
  plt.show()

# =========================================================
# GABUNGKAN SEMUA MODES DAN RESIDUE ICEEMDAN
# =========================================================
# Residue I-CEEMDAN disimpam tanpa VMD
all_vmd_components['ICEEMDAN_Residue'] = iceemdan_residue

# Konversi seluruh hasil ke DataFrame
df_final_components = pd.DataFrame(all_vmd_components)
df_final_components['date'] = data_clean['date'].values

print('\n' + '=' * 65)
print('✅ PROSES DEKOMPOSISI VMD SELESAI (K <= 12)')
print('=' * 65)
print('Daftar Seluruh Komponen yang Dihasilkan:')
print(df_final_components.columns.tolist())


# =========================================================
# SIMPAN HASIL DEKOMPOSISI (CSV & PICKLE)
# =========================================================
output_dir = 'hasil-dekomposisi'
os.makedirs(output_dir, exist_ok=True)

df_imfs = df_final_components.copy()
if 'date' in df_imfs.columns:
  dates = df_imfs['date']
  df_imfs_numeric = df_imfs.drop(columns=['date'])
else:
  dates = data_clean['date']
  df_imfs_numeric = df_imfs.copy()

print(
    'Total komponen akhir hybrid ICEEMDAN-VMD:'
    f' {df_imfs_numeric.shape[1]} komponen'
)
print('Daftar kolom komponen:')
for col in df_imfs_numeric.columns:
  print(f' - {col}')

imfs = df_imfs_numeric.copy()
imfs['date'] = dates.values

df_imfs_numeric.to_csv(os.path.join(output_dir, 'imfs.csv'), index=False)
df_imfs_numeric.to_pickle(os.path.join(output_dir, 'imfs.pkl'))
imfs.to_csv(os.path.join(output_dir, 'imfs_with_date.csv'), index=False)

print(f'\n💾 Hasil dekomposisi hybrid berhasil disimpan di folder: {output_dir}/')
print(f'   - {output_dir}/imfs.csv')
print(f'   - {output_dir}/imfs.pkl')
print(f'   - {output_dir}/imfs_with_date.csv')


# =========================================================================
# =========================================================================
#   EKSPOR EXCEL LENGKAP: PENCARIAN PARAMETER, PARAMETER OPTIMAL,
#   DEKOMPOSISI VMD, DAN PERHITUNGAN MANUAL METRIK EVALUASI
# =========================================================================
# =========================================================================
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ─── STYLE UMUM (konsisten dengan format Excel ICEEMDAN sebelumnya) ─────
header_fill = PatternFill('solid', start_color='1F4E79', fgColor='1F4E79')
alt_fill = PatternFill('solid', start_color='D6E4F0', fgColor='D6E4F0')
note_fill = PatternFill('solid', start_color='FFF2CC', fgColor='FFF2CC')
best_fill = PatternFill('solid', start_color='C6EFCE', fgColor='C6EFCE')
header_font = Font(bold=True, color='FFFFFF', name='Arial', size=11)
data_font = Font(name='Arial', size=10)
bold_font = Font(name='Arial', size=10, bold=True)
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


wb_vmd = openpyxl.Workbook()

# ------------------------------------------------------------------
# SHEET 1: Pencarian Parameter (semua kandidat K & Alpha yang diuji)
# ------------------------------------------------------------------
ws1 = wb_vmd.active
ws1.title = 'Pencarian_Parameter'
r = 1
r = title_block(
    ws1, r,
    'Rekap Pencarian Parameter VMD (Fine-Tuning K & Alpha) per Komponen IMF',
    span=6,
)
r = note_block(
    ws1, r,
    'Setiap baris merupakan satu kandidat (K, Alpha) yang diuji dalam proses grid-search. '
    'Pencarian Alpha untuk tiap K dihentikan (early-stop) ketika kenaikan korelasi antar-mode '
    'melebihi ambang batas corr_threshold = 1.2 dikali korelasi pada alpha sebelumnya.',
    span=6,
    height=44,
)
r += 1
r = table_header(
    ws1, r, ['IMF Asal', 'K', 'Alpha', 'Korelasi Antar-Mode', 'ELC (Error Rekonstruksi)', 'Bandwidth Rata-rata']
)
df_candidates = pd.DataFrame(all_candidates_records)
for i, row in df_candidates.iterrows():
  r = table_row(
      ws1, r,
      [
          row['IMF_Origin'], int(row['K']), int(row['alpha']),
          round(float(row['Corr']), 6), round(float(row['ELC']), 6),
          round(float(row['BW']), 6),
      ],
      alt=(i % 2 == 0),
  )
for i, w in enumerate([16, 8, 10, 20, 22, 20], start=1):
  ws1.column_dimensions[get_column_letter(i)].width = w

# ------------------------------------------------------------------
# SHEET 2: Parameter Optimal Terpilih per IMF
# ------------------------------------------------------------------
ws2 = wb_vmd.create_sheet('Parameter_Optimal')
r = 1
r = title_block(
    ws2, r, 'Parameter VMD Optimal Terpilih (Seleksi Hierarkis: BW → ELC → Korelasi)', span=5
)
r = note_block(
    ws2, r,
    'Seleksi dilakukan dari kandidat dengan ELC < 0.01 (jika tersedia), lalu dipilih berdasarkan '
    'urutan prioritas: (1) Bandwidth rata-rata terkecil (dibulatkan 5 desimal), '
    '(2) ELC terkecil, (3) Korelasi antar-mode terkecil.',
    span=5, height=44,
)
r += 1
r = table_header(ws2, r, ['IMF Asal', 'K Optimal', 'Alpha Optimal', 'Korelasi', 'ELC', 'Bandwidth'])
df_summary = pd.DataFrame(vmd_summary_params)
for i, row in df_summary.iterrows():
  r = table_row(
      ws2, r,
      [
          row['IMF_Origin'], int(row['K']), int(row['Alpha']),
          round(float(row['Corr']), 6), round(float(row['ELC']), 6),
          round(float(row['BW']), 6),
      ],
      alt=(i % 2 == 0), highlight=True,
  )
for i, w in enumerate([16, 12, 14, 16, 16, 16], start=1):
  ws2.column_dimensions[get_column_letter(i)].width = w

# ------------------------------------------------------------------
# SHEET 3: Hasil Dekomposisi VMD (semua sub-mode + residue ICEEMDAN)
# ------------------------------------------------------------------
ws3 = wb_vmd.create_sheet('Dekomposisi_VMD')
r = 1
n_cols_vmd = len(df_imfs_numeric.columns) + 1
r = title_block(
    ws3, r,
    'Hasil Akhir Dekomposisi Hybrid I-CEEMDAN-VMD (Seluruh Sub-mode + Residue)',
    span=min(n_cols_vmd, 12),
)
r += 1
vmd_headers = ['Tanggal'] + list(df_imfs_numeric.columns)
r = table_header(ws3, r, vmd_headers)
dates_vmd = (
    pd.to_datetime(dates).dt.strftime('%Y-%m-%d').values
    if hasattr(dates, 'dt') else [str(d)[:10] for d in dates]
)
for i in range(len(df_imfs_numeric)):
  row_vals = [dates_vmd[i]] + [
      round(float(df_imfs_numeric.iloc[i, c]), 6)
      for c in range(len(df_imfs_numeric.columns))
  ]
  r = table_row(ws3, r, row_vals, alt=(i % 2 == 0))
for i in range(1, n_cols_vmd + 1):
  ws3.column_dimensions[get_column_letter(i)].width = 16

# ------------------------------------------------------------------
# SHEET 4: Perhitungan Manual — Ilustrasi Rumus Metrik VMD
# ------------------------------------------------------------------
ws4 = wb_vmd.create_sheet('Perhitungan_Manual_VMD')
r = 1
r = title_block(
    ws4, r, 'PERHITUNGAN MANUAL METRIK EVALUASI VMD (Korelasi, ELC, Bandwidth)', span=7, size=14,
)
r = note_block(
    ws4, r,
    'Ilustrasi diambil dari IMF pertama (IMF_1) hasil I-CEEMDAN dengan parameter optimalnya, '
    'ditampilkan untuk 5 titik data pertama guna menunjukkan penerapan rumus. '
    'Perhitungan lengkap untuk seluruh data & seluruh mode dijalankan melalui software (Python).',
    span=7, height=44,
)
r += 1

# Ambil contoh IMF pertama & parameter optimalnya
imf0_name = vmd_summary_params[0]['IMF_Origin']
K0 = vmd_summary_params[0]['K']
alpha0 = vmd_summary_params[0]['Alpha']
f0 = iceemdan_imfs[0]
u0, u_hat0, omega0 = VMD(f0, alpha0, tau, K0, DC, init, tol)

# --- A. Korelasi antar-mode (Pearson) ---
r = title_block(ws4, r, f'A. Korelasi Antar-Mode (Pearson) — Contoh Mode 1 vs Mode 2 dari {imf0_name}', span=7, size=12)
r = note_block(ws4, r, 'r = Σ(x-x̄)(y-ȳ) / √[Σ(x-x̄)² · Σ(y-ȳ)²]  ;  metrik akhir = rata-rata |r| antar mode berurutan', span=7, height=22)
r = table_header(ws4, r, ['g (Titik ke-)', 'x = Mode1(g)', 'y = Mode2(g)', 'x - x̄', 'y - ȳ', '(x-x̄)(y-ȳ)', '(x-x̄)²'])
x_m, y_m = u0[0][:5], u0[1][:5]
x_mean_full, y_mean_full = u0[0].mean(), u0[1].mean()
for k in range(5):
  dx = x_m[k] - x_mean_full
  dy = y_m[k] - y_mean_full
  r = table_row(
      ws4, r,
      [
          k + 1, round(float(x_m[k]), 6), round(float(y_m[k]), 6),
          round(float(dx), 6), round(float(dy), 6),
          round(float(dx * dy), 6), round(float(dx ** 2), 6),
      ],
      alt=(k % 2 == 0),
  )
corr_full, _ = pearsonr(u0[0], u0[1])
r = note_block(
    ws4, r,
    f'Hasil korelasi Mode1 vs Mode2 (seluruh data) = {corr_full:.6f}  →  '
    'dirata-ratakan dengan pasangan mode lain untuk memperoleh "Mean Correlation".',
    span=7, height=22,
)
r += 1

# --- B. ELC (Error Rekonstruksi / Energy Loss) ---
r = title_block(ws4, r, f'B. Error Rekonstruksi / Energy Loss Coefficient (ELC) — {imf0_name}', span=7, size=12)
r = note_block(ws4, r, 'ELC = Σ(residu)² / Σ(sinyal asli)²  ;  residu(g) = f(g) - Σ_k u_k(g)', span=7, height=22)
r = table_header(ws4, r, ['g (Titik ke-)', 'f(g) Sinyal Asli', 'Σu_k(g) Rekonstruksi', 'Residu = f - Σu', 'Residu²', 'f(g)²', ''])
recon0 = u0.sum(axis=0)
res0 = f0 - recon0
for k in range(5):
  r = table_row(
      ws4, r,
      [
          k + 1, round(float(f0[k]), 4), round(float(recon0[k]), 4),
          round(float(res0[k]), 6), round(float(res0[k] ** 2), 6),
          round(float(f0[k] ** 2), 4), '',
      ],
      alt=(k % 2 == 0),
  )
elc_full = np.sum(res0 ** 2) / np.sum(f0 ** 2)
r = note_block(
    ws4, r,
    f'ELC = Σ(residu²) / Σ(f²) [seluruh data] = {np.sum(res0**2):.4f} / '
    f'{np.sum(f0**2):.4f} = {elc_full:.6f}',
    span=7, height=22,
)
r += 1

# --- C. Bandwidth Rata-rata Mode (via spektrum PSD) ---
r = title_block(ws4, r, f'C. Bandwidth Mode (Variansi Frekuensi Ternormalisasi PSD) — Contoh Mode 1 dari {imf0_name}', span=7, size=12)
r = note_block(
    ws4, r,
    'mean_f = Σ(freq·PSD)/Σ(PSD)  ;  BW = Σ[(freq-mean_f)²·PSD]/Σ(PSD)  ;  '
    'PSD(g) = |FFT(mode)(g)|²  ;  hanya frekuensi ≥ 0 digunakan',
    span=7, height=32,
)
mode_fft0 = np.fft.fft(u0[0])
psd0 = np.abs(mode_fft0) ** 2
freqs0 = np.fft.fftfreq(len(u0[0]))
pos0 = freqs0 >= 0
psd_pos0 = psd0[pos0]
freqs_pos0 = freqs0[pos0]
r = table_header(ws4, r, ['k (indeks freq ≥0)', 'freq(k)', 'PSD(k)=|FFT|²', 'freq(k)·PSD(k)', '(freq-mean_f)²·PSD(k)', '', ''])
mean_f0 = np.sum(freqs_pos0 * psd_pos0) / np.sum(psd_pos0)
for k in range(5):
  r = table_row(
      ws4, r,
      [
          k + 1, round(float(freqs_pos0[k]), 6), round(float(psd_pos0[k]), 4),
          round(float(freqs_pos0[k] * psd_pos0[k]), 4),
          round(float(((freqs_pos0[k] - mean_f0) ** 2) * psd_pos0[k]), 4), '', '',
      ],
      alt=(k % 2 == 0),
  )
var_f0 = np.sum(((freqs_pos0 - mean_f0) ** 2) * psd_pos0) / np.sum(psd_pos0)
r = note_block(
    ws4, r,
    f'mean_f (seluruh titik) = {mean_f0:.6f}  ;  Bandwidth Mode 1 = '
    f'Σ[(freq-mean_f)²·PSD]/Σ(PSD) = {var_f0:.8f} '
    '(mendekati nilai BW pada sheet Pencarian_Parameter)',
    span=7, height=22,
)

for i in range(1, 8):
  ws4.column_dimensions[get_column_letter(i)].width = 20

# ─── SIMPAN FILE EXCEL ──────────────────────────────────────────────
xlsx_path_vmd = os.path.join(output_dir, 'vmd_hasil_lengkap.xlsx')
wb_vmd.save(xlsx_path_vmd)
print(f'\n💾 Excel lengkap VMD disimpan: {xlsx_path_vmd}')
print('   Sheet: Pencarian_Parameter, Parameter_Optimal, Dekomposisi_VMD, Perhitungan_Manual_VMD')