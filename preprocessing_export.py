
import pandas as pd
import re
import numpy as np
from brand_and_updated_quant import find_company_name, update_quantities
import joblib
# Import the EXPORT merge logic
from merge_files_export import merge_ingredients, convert_x2x, str_to_bool
import os

newFileName = "final 8 mã số thuế export"

downloaded_folder = "./Downloads/"
download_directory = os.path.abspath(downloaded_folder)
convert_x2x(download_directory+'/')

export_data = "True" # Just for flag, though not strictly used inside merge_ingredients for 33 columns
try:
    export_data = str_to_bool(export_data)
except ValueError as e:
    print(e)

df = merge_ingredients(downloaded_folder+"/", export_data=export_data)

# Re-implement the preprocessing logic
df_to_clean = df.copy()
df_to_clean['Date'] = pd.to_datetime(df_to_clean['Date'], format='%Y-%m-%d')
df_to_clean['Day'] = df_to_clean['Date'].dt.day
df_to_clean['Month'] = df_to_clean['Date'].dt.month
df_to_clean['Year'] = df_to_clean['Date'].dt.year

df_to_clean.insert(df_to_clean.columns.get_loc('Date')+1, 'Day', df_to_clean.pop('Day'))
df_to_clean.insert(df_to_clean.columns.get_loc('Date')+2, 'Month', df_to_clean.pop('Month'))
df_to_clean.insert(df_to_clean.columns.get_loc('Date')+3, 'Year', df_to_clean.pop('Year'))

df_to_clean['Mã_tờ_khai 11 số'] = df_to_clean['Mã_tờ_khai'].astype(str).str[:11] + df_to_clean['Số_lượng'].astype(str) + df_to_clean['Thành_tiền'].astype(str)
duplicated_rows = df_to_clean.duplicated(subset='Mã_tờ_khai 11 số', keep='first')
df_to_clean['is_duplicated']= duplicated_rows.astype(int)
df_to_clean = df_to_clean.drop(['Mã_tờ_khai 11 số'], axis=1)
df_to_clean.loc[duplicated_rows, 'is_duplicated'] = 1

def calculate_updated_đơn_giá(row):
    if row['Updated_Số_lượng'] != 0:
        return row['Thành_tiền'] / row['Updated_Số_lượng']
    else:
        return 0

def extract_after_keywords(text):
    keywords = ["tổng hợp","quốc tế","dịch vụ","thương mại", "TM", "sản xuất", "cổ phần", "MTV", "một thành viên", "TNHH", "trách nhiệm hữu hạn"]
    text_lower = text.lower()
    if text_lower.find("nhà ga"):
        keywords.pop(0)
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            start_index = text_lower.find(keyword_lower) + len(keyword_lower)
            result = text[start_index:].strip().replace("XUẤT NHẬP KHẨU", "XNK")
            return result
    return text

data_for_valid = df_to_clean.copy()
# 'Công_ty_nhập' IS THE EXPORTER (LOCAL COMPANY) in our mapping, so this finds the brand correctly
data_for_valid['Brand'] = data_for_valid['Mô_tả_sản_phẩm'].apply(find_company_name)
data_for_valid.insert(data_for_valid.columns.get_loc('Mô_tả_sản_phẩm') + 1, 'Brand', data_for_valid.pop('Brand'))

data_for_valid['Updated_Số_lượng'] = data_for_valid.apply(update_quantities, axis=1)
data_for_valid['Updated_Đơn_vị'] = ["kilogram"] * len(data_for_valid)
data_for_valid.insert(data_for_valid.columns.get_loc('Brand') + 1, 'Updated_Số_lượng', data_for_valid.pop('Updated_Số_lượng'))
data_for_valid.insert(data_for_valid.columns.get_loc('Brand') + 2, 'Updated_Đơn_vị', data_for_valid.pop('Updated_Đơn_vị'))

data_for_valid['Updated_Đơn_giá'] = data_for_valid.apply(lambda row: calculate_updated_đơn_giá(row), axis=1)
data_for_valid.insert(data_for_valid.columns.get_loc('Đơn_giá'), 'Updated_Đơn_giá', data_for_valid.pop('Updated_Đơn_giá'))

# Market Classification
if company := 'Công_ty_nhập': 
    comp_nice_name = company.lower().replace('_', " ")
    parent_company = 'Công ty nhập gộp'
    
    dim_file = '../../Data/Data for fill data/Updated dim_company_marketType.xlsx' 
    if os.path.exists(dim_file):
         df_marketclass = pd.read_excel(dim_file, sheet_name='phân loại thị trường')
         df_marketclass.columns = df_marketclass.columns.str.strip()
         df_marketclass['Công_ty_nhập'] = df_marketclass['Công_ty_nhập'].fillna('Unknown')
         
         result_df = pd.merge(data_for_valid[company], df_marketclass, on='Công_ty_nhập', how='left')
         result_df = result_df.iloc[:len(data_for_valid)]
         result_df = result_df.set_index(data_for_valid.index)
         
         data_for_valid['MarketClassification'] = result_df['MarketClassification']
         data_for_valid[f'Phân loại {comp_nice_name}'] = result_df['Phân loại công ty nhập']
         data_for_valid[parent_company] = result_df['Công ty nhập gộp']
    else:
         data_for_valid['MarketClassification'] = None
         data_for_valid[f'Phân loại {comp_nice_name}'] = None
         data_for_valid[parent_company] = None

    if parent_company not in data_for_valid.columns:
         data_for_valid[parent_company] = None
         
    if parent_company in data_for_valid.columns:
        data_for_valid.insert(data_for_valid.columns.get_loc(company) + 1, parent_company, data_for_valid.pop(parent_company))
    
    data_for_valid[parent_company] = data_for_valid[parent_company].fillna(
        data_for_valid[company].apply(extract_after_keywords)
    )

# Port mapping
def map_port_codes(port_code):
    port_mapping = {
        'HQSGKV1': 'Cảng Sài Gòn KV1', 'HQSGKV2': 'Cảng Sài Gòn KV2', 'HQSGKV3': 'Cảng Sài Gòn KV3',
        'HQSGKV4': 'Cảng Sài Gòn KV4', 'HQHPKV1': 'Cảng Hải Phòng KV1', 'HQHPKV2': 'Cảng Hải Phòng KV2',
        'HQHPKV3': 'Cảng Hải Phòng KV3', 'HQCNC': 'Cảng Nội Bài', 'HQCPNHCM': 'Cảng Phú Mỹ HCM',
        'HQCPNHN': 'Cảng Phú Mỹ Hà Nội', 'HQDINHVU': 'Cảng Đình Vũ', 'HQTSNHAT': 'Cảng Tân Sơn Nhất',
        'HQTIENSON': 'Cảng Tiên Sơn', 'CKCDANANG': 'Cảng Đà Nẵng', 'HQCKCDNA': 'Cảng Đà Nẵng',
        'CKQUYNHON': 'Cảng Quy Nhon', 'CKLAOBAO': 'Cảng Lao Bảo', 'HQCAMAU': 'Cảng Cà Mau', 'HQVINH': 'Cảng Vinh',
    }
    return port_mapping.get(port_code, port_code)

if '海关代理代码' in data_for_valid.columns:
    data_for_valid['Cảng nhập'] = data_for_valid['海关代理代码'].apply(map_port_codes)

# Output
merged_df = data_for_valid.sort_index()

# Note: We are using 'Công_ty_nhập' to hold the Local Exporter info.
# We are using 'Nhà_cung_cấp' to hold the Foreign Partner info.
# We are using 'Nước_nhập_khẩu' to hold the Destination Country.

columns_to_select = [
    'Day', 'Month', 'Year', 'Mã_tờ_khai', 
    'Công_ty_nhập', # Mapped from Exporter (Local)
    'Công ty nhập gộp', 
    'Công_ty_nhập (TA)', 
    'Địa_chỉ', 'Mã_số_thuế', 
    'Nhà_cung_cấp', # Mapped from Importer (Foreign)
    'Nhà Cung Cấp Gộp', 
    'Địa_chỉ_(ncc)', 
    'Nước_nhập_khẩu', # Destination Country
    'HScode', 'Mô_tả_sản_phẩm', 'Brand', 'Thương hiệu gộp', 'Hợp_lệ', 
    'Updated_Số_lượng', 'Updated_Đơn_vị', 'Số_lượng', 'Đơn_vị', 'Khối_lượng', 
    'Thành_tiền', 'Tiền_tệ', 'Updated_Đơn_giá', 'Đơn_giá', 'Tỷ giá', 
    'Điều_kiện_giao_hàng', 'Cảng xuất', 'Cảng nhập', 'MarketClassification', 
    'Phân loại công ty nhập', 'is_duplicated', 'Sản phẩm'
]

# Rename columns to reflect the Export context in the Final Output
new_column_names = [
    'Day', 'Month', 'Year', 'Mã tờ khai', 
    'Công ty xuất khẩu (VN)', # Renamed from Công_ty_nhập
    'Công ty xuất khẩu gộp', # Renamed from Công ty nhập gộp
    'Công ty xuất khẩu (TA)', # Renamed from Công_ty_nhập (TA)
    'Địa chỉ', 'Mã số thuế', 
    'Khách hàng (Foreign)', # Renamed from Nhà_cung_cấp
    'Khách hàng gộp', # Renamed from Nhà Cung Cấp Gộp
    'Địa chỉ (Khách hàng)', # Renamed from Địa_chỉ_(ncc)
    'Quốc gia nhập khẩu', # Destination Country
    'HScode', 'Mô tả sản phẩm', 'Thương hiệu', 'Thương hiệu gộp', 'Hợp lệ',    
    'updated Số lượng', 'updated Đơn vị', 'Số lượng', 'Đơn vị', 'Khối lượng', 
    'Thành tiền', 'Tiền tệ', 'Updated Đơn giá', 'Đơn giá', 'Tỷ giá', 
    'Điều kiện giao hàng', 'Cảng xuất', 'Cảng nhập', 'Phân loại thị trường', 
    'Phân loại công ty xuất', # Renamed
    'is duplicate', 'Sản phẩm'
]

available_columns = [col for col in columns_to_select if col in merged_df.columns]
available_new_names = [new_column_names[i] for i, col in enumerate(columns_to_select) if col in merged_df.columns]

selected_columns_df = merged_df[available_columns]
selected_columns_df.columns = available_new_names

output_path = f"../../Data/data final/Data Code Out/{newFileName}.xlsx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
selected_columns_df.to_excel(output_path, index=False, header=True, sheet_name="Data")
print(f"File created at: {output_path}")
