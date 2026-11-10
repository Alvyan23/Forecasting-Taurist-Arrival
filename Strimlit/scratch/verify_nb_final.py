import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Notebook loaded successfully. Total cells: {len(nb['cells'])}")
src6 = "".join(nb["cells"][6]["source"])
print(f"Cell 6 starts with: {repr(src6[:35])}")
print(f"Cell 6 contains muat_vmd_all_dari_folder: {'muat_vmd_all_dari_folder' in src6}")
print(f"Cell 6 contains fig_vmd_search: {'fig_vmd_search' in src6}")
print(f"Cell 6 calls _render_detail_notebook in render_hasil_admin: {'_render_detail_notebook(h, kp)' in src6}")

src8 = "".join(nb["cells"][8]["source"])
print(f"Cell 8 starts with: {repr(src8[:25])}")
print("Verification complete!")
