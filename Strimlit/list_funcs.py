import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('admin_methods.py', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('def '):
            print(line.strip())
