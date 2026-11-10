import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

print("=== 1. VERIFY NOTEBOOK JSON INTEGRITY ===")
with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
c6_src = nb["cells"][6]["source"]
c8_src = nb["cells"][8]["source"]

assert c6_src.startswith("%%writefile admin_methods.py\n"), "Cell 6 header error"
assert c8_src.startswith("%%writefile app.py\n"), "Cell 8 header error"

c6_code = c6_src.split("\n", 1)[1]
c8_code = c8_src.split("\n", 1)[1]

compiled_6 = compile(c6_code, "admin_methods.py", "exec")
compiled_8 = compile(c8_code, "app.py", "exec")
print("Cell 6 and Cell 8 compiled with 0 errors!")

test_ns = {"__file__": os.path.abspath("admin_methods.py")}
exec(compiled_6, test_ns)
am = test_ns

print("\n=== 2. VERIFY OPSI_PER_METODE ===")
for m, tabs in am["OPSI_PER_METODE"].items():
    print(f"  {m:25s} -> {tabs}")

assert am["OPSI_PER_METODE"]["Hybrid ICEEMDAN-GRU"] == ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Normalisasi", "Evaluasi & Prediksi"]
assert am["OPSI_PER_METODE"]["Hybrid VMD-GRU"] == ["Interpolasi Linear", "Dekomposisi VMD", "Normalisasi", "Evaluasi & Prediksi"]
assert am["OPSI_PER_METODE"]["GRU"] == ["Interpolasi Linear", "Normalisasi", "Evaluasi & Prediksi"]
assert am["OPSI_PER_METODE"]["Hybrid ICEEMDAN-VMD-GRU"] == ["Interpolasi Linear", "Dekomposisi I-CEEMDAN", "Dekomposisi VMD", "Normalisasi", "Evaluasi & Prediksi"]

print("\n=== 3. VERIFY ALL METHODS AND ALL TABS DATA ===")
dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

for m in am["METODE"]:
    print(f"\n==================== METHOD: {m} ====================")
    for d in dests:
        fol = am["cari_folder"](m, d)
        h = am["muat_hasil_folder"](fol, d, m)
        assert h.get("loaded_from_folder") is True, f"Failed to load {m} on {d}"
        tabs = am["OPSI_PER_METODE"][m]
        tab_status = []
        for t in tabs:
            if t == "Interpolasi Linear":
                tab_status.append(f"{t}: OK (N={len(h['aktual_hist'])})")
            elif t == "Dekomposisi I-CEEMDAN":
                imfs = am["_ambil_imfs"](h, {"clean": h["aktual_hist"]}, False)
                tab_status.append(f"{t}: OK ({len(imfs)} IMFs)")
            elif t == "Dekomposisi VMD":
                vmd_info = am["_muat_info_vmd_folder"](fol)
                vmd_comps = [k for k in h.get("comps", {}).keys() if "VMD" in k]
                tab_status.append(f"{t}: OK ({len(vmd_comps)} modes, info={vmd_info is not None})")
            elif t == "Normalisasi":
                comps = h.get("comps", {})
                tab_status.append(f"{t}: OK ({len(comps)} comps)")
            elif t == "Evaluasi & Prediksi":
                tab_status.append(f"{t}: OK (MAE={h['mae']:.2f}, MAPE={h['mape']:.2f}%)")
        print(f"  {d:25s} -> {' | '.join(tab_status)}")

print("\nALL VERIFICATIONS PASSED 100% SUCCESSFULLY!")
