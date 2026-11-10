import os, sys, json, gzip, base64

os.makedirs("scratch/test_new_admin", exist_ok=True)

with open("scratch/benchmarks_admin_b64.txt", "r", encoding="utf-8") as f:
    b64_str = f.read().strip()

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    c6_orig = f.read()

# Let's inspect c6 imports
# Need to make sure json, gzip, base64 are imported
imports_to_add = "import json\nimport gzip\nimport base64\n"
if "import json" not in c6_orig:
    c6_orig = c6_orig.replace("import os\n", "import os\nimport json\nimport gzip\nimport base64\n")

# Benchmark block
benchmark_block = f'''
# ============================================================
# BENCHMARK RESMI SELURUH METODE (ADMIN)
# Berisi hasil resmi (Hybrid ICEEMDAN-VMD-GRU, Hybrid ICEEMDAN-GRU,
# Hybrid VMD-GRU, GRU) untuk seluruh 5 destinasi.
# Memungkinkan hasil evaluasi langsung tampil instan tanpa training ulang
# di Google Colab maupun lokal.
# ============================================================
_BENCHMARKS_ADMIN_B64 = """{b64_str}"""

try:
    BENCHMARKS_ADMIN = json.loads(gzip.decompress(base64.b64decode(_BENCHMARKS_ADMIN_B64.encode("ascii"))).decode("utf-8"))
except Exception:
    BENCHMARKS_ADMIN = {{}}


def _cari_benchmark(metode, destinasi):
    """Cari data benchmark resmi toleran nama metode dan destinasi."""
    m_k = _nn(metode)
    d_k = _nn(destinasi)
    if m_k in BENCHMARKS_ADMIN and d_k in BENCHMARKS_ADMIN[m_k]:
        return dict(BENCHMARKS_ADMIN[m_k][d_k])
    aliases = [_nn(a) for a in DEST_ALIASES.get(destinasi.lower(), [])] + [d_k]
    for mk, d_dict in BENCHMARKS_ADMIN.items():
        if mk == m_k or mk in m_k or m_k in mk:
            for ak in aliases:
                if ak in d_dict:
                    return dict(d_dict[ak])
    return None

'''

# Insert benchmark_block after BULAN_PENDEK
idx_bulan = c6_orig.find('BULAN_PENDEK =')
if idx_bulan != -1:
    end_of_line = c6_orig.find('\n', idx_bulan)
    c6_new = c6_orig[:end_of_line+1] + benchmark_block + c6_orig[end_of_line+1:]
else:
    c6_new = benchmark_block + c6_orig

# Now update jalankan_metode
target_jalankan = '''    if fol:
        lapor(0.40, f"Memuat hasil ({os.path.basename(fol)})...")
        res, alasan = _muat_cached(fol, destinasi, metode, _signature(fol))
        if res:
            lapor(1.0, "Selesai")
            return res
    else:
        alasan = ("Folder hasil tidak ditemukan. Dicari di: "
                  + "; ".join(_daftar_dicari(metode)) + f"/<{destinasi}>/hasil-interpolasi/...")

    if destinasi.lower() in WAJIB_DARI_FOLDER.get(metode, set()):'''

replace_jalankan = '''    if fol:
        lapor(0.40, f"Memuat hasil ({os.path.basename(fol)})...")
        res, alasan = _muat_cached(fol, destinasi, metode, _signature(fol))
        if res:
            lapor(1.0, "Selesai")
            return res
    else:
        alasan = ("Folder hasil tidak ditemukan. Dicari di: "
                  + "; ".join(_daftar_dicari(metode)) + f"/<{destinasi}>/hasil-interpolasi/...")

    # Benchmark resmi (instan, tanpa training ulang, bekerja langsung di Google Colab)
    bm = _cari_benchmark(metode, destinasi)
    if bm is not None:
        lapor(0.70, f"Memuat hasil resmi benchmark skripsi ({metode})...")
        lapor(1.0, "Selesai")
        res = dict(bm)
        if data_clean is not None and "visitors" in data_clean:
            sinyal = data_clean["visitors"].values.astype(float)
            if len(sinyal) == len(res.get("aktual_hist", [])):
                res["aktual_hist"] = [float(v) for v in sinyal]
                res["aktual_uji"] = [float(v) for v in sinyal[-len(res["prediksi_uji"]):]]
        return _lengkapi(res)

    if destinasi.lower() in WAJIB_DARI_FOLDER.get(metode, set()):'''

assert target_jalankan in c6_new, "target_jalankan not found in c6_new"
c6_new = c6_new.replace(target_jalankan, replace_jalankan)

# Update OPSI_PER_METODE
target_opsi = '''OPSI_PER_METODE = {
    "Hybrid ICEEMDAN-VMD-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD",
                                "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid ICEEMDAN-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN",
                            "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid VMD-GRU": ["Interpolasi Linear", "Dekomposisi VMD",
                       "Normalisasi", "Evaluasi & Prediksi"],
    "GRU": ["Interpolasi Linear", "Normalisasi", "Evaluasi & Prediksi"],
}'''

replace_opsi = '''OPSI_PER_METODE = {
    "Hybrid ICEEMDAN-VMD-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD",
                                "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid ICEEMDAN-GRU": ["Evaluasi & Prediksi"],
    "Hybrid VMD-GRU": ["Evaluasi & Prediksi"],
    "GRU": ["Evaluasi & Prediksi"],
}'''

assert target_opsi in c6_new, "target_opsi not found in c6_new"
c6_new = c6_new.replace(target_opsi, replace_opsi)

# Update render_hasil_admin
target_render = '''    with st.container(border=True):
        _head("Pilih Visualisasi Tahapan",
              f"Alur {metode.replace('Hybrid ', '')}: dari data aktual sampai hasil peramalan")
        pilihan = _menu_tahapan(opsi, key=f"{kp}_menu")
    st.write("")

    # Tahap pra-proses (khusus ICEEMDAN-VMD-GRU); evaluasi & prediksi tetap seperti semula
    if pilihan != "Evaluasi & Prediksi":
        if metode == "Hybrid ICEEMDAN-VMD-GRU":
            render_tahap_praproses(h, pilihan, kp, raw_df)
        return

    # ---------------- Evaluasi & Prediksi (TIDAK DIUBAH) ----------------
    # ... biarkan seluruh isi lama mulai dari `if True:` sampai akhir fungsi ...

    # ---------------- Evaluasi & Prediksi ----------------
    if True:'''

replace_render = '''    if metode == "Hybrid ICEEMDAN-VMD-GRU":
        with st.container(border=True):
            _head("Pilih Visualisasi Tahapan",
                  f"Alur {metode.replace('Hybrid ', '')}: dari data aktual sampai hasil peramalan")
            pilihan = _menu_tahapan(opsi, key=f"{kp}_menu")
        st.write("")

        # Tahap pra-proses (khusus ICEEMDAN-VMD-GRU); evaluasi & prediksi tetap seperti semula
        if pilihan != "Evaluasi & Prediksi":
            render_tahap_praproses(h, pilihan, kp, raw_df)
            return
    else:
        # Untuk metode lain, langsung masuk ke bagian Evaluasi & Prediksi tanpa tahap kosong
        pilihan = "Evaluasi & Prediksi"
        st.session_state[f"{kp}_menu"] = "Evaluasi & Prediksi"
        st.session_state[f"_tahap_{kp}_menu"] = "Evaluasi & Prediksi"

    # ---------------- Evaluasi & Prediksi ----------------
    if True:'''

assert target_render in c6_new, "target_render not found in c6_new"
c6_new = c6_new.replace(target_render, replace_render)

# Write to scratch/test_new_admin/admin_methods.py
clean_c6 = c6_new
if clean_c6.startswith("%%writefile"):
    clean_c6 = clean_c6.split("\n", 1)[1]

with open("scratch/test_new_admin/admin_methods.py", "w", encoding="utf-8") as f:
    f.write(clean_c6)

print("scratch/test_new_admin/admin_methods.py written successfully!")
