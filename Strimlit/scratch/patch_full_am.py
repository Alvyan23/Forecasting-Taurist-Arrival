import sys, os, re, pandas as pd

with open("scratch/benchmarks_admin_full_b64.txt", "r", encoding="utf-8") as f:
    full_b64 = f.read().strip()

with open("admin_methods.py", "r", encoding="utf-8") as f:
    orig = f.read()

# Replace the _BENCHMARKS_ADMIN_B64
b64_pattern = r'_BENCHMARKS_ADMIN_B64 = """[\s\S]*?"""'
assert re.search(b64_pattern, orig), "Cannot find _BENCHMARKS_ADMIN_B64"
updated = re.sub(b64_pattern, f'_BENCHMARKS_ADMIN_B64 = """{full_b64}"""', orig)

# Add helpers _muat_ice_xlsx and _muat_info_vmd_folder before _baca_tabel
helpers = '''
def _muat_ice_xlsx(folder):
    """Ambil IMF dan Residue dari output_hasil/iceemdan_decomposition.xlsx."""
    ice_xlsx = os.path.join(folder, "output_hasil", "iceemdan_decomposition.xlsx")
    if os.path.exists(ice_xlsx):
        try:
            df_ice = pd.read_excel(ice_xlsx, header=None)
            for idx, row in df_ice.iterrows():
                row_str = [str(x).strip().lower() for x in row.values]
                if "imf_1" in row_str:
                    df_ice.columns = [str(x).strip() for x in row.values]
                    df_ice_data = df_ice.iloc[idx + 1:].dropna(how="all")
                    ice = {}
                    for c in df_ice_data.columns:
                        if re.match(r"^IMF_\d+$", c) or "residue" in c.lower():
                            ice[c] = pd.to_numeric(df_ice_data[c], errors="coerce").fillna(0).astype(float).tolist()
                    return ice
        except Exception:
            pass
    return {}


def _muat_info_vmd_folder(folder):
    """Ambil tabel parameter optimal & pencarian VMD dari vmd_hasil_lengkap.xlsx."""
    p = os.path.join(folder, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    if not os.path.exists(p):
        return None
    try:
        def _baca_sheet(sheet):
            df = pd.read_excel(p, sheet_name=sheet, header=None)
            for idx, row in df.iterrows():
                first_val = str(row.values[0]).strip().lower()
                if first_val in ("sinyal", "imf asal"):
                    header = [str(c).strip() for c in row.values]
                    data = df.iloc[idx + 1:].copy()
                    data.columns = header
                    return data.dropna(how="all").reset_index(drop=True)
            return df
        return {
            "optimal": _baca_sheet("Parameter_Optimal"),
            "candidates": _baca_sheet("Pencarian_Parameter"),
        }
    except Exception:
        return None
'''

if "_muat_info_vmd_folder" not in updated:
    idx_baca = updated.find("def _baca_tabel(path):")
    assert idx_baca != -1, "Cannot find def _baca_tabel"
    updated = updated[:idx_baca] + helpers + "\n\n" + updated[idx_baca:]

# In _ambil_imfs:
target_ambil_imfs = '''def _ambil_imfs(h, pra, dari_unggahan):
    """ICEEMDAN: dari folder notebook bila ada & tidak ada unggahan baru; selain itu hitung."""
    ice = h.get("ice_data") or {}
    if (not dari_unggahan) and h.get("loaded_from_folder") and ice:
        return {k: np.asarray(v, float) for k, v in ice.items()}
    with st.spinner("Menjalankan I-CEEMDAN (trials=100, ε0=0.2, seed=42)... "
                    "pertama kali bisa beberapa menit, selanjutnya instan."):
        return hitung_iceemdan(np.asarray(pra["clean"], float))'''

replace_ambil_imfs = '''def _ambil_imfs(h, pra, dari_unggahan):
    """ICEEMDAN: dari folder notebook / benchmark bila ada & tidak ada unggahan baru; selain itu hitung."""
    ice = h.get("ice_data") or {}
    if (not dari_unggahan) and ice:
        return {k: np.asarray(v, float) for k, v in ice.items()}
    fol = h.get("folder", "")
    if fol and not dari_unggahan:
        ice_fol = _muat_ice_xlsx(fol)
        if ice_fol:
            return {k: np.asarray(v, float) for k, v in ice_fol.items()}
    if (not dari_unggahan) and h.get("comps") and h.get("metode") == "Hybrid ICEEMDAN-GRU":
        return {k: np.asarray(v, float) for k, v in h["comps"].items()}
    with st.spinner("Menjalankan I-CEEMDAN (trials=100, ε0=0.2, seed=42)... "
                    "pertama kali bisa beberapa menit, selanjutnya instan."):
        return hitung_iceemdan(np.asarray(pra["clean"], float))'''

assert target_ambil_imfs in updated, "target_ambil_imfs not found"
updated = updated.replace(target_ambil_imfs, replace_ambil_imfs)

# In _muat_inti:
target_muat_inti_comps = '''    comps, ice_data = _muat_dekomposisi(folder, list(sub_mode_preds.keys()))
    if metode == "Hybrid ICEEMDAN-GRU" and not ice_data:
        ice_data = dict(comps)
    if metode == "GRU" and not comps:
        comps = {"GRU": list(visitors_clean)}
    _, vmd_modes = _turunan_dari_comps(comps, metode)'''

replace_muat_inti_comps = '''    comps, ice_data = _muat_dekomposisi(folder, list(sub_mode_preds.keys()))
    ice_xlsx_data = _muat_ice_xlsx(folder)
    if ice_xlsx_data:
        ice_data.update(ice_xlsx_data)
    if metode == "Hybrid ICEEMDAN-GRU" and not ice_data:
        ice_data = dict(comps)
    ice_derived, vmd_modes = _turunan_dari_comps(comps, metode)
    if not ice_data and ice_derived:
        ice_data = ice_derived
    if metode == "GRU" and not comps:
        comps = {"GRU": list(visitors_clean)}'''

assert target_muat_inti_comps in updated, "target_muat_inti_comps not found"
updated = updated.replace(target_muat_inti_comps, replace_muat_inti_comps)

# Update OPSI_PER_METODE:
target_opsi = '''OPSI_PER_METODE = {
    "Hybrid ICEEMDAN-VMD-GRU": ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD",
                                "Normalisasi", "Evaluasi & Prediksi"],
    "Hybrid ICEEMDAN-GRU": ["Evaluasi & Prediksi"],
    "Hybrid VMD-GRU": ["Evaluasi & Prediksi"],
    "GRU": ["Evaluasi & Prediksi"],
}'''

replace_opsi = '''OPSI_PER_METODE = {
    "Hybrid ICEEMDAN-VMD-GRU": [
        "Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD",
        "Normalisasi", "Evaluasi & Prediksi"
    ],
    "Hybrid ICEEMDAN-GRU": [
        "Interpolasi Linear", "Dekomposisi I-CEEMDAN",
        "Normalisasi", "Evaluasi & Prediksi"
    ],
    "Hybrid VMD-GRU": [
        "Interpolasi Linear", "Dekomposisi VMD",
        "Normalisasi", "Evaluasi & Prediksi"
    ],
    "GRU": [
        "Interpolasi Linear",
        "Normalisasi", "Evaluasi & Prediksi"
    ],
}'''

assert target_opsi in updated, "target_opsi not found"
updated = updated.replace(target_opsi, replace_opsi)

# Now update render_hasil_admin:
target_render_adm = '''    if metode == "Hybrid ICEEMDAN-VMD-GRU":
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

    # ---------------- Evaluasi & Prediksi ----------------'''

replace_render_adm = '''    with st.container(border=True):
        _head("Pilih Visualisasi Tahapan",
              f"Alur {metode.replace('Hybrid ', '')}: dari data aktual sampai hasil peramalan")
        pilihan = _menu_tahapan(opsi, key=f"{kp}_menu")
    st.write("")

    # Tahap pra-proses untuk semua metode (Interpolasi, Dekomposisi, Normalisasi)
    if pilihan != "Evaluasi & Prediksi":
        render_tahap_praproses(h, pilihan, kp, raw_df)
        return

    # ---------------- Evaluasi & Prediksi ----------------'''

assert target_render_adm in updated, "target_render_adm not found"
updated = updated.replace(target_render_adm, replace_render_adm)

# Now update render_tahap_praproses:
# Find render_tahap_praproses start and end
idx_render_tp = updated.find("def render_tahap_praproses(h, tahap, kp, raw_df=None):")
assert idx_render_tp != -1, "Cannot find def render_tahap_praproses"
idx_next_sec = updated.find("# ============================================================", idx_render_tp)
assert idx_next_sec != -1, "Cannot find end of render_tahap_praproses"

new_render_tahap_praproses = '''def render_tahap_praproses(h, tahap, kp, raw_df=None):
    if go is None or make_subplots is None:
        st.error("Plotly belum terpasang.")
        return
    df = raw_df if raw_df is not None else _raw_df_dari_h(h)
    pra = proses_interpolasi(df)
    tgl = pra["dates"]
    metode = h.get("metode", "Hybrid ICEEMDAN-VMD-GRU")

    dari_unggahan = False
    if raw_df is not None:
        a = np.asarray(h.get("aktual_hist", []), float)
        b = np.asarray(pra["clean"], float)
        dari_unggahan = (len(a) != len(b)) or (len(a) > 0 and float(np.max(np.abs(a - b))) > 2.0)

    # ============ 1. INTERPOLASI LINEAR (SEMUA METODE) ============
    if tahap == "Interpolasi Linear":
        n0 = len(pra["idx_nol"])
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            _mcard("a", "TOTAL DATA", _fmt_id(len(df)), "observasi bulanan")
        with c2:
            _mcard("b", "NILAI 0 TERDETEKSI", _fmt_id(n0),
                   f"{n0 / max(len(df), 1) * 100:.1f}% dari data")
        with c3:
            _mcard("a", "METODE PENANGANAN", "Linear", "0 → NaN → interpolasi linear")
        st.write("")
        with st.container(border=True):
            _head("Data Aktual (Sebelum Interpolasi)",
                  "Titik merah = nilai 0 yang terdeteksi pada file masukan")
            _show_chart(fig_deteksi_nol(pra), key=f"{kp}_deteksi")
        st.write("")
        with st.container(border=True):
            _head("Hasil Interpolasi Linear",
                  "Tanda x = nilai 0 yang berhasil diinterpolasi")
            _show_chart(fig_interpolasi_x(pra), key=f"{kp}_interp")
            if n0:
                with st.expander("Lihat tabel nilai 0 yang diimputasi"):
                    i0 = pra["idx_nol"]
                    _show_df(pd.DataFrame({
                        "Bulan": [_tgl_id(d) for d in tgl.iloc[i0]],
                        "Nilai Awal": [0] * n0,
                        "Hasil Interpolasi": [_fmt_id(v) for v in pra["clean"][i0]],
                    }), hide_index=True)
            else:
                st.info("Tidak ada nilai 0, data digunakan apa adanya.")
        return

    # ============ 2. DEKOMPOSISI I-CEEMDAN (ICEEMDAN-VMD-GRU & ICEEMDAN-GRU) ============
    if tahap == "Dekomposisi I-CEEMDAN":
        imfs = _ambil_imfs(h, pra, dari_unggahan)
        keys = list(imfs.keys())
        with st.container(border=True):
            _head("Dekomposisi I-CEEMDAN",
                  "Pemisahan sinyal historis menjadi sejumlah Intrinsic Mode Functions (IMF) dan Residu")
            items = [("Sinyal Input (Hasil Interpolasi)", pra["clean"])]
            items += [(k, imfs[k]) for k in keys]
            _show_chart(_stack_fig(tgl, items), key=f"{kp}_ice")
            rec = np.sum([imfs[k] for k in keys], axis=0)
            st.caption(f"MAE rekonstruksi (Σ IMF + residu vs sinyal): "
                       f"{_fmt_id(np.mean(np.abs(pra['clean'] - rec)), 6)}")

        # Jika ada tabel evaluasi rekonstruksi bertahap di folder
        fol = h.get("folder", "")
        mae_rek_p = os.path.join(fol, "hasil-dekomposisi", "mae_rekonstruksi_bertahap.csv") if fol else ""
        if mae_rek_p and os.path.exists(mae_rek_p):
            with st.expander("Lihat Evaluasi MAE Rekonstruksi Bertahap (Notebook)"):
                _show_df(pd.read_csv(mae_rek_p), hide_index=True)
        return

    # ============ 3. DEKOMPOSISI VMD (VMD-GRU & ICEEMDAN-VMD-GRU) ============
    if tahap == "Dekomposisi VMD":
        fol = h.get("folder", "")
        vmd_info = _muat_info_vmd_folder(fol) if (fol and not dari_unggahan) else None

        # Kasus A: Hybrid VMD-GRU (dekomposisi langsung sinyal pengunjung)
        if metode == "Hybrid VMD-GRU":
            if vmd_info and vmd_info.get("optimal") is not None:
                with st.container(border=True):
                    _head("Parameter VMD Optimal (Sinyal Pengunjung)",
                          "Hasil fine-tuning K=12 dan Alpha=100 pada data pengunjung")
                    _show_df(vmd_info["optimal"], hide_index=True)

            vmd_modes = {}
            if h.get("comps"):
                for k, v in h["comps"].items():
                    if k.startswith("VMD_"):
                        vmd_modes[k] = np.asarray(v, float)

            if vmd_modes:
                with st.container(border=True):
                    _head(f"Hasil Dekomposisi VMD ({len(vmd_modes)} Mode)",
                          "Pemisahan sinyal pengunjung menjadi 12 mode variasi frekuensi")
                    mode_keys = sorted(vmd_modes.keys(),
                                       key=lambda x: int(x.split("_")[1]) if x.split("_")[1].isdigit() else 0)
                    items = [("Sinyal Input (Hasil Interpolasi)", pra["clean"])]
                    items += [(k, vmd_modes[k]) for k in mode_keys]
                    _show_chart(_stack_fig(tgl, items, h_per=130), key=f"{kp}_vmd_all")
            else:
                st.info("Data mode VMD tidak tersedia.")

            if vmd_info and vmd_info.get("candidates") is not None:
                with st.expander("Lihat Rekap Pencarian Parameter VMD (Fine-Tuning K & Alpha)"):
                    _show_df(vmd_info["candidates"], hide_index=True)
            return

        # Kasus B: Hybrid ICEEMDAN-VMD-GRU (dekomposisi VMD per-IMF)
        if metode == "Hybrid ICEEMDAN-VMD-GRU":
            if vmd_info and vmd_info.get("optimal") is not None:
                with st.container(border=True):
                    _head("Parameter VMD Terbaik per IMF",
                          "Hasil fine-tuning K & Alpha optimal untuk setiap IMF hasil I-CEEMDAN")
                    _show_df(vmd_info["optimal"], hide_index=True)

            imf_vmd_groups = {}
            if h.get("comps"):
                for k, v in h["comps"].items():
                    m = re.match(r"^(IMF_\d+)_VMD_\d+$", k)
                    if m:
                        imf_vmd_groups.setdefault(m.group(1), {})[k] = np.asarray(v, float)

            imfs = _ambil_imfs(h, pra, dari_unggahan)
            if imf_vmd_groups:
                st.write("")
                for i, imf_name in enumerate(sorted(imf_vmd_groups.keys())):
                    modes_dict = imf_vmd_groups[imf_name]
                    mode_keys = sorted(modes_dict.keys(),
                                       key=lambda x: int(x.split("_VMD_")[1]) if x.split("_VMD_")[1].isdigit() else 0)
                    with st.expander(f"{imf_name} — optimal {len(mode_keys)} Mode VMD", expanded=(i == 0)):
                        if vmd_info and vmd_info.get("candidates") is not None:
                            df_c = vmd_info["candidates"]
                            first_col = df_c.columns[0]
                            cands_imf = df_c[df_c[first_col].astype(str) == imf_name]
                            if not cands_imf.empty:
                                _head(f"Pencarian Parameter VMD ({imf_name})")
                                _show_df(cands_imf, hide_index=True)
                        _head(f"Hasil Dekomposisi VMD ({imf_name})", f"{len(mode_keys)} mode")
                        inp_sig = imfs.get(imf_name, np.sum(list(modes_dict.values()), axis=0))
                        items = [(f"Sinyal Input ({imf_name})", inp_sig)]
                        items += [(f"Mode {m_idx + 1} ({k})", modes_dict[k]) for m_idx, k in enumerate(mode_keys)]
                        _show_chart(_stack_fig(tgl, items, h_per=130), key=f"{kp}_vm_{imf_name}")
                return
            else:
                bar, cb = _progress_ui()
                try:
                    vmd_all = hitung_semua_vmd(imfs, cb)
                except Exception as e:
                    bar.empty()
                    st.error(f"VMD gagal dijalankan: {e}")
                    return
                bar.empty()
                with st.container(border=True):
                    _head("Parameter VMD Terbaik per IMF")
                    _show_df(pd.DataFrame([{
                        "IMF": n, "K": r["best"]["K"], "Alpha": r["best"]["alpha"],
                        "Corr": round(r["best"]["Corr"], 5), "ELC": round(r["best"]["ELC"], 5),
                        "BW": round(r["best"]["BW"], 5)} for n, r in vmd_all.items()]),
                        hide_index=True)
                st.write("")
                for i, (name, r) in enumerate(vmd_all.items()):
                    b = r["best"]
                    with st.expander(f"{name} — optimal K={b['K']}, Alpha={b['alpha']}", expanded=(i == 0)):
                        _head(f"Pencarian Parameter VMD ({name})",
                              f"Garis merah = K optimal (K={b['K']}, Alpha={b['alpha']})")
                        _show_chart(fig_vmd_search(r["candidates"], b), key=f"{kp}_vs_{name}")
                        _head(f"Hasil Dekomposisi VMD ({name})", f"{b['K']} mode")
                        items = [(f"Sinyal Input ({name})", imfs[name])]
                        items += [(f"Mode {m + 1}", r["modes"][m]) for m in range(r["modes"].shape[0])]
                        _show_chart(_stack_fig(tgl, items, h_per=130), key=f"{kp}_vm_{name}")
                return

    # ============ 4. NORMALISASI MIN-MAX (SEMUA METODE) ============
    if tahap == "Normalisasi":
        if h.get("comps"):
            comps = {k: np.asarray(v, float) for k, v in h["comps"].items()}
        elif (not dari_unggahan) and h.get("loaded_from_folder") and h.get("comps"):
            comps = {k: np.asarray(v, float) for k, v in h["comps"].items()}
        else:
            comps = {k: np.asarray(v, float)
                     for k, v in _komponen(h.get("destinasi", ""), metode, pra["clean"]).items()}

        nama = st.selectbox("Pilih komponen", list(comps.keys()), key=f"{kp}_pilih_norm")
        y = comps[nama].reshape(-1, 1)
        sc = MinMaxScaler(feature_range=(0, 1))
        y_norm = sc.fit_transform(y).ravel()
        with st.container(border=True):
            _head("Normalisasi Min-Max per Komponen", f"Komponen terpilih: {nama}")
            _show_chart(fig_norm_pra(tgl, y.ravel(), y_norm, nama), key=f"{kp}_norm")
            with st.expander("Ringkasan Min–Max seluruh komponen"):
                _show_df(pd.DataFrame([{
                    "Komponen": k, "x_min": round(float(np.min(v)), 4),
                    "x_max": round(float(np.max(v)), 4),
                    "Range": round(float(np.max(v) - np.min(v)), 4)}
                    for k, v in comps.items()]), hide_index=True)

            fol = h.get("folder", "")
            norm_xlsx = os.path.join(fol, "hasil-normalisasi", "normalisasi_hasil_lengkap.xlsx") if fol else ""
            if norm_xlsx and os.path.exists(norm_xlsx):
                with st.expander("Lihat Ringkasan Nilai Min & Max Notebook (Excel)"):
                    try:
                        df_n = pd.read_excel(norm_xlsx, sheet_name="Ringkasan_MinMax", header=2)
                        _show_df(df_n, hide_index=True)
                    except Exception:
                        pass
        return
'''

updated = updated[:idx_render_tp] + new_render_tahap_praproses + "\n\n" + updated[idx_next_sec:]

with open("scratch/test_tab_render/admin_methods.py", "w", encoding="utf-8") as f:
    f.write(updated)

print("Generated scratch/test_tab_render/admin_methods.py successfully!")
