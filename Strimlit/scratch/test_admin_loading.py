import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

sys.path.insert(0, os.path.abspath("."))

import importlib.util
spec = importlib.util.spec_from_file_location("nb_am", "scratch/nb_cell6_admin_methods.py")
nb_am = importlib.util.module_from_spec(spec)
with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    code = f.read()
if code.startswith("%%writefile"):
    code = code.split("\n", 1)[1]

compiled = compile(code, "nb_cell6_admin_methods.py", "exec")
exec(compiled, nb_am.__dict__)

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

print("METODE list:", nb_am.METODE)
for m in nb_am.METODE:
    print(f"\n==================== METHOD: {m} ====================")
    for d in dests:
        folder = nb_am.cari_folder(m, d)
        print(f"Dest: {d:25s} -> Folder: {folder}")
        if folder:
            try:
                h = nb_am.muat_hasil_folder(folder, d, m)
                ok = h.get("loaded_from_folder")
                err = h.get("folder_load_error")
                r2 = h.get("r2")
                mape = h.get("mape")
                rmse = h.get("rmse")
                r2_str = f"{r2:.4f}" if r2 is not None else "None"
                mape_str = f"{mape:.2f}%" if mape is not None else "None"
                rmse_str = f"{rmse:.2f}" if rmse is not None else "None"
                print(f"       Loaded: {ok}, err: {err}, R2: {r2_str} MAPE: {mape_str} RMSE: {rmse_str}")
            except Exception as e:
                import traceback
                print(f"       ERROR loading: {e}")
                traceback.print_exc()
        else:
            print(f"       Folder not found!")
