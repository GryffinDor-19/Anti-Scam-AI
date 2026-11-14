"""
Compatibility Layer: Tương thích ngược 100% cho mọi import cũ từ modules.*
Tự động ánh xạ sang các mảng kiến trúc mới (engines, emergency, knowledge).
"""

from backend.engines.fast_filter import FastFilter
from backend.engines.rag_case_matcher import RAGCaseMatcher
from backend.engines.semantic_analyzer import analyze_scam_content, local_fallback_6_fields
from backend.engines.fake_bill_detector import FakeBillDetector
from backend.emergency.emergency_manager import EmergencyManager
from backend.knowledge.retriever import find_matching_article, load_knowledge_articles

__all__ = [
    "FastFilter",
    "RAGCaseMatcher",
    "analyze_scam_content",
    "local_fallback_6_fields",
    "FakeBillDetector",
    "EmergencyManager",
    "find_matching_article",
    "load_knowledge_articles"
]
