import sys, os, gzip, base64, json, re

# Read base64 benchmarks string from scratch
with open("scratch/benchmarks_admin_b64.txt", "r", encoding="utf-8") as f:
    b64_str = f.read().strip()

# Read current cell 6 admin_methods
with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    code = f.read()

# Strip %%writefile admin_methods.py if present
lines = code.splitlines()
has_magic = lines[0].startswith("%%writefile")
if has_magic:
    header_magic = lines[0]
    lines = lines[1:]

print(f"Total lines in original cell 6: {len(lines)}")
