with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if any(k in line for k in ['def render_tahap_praproses', 'def render_hasil_admin', '_render_detail_notebook', 'fig_vmd_search']):
        print(f'{i+1}: {line.strip()}')
