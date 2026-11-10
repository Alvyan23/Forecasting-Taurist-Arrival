with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def _muat_info_vmd_folder' in line:
        for j in range(i, min(len(lines), i+45)):
            print(f"{j+1}: {lines[j]}", end="")
        break
