import os, glob, pandas as pd

methods = ['ICEEMDAN-VMD-GRU', 'ICEEMDAN-GRU', 'VMD-GRU', 'GRU']
dest = "Gunung geger"

for m in methods:
    p = os.path.join(m, dest)
    if not os.path.exists(p):
        p = os.path.join(m, "Gunung Geger")
    print(f"\n==================== {m} ====================")
    decomp_dir = os.path.join(p, "hasil-dekomposisi")
    if os.path.exists(decomp_dir):
        files = os.listdir(decomp_dir)
        print(f"  files in hasil-dekomposisi: {files}")
        for f in files:
            fp = os.path.join(decomp_dir, f)
            if f.endswith('.xlsx'):
                xl = pd.read_excel(fp)
                print(f"    {f} columns ({xl.shape}): {list(xl.columns)}")
            elif f.endswith('.csv'):
                csv = pd.read_csv(fp)
                print(f"    {f} columns ({csv.shape}): {list(csv.columns)}")
    else:
        print("  hasil-dekomposisi DOES NOT EXIST")
    
    norm_dir = os.path.join(p, "hasil-normalisasi")
    if os.path.exists(norm_dir):
        files = os.listdir(norm_dir)
        print(f"  files in hasil-normalisasi: {files}")
        for f in files[:3]:
            fp = os.path.join(norm_dir, f)
            if f.endswith('.xlsx'):
                xl = pd.read_excel(fp)
                print(f"    {f} columns: {list(xl.columns)}")
            elif f.endswith('.csv'):
                csv = pd.read_csv(fp)
                print(f"    {f} columns: {list(csv.columns)}")
