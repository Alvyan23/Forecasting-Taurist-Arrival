import json

with open("noteboke (1).ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src6 = "".join(nb["cells"][6]["source"])
src8 = "".join(nb["cells"][8]["source"])

target_call = 'st.session_state["adm_result"] = {"key": state_key, "hasil": hasil}'

print("Cell 6 starts with %%writefile admin_methods.py:", src6.startswith('%%writefile admin_methods.py'))
print("Cell 8 starts with %%writefile app.py:", src8.startswith('%%writefile app.py'))
print("Cell 8 adm_active removed:", ('adm_active' not in src8))
print("Cell 8 go_btn controls adm_result:", ('if go_btn:' in src8 and target_call in src8))
