"""
Knowledge Retriever Module: Truy vấn tri thức bài báo cảnh báo từ Cục ATTT.
Phụ trách: Mảng 4 - Kho tri thức & Dữ liệu (TV2)
"""

import os
import json
from typing import Optional, Dict, Any, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KNOWLEDGE_PATH = os.path.join(CURRENT_DIR, "data", "scam_knowledge.json")
if not os.path.exists(DEFAULT_KNOWLEDGE_PATH):
    # Fallback to backend/data/scam_knowledge.json
    backend_dir = os.path.dirname(CURRENT_DIR)
    DEFAULT_KNOWLEDGE_PATH = os.path.join(backend_dir, "data", "scam_knowledge.json")


def load_knowledge_articles(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Đọc danh sách 20 bài báo chính thống từ file JSON."""
    target_path = path or DEFAULT_KNOWLEDGE_PATH
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def find_matching_article(user_text: str, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Thuật toán so khớp từ khóa và ngữ nghĩa bốc bài báo tương đồng nhất.
    Chỉ trả về bài báo nếu đạt ngưỡng khớp từ khóa >= 2 điểm.
    """
    articles = load_knowledge_articles(path)
    if not articles or not user_text:
        return None

    text_lower = user_text.lower()
    best_article = None
    max_score = 0

    for article in articles:
        score = 0
        for kw in article.get("keywords", []):
            kw_lower = kw.lower()
            if kw_lower in text_lower:
                score += 3  # Khớp cả cụm từ khóa ưu tiên
            else:
                for word in kw_lower.split():
                    if len(word) >= 4 and word in text_lower:
                        score += 1  # Khớp từ đơn có ý nghĩa

        if score > max_score:
            max_score = score
            best_article = article

    return best_article if max_score >= 2 else None
