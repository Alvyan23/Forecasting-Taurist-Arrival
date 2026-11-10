"""Full sanity check: all 5 destinations x all 4 methods."""
import sys, os, warnings
sys.path.insert(0, "c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit")
os.chdir("c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit")
warnings.filterwarnings("ignore")
import admin_methods as am

DESTS = [
    "Gunung Geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil",
]

ok = 0
fail = 0
for dest in DESTS:
    for metode in am.METODE:
        fol = am.cari_folder(metode, dest)
        if not fol:
            print(f"FAIL folder: {dest} | {metode}")
            fail += 1
            continue
        res = am.muat_hasil_folder(fol, dest, metode)
        if not res or not res.get("loaded_from_folder"):
            print(f"FAIL load: {dest} | {metode}")
            fail += 1
            continue
        if len(res["tgl_uji"]) == 0:
            print(f"FAIL no test data: {dest} | {metode}")
            fail += 1
            continue
        print(f"OK: {dest:30s} | {metode:28s} | MAE={res['mae']:.2f} | MAPE={res['mape']:.2f}%")
        ok += 1

print(f"\nResults: {ok} OK, {fail} FAIL")
