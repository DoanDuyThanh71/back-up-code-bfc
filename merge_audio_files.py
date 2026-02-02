import os
import re
from datetime import datetime
from pydub import AudioSegment
import glob

def extract_timestamp_from_filename(filename):
    """
    Trích xuất timestamp từ tên file ElevenLabs
    Format: ElevenLabs_YYYY-MM-DDTHH_MM_SS_...
    """
    # Pattern để tìm timestamp trong tên file
    pattern = r'ElevenLabs_(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})'
    match = re.search(pattern, filename)
    
    if match:
        timestamp_str = match.group(1)
        # Chuyển đổi format từ YYYY-MM-DDTHH_MM_SS thành datetime object
        # Thay thế _ bằng : để có format chuẩn
        timestamp_str = timestamp_str.replace('_', ':')
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return None
    return None

def merge_audio_files_by_timestamp(input_folder, output_file="merged_audio.mp3"):
    """
    Gộp các file audio theo thứ tự timestamp tăng dần
    """
    
    if not os.path.exists(input_folder):
        print(f"Thư mục không tồn tại: {input_folder}")
        return
    
    # Lấy tất cả file audio trong thư mục
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.aac', '*.ogg']
    audio_files = []
    
    for extension in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_folder, extension)))
    
    if not audio_files:
        print("Không tìm thấy file audio nào trong thư mục!")
        return
    
    print(f"Tìm thấy {len(audio_files)} file audio:")
    
    # Tạo danh sách file với timestamp
    files_with_timestamp = []
    for file_path in audio_files:
        filename = os.path.basename(file_path)
        timestamp = extract_timestamp_from_filename(filename)
        
        if timestamp:
            files_with_timestamp.append((timestamp, file_path, filename))
            print(f"  - {filename} -> {timestamp}")
        else:
            print(f"  - {filename} -> Không thể trích xuất timestamp")
    
    if not files_with_timestamp:
        print("Không có file nào có timestamp hợp lệ!")
        return
    
    # Sắp xếp theo timestamp tăng dần
    files_with_timestamp.sort(key=lambda x: x[0])
    
    print(f"\nThứ tự gộp file (theo timestamp tăng dần):")
    for i, (timestamp, file_path, filename) in enumerate(files_with_timestamp, 1):
        print(f"  {i}. {filename} ({timestamp})")
    
    # Bắt đầu gộp file
    print(f"\nĐang gộp {len(files_with_timestamp)} file audio...")
    
    try:
        # Load file đầu tiên
        merged_audio = AudioSegment.from_mp3(files_with_timestamp[0][1])
        print(f"✓ Đã load file: {files_with_timestamp[0][2]}")
        
        # Gộp các file còn lại
        for i, (timestamp, file_path, filename) in enumerate(files_with_timestamp[1:], 2):
            try:
                audio = AudioSegment.from_mp3(file_path)
                merged_audio += audio
                print(f"✓ Đã gộp file {i}/{len(files_with_timestamp)}: {filename}")
            except Exception as e:
                print(f"✗ Lỗi khi gộp file {filename}: {str(e)}")
                continue
        
        # Xuất file kết quả
        output_path = os.path.join(input_folder, output_file)
        merged_audio.export(output_path, format="mp3")
        
        print(f"\n✓ Hoàn thành! File đã được gộp và lưu tại: {output_path}")
        print(f"✓ Tổng thời lượng: {len(merged_audio) / 1000:.2f} giây ({len(merged_audio) / 60000:.2f} phút)")
        
        return output_path
        
    except Exception as e:
        print(f"✗ Lỗi khi gộp file: {str(e)}")
        return None

def main():
    # Thư mục chứa file audio
    voice_folder = "VOICE"
    
    # Tên file output
    output_filename = "merged_voice_audio.mp3"
    
    print("=== CHƯƠNG TRÌNH GỘP FILE AUDIO THEO THỨ TỰ TIMESTAMP ===")
    print(f"Thư mục: {voice_folder}")
    print(f"File kết quả: {output_filename}")
    print("=" * 60)
    
    # Thực hiện gộp file
    result = merge_audio_files_by_timestamp(voice_folder, output_filename)
    
    if result:
        print("\n=== HOÀN THÀNH ===")
        print(f"File audio đã được gộp thành công!")
    else:
        print("\n=== LỖI ===")
        print("Không thể gộp file audio!")

if __name__ == "__main__":
    main()

