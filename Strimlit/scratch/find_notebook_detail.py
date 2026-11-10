import os

for fname in ['admin_methods.py', 'app.py', 'user_methods.py']:
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if '_render_detail_notebook' in line or 'Ringkasan Evaluasi Seperti Notebook' in line:
                print(f'{fname}:{idx+1}: {line}')
