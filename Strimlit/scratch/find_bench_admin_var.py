with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'BENCHMARKS_ADMIN' in line:
        print(f"{i+1}: {line.strip()[:80]}")
