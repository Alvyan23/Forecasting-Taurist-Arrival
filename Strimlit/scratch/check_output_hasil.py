import os

for m in ['ICEEMDAN-VMD-GRU', 'ICEEMDAN-GRU', 'VMD-GRU', 'GRU']:
    p = os.path.join(m, "Gunung geger")
    if not os.path.exists(p):
        p = os.path.join(m, "Gunung Geger")
    out_dir = os.path.join(p, "output_hasil")
    if os.path.exists(out_dir):
        print(f"=== {m} output_hasil ===")
        for f in os.listdir(out_dir):
            print(" ", f)
