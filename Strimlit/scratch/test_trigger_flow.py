import sys
sys.stdout.reconfigure(encoding='utf-8')

session_state = {}

def simulate_admin_step(dest, metode, file_name, data_len, go_btn):
    state_key = f"{dest}|{metode}|{file_name}|{data_len}"
    
    if go_btn:
        # Dummy hasil
        hasil = {"metode": metode, "destinasi": dest}
        _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
        session_state[f"{_kp}_menu"] = "Interpolasi Linear"
        session_state[f"_tahap_{_kp}_menu"] = "Interpolasi Linear"
        session_state["adm_result"] = {"key": state_key, "hasil": hasil}

    res = session_state.get("adm_result")
    if res and res.get("key") == state_key:
        return "TAMPILKAN_HASIL"
    else:
        return "TAMPILKAN_SKELETON_KLIK_PREDIKSI"

# Skenario 1: Upload dataset, metode = Hybrid ICEEMDAN-VMD-GRU, belum klik go_btn
s1 = simulate_admin_step("Gunung Geger", "Hybrid ICEEMDAN-VMD-GRU", "dataset.xlsx", 1000, go_btn=False)
print("1. Baru upload file (belum klik Mulai Prediksi):", s1)
assert s1 == "TAMPILKAN_SKELETON_KLIK_PREDIKSI"

# Skenario 2: Klik go_btn
s2 = simulate_admin_step("Gunung Geger", "Hybrid ICEEMDAN-VMD-GRU", "dataset.xlsx", 1000, go_btn=True)
print("2. Klik Mulai Prediksi:", s2)
assert s2 == "TAMPILKAN_HASIL"

# Skenario 3: Interaksi UI di tahapan (metode tetap, go_btn=False)
s3 = simulate_admin_step("Gunung Geger", "Hybrid ICEEMDAN-VMD-GRU", "dataset.xlsx", 1000, go_btn=False)
print("3. Interaksi tab tahapan (rerun normal):", s3)
assert s3 == "TAMPILKAN_HASIL"

# Skenario 4: User ubah pilihan metode ke Hybrid VMD-GRU di sidebar (belum klik tombol)
s4 = simulate_admin_step("Gunung Geger", "Hybrid VMD-GRU", "dataset.xlsx", 1000, go_btn=False)
print("4. Ganti metode ke Hybrid VMD-GRU (belum klik tombol):", s4)
assert s4 == "TAMPILKAN_SKELETON_KLIK_PREDIKSI"

# Skenario 5: User klik tombol Mulai Prediksi untuk Hybrid VMD-GRU
s5 = simulate_admin_step("Gunung Geger", "Hybrid VMD-GRU", "dataset.xlsx", 1000, go_btn=True)
print("5. Klik Mulai Prediksi untuk metode baru:", s5)
assert s5 == "TAMPILKAN_HASIL"

print("\nALUR FLOW TRIGGER PREDIKSI BERHASIL 100%!")
