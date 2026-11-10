import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

import admin_methods as am
import forecasting_engine as fe

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

print("METODE and their tabs:")
for m, tabs in am.OPSI_PER_METODE.items():
    print(f"  {m:25s} -> {tabs}")
