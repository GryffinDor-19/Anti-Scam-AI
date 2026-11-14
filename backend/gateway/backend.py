"""
Backend API Gateway: Điểm đón tiếp và phân phối yêu cầu duy nhất cho Frontend.
Phụ trách: Mảng 2 - Cổng điều phối & Chuẩn hóa
"""

from typing import Dict, Any, Optional
from .pipeline import run_pipeline


def analyze_scam(user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Cổng API chính tiếp nhận tin nhắn từ Web Streamlit:
    - Tiếp nhận text và api_key (nếu người dùng nhập trên giao diện)
    - Điều phối qua chuỗi Pipeline 3 lớp
    - Đảm bảo trả về đúng chuẩn 6 trường theo mock_response.json
    """
    return run_pipeline(user_text, api_key=api_key)
