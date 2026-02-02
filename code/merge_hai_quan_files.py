import pandas as pd
import os
import glob
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def merge_hai_quan_files(folder_path, output_file="merged_hai_quan_data.xlsx"):
    """
    Nối tất cả các file Excel trong thư mục dữ liệu hải quan
    Loại trừ file 'Form lấy dữ liệu hải quan.xlsx'
    Thêm cột 'Ten_File_Goc' để nhận biết file gốc
    """
    
    # Kiểm tra thư mục có tồn tại không
    if not os.path.exists(folder_path):
        print(f"Thư mục không tồn tại: {folder_path}")
        return
    
    # Lấy danh sách tất cả file Excel
    excel_files = glob.glob(os.path.join(folder_path, "*.xls*"))
    
    # Loại trừ file form
    excel_files = [f for f in excel_files if "Form lấy dữ liệu hải quan" not in os.path.basename(f)]
    
    print(f"Tìm thấy {len(excel_files)} file Excel để nối:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    if not excel_files:
        print("Không tìm thấy file Excel nào để nối!")
        return
    
    # Danh sách để lưu tất cả DataFrame
    all_dataframes = []
    
    # Đọc từng file
    for file_path in excel_files:
        try:
            print(f"\nĐang xử lý: {os.path.basename(file_path)}")
            
            # Lấy tên file (không có extension)
            file_name = Path(file_path).stem
            
            # Đọc file Excel với engine phù hợp
            # Thử đọc tất cả sheet trước
            try:
                # Thử với engine xlrd cho file .xls
                if file_path.endswith('.xls'):
                    excel_file = pd.ExcelFile(file_path, engine='xlrd')
                else:
                    excel_file = pd.ExcelFile(file_path)
            except:
                # Nếu xlrd không hoạt động, thử openpyxl
                try:
                    excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                except:
                    # Cuối cùng thử calamine cho file .xls
                    try:
                        excel_file = pd.ExcelFile(file_path, engine='calamine')
                    except Exception as e:
                        print(f"    ✗ Không thể đọc file với bất kỳ engine nào: {str(e)}")
                        continue
            
            sheet_names = excel_file.sheet_names
            
            print(f"  - Số sheet: {len(sheet_names)}")
            print(f"  - Tên các sheet: {sheet_names}")
            
            # Đọc từng sheet
            for sheet_name in sheet_names:
                try:
                    # Đọc sheet với engine phù hợp
                    if file_path.endswith('.xls'):
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                    else:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Kiểm tra nếu DataFrame không rỗng
                    if not df.empty:
                        # Thêm cột để nhận biết file và sheet gốc
                        df['Ten_File_Goc'] = file_name
                        df['Ten_Sheet_Goc'] = sheet_name
                        
                        # Thêm vào danh sách
                        all_dataframes.append(df)
                        print(f"    ✓ Sheet '{sheet_name}': {len(df)} dòng")
                    else:
                        print(f"    - Sheet '{sheet_name}': Rỗng, bỏ qua")
                        
                except Exception as e:
                    print(f"    ✗ Lỗi khi đọc sheet '{sheet_name}': {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"✗ Lỗi khi đọc file {os.path.basename(file_path)}: {str(e)}")
            continue
    
    # Nối tất cả DataFrame
    if all_dataframes:
        print(f"\nĐang nối {len(all_dataframes)} DataFrame...")
        
        # Nối tất cả DataFrame
        merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        print(f"✓ Hoàn thành! Tổng số dòng: {len(merged_df)}")
        print(f"✓ Số cột: {len(merged_df.columns)}")
        
        # Hiển thị thống kê
        print(f"\nThống kê theo file gốc:")
        file_counts = merged_df['Ten_File_Goc'].value_counts()
        for file_name, count in file_counts.items():
            print(f"  - {file_name}: {count} dòng")
        
        # Lưu file kết quả
        output_path = os.path.join(folder_path, output_file)
        merged_df.to_excel(output_path, index=False)
        print(f"\n✓ Đã lưu file kết quả: {output_path}")
        
        # Hiển thị vài dòng đầu
        print(f"\nVài dòng đầu của dữ liệu đã nối:")
        print(merged_df.head())
        
        return merged_df
    else:
        print("Không có dữ liệu nào để nối!")
        return None

def main():
    # Đường dẫn thư mục chứa dữ liệu hải quan
    folder_path = r"D:\BFC\Data\Du lieu hai quan\Thang 8 lan 1"
    
    # Tên file output
    output_file = "merged_hai_quan_thang8_lan1.xlsx"
    
    print("=== CHƯƠNG TRÌNH NỐI FILE DỮ LIỆU HẢI QUAN ===")
    print(f"Thư mục: {folder_path}")
    print(f"File kết quả: {output_file}")
    print("=" * 50)
    
    # Thực hiện nối file
    result = merge_hai_quan_files(folder_path, output_file)
    
    if result is not None:
        print("\n=== HOÀN THÀNH ===")
        print(f"Tổng số dòng dữ liệu: {len(result)}")
        print(f"Số file đã xử lý: {result['Ten_File_Goc'].nunique()}")
        print(f"Số sheet đã xử lý: {result['Ten_Sheet_Goc'].nunique()}")
    else:
        print("\n=== LỖI ===")
        print("Không thể nối dữ liệu!")

if __name__ == "__main__":
    main()
