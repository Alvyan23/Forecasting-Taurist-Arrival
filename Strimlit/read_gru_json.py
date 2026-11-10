import json

with open("./ICEEMDAN-VMD-GRU/Makam Syaikhona Kholil/best-parameter-gru/best_gru_params_per_mode.json") as f:
    data = json.load(f)
print("Keys count:", len(data))
print("First 10 keys:", list(data.keys())[:10])
