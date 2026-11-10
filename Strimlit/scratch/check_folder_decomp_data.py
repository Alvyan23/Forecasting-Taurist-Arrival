import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import admin_methods as am

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

for m in am.METODE:
    print(f"\n==================== METHOD: {m} ====================")
    fol = am.cari_folder(m, dests[0])
    h = am.muat_hasil_folder(fol, dests[0], m)
    print("  comps keys:", list(h.get("comps", {}).keys()))
    print("  ice_data keys:", list(h.get("ice_data", {}).keys()))
    print("  vmd_data keys:", list(h.get("vmd_data", {}).keys()))
    if "modes" in h.get("vmd_data", {}):
        print("  vmd_data['modes'] keys:", list(h["vmd_data"]["modes"].keys())[:5])
    if "params" in h.get("vmd_data", {}):
        print("  vmd_data['params'] count:", len(h["vmd_data"]["params"]))
    print("  norm_data keys:", list(h.get("norm_data", {}).keys())[:5])
    print("  min_max_summary count:", len(h.get("min_max_summary", [])))
