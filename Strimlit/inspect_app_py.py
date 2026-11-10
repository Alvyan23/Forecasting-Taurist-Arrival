import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('app.py', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines[970:1025]):
    print(f'{i+971}: {l}', end='')
