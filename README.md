# EnglishTestPro — Hệ Thống Kiểm Tra Trình Độ Tiếng Anh (PowerPoint + MP3 Nghe + Đáp Án Đa Dạng)

Hệ thống web kiểm tra trình độ tiếng Anh trực quan được xây dựng hoàn chỉnh với Flask, SQLite, Tailwind CSS, bộ công cụ tự động chuyển đổi slide PowerPoint và trình phát âm thanh nghe (Listening Audio Player).

---

## 🌟 Tính Năng Nổi Bật

### 1. Dành cho Học viên / Thí sinh (User)
- **Đăng ký thông tin thí sinh trước khi làm bài**:
  - Khi bắt đầu làm bài, thí sinh được yêu cầu nhập đầy đủ: **Họ và tên**, **Số điện thoại**, và **Email**.
  - Hệ thống tự động ghi nhớ thông tin trong phiên làm việc, có nút sửa thông tin linh hoạt trên thanh điều hướng và phiếu làm bài.
- **Trang chủ chọn trình độ**: Giao diện đẹp mắt với các cấp độ từ **A1 (Căn bản)**, **A2 (Sơ cấp)**, **B1 (Trung cấp)**, **B2 (Trung cao cấp)** đến **Luyện thi IELTS & TOEIC**.
- **Bốc đề ngẫu nhiên**: Mỗi trình độ chứa nhiều đề thi khác nhau. Khi thí sinh nhấp chọn trình độ, hệ thống sẽ **tự động bốc ngẫu nhiên một đề thi** từ kho đề.
- **Trình phát âm thanh nghe (Listening Audio Player)**:
  - Tích hợp thanh nghe chuyên dụng cho các đề thi có phần nghe (IELTS Listening, TOEIC, bài nghe giao tiếp).
  - Đầy đủ nút: Phát / Tạm dừng, tua lùi 10s (`-10s`), tua tới 10s (`+10s`), chỉnh tốc độ nghe linh hoạt (`0.75x`, `1.0x`, `1.25x`, `1.5x`), thanh trượt âm lượng và thời gian phát.
- **Trình chiếu Slide PowerPoint trực quan**:
  - Màn hình trình chiếu slide độ nét cao, hỗ trợ chuyển slide tới/lui, nhảy đến slide bất kỳ hoặc phóng to toàn màn hình.
  - Hỗ trợ phím tắt bàn phím: <kbd>←</kbd> và <kbd>→</kbd> hoặc phím <kbd>Space</kbd>.
- **Phiếu làm bài đáp án thông minh (Hỗ trợ nhiều dạng câu hỏi)**:
  - **Trắc nghiệm**: Tích chọn nhanh A, B, C, D.
  - **Điền từ vựng (Vocabulary)**: Ô nhập từ vựng chuẩn xác.
  - **Viết cả câu (Sentence)**: Ô nhập cả câu tiếng Anh.
  - Tự động lưu tiến độ, hiển thị câu đã làm/chưa làm.
  - Nút **"Xem Slide câu này"** giúp thí sinh tự động chuyển trình chiếu đến đúng slide chứa câu hỏi tương ứng.
  - Đồng hồ đếm ngược thời gian làm bài với cảnh báo khi sắp hết giờ.
- **Báo cáo kết quả tức thì**:
  - **Hiển thị chính xác số lượng câu đúng** (Ví dụ: `8 / 10 câu đúng`), tỷ lệ chính xác %, điểm số và trạng thái Đạt/Chưa đạt.
  - Bảng đối chiếu chi tiết: Đáp án thí sinh đã chọn/điền vs Đáp án chính xác của từng câu, kèm giải thích ngữ pháp.

### 2. Dành cho Quản trị viên (Admin)
- **Đăng nhập quản trị**: Bảo mật với tài khoản Admin mặc định (`admin` / `admin123`).
- **Tìm kiếm và lọc bài làm của từng học viên theo Tên, Số điện thoại hoặc Email**:
  - Thanh tìm kiếm thông minh: Gõ tên (ví dụ `Trần Thu`), số điện thoại (`0912345678`) hoặc email (`thu@gmail.com`) để tra cứu toàn bộ bài thi của người đó.
  - Bảng bài làm hiển thị rõ thông tin liên hệ: Tên, SĐT, Email, đề thi, số câu đúng và ngày giờ làm bài.
  - Trang chi tiết có nút gọi trực tiếp (`tel:`) và gửi email (`mailto:`) cho thí sinh.
- **Thêm đề thi mới với File PowerPoint (.pptx / .ppt) & File Nghe MP3 (.mp3, .wav)**:
  - Tải lên file PPT/PPTX, hệ thống tự động trích xuất các slide thành hình ảnh trình chiếu chất lượng cao.
  - Tải lên file âm thanh MP3/WAV cho phần nghe (Listening).
  - Chọn trình độ áp dụng (A1, A2, B1...), cài đặt thời gian làm bài và điểm đạt.
- **Cấu hình đáp án cực nhanh & thông minh**:
  - Hỗ trợ nhập nhanh (Bulk Paste) cả trắc nghiệm và từ vựng/câu văn:
    ```
    1. A
    2. B
    3. environment
    4. She arrived on Monday.
    5. center / centre
    ```
  - Tự động nhận diện loại câu hỏi (Trắc nghiệm hoặc Điền từ/câu).
  - Hỗ trợ nhiều đáp án tương đương bằng dấu `/` hoặc `|` (Ví dụ: `center / centre` hoặc `don't / do not`).
  - So khớp thông minh: Không phân biệt hoa/thường, tự động chuẩn hóa khoảng trắng và dấu câu cuối câu.
- **Xem và kiểm tra đáp án của thí sinh (User Submissions)**:
  - Bảng thống kê toàn bộ lượt làm bài với tính năng tìm kiếm theo tên thí sinh, lọc theo trình độ và đề thi.
  - Trang xem chi tiết bài làm: Hiển thị rõ **đáp án thí sinh đã điền**, **đáp án chuẩn của hệ thống**, câu đúng/sai và **ảnh slide trình chiếu tương ứng** của câu hỏi đó.
- **Quản lý danh sách trình độ & đề thi**: Thêm, sửa, xóa trình độ và đề thi linh hoạt.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Cách 1: Chạy nhanh bằng 1 click trên Windows
Nhấp đúp chuột vào file:
```
run.bat
```

### Cách 2: Chạy bằng dòng lệnh Terminal
1. Cài đặt các thư viện cần thiết (nếu chưa cài):
```bash
pip install -r requirements.txt
```

2. Khởi chạy server:
```bash
python app.py
```

3. Mở trình duyệt web và truy cập:
```
http://localhost:5000
```

---

## 🔑 Tài Khoản Quản Trị Viên (Admin) Mặc Định

| Mục | Thông tin |
| :--- | :--- |
| **Đường dẫn đăng nhập** | [http://localhost:5000/admin/login](http://localhost:5000/admin/login) |
| **Tên đăng nhập** | `admin` |
| **Mật khẩu** | `admin123` |

---

## 📂 Cấu Trúc Dự Án

```
phanmentestav/
│
├── app.py                   # File chính xử lý routes web, API chấm điểm & âm thanh
├── models.py                # Mô hình CSDL (User, Level, Test, Question, Submission)
├── ppt_converter.py         # Module chuyển đổi PPTX/PPT sang ảnh slide chất lượng cao
├── seed_data.py             # Script nạp dữ liệu mẫu ban đầu (5 cấp độ & các đề thi PPT)
├── requirements.txt         # Danh sách thư viện Python
├── run.bat                  # Script khởi động nhanh cho Windows
├── english_test.db          # Cơ sở dữ liệu SQLite
│
├── static/
│   ├── css/custom.css       # Hiệu ứng chuyển động & giao diện phiếu trắc nghiệm/điền từ
│   ├── js/
│   │   ├── main.js          # Script tiện ích chung
│   │   └── test_taker.js    # Logic trình chiếu PPT, trình phát MP3, phiếu làm bài
│   └── uploads/tests/       # Thư mục lưu file PPT, file âm thanh MP3 và ảnh slide
│
└── templates/
    ├── base.html            # Khung giao diện chuẩn (Navbar, Footer, Thông báo)
    ├── home.html            # Trang chủ chọn trình độ
    ├── test_taking.html     # Trang làm bài thi (Trình chiếu PPT + Nghe MP3 + Phiếu đáp án)
    ├── test_result.html     # Trang kết quả (Số câu đúng, bảng đối chiếu đáp án)
    └── admin/
        ├── login.html       # Đăng nhập Admin
        ├── dashboard.html   # Bảng điều khiển thống kê tổng quan
        ├── levels.html      # Quản lý các trình độ tiếng Anh
        ├── tests.html       # Danh sách và quản lý các đề thi
        ├── test_new.html    # Thêm đề PPT + File MP3 + Nhập đáp án đa dạng
        ├── test_edit.html   # Chỉnh sửa đề thi, file nghe và đáp án
        ├── submissions.html # Danh sách bài làm của học viên
        └── submission_detail.html # Chi tiết đáp án học viên đã điền & xem slide
```
#   e n g l i s h - t e s t - w e b  
 