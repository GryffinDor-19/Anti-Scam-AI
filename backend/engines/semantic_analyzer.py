"""
Lớp 3: Semantic Analyzer Coordinator.
Phụ trách: Thành viên 1
Kết nối: llm_analyzer.py (Gemini 3.8 / 4) và dynamic_scorer.py (Multi-factor scoring).
"""

import os
from typing import Dict, Any, Optional
from .dynamic_scorer import calculate_dynamic_risk
from .llm_analyzer import call_gemini_semantic_analysis


def local_fallback_6_fields(user_text: str, rag_article: Optional[dict] = None) -> Dict[str, Any]:
    """Hàm tính điểm đa tiêu chí động phục vụ tương thích ngược."""
    return calculate_dynamic_risk(user_text, rag_article)


def analyze_scam_content(user_text: str, rag_article: Optional[dict] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Hàm phân tích chính: Ưu tiên Gemini 3.8 / 4, tự động kích hoạt dynamic scorer nếu chưa có key."""
    active_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    if active_key and active_key.strip() and "YOUR_API_KEY" not in active_key and "API KEY" not in active_key:
        rag_context = "Không có bài báo đối chiếu trực tiếp."
        if rag_article:
            rag_context = f"Tiêu đề: {rag_article.get('title')} ({rag_article.get('source')}) | Thủ đoạn: {rag_article.get('category_name')} | Tóm tắt: {rag_article.get('summary')}"

        llm_result = call_gemini_semantic_analysis(user_text, rag_context, active_key)
        if llm_result:
            return llm_result

    return calculate_dynamic_risk(user_text, rag_article)
