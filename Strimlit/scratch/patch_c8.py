with open("scratch/nb_cell8_app.py", "r", encoding="utf-8") as f:
    c8_orig = f.read()

target_block = '''    # Hasil dari folder notebook sudah instan, jadi TIDAK memakai cache JSON.
    # Cache hanya dipakai untuk hasil training ulang (jika folder hasil tidak ada).
    key = fe.kunci_cache(f"{dest}|{metode}", data_bytes)
    state_key = f"{dest}|{metode}|{up.name}|{len(data_bytes)}"

    if go_btn:
        bar = st.progress(0.0, text="Memulai proses...")
        try:
            hasil = None
            if am.cari_folder(metode, dest) is None:
                hasil = fe.muat_cache(key)          # cache hasil training lama
            if hasil is None:
                hasil = am.jalankan_metode(
                    dest, data_clean, metode,
                    progress=lambda f, t: bar.progress(min(max(f, 0.0), 1.0) * 0.4, text=t))
                if not hasil.get("loaded_from_folder"):
                    fe.simpan_cache(key, hasil)

            # Pra-hitung ICEEMDAN + VMD agar tab Dekomposisi/Normalisasi langsung muncul
            pra = getattr(am, "siapkan_praproses", None)
            if pra is not None:
                try:
                    pra(hasil, raw_df=info["raw_df"],
                        progress=lambda f, t: bar.progress(
                            0.4 + 0.6 * min(max(f, 0.0), 1.0), text=t))
                except Exception as e:
                    st.warning(f"Pra-hitung dekomposisi dilewati: {e}")
        except Exception as e:
            bar.empty()
            st.error(f"Proses gagal dijalankan: {e}")
            dash_footer()
            return
        bar.empty()

        # Setelah proses selesai, selalu buka tab "Interpolasi Linear" lebih dulu
        _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
        st.session_state[f"{_kp}_menu"] = "Interpolasi Linear"
        st.session_state[f"_tahap_{_kp}_menu"] = "Interpolasi Linear"

        st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}

    res = st.session_state.get("adm_result")
    if res and res["key"] == state_key:'''

replace_block = '''    key = fe.kunci_cache(f"{dest}|{metode}", data_bytes)
    state_key = f"{dest}|{metode}|{up.name}|{len(data_bytes)}"
    curr_dataset = f"{up.name}|{len(data_bytes)}"

    # Cek apakah analisis admin sudah pernah dimulai untuk dataset ini
    adm_active = st.session_state.get("adm_active_dataset") == curr_dataset

    if go_btn:
        st.session_state["adm_active_dataset"] = curr_dataset
        adm_active = True

    if adm_active:
        res = st.session_state.get("adm_result")
        # Jika hasil belum ada atau admin mengganti destinasi/metode di sidebar: langsung muat instan
        if not (res and res.get("key") == state_key):
            try:
                hasil = None
                if am.cari_folder(metode, dest) is None:
                    hasil = fe.muat_cache(key)          # cache hasil training lama
                if hasil is None:
                    hasil = am.jalankan_metode(dest, data_clean, metode)
                    if not hasil.get("loaded_from_folder"):
                        fe.simpan_cache(key, hasil)

                _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
                if metode == "Hybrid ICEEMDAN-VMD-GRU":
                    st.session_state.setdefault(f"{_kp}_menu", "Interpolasi Linear")
                    st.session_state.setdefault(f"_tahap_{_kp}_menu", "Interpolasi Linear")
                else:
                    st.session_state[f"{_kp}_menu"] = "Evaluasi & Prediksi"
                    st.session_state[f"_tahap_{_kp}_menu"] = "Evaluasi & Prediksi"

                st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}
            except Exception as e:
                st.error(f"Gagal memuat hasil metode {metode}: {e}")
                dash_footer()
                return

    res = st.session_state.get("adm_result")
    if res and res.get("key") == state_key:'''

assert target_block in c8_orig, "target_block not found in c8_orig"
c8_new = c8_orig.replace(target_block, replace_block)

clean_c8 = c8_new
if clean_c8.startswith("%%writefile"):
    clean_c8 = clean_c8.split("\n", 1)[1]

with open("scratch/test_new_admin/app.py", "w", encoding="utf-8") as f:
    f.write(clean_c8)

print("scratch/test_new_admin/app.py written successfully!")
