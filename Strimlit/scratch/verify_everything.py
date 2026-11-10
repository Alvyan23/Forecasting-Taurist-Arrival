import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

print("=== 1. VERIFY NOTEBOOK JSON ===")
with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb["cells"]):
    src = cell["source"]
    first = src.split("\n")[0] if isinstance(src, str) else src[0] if src else ""
    print(f"  Cell {i} ({cell['cell_type']}): {first[:60]}")

print("\n=== 2. VERIFY COMPILATION OF CELL 6 & CELL 8 ===")
c6_src = nb["cells"][6]["source"]
c8_src = nb["cells"][8]["source"]

assert c6_src.startswith("%%writefile admin_methods.py\n"), "Cell 6 must start with %%writefile admin_methods.py"
assert c8_src.startswith("%%writefile app.py\n"), "Cell 8 must start with %%writefile app.py"

c6_code = c6_src.split("\n", 1)[1]
c8_code = c8_src.split("\n", 1)[1]

compiled_6 = compile(c6_code, "admin_methods.py", "exec")
compiled_8 = compile(c8_code, "app.py", "exec")
print("Cell 6 and Cell 8 compiled cleanly without any errors!")

print("\n=== 3. VERIFY EXECUTION OF ADMIN_METHODS ===")
test_ns = {"__file__": os.path.abspath("admin_methods.py")}
exec(compiled_6, test_ns)

am = test_ns
print("METODE in admin_methods:", am["METODE"])
print("OPSI_PER_METODE:", am["OPSI_PER_METODE"])

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

print("\n=== 4. TEST JALANKAN_METODE WITHOUT DISK FOLDERS (COLAB MODE) ===")
# Force cari_folder to None to test pure benchmark mode
am["cari_folder"] = lambda m, d: None

for m in am["METODE"]:
    print(f"--- Method: {m} ---")
    for d in dests:
        res = am["jalankan_metode"](d, None, m)
        assert res.get("loaded_from_folder") is True, f"Failed loaded_from_folder for {m} {d}"
        mae = res.get("mae")
        mape = res.get("mape")
        rmse = res.get("rmse")
        n_uji = len(res.get("prediksi_uji", []))
        n_fut = len(res.get("prediksi_fut", []))
        print(f"  {d:25s} -> MAE: {mae:10.2f} | RMSE: {rmse:10.2f} | MAPE: {mape:6.2f}% | Uji: {n_uji} | Fut: {n_fut}")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
