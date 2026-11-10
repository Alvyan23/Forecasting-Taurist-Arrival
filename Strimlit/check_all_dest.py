import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
base = "./ICEEMDAN-VMD-GRU"
for d in os.listdir(base):
    dp = os.path.join(base, d)
    if os.path.isdir(dp):
        print(f"--- {d} ---")
        gpath = os.path.join(dp, "output_hasil/grafik")
        if os.path.exists(gpath):
            print("  grafik:", os.listdir(gpath))
        else:
            print("  no output_hasil/grafik")
