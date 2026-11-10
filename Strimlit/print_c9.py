import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== CELL 9 ===")
with open("cell_9.py", "r", encoding="utf-8") as f:
    text = f.read()
    # Print lines that define plt or plot
    for line in text.split("\n"):
        if "plt." in line or "savefig" in line or "subplot" in line or "title" in line:
            print(line)
