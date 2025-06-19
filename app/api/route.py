# app/api/route.py

from fastapi import APIRouter, HTTPException, Path
from typing import List
from ..services import recommend
from ..schemas import req_res

router = APIRouter(
    prefix="/api",
    tags=["Recommendation"]
)

@router.get(
    "/recommend/{user_id}",
    response_model=List[req_res.PostRecommendation],
    summary="Get post recommendations for a user",
    description="Trả về danh sách 10 bài viết được gợi ý cho một user_id cụ thể."
)
def recommend_posts(
    user_id: str = Path(..., description="ID của người dùng cần được gợi ý")
):
    """
    Endpoint để lấy gợi ý bài viết.
    - **user_id**: ID của người dùng.
    - **Returns**: Một danh sách các bài viết, mỗi bài gồm `_id` và `title`.
    """
    recommendations = recommend.get_recommendations_for_user(user_id=user_id, n_recommendations=10)

    if not recommendations:
        # Nếu không có gợi ý (có thể do user không tồn tại hoặc không có đủ dữ liệu)
        # trả về lỗi 404 Not Found.
        raise HTTPException(
            status_code=404,
            detail=f"Không thể tạo gợi ý cho User ID '{user_id}'. User có thể không tồn tại hoặc chưa có tương tác."
        )

    return recommendations