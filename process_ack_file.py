"""
Script để xử lý file ACK 082025 - Copy.xlsx
Thêm các cột mới: Brand, Updated_Số_lượng, Updated_Đơn_vị, Updated_Đơn_giá
Dựa trên code preprocessing từ notebook __Preprocessing_all (2).ipynb
"""

import pandas as pd
import re
import numpy as np
import os
import sys
sys.path.append('./code')
from brand_and_updated_quant import find_company_name, update_quantities

def calculate_updated_đơn_giá(row):
    """
    Tính toán đơn giá cập nhật dựa trên Thành_tiền / updated_Số_lượng
    """
    if row['updated_Số_lượng'] != 0:
        return row['Thành_tiền'] / row['updated_Số_lượng']
    else:
        return 0  # Trả về 0 nếu updated_Số_lượng = 0 để tránh chia cho 0

def update_quantities_for_ack(row):
    """
    Wrapper function để sử dụng hàm update_quantities với tên cột chính xác
    """
    # Tạo một row mới với tên cột đúng
    new_row = row.copy()
    if 'Số lượng' in row:
        new_row['Số_lượng'] = row['Số lượng']
    if 'Đơn_vị' in row:
        new_row['Đơn_vị'] = row['Đơn_vị']
    if 'Mô_tả_sản_phẩm' in row:
        new_row['Mô_tả_sản_phẩm'] = row['Mô_tả_sản_phẩm']
    
    return update_quantities(new_row)

def process_ack_file(input_file_path, output_file_path=None):
    """
    Xử lý file ACK để thêm các cột mới
    
    Args:
        input_file_path (str): Đường dẫn file input
        output_file_path (str): Đường dẫn file output (tùy chọn)
    
    Returns:
        pd.DataFrame: DataFrame đã được xử lý
    """
    
    print("🔄 Đang đọc file ACK...")
    
    # Đọc file Excel
    try:
        df = pd.read_excel(input_file_path)
        print(f"✅ Đã đọc file thành công: {df.shape[0]} dòng, {df.shape[1]} cột")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return None
    
    # Tạo bản sao để xử lý
    df_processed = df.copy()
    
    print("\n🔄 Đang thêm cột Brand...")
    
    # Thêm cột Brand bằng cách áp dụng hàm find_company_name
    df_processed['Brand'] = df_processed['Mô_tả_sản_phẩm'].apply(find_company_name)
    
    # Chèn cột Brand sau cột Mô_tả_sản_phẩm
    mô_tả_position = df_processed.columns.get_loc('Mô_tả_sản_phẩm')
    df_processed.insert(mô_tả_position + 1, 'Brand', df_processed.pop('Brand'))
    
    print(f"✅ Đã thêm cột Brand. Số thương hiệu được tìm thấy: {df_processed['Brand'].notna().sum()}")
    
    print("\n🔄 Đang cập nhật cột updated_Số_lượng...")
    
    # Cập nhật cột updated_Số_lượng bằng cách áp dụng hàm update_quantities
    if 'updated_Số_lượng' in df_processed.columns:
        df_processed['updated_Số_lượng'] = df_processed.apply(update_quantities_for_ack, axis=1)
        print("✅ Đã cập nhật cột updated_Số_lượng")
    else:
        print("⚠️ Không tìm thấy cột updated_Số_lượng")
    
    print("\n🔄 Đang cập nhật cột updated_Đơn_vị...")
    
    # Cập nhật cột updated_Đơn_vị (mặc định là "kilogram")
    if 'updated_Đơn_vị' in df_processed.columns:
        df_processed['updated_Đơn_vị'] = "kilogram"
        print("✅ Đã cập nhật cột updated_Đơn_vị")
    else:
        print("⚠️ Không tìm thấy cột updated_Đơn_vị")
    
    print("\n🔄 Đang cập nhật cột Updated_Đơn_giá...")
    
    # Cập nhật cột Updated_Đơn_giá bằng cách tính toán
    if 'Updated_Đơn_giá' in df_processed.columns:
        df_processed['Updated_Đơn_giá'] = df_processed.apply(calculate_updated_đơn_giá, axis=1)
        print("✅ Đã cập nhật cột Updated_Đơn_giá")
    else:
        print("⚠️ Không tìm thấy cột Updated_Đơn_giá")
    
    # Hiển thị thống kê
    print(f"\n📊 Thống kê sau khi xử lý:")
    print(f"  - Tổng số bản ghi: {len(df_processed)}")
    print(f"  - Số thương hiệu được tìm thấy: {df_processed['Brand'].notna().sum()}")
    
    if 'Số lượng' in df_processed.columns:
        print(f"  - Số lượng trung bình gốc: {df_processed['Số lượng'].mean():.2f}")
    if 'updated_Số_lượng' in df_processed.columns:
        print(f"  - Số lượng trung bình cập nhật: {df_processed['updated_Số_lượng'].mean():.2f}")
    if 'Đơn_giá' in df_processed.columns:
        print(f"  - Đơn giá trung bình gốc: {df_processed['Đơn_giá'].mean():.2f}")
    if 'Updated_Đơn_giá' in df_processed.columns:
        print(f"  - Đơn giá trung bình cập nhật: {df_processed['Updated_Đơn_giá'].mean():.2f}")
    
    # Hiển thị top 5 thương hiệu
    if df_processed['Brand'].notna().any():
        print(f"\n📈 Top 5 thương hiệu được tìm thấy:")
        brand_counts = df_processed['Brand'].value_counts().head()
        for brand, count in brand_counts.items():
            print(f"  - {brand}: {count} lần")
    
    # Xuất file nếu có đường dẫn output
    if output_file_path:
        print(f"\n🔄 Đang xuất file kết quả...")
        try:
            df_processed.to_excel(output_file_path, index=False, sheet_name="Data")
            print(f"✅ Đã xuất file thành công: {output_file_path}")
            print(f"📊 Kích thước file kết quả: {df_processed.shape[0]} dòng, {df_processed.shape[1]} cột")
        except Exception as e:
            print(f"❌ Lỗi khi xuất file: {e}")
    
    return df_processed

def main():
    """
    Hàm main để chạy script
    """
    # Đường dẫn file input
    input_file = "ACK 082025 - Copy.xlsx"
    
    # Đường dẫn file output
    output_file = "ACK 082025 - Copy_processed.xlsx"
    
    # Kiểm tra file input có tồn tại không
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    print("=" * 60)
    print("🚀 BẮT ĐẦU XỬ LÝ FILE ACK 082025 - Copy.xlsx")
    print("=" * 60)
    
    # Xử lý file
    result_df = process_ack_file(input_file, output_file)
    
    if result_df is not None:
        print("\n" + "=" * 60)
        print("✅ HOÀN THÀNH XỬ LÝ FILE")
        print("=" * 60)
        
        # Hiển thị một số dòng đầu tiên để kiểm tra
        print("\n📋 Một số dòng đầu tiên của kết quả:")
        display_columns = ['Mô_tả_sản_phẩm', 'Brand']
        if 'Số lượng' in result_df.columns:
            display_columns.append('Số lượng')
        if 'updated_Số_lượng' in result_df.columns:
            display_columns.append('updated_Số_lượng')
        if 'Đơn_vị' in result_df.columns:
            display_columns.append('Đơn_vị')
        if 'updated_Đơn_vị' in result_df.columns:
            display_columns.append('updated_Đơn_vị')
        if 'Đơn_giá' in result_df.columns:
            display_columns.append('Đơn_giá')
        if 'Updated_Đơn_giá' in result_df.columns:
            display_columns.append('Updated_Đơn_giá')
        
        print(result_df[display_columns].head())
        
        # Hiển thị thông tin về các cột đã xử lý
        print(f"\n📋 Các cột đã được xử lý:")
        processed_columns = ['Brand', 'updated_Số_lượng', 'updated_Đơn_vị', 'Updated_Đơn_giá']
        for col in processed_columns:
            if col in result_df.columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} - Không tìm thấy")
    else:
        print("\n❌ XỬ LÝ FILE THẤT BẠI")

if __name__ == "__main__":
    main()
