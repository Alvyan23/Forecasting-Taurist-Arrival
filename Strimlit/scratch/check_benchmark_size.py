import sys, os, json, gzip, base64
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from scratch.test_admin_loading import nb_am

dests = [
    "Gunung geger",
    "Kolla Langgundi",
    "Makam Air Mata Ibu",
    "Makam Sunan Cendana",
    "Makam Syaikhona Kholil"
]

benchmarks_all = {}
for m in nb_am.METODE:
    benchmarks_all[m] = {}
    for d in dests:
        folder = nb_am.cari_folder(m, d)
        h = nb_am.muat_hasil_folder(folder, d, m)
        # remove local path references that are irrelevant for portability
        h_clean = dict(h)
        if "folder" in h_clean:
            del h_clean["folder"]
        # In png_map, keep filename or base64 or relative path
        benchmarks_all[m][d] = h_clean

raw_json = json.dumps(benchmarks_all)
compressed = gzip.compress(raw_json.encode('utf-8'))
b64 = base64.b64encode(compressed).decode('ascii')

print(f"Raw JSON size: {len(raw_json)} bytes ({len(raw_json)/1024:.1f} KB)")
print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
print(f"Base64 string length: {len(b64)} chars ({len(b64)/1024:.1f} KB)")
