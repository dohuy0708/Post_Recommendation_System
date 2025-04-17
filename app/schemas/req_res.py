from pydantic import BaseModel
from typing import List

# Schema để nhận yêu cầu từ frontend
class RecommendRequest(BaseModel):
    user_id: int  # ID của người dùng

# Schema để trả kết quả gợi ý cho frontend
class RecommendResponse(BaseModel):
    user_id: int
    recommendations: List[str]  # Danh sách các anime được gợi ý