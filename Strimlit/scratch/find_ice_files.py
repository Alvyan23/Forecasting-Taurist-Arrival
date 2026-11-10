import os

dest_dir = "ICEEMDAN-VMD-GRU/Gunung geger"
for root, dirs, files in os.walk(dest_dir):
    for f in files:
        if "iceemdan" in f.lower() or "dekomposisi" in root.lower():
            print(os.path.join(root, f))
