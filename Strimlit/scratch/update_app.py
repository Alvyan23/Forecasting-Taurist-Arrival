import sys, shutil, time

sys.stdout.reconfigure(encoding='utf-8')

# Backup app.py
ts = time.strftime("%Y%m%d_%H%M%S")
bak_app = f"app.py.bak_{ts}"
shutil.copy("app.py", bak_app)
print(f"Backed up app.py to {bak_app}")

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

target_str = """    key = fe.kunci_cache(f"{dest}|{metode}", data_bytes)
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
                st.session_state.setdefault(f"{_kp}_menu", "Interpolasi Linear")
                st.session_state.setdefault(f"_tahap_{_kp}_menu", "Interpolasi Linear")

                st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}
            except Exception as e:
                st.error(f"Gagal memuat hasil metode {metode}: {e}")
                dash_footer()
                return"""

replacement_str = """    key = fe.kunci_cache(f"{dest}|{metode}", data_bytes)
    state_key = f"{dest}|{metode}|{up.name}|{len(data_bytes)}"

    if go_btn:
        try:
            hasil = None
            if am.cari_folder(metode, dest) is None:
                hasil = fe.muat_cache(key)          # cache hasil training lama
            if hasil is None:
                hasil = am.jalankan_metode(dest, data_clean, metode)
                if not hasil.get("loaded_from_folder"):
                    fe.simpan_cache(key, hasil)

            _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
            st.session_state[f"{_kp}_menu"] = "Interpolasi Linear"
            st.session_state[f"_tahap_{_kp}_menu"] = "Interpolasi Linear"

            st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}
        except Exception as e:
            st.error(f"Gagal memuat hasil metode {metode}: {e}")
            dash_footer()
            return"""

# Normalize \r\n to \n for replacement
norm_content = content.replace("\r\n", "\n")
norm_target = target_str.replace("\r\n", "\n")
norm_rep = replacement_str.replace("\r\n", "\n")

assert norm_target in norm_content, "target string not found in app.py!"
new_content = norm_content.replace(norm_target, norm_rep, 1)

# Write back with CRLF
with open("app.py", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(new_content)

print("Successfully updated app.py!")
