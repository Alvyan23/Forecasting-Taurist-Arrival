import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
subdirs = ["hasil-interpolasi", "hasil-dekomposisi", "output_hasil/grafik", "hasil-normalisasi", "scaler", "retrain-preds", "hasil-prediksi-future"]
for sd in subdirs:
    p = os.path.join(folder, sd)
    if os.path.exists(p):
        print(f"=== {sd} ===")
        for item in os.listdir(p)[:10]:
            print(f"  {item}")
