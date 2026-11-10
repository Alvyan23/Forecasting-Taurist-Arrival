with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '_muat_info_vmd_folder' in line:
        for j in range(max(0, i-5), min(len(lines), i+35)):
            print(f"{j+1}: {lines[j]}", end="")
        break
