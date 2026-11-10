import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
folder = "./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil"
for root, dirs, files in os.walk(folder):
    for f in files:
        if f.endswith('.json'):
            print(os.path.join(root, f))
