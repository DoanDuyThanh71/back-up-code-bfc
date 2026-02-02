import pandas as pd
import glob
import os

download_directory = "./Downloads/"
files = [f for f in os.listdir(download_directory) if f.endswith('.xlsx')]

if files:
    file_path = os.path.join(download_directory, files[0])
    print(f"Inspecting file: {files[0]}")
    # Read header row (row 1)
    df = pd.read_excel(file_path, header=1)
    
    # Check "目的国" (Destination Country) - likely column index 4 based on previous output
    print(f"Column 4 (Expected '目的国'): {df.columns[4]}")
    print("First 5 values in '目的国':")
    print(df.iloc[:5, 4])

    # Check "进口商地址" (Importer Address) - likely column index 3
    print(f"\nColumn 3 (Expected '进口商地址'): {df.columns[3]}")
    print("First 5 values in '进口商地址':")
    print(df.iloc[:5, 3])
else:
    print("No xlsx files found")
