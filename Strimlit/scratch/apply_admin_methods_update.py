import sys, os, shutil, time

sys.stdout.reconfigure(encoding='utf-8')

# Backup admin_methods.py
ts = time.strftime("%Y%m%d_%H%M%S")
bak_name = f"admin_methods.py.bak_{ts}"
shutil.copy("admin_methods.py", bak_name)
print(f"Backed up admin_methods.py to {bak_name}")

with open("admin_methods.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update _BENCHMARKS_ADMIN_B64
with open("scratch/benchmarks_admin_vmd_b64.txt", "r", encoding="utf-8") as f:
    b64_new = f.read().strip()

lines = content.splitlines(keepends=True)
for i, line in enumerate(lines):
    if line.startswith('_BENCHMARKS_ADMIN_B64 = """'):
        lines[i] = f'_BENCHMARKS_ADMIN_B64 = """{b64_new}"""\n'
        print(f"Updated _BENCHMARKS_ADMIN_B64 at line {i+1}")
        break

content = "".join(lines)

# 2. Update fig_vmd_search guard
old_fig_vmd = '''def fig_vmd_search(cands, best):
    """3 panel: Mean Bandwidth, ELC, Mean Correlation terhadap K (K optimal garis merah)."""
    df = pd.DataFrame(cands)'''

new_fig_vmd = '''def fig_vmd_search(cands, best):
    """3 panel: Mean Bandwidth, ELC, Mean Correlation terhadap K (K optimal garis merah)."""
    if go is None or make_subplots is None:
        return None
    df = pd.DataFrame(cands)'''

assert old_fig_vmd in content, "old_fig_vmd not found!"
content = content.replace(old_fig_vmd, new_fig_vmd, 1)
print("Updated fig_vmd_search guard.")

# 3. Add helper functions muat_vmd_all_dari_folder & _dapatkan_vmd_all before render_tahap_praproses
helpers = '''def muat_vmd_all_dari_folder(folder, metode, h):
    """Ambil candidates, best, dan modes VMD dari vmd_hasil_lengkap.xlsx pada folder notebook."""
    p = os.path.join(folder, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    if not os.path.exists(p):
        return None
    try:
        df_c_raw = pd.read_excel(p, sheet_name="Pencarian_Parameter", header=None)
        h_idx = -1
        for idx, row in df_c_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if "k" in row_str and "alpha" in row_str:
                h_idx = idx
                break
        if h_idx == -1:
            return None
        df_c = df_c_raw.iloc[h_idx + 1:].dropna(how="all").copy()
        df_c.columns = [str(x).strip() for x in df_c_raw.iloc[h_idx].values]

        df_b_raw = pd.read_excel(p, sheet_name="Parameter_Optimal", header=None)
        b_idx = -1
        for idx, row in df_b_raw.iterrows():
            row_str = [str(x).strip().lower() for x in row.values]
            if any("k optimal" in x or "k_optimal" in x for x in row_str):
                b_idx = idx
                break
        if b_idx == -1:
            return None
        df_b = df_b_raw.iloc[b_idx + 1:].dropna(how="all").copy()
        df_b.columns = [str(x).strip() for x in df_b_raw.iloc[b_idx].values]

        first_c = df_c.columns[0]
        first_b = df_b.columns[0]

        vmd_all = {}
        if metode == "Hybrid VMD-GRU":
            signal_name = "Visitors"
            cands = []
            for _, r in df_c.iterrows():
                cands.append({
                    "K": int(r["K"]),
                    "alpha": int(r["Alpha"]),
                    "Corr": float(r["Korelasi Antar-Mode"]),
                    "ELC": float(r["ELC (Error Rekonstruksi)"]),
                    "BW": float(r["Bandwidth Rata-rata"]),
                })
            r_b = df_b.iloc[0]
            best = {
                "K": int(r_b["K Optimal"]),
                "alpha": int(r_b["Alpha Optimal"]),
                "Corr": float(r_b["Korelasi"]),
                "ELC": float(r_b["ELC"]),
                "BW": float(r_b["Bandwidth"]),
            }
            vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith("VMD_")],
                              key=lambda x: int(x.split("_")[1]) if x.split("_")[1].isdigit() else 0)
            modes = np.array([h["comps"][k] for k in vmd_keys], dtype=float) if vmd_keys else np.zeros((best["K"], len(h.get("aktual_hist", []))))
            vmd_all[signal_name] = {"candidates": cands, "best": best, "modes": modes}

        elif metode == "Hybrid ICEEMDAN-VMD-GRU":
            for _, r_b in df_b.iterrows():
                imf_name = str(r_b[first_b]).strip()
                sub_c = df_c[df_c[first_c].astype(str).str.strip() == imf_name]
                cands = []
                for _, r in sub_c.iterrows():
                    cands.append({
                        "K": int(r["K"]),
                        "alpha": int(r["Alpha"]),
                        "Corr": float(r["Korelasi Antar-Mode"]),
                        "ELC": float(r["ELC (Error Rekonstruksi)"]),
                        "BW": float(r["Bandwidth Rata-rata"]),
                    })
                best = {
                    "K": int(r_b["K Optimal"]),
                    "alpha": int(r_b["Alpha Optimal"]),
                    "Corr": float(r_b["Korelasi"]),
                    "ELC": float(r_b["ELC"]),
                    "BW": float(r_b["Bandwidth"]),
                }
                prefix = f"{imf_name}_VMD_"
                vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith(prefix)],
                                  key=lambda x: int(x.split("_VMD_")[1]) if x.split("_VMD_")[1].isdigit() else 0)
                modes = np.array([h["comps"][k] for k in vmd_keys], dtype=float) if vmd_keys else np.zeros((best["K"], len(h.get("aktual_hist", []))))
                vmd_all[imf_name] = {"candidates": cands, "best": best, "modes": modes}

        return vmd_all
    except Exception:
        return None


def _dapatkan_vmd_all(h, pra, dari_unggahan):
    """Ambil vmd_all (candidates, best, modes) dari folder / benchmark resmi / fallback hitung."""
    metode = h.get("metode", "")
    fol = h.get("folder", "")
    vmd_all = None

    if fol and not dari_unggahan:
        vmd_all = muat_vmd_all_dari_folder(fol, metode, h)

    if not vmd_all and h.get("vmd_search_data") and not dari_unggahan:
        vmd_all = {}
        for name, d in h["vmd_search_data"].items():
            candidates = d.get("candidates", [])
            best = d.get("best", {})
            if metode == "Hybrid VMD-GRU":
                vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith("VMD_")],
                                  key=lambda x: int(x.split("_")[1]) if x.split("_")[1].isdigit() else 0)
            else:
                prefix = f"{name}_VMD_"
                vmd_keys = sorted([k for k in h.get("comps", {}).keys() if k.startswith(prefix)],
                                  key=lambda x: int(x.split("_VMD_")[1]) if x.split("_VMD_")[1].isdigit() else 0)
            if vmd_keys:
                modes = np.array([h["comps"][k] for k in vmd_keys], dtype=float)
            else:
                k_cnt = best.get("K", 1)
                modes = np.zeros((k_cnt, len(pra["clean"])))
            vmd_all[name] = {"candidates": candidates, "best": best, "modes": modes}

    if not vmd_all:
        bar, cb = _progress_ui()
        try:
            if metode == "Hybrid VMD-GRU":
                vmd_all = hitung_semua_vmd({"Visitors": pra["clean"]}, cb)
            else:
                imfs = _ambil_imfs(h, pra, dari_unggahan)
                vmd_all = hitung_semua_vmd(imfs, cb)
        except Exception as e:
            if bar:
                bar.empty()
            if st:
                st.error(f"VMD gagal dijalankan: {e}")
            return None
        if bar:
            bar.empty()

    return vmd_all


'''

target_praproses = 'def render_tahap_praproses(h, tahap, kp, raw_df=None):'
assert target_praproses in content, "target_praproses not found!"
content = content.replace(target_praproses, helpers + target_praproses, 1)
print("Added muat_vmd_all_dari_folder and _dapatkan_vmd_all.")

# 4. Replace Dekomposisi VMD section in render_tahap_praproses
vmd_target_start = '# ============ 3. DEKOMPOSISI VMD (VMD-GRU & ICEEMDAN-VMD-GRU) ============'
vmd_target_end = '# ============ 4. NORMALISASI MIN-MAX (SEMUA METODE) ============'

s_pos = content.find(vmd_target_start)
e_pos = content.find(vmd_target_end)
assert s_pos != -1 and e_pos != -1, "VMD section range not found!"

new_vmd_section = '''# ============ 3. DEKOMPOSISI VMD (VMD-GRU & ICEEMDAN-VMD-GRU) ============
    if tahap == "Dekomposisi VMD":
        vmd_all = _dapatkan_vmd_all(h, pra, dari_unggahan)
        if not vmd_all:
            if st:
                st.warning("Data visualisasi Dekomposisi VMD tidak tersedia.")
            return

        imfs = _ambil_imfs(h, pra, dari_unggahan) if "ICEEMDAN" in metode else {}

        # 1. Tabel Ringkasan Parameter Optimal VMD
        with st.container(border=True):
            if metode == "Hybrid VMD-GRU":
                b_vis = vmd_all.get("Visitors", {}).get("best", {})
                k_val = b_vis.get("K", 12)
                a_val = b_vis.get("alpha", 100)
                _head("Parameter VMD Optimal (Sinyal Pengunjung)",
                      f"Hasil fine-tuning K={k_val} dan Alpha={a_val} pada data pengunjung")
            else:
                _head("Parameter VMD Terbaik per IMF",
                      "Hasil fine-tuning K & Alpha optimal untuk setiap IMF hasil I-CEEMDAN")

            rows_opt = []
            for n, r in vmd_all.items():
                b = r["best"]
                lbl = "Sinyal Input" if metode == "Hybrid VMD-GRU" else "IMF"
                rows_opt.append({
                    lbl: n,
                    "K Optimal": int(b["K"]),
                    "Alpha Optimal": int(b["alpha"]),
                    "Mean Correlation": round(float(b.get("Corr", 0)), 5),
                    "Energy Loss (ELC)": round(float(b.get("ELC", 0)), 5),
                    "Mean Bandwidth": round(float(b.get("BW", 0)), 5),
                })
            _show_df(pd.DataFrame(rows_opt), hide_index=True)

        st.write("")

        # 2. Visualisasi Pencarian Parameter (fig_vmd_search) & Hasil Dekomposisi per Sinyal / IMF
        for i, (name, r) in enumerate(vmd_all.items()):
            b = r["best"]
            n_modes = len(r["modes"]) if isinstance(r["modes"], (list, np.ndarray)) else b.get("K", 12)
            lbl_title = f"{name} — Optimal K={b['K']}, Alpha={b['alpha']} ({n_modes} Mode VMD)"
            with st.expander(lbl_title, expanded=(i == 0)):
                _head(f"Pencarian Parameter VMD ({name})",
                      f"Garis merah = K optimal (K={b['K']}, Alpha={b['alpha']}) | 3 Panel: Mean Bandwidth, Energy Loss (ELC), Mean Correlation")
                if r.get("candidates"):
                    fig_search = fig_vmd_search(r["candidates"], b)
                    if fig_search:
                        _show_chart(fig_search, key=f"{kp}_vs_{name}")

                _head(f"Hasil Dekomposisi VMD ({name})", f"{n_modes} Mode Variasi Frekuensi")
                if metode == "Hybrid VMD-GRU":
                    inp_sig = pra["clean"]
                    nama_input = "Sinyal Pengunjung (Hasil Interpolasi)"
                else:
                    inp_sig = imfs.get(name)
                    if inp_sig is None:
                        inp_sig = np.sum(r["modes"], axis=0) if len(r["modes"]) else pra["clean"]
                    nama_input = f"Sinyal Input ({name})"

                items = [(nama_input, inp_sig)]
                modes = r["modes"]
                for m_idx in range(len(modes)):
                    items.append((f"Mode {m_idx + 1}", modes[m_idx]))
                _show_chart(_stack_fig(tgl, items, h_per=130), key=f"{kp}_vm_{name}")

                if r.get("candidates"):
                    with st.expander(f"Lihat Seluruh Rekap Pencarian Parameter VMD ({name})"):
                        df_cand = pd.DataFrame(r["candidates"])
                        df_cand = df_cand.rename(columns={
                            "K": "K", "alpha": "Alpha",
                            "Corr": "Mean Correlation",
                            "ELC": "Energy Loss (ELC)",
                            "BW": "Mean Bandwidth"
                        })
                        _show_df(df_cand, hide_index=True)
        return

    '''

content = content[:s_pos] + new_vmd_section + content[e_pos:]
print("Updated Dekomposisi VMD section.")

# 5. Remove _render_detail_notebook calls from render_hasil_admin
old_eval_block = '''    # ---------------- Evaluasi & Prediksi ----------------
    if True:
        if render_user is not None:
            render_user(h)
            _render_detail_notebook(h, kp)
            return
        if not _butuh(h, "tgl_uji", "tgl_fut"):
            return
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            _mcard("a", "MAE (Mean Absolute Error)", _fmt_id(h["mae"], 2),
                   "rata-rata selisih absolut aktual dan prediksi ")
        with c2:
            _mcard("b", "MAPE (Mean Absolute Percentage Error)", _fmt_id(h["mape"], 2) + "%",
                   "rata-rata persentase kesalahan prediksi")
        with st.container(border=True):
            _head("Visualisasi Data Aktual dan Prediksi",
                  f'Evaluasi pada periode uji {_tgl_id(h["tgl_uji"][0])} – '
                  f'{_tgl_id(h["tgl_uji"][-1])} ({len(h["tgl_uji"])} bulan)')
            _show_chart(fig_aktual_prediksi(h), key=f"{kp}_aktual")
        st.write("")
        with st.container(border=True):
            _head("Prediksi Kunjungan 12 Bulan ke Depan",
                  f'{_tgl_id(h["tgl_fut"][0])} – {_tgl_id(h["tgl_fut"][-1])}')
            _show_chart(fig_masa_depan(h), key=f"{kp}_future")
            with st.expander("Lihat tabel prediksi"):
                _show_df(pd.DataFrame({
                    "Bulan": [_tgl_id(d) for d in h["tgl_fut"]],
                    "Prediksi Pengunjung": [_fmt_id(v) for v in h["prediksi_fut"]],
                }), hide_index=True)
        _render_detail_notebook(h, kp)'''

new_eval_block = '''    # ---------------- Evaluasi & Prediksi ----------------
    if True:
        if render_user is not None:
            render_user(h)
            return
        if not _butuh(h, "tgl_uji", "tgl_fut"):
            return
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            _mcard("a", "MAE (Mean Absolute Error)", _fmt_id(h["mae"], 2),
                   "rata-rata selisih absolut aktual dan prediksi ")
        with c2:
            _mcard("b", "MAPE (Mean Absolute Percentage Error)", _fmt_id(h["mape"], 2) + "%",
                   "rata-rata persentase kesalahan prediksi")
        with st.container(border=True):
            _head("Visualisasi Data Aktual dan Prediksi",
                  f'Evaluasi pada periode uji {_tgl_id(h["tgl_uji"][0])} – '
                  f'{_tgl_id(h["tgl_uji"][-1])} ({len(h["tgl_uji"])} bulan)')
            _show_chart(fig_aktual_prediksi(h), key=f"{kp}_aktual")
        st.write("")
        with st.container(border=True):
            _head("Prediksi Kunjungan 12 Bulan ke Depan",
                  f'{_tgl_id(h["tgl_fut"][0])} – {_tgl_id(h["tgl_fut"][-1])}')
            _show_chart(fig_masa_depan(h), key=f"{kp}_future")
            with st.expander("Lihat tabel prediksi"):
                _show_df(pd.DataFrame({
                    "Bulan": [_tgl_id(d) for d in h["tgl_fut"]],
                    "Prediksi Pengunjung": [_fmt_id(v) for v in h["prediksi_fut"]],
                }), hide_index=True)
        return'''

assert old_eval_block in content, "old_eval_block not found in content!"
content = content.replace(old_eval_block, new_eval_block, 1)
print("Removed _render_detail_notebook calls from render_hasil_admin.")

# Write updated admin_methods.py
with open("admin_methods.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully written updated admin_methods.py!")
