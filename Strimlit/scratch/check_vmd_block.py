with open('admin_methods.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Cek bagian Dekomposisi VMD
vmd_start = text.find('# ============ 3. DEKOMPOSISI VMD (VMD-GRU & ICEEMDAN-VMD-GRU) ============')
norm_start = text.find('# ============ 4. NORMALISASI MIN-MAX (SEMUA METODE) ============')
print("VMD block length:", norm_start - vmd_start)
print(text[vmd_start:vmd_start + 300])
