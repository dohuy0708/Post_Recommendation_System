# Bước 1: Chọn một base image Python chính thức và ổn định
FROM python:3.10-slim

# Bước 2: Cài đặt các gói hệ thống cần thiết cho việc biên dịch
# build-essential chứa các công cụ như gcc, make... cần thiết để build các thư viện C/C++
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Bước 3: Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Bước 4: Sao chép file requirements trước để tận dụng Docker cache
# Nếu file này không đổi, Docker sẽ không cần chạy lại bước pip install
COPY requirement.txt .

# Bước 5: Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirement.txt

# Bước 6: Sao chép toàn bộ code ứng dụng của bạn vào container
# Dấu "." đầu tiên là thư mục hiện tại trên máy bạn (thư mục gốc dự án)
# Dấu "." thứ hai là thư mục làm việc hiện tại trong container (/app)
COPY . .

# Bước 7: Chạy ứng dụng khi container khởi động
# Lệnh này giống hệt lệnh trong render.yaml cũ
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:10000", "app.main:app"]