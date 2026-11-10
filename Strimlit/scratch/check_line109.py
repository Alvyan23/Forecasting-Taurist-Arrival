with open('admin_methods.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print("Line 109 length:", len(lines[108]))
print("Line 109 start:", lines[108][:40])
print("Line 109 end:", repr(lines[108][-40:]))
