"""
AntiScam Pipeline: Nhạc trưởng điều phối chuỗi 3 lớp phòng thủ AI.
Phụ trách: Mảng 2 - Cổng điều phối & Chuẩn hóa (TV1)
"""

import os
import sys
from typing import Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

for p in [CURRENT_DIR, BACKEND_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 1. Nạp Lớp 1: Fast Filter (TV2)
try:
    from modules.fast_filter import FastFilter
except ImportError:
    try:
        from backend.modules.fast_filter import FastFilter
    except ImportError:
        FastFilter = None

# 2. Nạp Lớp 2: Knowledge Retriever (TV2)
try:
    from knowledge.retriever import find_matching_article
except ImportError:
    from backend.knowledge.retriever import find_matching_article

# 3. Nạp Lớp 3: Semantic Analyzer (TV1 - Gemini 3.8 / 4)
try:
    from modules.semantic_analyzer import analyze_scam_content
except ImportError:
    from backend.modules.semantic_analyzer import analyze_scam_content

# 4. Nạp bộ chuẩn hóa Response Formatter
from .response_formatter import format_scam_response


class AntiScamPipeline:
    """
    Chuỗi xử lý 3 lớp phòng thủ liên hoàn:
    Lớp 1: Fast Filter (<0.05s) - Lọc nhanh từ khóa nóng & link lạ
    Lớp 2: RAG Retriever - Bốc bài báo chính thống từ Cục ATTT
    Lớp 3: Semantic LLM - Gemini 3.8 Flash & Gemini 4 bóc bẫy tâm lý chuyên sâu
    """

    def __init__(self):
        self.fast_filter = FastFilter() if FastFilter else None

    def execute(self, user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Thực thi toàn bộ chuỗi phân tích 3 lớp và đóng gói kết quả chuẩn 6 trường"""
        clean_text = (user_text or "").strip()
        if not clean_text:
            return format_scam_response({
                "risk_score": 0,
                "threat_level": "An toàn",
                "detected_tactic": "Không có nội dung",
                "explanation": "Vui lòng nhập nội dung cần kiểm tra.",
                "psychological_traps": ["Không phát hiện dấu hiệu thao túng tâm lý"],
                "action_recommendations": ["Nhập nội dung tin nhắn hoặc đường link nghi vấn để thẩm định."]
            })

        # BƯỚC 1: LỚP LỌC NHANH (Fast Filter)
        filter_meta = {}
        if self.fast_filter:
            try:
                filter_meta = self.fast_filter.check(clean_text)
            except Exception:
                filter_meta = {}

        # BƯỚC 2: ĐỐI SOÁT BÀI BÁO CHÍNH THỐNG (RAG Retriever)
        matched_article = find_matching_article(clean_text)

        # BƯỚC 3: PHÂN TÍCH NGỮ NGHĨA & CHẤM ĐIỂM RỦI RO
        ai_result = analyze_scam_content(
            user_text=clean_text,
            rag_article=matched_article,
            api_key=api_key
        )

        # BƯỚC 4: ĐÓNG GÓI CHUẨN HÓA 6 TRƯỜNG DỮ LIỆU
        final_response = format_scam_response(ai_result)
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # BƯỚC 5 (BỌC THÉP): TỰ ĐỘNG HỌC MỌI THỨ CHƯA BIẾT (OMNI-LEARNING)
        # ---------------------------------------------------------
        if not matched_article:
            try:
                import json
                import os
                
                # 1. Tự động mò đường dẫn tuyệt đối (Chống lỗi thiếu biến BACKEND_DIR)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(current_dir)
                data_dir = os.path.join(backend_dir, "data")
                knowledge_path = os.path.join(data_dir, "scam_knowledge.json")
                
                # 2. Tự động tạo thư mục 'data' nếu chưa có (Chống lỗi FileNotFoundError)
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                # 3. Đọc dữ liệu cũ
                db = []
                if os.path.exists(knowledge_path):
                    with open(knowledge_path, "r", encoding="utf-8") as f:
                        try:
                            db = json.load(f)
                        except Exception:
                            pass
                
                # 4. Gắn nhãn
                is_scam = final_response.get("risk_score", 0) >= 50
                prefix = "🚨 Mẫu lừa đảo" if is_scam else "✅ Mẫu an toàn"
                
                # Lấy text an toàn (nếu bạn dùng 'user_text' thay vì 'clean_text' ở trên)
                text_to_extract = locals().get('clean_text', locals().get('user_text', ''))
                
                new_item = {
                    "id": len(db) + 1,
                    "title": f"{prefix}: {final_response.get('detected_tactic', 'Phân tích mới')}",
                    "source": "Hệ thống tự học toàn diện (Omni-Learn)",
                    "url": "",
                    "category_name": final_response.get('detected_tactic', 'Giao tiếp thông thường'),
                    "summary": final_response.get('explanation', ''),
                    "keywords": [w for w in text_to_extract.lower().split() if len(w) > 3][:8]
                }
                
                db.append(new_item)
                
                # 5. Ghi file JSON
                with open(knowledge_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=4)
                
                # In thông báo thành công ra Terminal để bạn dễ theo dõi
                print(f"\n[AUTO-LEARN] ✅ Đã học kịch bản mới và lưu vào: {knowledge_path}\n")
                    
            except Exception as e:
                # THAY VÌ GIẤU LỖI (PASS), BÂY GIỜ HỆ THỐNG SẼ HÉT LÊN NẾU CÓ LỖI
                print(f"\n[AUTO-LEARN] ❌ LỖI LƯU DATA: {e}\n")
        # ---------------------------------------------------------
        # BƯỚC 6: TRẢ KẾT QUẢ VỀ CHO WEB (Dòng này cực kỳ quan trọng, đừng để mất nhé!)
        return final_response

# Khởi tạo singleton instance tiện dụng
pipeline_instance = AntiScamPipeline()


def run_pipeline(user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Hàm tiện ích gọi nhanh pipeline"""
    return pipeline_instance.execute(user_text, api_key=api_key)
