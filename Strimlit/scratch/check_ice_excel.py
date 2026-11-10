import pandas as pd

df = pd.read_excel("ICEEMDAN-VMD-GRU/Gunung geger/output_hasil/iceemdan_decomposition.xlsx")
print("ICEEMDAN-VMD-GRU iceemdan_decomposition.xlsx columns:")
print(list(df.columns))

df2 = pd.read_excel("ICEEMDAN-GRU/Gunung Geger/output_hasil/iceemdan_decomposition.xlsx")
print("\nICEEMDAN-GRU iceemdan_decomposition.xlsx columns:")
print(list(df2.columns))
