import pandas as pd
import glob
import os

download_directory = "./Downloads/"
files = [f for f in os.listdir(download_directory) if f.endswith('.xlsx')]

if files:
    file_path = os.path.join(download_directory, files[0])
    print(f"Inspecting file: {files[0]}")
    # Read without header
    df = pd.read_excel(file_path, header=None, nrows=10)
    print(df)
else:
    print("No xlsx files found")
