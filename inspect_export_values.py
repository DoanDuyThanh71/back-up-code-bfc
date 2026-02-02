import pandas as pd
import glob
import os

download_directory = "./Downloads/"
xlsx_files = glob.glob(os.path.join(download_directory, "*.xlsx"))

if xlsx_files:
    target_file = xlsx_files[0]
    print(f"Inspecting {target_file}")
    df = pd.read_excel(target_file, header=1)
    
    print("\n--- Column 2: 进口商 (Importer) ---")
    print(df.iloc[:5, 2])
    
    print("\n--- Column 5: 出口商 (Exporter) ---")
    print(df.iloc[:5, 5])
else:
    print("No xlsx files found.")
