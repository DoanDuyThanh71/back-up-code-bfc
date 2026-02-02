import pandas as pd
import glob
import os

download_directory = "./Downloads/"
files = [f for f in os.listdir(download_directory) if f.endswith('.xlsx')]

if files:
    file_path = os.path.join(download_directory, files[0])
    print(f"Inspecting file: {files[0]}")
    df = pd.read_excel(file_path)
    print(f"Number of columns: {len(df.columns)}")
    print("Columns:")
    for col in df.columns:
        print(f" - {col}")
else:
    print("No xlsx files found in Downloads")
