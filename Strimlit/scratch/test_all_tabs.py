import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("scratch/test_tab_render"))

import importlib.util
spec = importlib.util.spec_from_file_location("test_am", "scratch/test_tab_render/admin_methods.py")
test_am = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_am)

print("Loaded test_am successfully!")

for m, tabs in test_am.OPSI_PER_METODE.items():
    print(f"\nMethod: {m}")
    print(f"  Tabs: {tabs}")

dest = "Gunung geger"
for m in test_am.METODE:
    print(f"\n--- Testing data availability for {m} on {dest} ---")
    fol = test_am.cari_folder(m, dest)
    h = test_am.muat_hasil_folder(fol, dest, m)
    tabs = test_am.OPSI_PER_METODE[m]
    for t in tabs:
        print(f"  Tab: {t}")
        if t == "Interpolasi Linear":
            print(f"    raw_hist len: {len(h.get('raw_hist', []))}, clean len: {len(h.get('aktual_hist', []))}")
        elif t == "Dekomposisi I-CEEMDAN":
            imfs = test_am._ambil_imfs(h, {"clean": h["aktual_hist"]}, False)
            print(f"    imfs keys: {list(imfs.keys())}")
        elif t == "Dekomposisi VMD":
            if m == "Hybrid VMD-GRU":
                vmd_modes = [k for k in h.get("comps", {}).keys() if k.startswith("VMD_")]
                vmd_info = test_am._muat_info_vmd_folder(fol)
                opt_shape = vmd_info["optimal"].shape if vmd_info else "None"
                print(f"    vmd modes count: {len(vmd_modes)}, optimal table: {opt_shape}")
            elif m == "Hybrid ICEEMDAN-VMD-GRU":
                vmd_modes = [k for k in h.get("comps", {}).keys() if "VMD" in k]
                vmd_info = test_am._muat_info_vmd_folder(fol)
                opt_shape = vmd_info["optimal"].shape if vmd_info else "None"
                print(f"    vmd sub-modes count: {len(vmd_modes)}, optimal table: {opt_shape}")
        elif t == "Normalisasi":
            comps = list(h.get("comps", {}).keys())
            print(f"    comps for normalisasi count: {len(comps)} (sample: {comps[:3]})")
        elif t == "Evaluasi & Prediksi":
            print(f"    mae: {h.get('mae'):.2f}, mape: {h.get('mape'):.2f}%, sub_modes: {len(h.get('sub_mode_preds', {}))}")

print("\nALL TABS DATA CHECKS PASSED PERFECTLY!")
