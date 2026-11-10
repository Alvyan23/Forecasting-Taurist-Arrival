import os

dest = "Gunung geger"
dest_alt = "Gunung Geger"

for m in ['ICEEMDAN-VMD-GRU', 'ICEEMDAN-GRU', 'VMD-GRU', 'GRU']:
    p = os.path.join(m, dest)
    if not os.path.exists(p):
        p = os.path.join(m, dest_alt)
    print(f"\n=== {m} / {os.path.basename(p)} ===")
    if os.path.exists(p):
        for item in sorted(os.listdir(p)):
            subpath = os.path.join(p, item)
            if os.path.isdir(subpath):
                print(f"  [DIR]  {item} ({len(os.listdir(subpath))} files)")
            else:
                print(f"  [FILE] {item} ({os.path.getsize(subpath)} bytes)")
