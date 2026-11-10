import sys, gzip, base64, json

sys.stdout.reconfigure(encoding='utf-8')
with open('scratch/benchmarks_admin_vmd_b64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()
print('Length of b64:', len(b64))

data = json.loads(gzip.decompress(base64.b64decode(b64.encode('ascii'))).decode('utf-8'))
print('Keys in data:', list(data.keys()))
for met in data:
    for dest in list(data[met].keys())[:1]:
        vmd_data = data[met][dest].get('vmd_search_data')
        if vmd_data:
            print(f'{met} -> {dest} has vmd_search_data with keys: {list(vmd_data.keys())}')
            k0 = list(vmd_data.keys())[0]
            print(f'   {k0} best: {vmd_data[k0]["best"]}, num candidates: {len(vmd_data[k0]["candidates"])}')
print("Done check.")
