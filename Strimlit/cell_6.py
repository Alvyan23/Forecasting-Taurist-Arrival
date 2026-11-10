# Kedua kolom 'date' sudah berupa datetime, tidak perlu di-parse ulang

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(figsize=(15, 7), dpi=100)

ax.plot(
    data_clean['date'], 
    data_clean['visitors'], 
    label='Data Hasil Interpolasi (Trend)', 
    color='#2E86C1',
    linestyle='--', 
    linewidth=1.5,
    alpha=0.6
)

ax.plot(
    data['date'], 
    data['visitors'], 
    label='Data Asli (Sebelum Interpolasi)', 
    color='#1B4F72',
    linewidth=2.5,
    marker='o',
    markersize=4,
    markevery=3
)

ax.fill_between(
    data_clean['date'], 
    data['visitors'], 
    data_clean['visitors'], 
    where=(data['visitors'] == 0),
    color='#AED6F1', 
    alpha=0.4, 
    label='Area Pengisian Gap'
)

zero_indices = data.index[data['visitors'] == 0]


ax.set_title('Analisis Perbandingan Data Pengunjung: Original vs Imputasi Linear', 
             fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
ax.set_xlabel('Tahun & Bulan', fontsize=12, labelpad=10)
ax.set_ylabel('Jumlah Pengunjung', fontsize=12, labelpad=10)

date_form = DateFormatter("%b %Y")
ax.xaxis.set_major_formatter(date_form)

sns.despine(left=True, bottom=False)

ax.legend(loc='upper right', frameon=True, facecolor='white', fontsize=10)
ax.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()