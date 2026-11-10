import re

with open("scratch/nb_cell6_admin_methods.py", "r", encoding="utf-8") as f:
    text6 = f.read()

with open("scratch/nb_cell8_app.py", "r", encoding="utf-8") as f:
    text8 = f.read()

print("siapkan_praproses in cell6:", "siapkan_praproses" in text6)
print("siapkan_praproses in cell8:", "siapkan_praproses" in text8)
