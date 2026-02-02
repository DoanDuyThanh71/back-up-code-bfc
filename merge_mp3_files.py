#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để gộp tất cả các file MP3 trong thư mục theo thứ tự tăng dần
Tác giả: AI Assistant
"""

import os
import sys
from pathlib import Path
from pydub import AudioSegment
import re

def get_numeric_part(filename):
    """
    Trích xuất phần số từ tên file để sắp xếp
    Ví dụ: "voice 1.mp3" -> 1, "voice 10.mp3" -> 10
    """
    # Tìm số trong tên file
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[0])
    return 0

def merge_mp3_files(input_folder, output_file=None):
    """
    Gộp tất cả file MP3 trong thư mục theo thứ tự tăng dần
    
    Args:
        input_folder (str): Đường dẫn thư mục chứa file MP3
        output_file (str): Tên file output (mặc định: merged_audio.mp3)
    """
    
    # Kiểm tra thư mục có tồn tại không
    if not os.path.exists(input_folder):
        print(f"❌ Thư mục '{input_folder}' không tồn tại!")
        return False
    
    # Lấy danh sách file MP3
    mp3_files = []
    for file in os.listdir(input_folder):
        if file.lower().endswith('.mp3'):
            mp3_files.append(file)
    
    if not mp3_files:
        print(f"❌ Không tìm thấy file MP3 nào trong thư mục '{input_folder}'!")
        return False
    
    # Sắp xếp file theo thứ tự tăng dần của số trong tên file
    mp3_files.sort(key=get_numeric_part)
    
    print(f"📁 Thư mục: {input_folder}")
    print(f"🎵 Tìm thấy {len(mp3_files)} file MP3:")
    for i, file in enumerate(mp3_files, 1):
        print(f"   {i}. {file}")
    
    # Tạo file output nếu chưa có
    if output_file is None:
        output_file = "merged_audio.mp3"
    
    output_path = os.path.join(input_folder, output_file)
    
    try:
        # Khởi tạo AudioSegment rỗng
        merged_audio = AudioSegment.empty()
        
        print(f"\n🔄 Đang gộp {len(mp3_files)} file MP3...")
        
        for i, mp3_file in enumerate(mp3_files, 1):
            file_path = os.path.join(input_folder, mp3_file)
            print(f"   📥 Đang xử lý: {mp3_file} ({i}/{len(mp3_files)})")
            
            # Đọc file MP3
            audio = AudioSegment.from_mp3(file_path)
            
            # Gộp vào audio chung
            merged_audio += audio
            
            # Thêm khoảng nghỉ ngắn giữa các file (tùy chọn)
            # merged_audio += AudioSegment.silent(duration=500)  # 0.5 giây im lặng
        
        # Xuất file gộp
        print(f"💾 Đang lưu file gộp: {output_path}")
        merged_audio.export(output_path, format="mp3")
        
        # Thông tin kết quả
        duration_seconds = len(merged_audio) / 1000.0
        duration_minutes = duration_seconds / 60.0
        
        print(f"\n✅ Gộp thành công!")
        print(f"📄 File output: {output_path}")
        print(f"⏱️  Thời lượng: {duration_minutes:.2f} phút ({duration_seconds:.2f} giây)")
        print(f"📊 Số file đã gộp: {len(mp3_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi gộp file: {str(e)}")
        return False

def main():
    """Hàm chính"""
    
    # Đường dẫn thư mục chứa file MP3
    input_folder = r"D:\BFC\Voice\Sukien25nam"
    
    # Tên file output (có thể thay đổi)
    output_file = "sukien25nam_merged.mp3"
    
    print("🎵 === CÔNG CỤ GỘP FILE MP3 === 🎵")
    print("=" * 40)
    
    # Thực hiện gộp file
    success = merge_mp3_files(input_folder, output_file)
    
    if success:
        print("\n🎉 Hoàn thành! File MP3 đã được gộp thành công.")
    else:
        print("\n💥 Có lỗi xảy ra. Vui lòng kiểm tra lại.")
        sys.exit(1)

if __name__ == "__main__":
    main()
