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

        # BƯỚC 3: PHÂN TÍCH NGỮ NGHĨA & CHẤM ĐIỂM RỦI RO (Semantic Analyzer LLM)
        ai_result = analyze_scam_content(
            user_text=clean_text,
            rag_article=matched_article,
            api_key=api_key
        )

        # BƯỚC 4: ĐÓNG GÓI CHUẨN HÓA 6 TRƯỜNG DỮ LIỆU
        return format_scam_response(ai_result)


# Khởi tạo singleton instance tiện dụng
pipeline_instance = AntiScamPipeline()


def run_pipeline(user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Hàm tiện ích gọi nhanh pipeline"""
    return pipeline_instance.execute(user_text, api_key=api_key)
