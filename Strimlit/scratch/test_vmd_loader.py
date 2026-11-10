import sys, os, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

def muat_info_vmd(folder):
    p = os.path.join(folder, "hasil-dekomposisi", "vmd_hasil_lengkap.xlsx")
    if not os.path.exists(p):
        return None
    try:
        xls = pd.ExcelFile(p)
        df_opt = pd.read_excel(p, sheet_name="Parameter_Optimal", skiprows=2)
        df_cand = pd.read_excel(p, sheet_name="Pencarian_Parameter", skiprows=2)
        return {
            "optimal": df_opt,
            "candidates": df_cand
        }
    except Exception as e:
        print("Error reading vmd_hasil_lengkap:", e)
        return None

for m in ["VMD-GRU", "ICEEMDAN-VMD-GRU"]:
    fol = os.path.join(m, "Gunung geger")
    info = muat_info_vmd(fol)
    print(f"\n=== {m} ===")
    if info:
        print("Optimal table:")
        print(info["optimal"].to_string())
        print("\nCandidates top 5:")
        print(info["candidates"].head(5).to_string())
    else:
        print("Not found!")
