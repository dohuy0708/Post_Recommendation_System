# Dockerfile

# Bước 1: Chọn một base image Python chính thức và ổn định
FROM python:3.10-slim-bullseye

# Bước 2: Thiết lập biến môi trường để Python không tạo file .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Bước 3: Cài đặt các gói hệ thống cần thiết tối thiểu
# build-essential đã bao gồm gcc và g++
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Bước 4: Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Bước 5: Nâng cấp pip và sao chép file requirements
RUN pip install --no-cache-dir --upgrade pip
COPY requirement.txt .

# Bước 6: Cài đặt tất cả các thư viện Python
# Cài đặt một lần duy nhất từ file requirements.
# pip sẽ tự xử lý thứ tự phụ thuộc.
RUN pip install --no-cache-dir -r requirement.txt

# Bước 7: Sao chép toàn bộ code ứng dụng của bạn vào container
COPY . .

# Bước 8: Chạy ứng dụng khi container khởi động
# Chạy trên cổng 10000, Render sẽ tự động map ra ngoài
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:10000", "app.main:app"]