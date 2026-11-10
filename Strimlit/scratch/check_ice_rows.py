import pandas as pd

df = pd.read_excel("ICEEMDAN-VMD-GRU/Gunung geger/output_hasil/iceemdan_decomposition.xlsx", header=None)
print("Shape:", df.shape)
for i in range(min(7, len(df))):
    print(f"Row {i}: {df.iloc[i].values}")
