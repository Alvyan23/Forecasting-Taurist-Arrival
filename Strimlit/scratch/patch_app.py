"""Patch app.py: replace render dispatch in admin_page to use am.render_hasil_admin()."""
path = "c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit/app.py"
with open(path, 'rb') as f:
    content = f.read()

old = (b'        if metode == "Hybrid ICEEMDAN-VMD-GRU":\r\n'
       b'            am.render_hasil_iceemdan_vmd_gru(res["hasil"])\r\n'
       b'        else:\r\n'
       b'            render_hasil(res["hasil"])')

new = b'        am.render_hasil_admin(res["hasil"])'

if old in content:
    content = content.replace(old, new)
    with open(path, 'wb') as f:
        f.write(content)
    print("PATCHED OK")
else:
    # Find context
    idx = content.find(b'render_hasil_iceemdan_vmd_gru')
    print(f"Pattern not found! Context at idx {idx}:")
    if idx > 0:
        print(repr(content[idx-200:idx+200]))
