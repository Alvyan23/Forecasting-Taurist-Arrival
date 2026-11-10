with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '["comps"]' in l or "['comps']" in l or '["ice_data"]' in l or "['ice_data']" in l or '.get("comps")' in l or '.get("ice_data")' in l:
        print(f"L{i+1}: {l.strip()}")
