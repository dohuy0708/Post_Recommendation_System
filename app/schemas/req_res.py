# app/schemas/req_res.py

from pydantic import BaseModel, Field
from typing import List

# Định nghĩa cấu trúc của một bài viết được gợi ý
class PostRecommendation(BaseModel):
    id: str = Field(..., alias='_id', description="ID của bài viết")
    title: str = Field(..., description="Tiêu đề của bài viết")

    # Cấu hình để Pydantic có thể làm việc với các đối tượng Python
    # và cho phép sử dụng alias `_id`
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Mặc dù không có request body, chúng ta có thể định nghĩa
# một lớp response để làm rõ đầu ra là một danh sách các PostRecommendation
# Tuy nhiên, trong route, ta sẽ dùng List[PostRecommendation] trực tiếp.