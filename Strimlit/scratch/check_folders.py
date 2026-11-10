import os

methods = ['ICEEMDAN-VMD-GRU', 'ICEEMDAN-GRU', 'VMD-GRU', 'GRU']
for d in methods:
    if os.path.exists(d):
        print(f"=== {d} ===")
        subdirs = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]
        files = [o for o in os.listdir(d) if os.path.isfile(os.path.join(d, o))]
        print(f"  Root files: {len(files)}, Subdirs: {len(subdirs)}")
        for f in files[:5]:
            print(f"    file: {f}")
        for s in subdirs:
            sub_files = os.listdir(s)
            print(f"    subdir {os.path.basename(s)}: {len(sub_files)} items, e.g. {sub_files[:3]}")
    else:
        print(f"=== {d} NOT FOUND ===")
