# app/main.py

from fastapi import FastAPI
from .api import route
from .services import recommend

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Post Recommendation API",
    description="Một API đơn giản để gợi ý bài viết cho người dùng.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """
    Hành động được thực hiện khi ứng dụng khởi động.
    Tải model vào bộ nhớ.
    """
    recommend.load_recommender()

# Bao gồm các routes từ file route.py
app.include_router(route.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint gốc để kiểm tra API có hoạt động không.
    """
    return {"message": "Chào mừng đến với API Gợi ý Bài viết!"}