import sys, os
sys.path.insert(0, os.path.abspath("."))
import admin_methods as am

for m_k, d_dict in am.BENCHMARKS_ADMIN.items():
    print(f"\nBenchmark method: {m_k}")
    sample_d = list(d_dict.keys())[0]
    entry = d_dict[sample_d]
    print(f"  Destination: {sample_d}")
    print(f"  comps: {list(entry.get('comps', {}).keys())[:5]} (len: {len(entry.get('comps', {}))})")
    print(f"  ice_data: {list(entry.get('ice_data', {}).keys())[:5]} (len: {len(entry.get('ice_data', {}))})")
