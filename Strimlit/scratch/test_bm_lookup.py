import sys, os, json, gzip, base64, re
sys.stdout.reconfigure(encoding='utf-8')

with open("scratch/benchmarks_admin_b64.txt", "r", encoding="utf-8") as f:
    b64 = f.read().strip()

data = json.loads(gzip.decompress(base64.b64decode(b64.encode('ascii'))).decode('utf-8'))

def _nn(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

print("Loaded benchmarks methods:", list(data.keys()))
for m in ["Hybrid ICEEMDAN-VMD-GRU", "Hybrid ICEEMDAN-GRU", "Hybrid VMD-GRU", "GRU"]:
    m_k = _nn(m)
    print(f"\n--- Method: {m} (key: {m_k}) ---")
    for d in ["Gunung geger", "Kolla Langgundi", "Makam Air Mata Ibu", "Makam Sunan Cendana", "Makam Syaikhona Kholil"]:
        d_k = _nn(d)
        res = data.get(m_k, {}).get(d_k)
        if res:
            print(f"  {d:25s} -> MAE: {res['mae']:.2f}, RMSE: {res['rmse']:.2f}, MAPE: {res['mape']:.2f}%, Test points: {len(res['prediksi_uji'])}, Future: {len(res['prediksi_fut'])}")
        else:
            print(f"  {d:25s} -> NOT FOUND!")
