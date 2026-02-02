import pandas as pd
import glob
import os

download_directory = "./Downloads/"
files = [f for f in os.listdir(download_directory) if f.endswith('.xlsx')]

if files:
    file_path = os.path.join(download_directory, files[0])
    # Read row 1 as header
    df = pd.read_excel(file_path, header=1)
    print("Headers match:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
