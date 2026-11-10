import gzip, base64, json

with open('scratch/benchmarks_admin_vmd_b64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()

data = json.loads(gzip.decompress(base64.b64decode(b64.encode('ascii'))).decode('utf-8'))
for met in ['hybridvmdgru', 'hybridiceemdanvmdgru']:
    print(f"=== {met} ===")
    for dest, d in data[met].items():
        vmd_keys = list(d.get('vmd_search_data', {}).keys())
        print(f"  {dest}: keys = {vmd_keys}")
        for k in vmd_keys:
            c_cnt = len(d['vmd_search_data'][k]['candidates'])
            best = d['vmd_search_data'][k]['best']
            modes_len = len(d['vmd_search_data'][k]['modes'])
            print(f"     {k}: {c_cnt} candidates, best={best}, modes={modes_len}")
