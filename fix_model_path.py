# fix_model_path.py
import pickle
import sys
import os

# Thêm thư mục gốc vào sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

# Import lớp từ đường dẫn đúng
from app.model.model_class import HybridRecommender

# Đường dẫn đến model cũ và model mới
OLD_MODEL_PATH = os.path.join(project_root, 'app', 'model', 'recommender.pkl')
NEW_MODEL_PATH = os.path.join(project_root, 'app', 'model', 'recommender_fixed.pkl')

def fix_pickle_file():
    print(f"Đang đọc file model cũ từ: {OLD_MODEL_PATH}")
    
    # Áp dụng mẹo để tải file cũ
    sys.modules['__main__'].HybridRecommender = HybridRecommender
    
    try:
        with open(OLD_MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Tải model cũ thành công.")
        
        # Lưu lại model, lần này pickle sẽ sử dụng đường dẫn import đúng
        print(f"Đang lưu model đã sửa vào: {NEW_MODEL_PATH}")
        with open(NEW_MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print("Hoàn tất! Bạn có thể đổi tên 'recommender_fixed.pkl' thành 'recommender.pkl' và sử dụng.")
            
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

if __name__ == "__main__":
    fix_pickle_file()