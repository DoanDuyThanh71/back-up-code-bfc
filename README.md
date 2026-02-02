# Công cụ gộp file MP3

Script Python để gộp tất cả các file MP3 trong thư mục theo thứ tự tăng dần.

## Cài đặt

1. Cài đặt Python (phiên bản 3.6 trở lên)

2. Cài đặt thư viện cần thiết:
```bash
pip install -r requirements.txt
```

Hoặc cài đặt trực tiếp:
```bash
pip install pydub
```

**Lưu ý:** Nếu gặp lỗi khi cài đặt pydub, có thể cần cài đặt thêm ffmpeg:
- Windows: Tải ffmpeg từ https://ffmpeg.org/download.html
- Hoặc cài đặt qua chocolatey: `choco install ffmpeg`

## Cách sử dụng

1. Đặt tất cả file MP3 cần gộp vào thư mục `D:\BFC\Voice\Sukien25nam`
2. Chạy script:
```bash
python merge_mp3_files.py
```

## Tính năng

- ✅ Tự động tìm tất cả file MP3 trong thư mục
- ✅ Sắp xếp theo thứ tự tăng dần (dựa trên số trong tên file)
- ✅ Gộp thành 1 file MP3 duy nhất
- ✅ Hiển thị thông tin chi tiết về quá trình gộp
- ✅ Thông báo thời lượng file gộp cuối cùng

## Cấu trúc thư mục

```
D:\BFC\Voice\Sukien25nam\
├── voice 1.mp3
├── voice 2.mp3
├── voice 3.mp3
├── voice 4.mp3
├── voice 5.mp3
├── voice 6.mp3
└── sukien25nam_merged.mp3 (file output)
```

## Tùy chỉnh

Bạn có thể chỉnh sửa các thông số trong file `merge_mp3_files.py`:

- `input_folder`: Đường dẫn thư mục chứa file MP3
- `output_file`: Tên file output
- Thêm khoảng nghỉ giữa các file (bỏ comment dòng `merged_audio += AudioSegment.silent(duration=500)`)

## Xử lý lỗi

Nếu gặp lỗi "ffmpeg not found":
1. Tải ffmpeg từ https://ffmpeg.org/download.html
2. Giải nén và thêm vào PATH
3. Hoặc cài đặt qua package manager
