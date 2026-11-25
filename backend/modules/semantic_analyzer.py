"""
Semantic Analyzer Module (Compatibility Route).
Tự động chuyển tiếp 100% sang backend.engines.semantic_analyzer.
"""

from backend.engines.semantic_analyzer import (
    analyze_scam_content,
    local_fallback_6_fields,
    fetch_live_url_preview,
    get_gemini_client,
    ai_error_response
)

__all__ = [
    "analyze_scam_content",
    "local_fallback_6_fields",
    "fetch_live_url_preview",
    "get_gemini_client",
    "ai_error_response"
]
