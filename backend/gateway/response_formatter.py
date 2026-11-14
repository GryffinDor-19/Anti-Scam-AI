"""
Response Formatter Module: Đóng gói và chuẩn hóa dữ liệu đầu ra 6 trường JSON.
Phụ trách: Mảng 2 - Cổng điều phối & Chuẩn hóa
"""

from typing import Dict, Any, List
from .threat_classifier import classify_threat_level


def format_scam_response(
    raw_ai_data: Dict[str, Any],
    fallback_score: int = 12,
    fallback_tactic: str = "Giao tiếp sinh hoạt thông thường"
) -> Dict[str, Any]:
    """
    Chuẩn hóa kết quả trả về đúng chuẩn 6 trường theo schema mock_response.json:
    1. risk_score (int)
    2. threat_level (str)
    3. detected_tactic (str)
    4. explanation (str)
    5. psychological_traps (list[str])
    6. action_recommendations (list[str])
    """
    raw = raw_ai_data or {}

    try:
        score = int(raw.get("risk_score", fallback_score))
        score = max(0, min(100, score))
    except (ValueError, TypeError):
        score = fallback_score

    calculated_level, _ = classify_threat_level(score)
    threat_level = raw.get("threat_level") or calculated_level
    if threat_level not in ["An toàn", "Đáng ngờ", "Nguy cơ cao"]:
        threat_level = calculated_level

    tactic = raw.get("detected_tactic") or fallback_tactic

    explanation = raw.get("explanation")
    if not explanation or not str(explanation).strip():
        if threat_level == "An toàn":
            explanation = "Không phát hiện dấu hiệu lừa đảo hay bẫy tài chính trong tin nhắn."
        else:
            explanation = "Hệ thống phát hiện kịch bản thao túng tâm lý có dấu hiệu nguy cơ chiếm đoạt tài sản."

    traps = raw.get("psychological_traps")
    if not isinstance(traps, list) or not traps:
        if threat_level == "An toàn":
            traps = ["Không phát hiện dấu hiệu thao túng tâm lý"]
        else:
            traps = ["Đánh vào sự mất cảnh giác hoặc tạo áp lực tâm lý"]

    recommendations = raw.get("action_recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        if threat_level == "An toàn":
            recommendations = [
                "Có thể yên tâm tiếp tục trò chuyện bình thường.",
                "Luôn giữ thói quen bảo mật mã OTP ngân hàng và không chia sẻ cho bất kỳ ai."
            ]
        else:
            recommendations = [
                "Tuyệt đối không chuyển tiền và không bấm vào đường link lạ.",
                "Xác minh trực tiếp qua hotline chính thức của đơn vị hoặc kiểm tra ứng dụng thật.",
                "Chụp ảnh màn hình lưu bằng chứng và phản ánh đến Tổng đài 156 hoặc Hotline A05."
            ]

    return {
        "risk_score": score,
        "threat_level": str(threat_level),
        "detected_tactic": str(tactic),
        "explanation": str(explanation),
        "psychological_traps": [str(t) for t in traps],
        "action_recommendations": [str(r) for r in recommendations]
    }
