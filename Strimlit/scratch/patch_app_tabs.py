with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

target = '''                _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
                if metode == "Hybrid ICEEMDAN-VMD-GRU":
                    st.session_state.setdefault(f"{_kp}_menu", "Interpolasi Linear")
                    st.session_state.setdefault(f"_tahap_{_kp}_menu", "Interpolasi Linear")
                else:
                    st.session_state[f"{_kp}_menu"] = "Evaluasi & Prediksi"
                    st.session_state[f"_tahap_{_kp}_menu"] = "Evaluasi & Prediksi"'''

replace = '''                _kp = "adm_" + metode.replace(" ", "_").replace("-", "_")
                st.session_state.setdefault(f"{_kp}_menu", "Interpolasi Linear")
                st.session_state.setdefault(f"_tahap_{_kp}_menu", "Interpolasi Linear")'''

assert target in app_code, "target not found in app.py"
app_new = app_code.replace(target, replace)

with open("scratch/test_tab_render/app.py", "w", encoding="utf-8") as f:
    f.write(app_new)

print("Generated scratch/test_tab_render/app.py successfully!")
