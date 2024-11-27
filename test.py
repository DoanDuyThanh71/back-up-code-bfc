import pandas as pd
df = pd.read_excel("../Data/SFC/3010/Dữ Liệu Target KQKD.xlsx")
print(df.shape)
df.to_excel("../Data/SFC/3010/Output.xlsx", index=False)