import gzip, base64, json

with open('scratch/benchmarks_admin_vmd_b64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()

data = json.loads(gzip.decompress(base64.b64decode(b64.encode('ascii'))).decode('utf-8'))
for met in ['hybridvmdgru', 'hybridiceemdanvmdgru']:
    print(f"=== {met} ===")
    for dest, d in data[met].items():
        vmd_keys = list(d.get('vmd_search_data', {}).keys())
        comp_count = len(d.get('comps', {}))
        print(f"  {dest}: vmd_keys = {vmd_keys}, comp_count = {comp_count}")
        for k in vmd_keys:
            cands = d['vmd_search_data'][k]['candidates']
            best = d['vmd_search_data'][k]['best']
            print(f"     {k}: {len(cands)} candidates, best = {best}")
