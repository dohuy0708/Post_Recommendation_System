# Bước 1: Chọn một base image Python chính thức và ổn định
FROM python:3.10-slim

# Bước 2: Cài đặt các gói hệ thống cần thiết cho việc biên dịch
# build-essential chứa các công cụ như gcc, make...
# git là cần thiết nếu requirement.txt có link git
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git

# Bước 3: Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Bước 4: Sao chép file requirements
COPY requirement.txt .

# === BƯỚC 5: THAY ĐỔI QUAN TRỌNG NHẤT ===
# Cài đặt các thư viện cần biên dịch trước tiên.
# Điều này giúp đảm bảo chúng được cài đặt đúng cách trước khi các thư viện khác phụ thuộc vào chúng.
# Thêm --no-cache-dir để giảm kích thước image.
# Nâng cấp pip và cài đặt wheel để hỗ trợ build tốt hơn.
RUN pip install --no-cache-dir --upgrade pip wheel
RUN pip install --no-cache-dir "numpy<2.0" cython
RUN pip install --no-cache-dir -r requirement.txt

# Bước 6: Sao chép toàn bộ code ứng dụng của bạn vào container
COPY . .

# Bước 7: Chạy ứng dụng khi container khởi động
# Chạy trên cổng 10000, Render sẽ tự động map ra ngoài
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:10000", "app.main:app"]