from fastapi import APIRouter
from app.services.recommend import get_recommendations
from app.schemas.req_res import RecommendRequest, RecommendResponse

router = APIRouter()

@router.post("/recommend", response_model=RecommendResponse)
def recommend_anime(req: RecommendRequest):
    # Gọi hàm gợi ý anime dựa trên user_id
    recommendations = get_recommendations(req.user_id)
    return RecommendResponse(user_id=req.user_id, recommendations=recommendations)
