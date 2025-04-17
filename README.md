# Product Description Generator

Ứng dụng web Flask tạo mô tả sản phẩm chi tiết và tối ưu hóa SEO từ hình ảnh bằng OpenAI và Ollama.

## Tính năng

- Tải lên hình ảnh sản phẩm và nhận mô tả được tạo bởi AI
- Sử dụng GPT-4o của OpenAI để phân tích hình ảnh và tạo mô tả ban đầu
- Tăng cường mô tả với mô hình LLaMA 3.2 của Ollama
- Giao diện người dùng hiện đại, đáp ứng

## Thiết lập

### Điều kiện tiên quyết

- Python 3.8+
- Khóa API OpenAI
- Ollama đang chạy cục bộ hoặc có thể truy cập qua API

### Cài đặt

1. Sao chép kho lưu trữ:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Cài đặt các gói phụ thuộc:
   ```
   pip install -r requirements.txt
   ```

4. Tạo tệp `.env` với khóa API của bạn:
   ```
   cp .env.example .env
   ```
   Sau đó chỉnh sửa tệp `.env` để thêm khóa API OpenAI thực tế của bạn.

### Chạy ứng dụng

1. Khởi động máy chủ phát triển Flask:
   ```
   python run.py
   ```

2. Mở trình duyệt web và điều hướng đến:
   ```
   http://127.0.0.1:5000
   ```

## Cấu trúc dự án

```
├── app/                  # Gói ứng dụng
│   ├── __init__.py       # Factory ứng dụng
│   ├── routes.py         # Định nghĩa các route
│   ├── services/         # Logic nghiệp vụ
│   │   ├── __init__.py
│   │   ├── product_description.py  # Xử lý mô tả sản phẩm
│   │   └── prompts/      # Thư mục chứa các prompt mẫu
│   │       ├── __init__.py
│   │       ├── openai_prompts.py   # Prompt cho OpenAI
│   │       └── ollama_prompts.py   # Prompt cho Ollama
│   ├── static/           # Tài sản tĩnh
│   │   ├── css/          # Tệp CSS
│   │   ├── js/           # Tệp JavaScript
│   │   ├── markdown/     # Tài nguyên markdown
│   │   └── uploads/      # Thư mục tải lên hình ảnh
│   └── templates/        # Mẫu HTML
│       ├── index.html    # Trang chính
│       └── markdown.html # Mẫu hiển thị markdown
├── .env                  # Biến môi trường (tạo từ .env.example)
├── .env.example          # Biến môi trường mẫu
├── .cursorrules          # Quy tắc mã hóa cho dự án
├── .gitignore            # Tệp Git ignore
├── requirements.txt      # Các gói phụ thuộc Python
├── README.md             # Tài liệu dự án
└── run.py                # Điểm vào ứng dụng
```

## Sử dụng

1. Tải lên hình ảnh sản phẩm của bạn
2. Nhập yêu cầu mô tả (chi tiết tùy chọn về sản phẩm)
3. Nhấp vào "Tạo mô tả"
4. Xem mô tả sản phẩm được tạo bởi AI

## Quy tắc mã hóa

Dự án tuân theo các quy tắc mã hóa được định nghĩa trong tệp `.cursorrules`, bao gồm:
- Tổ chức mã
- Quy ước đặt tên
- Định dạng mã
- Tích hợp API
- Bảo mật
- Hiệu suất
- Kiểm thử 