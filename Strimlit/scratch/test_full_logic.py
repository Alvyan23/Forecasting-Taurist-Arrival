import sys, os, pandas as pd, numpy as np
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

import admin_methods as am
from scratch.test_vmd_all_builder import muat_vmd_all_dari_folder

# Cek pemuatan benchmark
dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

with open('scratch/benchmarks_admin_vmd_b64.txt', 'r', encoding='utf-8') as f:
    b64_new = f.read().strip()

import gzip, base64, json
bench_dict = json.loads(gzip.decompress(base64.b64decode(b64_new.encode('ascii'))).decode('utf-8'))

for m in ["Hybrid VMD-GRU", "Hybrid ICEEMDAN-VMD-GRU"]:
    m_key = am._nn(m)
    print(f"\n==================== {m} ====================")
    for d in dests:
        d_key = am._nn(d)
        h = bench_dict[m_key][d_key]
        fol = am.cari_folder(m, d)
        
        # Test 1: muat dari folder
        v_folder = muat_vmd_all_dari_folder(fol, m, h)
        # Test 2: muat dari benchmark
        v_bench = h.get("vmd_search_data", {})
        
        print(f"Dest: {d}")
        print(f"  Folder loaded: {list(v_folder.keys()) if v_folder else None}")
        print(f"  Benchmark keys: {list(v_bench.keys()) if v_bench else None}")
        
        # Test candidate structure for fig_vmd_search
        for name, r in (v_folder or v_bench).items():
            cands = r["candidates"]
            best = r["best"]
            df_cands = pd.DataFrame(cands)
            assert "K" in df_cands.columns and "alpha" in df_cands.columns
            assert "BW" in df_cands.columns and "ELC" in df_cands.columns and "Corr" in df_cands.columns
            assert "K" in best and "alpha" in best and "BW" in best and "ELC" in best and "Corr" in best
        print(f"  Validation passed for {d}!")

print("\nALL VALIDATIONS SUCCESSFUL!")
