# app/services/recommend.py

import pickle
import pandas as pd
import os
import sys  # <<< THÊM VÀO >>>
from typing import List, Dict

# Import lớp từ file chung
from ..model.model_class import HybridRecommender

# Biến toàn cục để giữ model
recommender_instance: HybridRecommender = None
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "..", "model", "recommender.pkl")

def load_recommender():
    global recommender_instance
    print(f"Đang tải model từ: {MODEL_PATH}")
    
    # <<< --- THAY ĐỔI QUAN TRỌNG Ở ĐÂY --- >>>
    # Mẹo để xử lý lỗi pickle 'Can't get attribute on __main__'
    # Gán lớp HybridRecommender đã được import vào module __main__
    # để pickle có thể tìm thấy nó khi tải model được huấn luyện từ một script khác.
    # sys.modules['__main__'].HybridRecommender = HybridRecommender
    # <<< --- KẾT THÚC THAY ĐỔI --- >>>

    try:
        with open(MODEL_PATH, 'rb') as file:
            recommender_instance = pickle.load(file)
        print("Tải model thành công!")
        if recommender_instance and hasattr(recommender_instance, 'post_df'):
            print(f"Model chứa thông tin của {len(recommender_instance.post_df)} bài viết.")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file model tại '{MODEL_PATH}'.")
        recommender_instance = None
    except Exception as e:
        print(f"Lỗi khi tải model: {e}")
        recommender_instance = None


def get_recommendations_for_user(user_id: str, n_recommendations: int = 10) -> List[Dict]:
    if recommender_instance is None:
        print("Lỗi: Model chưa được tải.")
        return []

    # Kiểm tra user có tồn tại trong user_df của model đã tải không
    if user_id not in recommender_instance.user_df['_id'].values:
        print(f"User ID '{user_id}' không tồn tại trong dữ liệu.")
        return []

    # Sử dụng phương thức recommend từ đối tượng model đã tải
    recommended_post_ids = recommender_instance.recommend(user_id, n_recommendations=n_recommendations)

    if not recommended_post_ids:
        return []

    all_posts_info = recommender_instance.post_df
    results_df = all_posts_info[all_posts_info['_id'].isin(recommended_post_ids)][['_id', 'title']]
    ordered_results_df = pd.DataFrame({'_id': recommended_post_ids}).merge(results_df, on='_id', how='left')

    return ordered_results_df.to_dict('records')