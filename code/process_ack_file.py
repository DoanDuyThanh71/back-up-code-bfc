import pandas as pd
import re
import numpy as np

def find_company_name(description):
    """Tìm thương hiệu từ mô tả sản phẩm"""
    if pd.isna(description):
        return ""
    
    # Danh sách các từ khóa
    keywords = ['Producer', 'hãng sx', 'hãng sản xuất', 'hang san xuat', 'hsx', 'manufacturer', 'Manufacturer', 'publisher', 'nhà sản xuất', 'hãng',
                'Nhà SX', 'Nhà sx', 'nha sx', 'NSX', 'nsx', 'ncc', 'brand', 'hiệu', 'hang', 'nhà sx']

    # Danh sách các tháng bằng tiếng Anh
    months = ["ngày", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # Tạo chuỗi regex cho các tháng, không phân biệt hoa thường
    months_pattern = '|'.join(months)

    # Tạo regex pattern để loại bỏ các tháng
    remove_months_pattern = re.compile(r'\b(' + months_pattern + r')\b', re.IGNORECASE)

    # Loại bỏ các tháng khỏi mô tả
    description_without_months = re.sub(remove_months_pattern, '', description)

    # Tạo regex pattern để tìm kiếm từ khóa
    keywords_pattern = re.compile(r'(' + '|'.join(keywords) + r')\s*:\s*([^\n.;:@!0-9(]+)', re.IGNORECASE)

    # Tìm các trận đấu
    matches = keywords_pattern.findall(description_without_months)

    # Duyệt qua các kết quả tìm thấy để tìm giá trị đầu tiên không rỗng
    result = ""
    for match in matches:
        if match[1].strip():  # Kiểm tra xem giá trị có rỗng không
            result = match[1].strip()
            break
    return result

def convert_quantity_to_kg(row):
    """Chuyển đổi khối lượng về kg"""
    unit_mapping = {
        'kilogram': 1,
        'kilograms': 1,
        'kgm': 1,
        'kg': 1,
        'kgs': 1,
        'gram': 0.001,
        'g': 0.001,
        'ton': 1000,
        'cubic meter': 1000,
        'tne': 1000,
        'milligram': 0.000001,
        'mg': 0.000001,
        'microgram': 0.000000001,
        'µg': 0.000000001,
        'metric ton': 1000,
        'tonne': 1000,
        'pound': 0.453592,
        'lb': 0.453592,
        'ounce': 0.0283495,
        'oz': 0.0283495,
        'ml': 0.001
    }
    
    # Kiểm tra nếu có cột Đơn_vị
    if 'Đơn_vị' in row.index and pd.notna(row['Đơn_vị']):
        unit = str(row['Đơn_vị']).lower()
        if unit in unit_mapping:
            return row['updated_Số_lượng'] * unit_mapping[unit]
    
    # Nếu không có đơn vị rõ ràng, tìm trong mô tả sản phẩm
    if pd.notna(row['Mô_tả_sản_phẩm']):
        match = re.search(r'(\d+(?:[.,]\s?\d+)?)\s*({})'.format('|'.join(map(re.escape, unit_mapping.keys()))), 
                         str(row['Mô_tả_sản_phẩm']), re.IGNORECASE)
        
        if match:
            captured_value = match.group(1).replace(',', '.').replace(' ', '')
            unit_found = match.group(2).lower()
            
            if unit_found in unit_mapping:
                return row['updated_Số_lượng'] * unit_mapping[unit_found]
    
    return row['updated_Số_lượng']

def process_ack_file(file_path):
    """Xử lý file ACK 082025"""
    try:
        # Đọc file Excel
        df = pd.read_excel(file_path)
        
        print("Cấu trúc file:")
        print(df.columns.tolist())
        print(f"\nSố dòng: {len(df)}")
        print(f"Số cột: {len(df.columns)}")
        
        # Hiển thị vài dòng đầu để xem cấu trúc
        print("\nVài dòng đầu:")
        print(df.head())
        
        # Tạo cột thương hiệu từ Mô_tả_sản_phẩm
        if 'Mô_tả_sản_phẩm' in df.columns:
            df['Thương_hiệu'] = df['Mô_tả_sản_phẩm'].apply(find_company_name)
            print(f"\nĐã tạo cột 'Thương_hiệu'")
            
            # Hiển thị các thương hiệu tìm được
            brands_found = df[df['Thương_hiệu'] != '']['Thương_hiệu'].unique()
            print(f"Các thương hiệu tìm được: {brands_found}")
        
        # Chuyển đổi khối lượng nếu có cột updated_Số_lượng
        if 'updated_Số_lượng' in df.columns:
            df['Số_lượng_kg'] = df.apply(convert_quantity_to_kg, axis=1)
            print(f"\nĐã tạo cột 'Số_lượng_kg'")
            
            # Tạo cột so sánh
            df['Chênh_lệch_số_lượng'] = df['Số_lượng_kg'] - df['updated_Số_lượng']
            print(f"Đã tạo cột 'Chênh_lệch_số_lượng'")
        
        # Lưu file kết quả
        output_path = file_path.replace('.xlsx', '_processed.xlsx')
        df.to_excel(output_path, index=False)
        print(f"\nĐã lưu file kết quả: {output_path}")
        
        return df
        
    except Exception as e:
        print(f"Lỗi khi xử lý file: {e}")
        return None

if __name__ == "__main__":
    # Xử lý file ACK 082025
    file_path = "../ACK 082025 - Copy.xlsx"
    result_df = process_ack_file(file_path)
