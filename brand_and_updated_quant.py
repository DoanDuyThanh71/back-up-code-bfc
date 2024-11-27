import re
import pandas as pd

def find_company_name(description):
    if pd.isna(description):
        return 0
    
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
    # Sửa đổi regex để chấp nhận dấu phẩy và dấu cách, loại bỏ các ký tự khác
    keywords_pattern = re.compile(r'(' + '|'.join(keywords) + r')\s*:\s*([^\n.;:@!0-9(]+)', re.IGNORECASE)

    # Tìm các trận đấu
    matches = keywords_pattern.findall(description_without_months)

    # Duyệt qua các kết quả tìm thấy để tìm giá trị đầu tiên không rỗng
    result = None
    for match in matches:
        if match[1].strip():  # Kiểm tra xem giá trị có rỗng không
            result = match[1].strip()
            break
    return result


def update_quantities(row):
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
        'ton': 1000,
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
        'stone': 6.35029,
        'st': 6.35029,
        'cara': 0.0002,
        'car': 0.0002, 
        'ct': 0.0002,
        'grain': 0.00006479891,
        'gr': 0.00006479891,
        'ml': 0.001,
        'mg': 0.001
    }
    
    unit = row['Đơn_vị'].lower()

    if unit in unit_mapping:
        return row['Số_lượng'] * unit_mapping[unit]
    else:
        match = re.search(r'(\d+(?:[.,]\s?\d+)?)\s*({})'.format('|'.join(map(re.escape, unit_mapping.keys()))), row['Mô_tả_sản_phẩm'], re.IGNORECASE)

        if match:
            captured_value = match.group(1).replace(',', '.').replace(' ', '')

            if match.group(2).lower() in unit_mapping:
                exchange_rate = float(captured_value) * unit_mapping[match.group(2).lower()]
            else:
                exchange_rate = 1.0  # Default to 1 if the unit is not found in unit_mapping

            return row['Số_lượng'] * exchange_rate
    return row['Số_lượng']