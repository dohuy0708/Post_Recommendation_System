FROM python:3.10-slim

# Thêm các gói hỗ trợ build numpy và thư viện C-based khác
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    gcc \
    g++ \
    libatlas-base-dev \
    libffi-dev \
    libpq-dev \
    libssl-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirement.txt .

# Upgrade pip và cài thư viện nền tảng
RUN pip install --no-cache-dir --upgrade pip wheel
RUN pip install --no-cache-dir "numpy<2.0" cython

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:10000", "app.main:app"]
