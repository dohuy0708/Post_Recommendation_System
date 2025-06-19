# app/model/model_class.py

# File này chỉ dùng để định nghĩa cấu trúc của lớp Recommender
# để có thể được import nhất quán ở cả nơi huấn luyện và nơi phục vụ.

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD

class HybridRecommender:
    """
    Lớp này đóng gói toàn bộ logic cho mô hình gợi ý hybrid.
    """
    def __init__(self, content_weight=0.7):
        if not 0 <= content_weight <= 1:
            raise ValueError("content_weight phải nằm trong khoảng từ 0 đến 1.")
        self.content_weight = content_weight
        self.collaborative_weight = 1 - content_weight
        self.svd_model = None
        self.tfidf_vectorizer = None
        self.post_df = None
        self.user_df = None
        self.view_df = None
        self.cosine_sim = None
        self.post_id_to_idx = None # Ánh xạ từ postId sang index của ma trận

    def fit(self, user_df, post_df, view_df):
        print("\n[BƯỚC 2] Bắt đầu huấn luyện mô hình Hybrid...")
        self.user_df, self.post_df, self.view_df = user_df, post_df, view_df
        
        print("   -> Đang huấn luyện thành phần Content-Based...")
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.post_df['title'])
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        self.post_id_to_idx = pd.Series(self.post_df.index, index=self.post_df['_id']).to_dict()
        print("   -> Huấn luyện Content-Based hoàn tất.")

        print("   -> Đang huấn luyện thành phần Collaborative Filtering...")
        view_df_with_rating = view_df.copy()
        view_df_with_rating['rating'] = 1.0 
        
        valid_users = self.user_df['_id'].unique()
        valid_posts = self.post_df['_id'].unique()
        view_df_with_rating = view_df_with_rating[
            view_df_with_rating['userId'].isin(valid_users) &
            view_df_with_rating['postId'].isin(valid_posts)
        ]

        reader = Reader(rating_scale=(1, 1))
        data = Dataset.load_from_df(view_df_with_rating[['userId', 'postId', 'rating']], reader)
        trainset = data.build_full_trainset()
        
        self.svd_model = SVD(n_factors=50, n_epochs=30, random_state=42, lr_all=0.005, reg_all=0.02)
        self.svd_model.fit(trainset)
        print("   -> Huấn luyện Collaborative Filtering hoàn tất.")
        print("[BƯỚC 2] Huấn luyện toàn bộ mô hình thành công.")


    def _get_content_based_score(self, user_id, candidate_post_id):
        user_viewed_posts = self.view_df[self.view_df['userId'] == user_id]['postId']
        if user_viewed_posts.empty: return 0.0
        candidate_idx = self.post_id_to_idx.get(candidate_post_id)
        if candidate_idx is None: return 0.0
        total_similarity, count = 0, 0
        for viewed_post_id in user_viewed_posts:
            viewed_idx = self.post_id_to_idx.get(viewed_post_id)
            if viewed_idx is not None:
                total_similarity += self.cosine_sim[candidate_idx, viewed_idx]
                count += 1
        return total_similarity / count if count > 0 else 0.0

    def recommend(self, user_id, n_recommendations=10):
        if self.svd_model is None or self.cosine_sim is None:
            raise RuntimeError("Mô hình chưa được huấn luyện.")
        user_viewed_posts = set(self.view_df[self.view_df['userId'] == user_id]['postId'])
        all_posts = self.post_df['_id'].unique()
        scores = {}
        for post_id in all_posts:
            if post_id not in user_viewed_posts:
                collab_score = self.svd_model.predict(uid=user_id, iid=post_id).est
                content_score = self._get_content_based_score(user_id, post_id)
                hybrid_score = (self.content_weight * content_score) + (self.collaborative_weight * collab_score)
                scores[post_id] = hybrid_score
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        recommended_post_ids = [post_id for post_id, score in sorted_scores[:n_recommendations]]
        return recommended_post_ids