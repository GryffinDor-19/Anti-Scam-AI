"""
Semantic Analyzer Module (Compatibility Route).
Chuyển tiếp trực tiếp sang backend.engines.semantic_analyzer.
"""

from backend.engines.semantic_analyzer import analyze_scam_content, local_fallback_6_fields

__all__ = ["analyze_scam_content", "local_fallback_6_fields"]
