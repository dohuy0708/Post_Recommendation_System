# CELL 2: HUẤN LUYỆN, ĐÁNH GIÁ VÀ LƯU MÔ HÌNH (CẬP NHẬT)
# Chạy cell này SAU KHI đã khởi động lại runtime.

# --- 1. Import các thư viện cần thiết ---
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD

import warnings

warnings.filterwarnings('ignore')
print("Đã import các thư viện thành công.")

# --- 2. Định nghĩa hàm tải và tiền xử lý dữ liệu ---
def load_and_preprocess_data(user_path, post_path, view_path):
    """
    Hàm này tải dữ liệu từ các file CSV và thực hiện các bước tiền xử lý.
    """
    print(f"\n[BƯỚC 1] Đang tải và tiền xử lý dữ liệu...")
    try:
        user_df = pd.read_csv(user_path)
        post_df = pd.read_csv(post_path)
        view_df = pd.read_csv(view_path)
        print("Tải dữ liệu từ file CSV thành công.")
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file '{e.filename}'. Hãy chắc chắn rằng bạn đã tải file lên Colab.")
        return None, None, None

    # Xóa các dòng có giá trị null ở các cột quan trọng
    view_df.dropna(subset=['userId', 'postId'], inplace=True)
    post_df.dropna(subset=['_id', 'title'], inplace=True)
    user_df.dropna(subset=['_id'], inplace=True)
    
    # Điền giá trị rỗng cho cột title bằng một chuỗi trống
    post_df['title'] = post_df['title'].fillna('')

    # Đảm bảo các ID đều là kiểu chuỗi (string) để khớp nhau
    user_df['_id'] = user_df['_id'].astype(str)
    post_df['_id'] = post_df['_id'].astype(str)
    view_df['userId'] = view_df['userId'].astype(str)
    view_df['postId'] = view_df['postId'].astype(str)

    print("Tiền xử lý dữ liệu hoàn tất.")
    return user_df, post_df, view_df

# --- 3. Định nghĩa lớp mô hình Hybrid Recommender ---
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
        
        # --- 2.1 Huấn luyện Content-Based ---
        print("   -> Đang huấn luyện thành phần Content-Based...")
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=2) # Loại bỏ các từ quá hiếm
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.post_df['title'])
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        # Tạo ánh xạ từ _id của post sang index (vị trí) trong post_df
        self.post_id_to_idx = pd.Series(self.post_df.index, index=self.post_df['_id']).to_dict()
        print("   -> Huấn luyện Content-Based hoàn tất.")

        # --- 2.2 Huấn luyện Collaborative Filtering ---
        print("   -> Đang huấn luyện thành phần Collaborative Filtering...")
        # Tạo cột 'rating' với giá trị là 1.0 cho mọi lượt xem
        view_df_with_rating = view_df.copy()
        view_df_with_rating['rating'] = 1.0 
        
        # Surprise chỉ chấp nhận các user/item có trong tập huấn luyện
        # Đảm bảo các view này có user và post tồn tại trong df chính
        valid_users = self.user_df['_id'].unique()
        valid_posts = self.post_df['_id'].unique()
        view_df_with_rating = view_df_with_rating[
            view_df_with_rating['userId'].isin(valid_users) &
            view_df_with_rating['postId'].isin(valid_posts)
        ]

        reader = Reader(rating_scale=(1, 1)) # Thang điểm rating chỉ là 1
        data = Dataset.load_from_df(view_df_with_rating[['userId', 'postId', 'rating']], reader)
        trainset = data.build_full_trainset()
        
        self.svd_model = SVD(n_factors=50, n_epochs=30, random_state=42, lr_all=0.005, reg_all=0.02)
        self.svd_model.fit(trainset)
        print("   -> Huấn luyện Collaborative Filtering hoàn tất.")
        print("[BƯỚC 2] Huấn luyện toàn bộ mô hình thành công.")


    def _get_content_based_score(self, user_id, candidate_post_id):
        # Lấy các bài viết người dùng đã xem
        user_viewed_posts = self.view_df[self.view_df['userId'] == user_id]['postId']
        if user_viewed_posts.empty: return 0.0

        # Lấy index của bài viết ứng viên
        candidate_idx = self.post_id_to_idx.get(candidate_post_id)
        if candidate_idx is None: return 0.0

        total_similarity, count = 0, 0
        for viewed_post_id in user_viewed_posts:
            viewed_idx = self.post_id_to_idx.get(viewed_post_id)
            if viewed_idx is not None:
                # Lấy độ tương đồng từ ma trận cosine
                total_similarity += self.cosine_sim[candidate_idx, viewed_idx]
                count += 1
        return total_similarity / count if count > 0 else 0.0

    def recommend(self, user_id, n_recommendations=10):
        if self.svd_model is None or self.cosine_sim is None:
            raise RuntimeError("Mô hình chưa được huấn luyện. Hãy gọi hàm .fit() trước.")

        # Lấy danh sách các bài post người dùng đã xem để loại trừ
        user_viewed_posts = set(self.view_df[self.view_df['userId'] == user_id]['postId'])
        
        # Lấy tất cả các bài post có thể gợi ý
        all_posts = self.post_df['_id'].unique()

        scores = {}
        for post_id in all_posts:
            if post_id not in user_viewed_posts:
                # Tính điểm collaborative
                collab_score = self.svd_model.predict(uid=user_id, iid=post_id).est
                
                # Tính điểm content-based
                content_score = self._get_content_based_score(user_id, post_id)
                
                # Kết hợp điểm
                hybrid_score = (self.content_weight * content_score) + (self.collaborative_weight * collab_score)
                scores[post_id] = hybrid_score

        # Sắp xếp các bài post theo điểm hybrid giảm dần
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        # Lấy top N bài post
        recommended_post_ids = [post_id for post_id, score in sorted_scores[:n_recommendations]]
        return recommended_post_ids

# --- 4. Chạy quy trình chính ---

# Đường dẫn tới các file dữ liệu trên Colab
USER_CSV_PATH = 'User.csv'
POST_CSV_PATH = 'Post.csv'
VIEW_CSV_PATH = 'View.csv'

# Tải và xử lý dữ liệu
user_df, post_df, view_df = load_and_preprocess_data(USER_CSV_PATH, POST_CSV_PATH, VIEW_CSV_PATH)

if user_df is not None and post_df is not None and view_df is not None:
    # Khởi tạo và huấn luyện mô hình với trọng số 0.7 cho Content-Based
    recommender = HybridRecommender(content_weight=0.7)
    recommender.fit(user_df, post_df, view_df)

    # --- 5. Đánh giá định tính (Thử nghiệm với một số user) ---
    print("\n[BƯỚC 3] Đánh giá định tính - Gợi ý thử nghiệm...")
    test_user_id = "68011e392ab2615d4649dc94" # User "LewyHoang"
    
    if test_user_id in recommender.user_df['_id'].values:
        print("-" * 50)
        # In ra các bài user này đã xem
        viewed = recommender.view_df[recommender.view_df['userId'] == test_user_id]['postId']
        print(f"User '{test_user_id}' đã xem các bài có chủ đề Lịch sử và Âm nhạc:")
        print(post_df[post_df['_id'].isin(viewed)][['title', 'topicId']])
        
        # Lấy gợi ý
        # <<< --- THAY ĐỔI Ở ĐÂY --- >>>
        recommendations = recommender.recommend(test_user_id, n_recommendations=10)
        print(f"\n>> 10 gợi ý HÀNG ĐẦU cho user '{test_user_id}':") # <<< --- VÀ THAY ĐỔI Ở ĐÂY --- >>>
        recommended_posts_info = post_df[post_df['_id'].isin(recommendations)][['_id', 'title', 'topicId']]
        print(recommended_posts_info)
        print("-" * 50)
    else:
        print(f"\n>> Không tìm thấy user '{test_user_id}' trong dữ liệu.")


    # --- 6. Lưu mô hình và tải về ---
    print("\n[BƯỚC 4] Đang lưu mô hình...")
    MODEL_PATH = 'recommender.pkl'
    try:
        with open(MODEL_PATH, 'wb') as file:
            pickle.dump(recommender, file)
        print(f"Mô hình đã được lưu thành công vào file: '{MODEL_PATH}'")
        
        print(f"Đang chuẩn bị để tải file '{MODEL_PATH}' về máy của bạn...")
        files.download(MODEL_PATH)
        print("Tải file hoàn tất!")
        
    except Exception as e:
        print(f"Lỗi khi lưu hoặc tải mô hình: {e}")

else:
    print("\nKhông thể huấn luyện mô hình do lỗi tải hoặc tiền xử lý dữ liệu.")