with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def _muat_benchmark_admin' in line:
        for j in range(i, min(len(lines), i+30)):
            print(f"{j+1}: {lines[j]}", end="")
        break
