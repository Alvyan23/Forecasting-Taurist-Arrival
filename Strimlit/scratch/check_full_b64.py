import os, sys

os.makedirs("scratch/test_tab_render", exist_ok=True)

with open("scratch/benchmarks_admin_full_b64.txt", "r", encoding="utf-8") as f:
    full_b64 = f.read().strip()

print(f"Full benchmark b64 size: {len(full_b64)} chars")
