import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import forecasting_engine as fe
import admin_methods as am

print("fe.CONFIG keys:", list(fe.CONFIG.keys()))
print("am.DEST_ALIASES keys:", list(am.DEST_ALIASES.keys()))
for d in fe.CONFIG.keys():
    print(f"Checking '{d}':")
    for m in am.METODE:
        fol = am.cari_folder(m, d)
        print(f"  {m:25s} -> {fol}")
