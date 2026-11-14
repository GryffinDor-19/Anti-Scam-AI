"""
Backend Main Entrypoint & API Facade.
Đóng vai trò cầu nối tương thích ngược 100% cho Frontend và các script kiểm thử.
Tự động chuyển tiếp yêu cầu đến Gateway Pipeline 3 lớp.
"""

import os
import sys
from typing import Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

for p in [CURRENT_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Nạp các hàm nghiệp vụ từ gateway và knowledge
from gateway.backend import analyze_scam
from gateway.threat_classifier import classify_threat_level
from gateway.response_formatter import format_scam_response
from gateway.pipeline import run_pipeline, AntiScamPipeline
from knowledge.retriever import find_matching_article, load_knowledge_articles

# Tương thích ngược với các lệnh gọi cũ
__all__ = [
    "analyze_scam",
    "find_matching_article",
    "load_knowledge_articles",
    "classify_threat_level",
    "format_scam_response",
    "run_pipeline",
    "AntiScamPipeline"
]

if __name__ == "__main__":
    from gateway.cli_test import run_cli
    run_cli()
