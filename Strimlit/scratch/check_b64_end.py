with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(108, 560):
    if '"""' in lines[i] or '_muat_benchmark_admin' in lines[i]:
        print(f"{i+1}: {lines[i][:50]}")
