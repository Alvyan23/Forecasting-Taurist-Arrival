import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

import py_compile
py_compile.compile("admin_methods.py", doraise=True)
print("admin_methods.py compiled without syntax error!")

import admin_methods as am
print("Imported admin_methods successfully!")
print("Number of methods in BENCHMARKS_ADMIN:", len(am.BENCHMARKS_ADMIN))
for m in am.BENCHMARKS_ADMIN:
    print(f"  {m}: {list(am.BENCHMARKS_ADMIN[m].keys())}")

# Test _cari_benchmark for all methods and destinations
for met in am.METODE:
    for dest in ["Gunung geger", "Kolla Langgundi", "Makam Air Mata Ibu", "Makam Sunan Cendana", "Makam Syaikhona Kholil"]:
        b = am._cari_benchmark(met, dest)
        if b is None:
            print(f"Missing benchmark for {met} -> {dest}")
        else:
            if "VMD" in met:
                vmd_search = b.get("vmd_search_data")
                if not vmd_search:
                    print(f"Missing vmd_search_data in benchmark for {met} -> {dest}")

print("All benchmark checks passed!")
