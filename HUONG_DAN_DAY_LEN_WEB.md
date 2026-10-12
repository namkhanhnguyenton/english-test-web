# Hướng Dẫn Đẩy Web Lên Để Chạy Trên Thiết Bị Khác (Điện Thoại, Tablet, Máy Tính Khác)

Có **3 phương án** phổ biến tùy theo nhu cầu của bạn:

---

## 📱 PHƯƠNG ÁN 1: Chạy Ngay Trên Điện Thoại & Máy Khác (Cùng Mạng Wi-Fi)
*(Nhanh nhất, không cần cài đặt hosting phức tạp)*

Máy tính của bạn đang đóng vai trò là máy chủ (Web Server). Bất kỳ điện thoại (iPhone, Android), iPad, hoặc máy tính khác đang kết nối chung mạng Wi-Fi đều có thể truy cập được ngay lập tức.

### Bước 1: Khởi động web trên máy tính
- Chạy file `run.bat` (hoặc lệnh `python app.py`).
- Máy chủ sẽ lắng nghe kết nối tại địa chỉ IP nội bộ: **`192.168.1.223`**

### Bước 2: Mở trên thiết bị khác
- Trên điện thoại / máy tính khác (đã kết nối cùng Wi-Fi với máy tính), mở trình duyệt (Chrome, Safari) và gõ:
  ```
  http://192.168.1.223:5000
  ```
- Bạn sẽ thấy giao diện web xuất hiện, chọn trình độ, nghe audio MP3 và làm bài trắc nghiệm / điền từ mượt mà trên điện thoại!

### ⚠️ Lưu ý quan trọng (Nếu điện thoại không tải được trang):
Do tính năng bảo mật của Windows Defender Firewall có thể chặn kết nối từ bên ngoài:
1. Nhấp chuột phải vào file **`mo_tuong_lua.bat`** trong thư mục dự án.
2. Chọn **"Run as administrator"** (Chạy với quyền Quản trị viên).
3. Sau khi mở cổng 5000 thành công, điện thoại sẽ truy cập bình thường.

---

## 🌐 PHƯƠNG ÁN 2: Chia Sẻ Link Công Khai Qua Internet (Miễn Phí 100%)
*(Dành cho học sinh ở xa, dùng 4G hoặc ở nhà khác truy cập qua Internet)*

Bạn có thể tạo một đường link Internet an toàn (có khóa bảo mật HTTPS) kết nối thẳng vào máy tính của bạn thông qua **Cloudflare Tunnel** hoặc **ngrok**.

### Sử dụng Cloudflare Tunnel (Không cần đăng ký tài khoản):
1. Tải công cụ miễn phí **cloudflared** từ Cloudflare:
   - Tải file `cloudflared-windows-amd64.exe` từ trang chính thức: [https://github.com/cloudflare/cloudflared/releases](https://github.com/cloudflare/cloudflared/releases)
   - Đổi tên file thành `cloudflared.exe` và để vào thư mục dự án.
2. Mở Command Prompt (cmd) và chạy lệnh:
   ```cmd
   cloudflared tunnel --url http://localhost:5000
   ```
3. Màn hình sẽ xuất hiện một đường link công khai có dạng:
   ```
   https://xyz-abc-random.trycloudflare.com
   ```
4. Gửi link này cho bất kỳ ai trên thế giới, họ có thể mở trên điện thoại hoặc máy tính để làm bài kiểm tra ngay lập tức!

---

## ☁️ PHƯƠNG ÁN 3: Đưa Lên Máy Chủ Cloud 24/7 (Render.com hoặc PythonAnywhere)
*(Web chạy liên tục trên mạng kể cả khi tắt máy tính cá nhân)*

Dự án đã được cấu hình sẵn các file chuẩn cho Cloud:
- **`Procfile`**: Cấu hình khởi chạy máy chủ Gunicorn trên Linux.
- **`requirements.txt`**: Tự động nhận diện hệ điều hành (chạy Gunicorn trên Linux, pywin32 trên Windows).
- **`ppt_converter.py`**: Tích hợp cơ chế tự động chuyển đổi slide bằng `python-pptx` và `Pillow` nên hoạt động tốt trên cả máy chủ Linux mà không cần cài Microsoft Office.

### Các bước đẩy lên Render.com (Miễn phí 100%):
1. **Tạo kho mã nguồn trên GitHub**:
   - Đăng nhập [https://github.com](https://github.com).
   - Tạo một Repository mới (ví dụ: `english-test-web`).
   - Đẩy toàn bộ thư mục dự án này lên repository đó:
     ```bash
     git init
     git add .
     git commit -m "Khoi tao he thong test tieng anh"
     git branch -M main
     git remote add origin https://github.com/namkhanhnguyenton/english-test-web.git
     git push -u origin main
     ```

2. **Kết nối và triển khai trên Render.com**:
   - Truy cập [https://render.com](https://render.com) và đăng ký tài khoản miễn phí bằng tài khoản GitHub.
   - Nhấn **New +** -> Chọn **Web Service**.
   - Chọn kho lưu trữ `english-test-web` vừa đẩy lên.
   - Cài đặt cấu hình:
     - **Name**: `englishtest-pro` (hoặc tên tùy thích)
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: `Free`
   - Nhấn **Create Web Service**.

3. **Nhận đường link trang web**:
   - Sau 1 - 2 phút cài đặt, Render sẽ cung cấp đường link cố định vĩnh viễn:
     ```
     https://englishtest-pro.onrender.com
     ```
   - Trang web của bạn sẽ chạy 24/7 trên toàn thế giới!

