with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('_BENCHMARKS_ADMIN_B64 = """'):
        start_idx = i
    if start_idx != -1 and line.strip() == '"""':
        end_idx = i
        break
print(f"Start: {start_idx + 1}, End: {end_idx + 1}")
print("Line after end:", lines[end_idx + 1].strip())
