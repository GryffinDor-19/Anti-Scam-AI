"""
Threat Classifier Module: Phân cấp mức độ nguy hại & Ngưỡng kích hoạt cảnh báo.
Phụ trách: Mảng 2 - Cổng điều phối & Chuẩn hóa (TV1 & TV3)
"""

from typing import Tuple


def classify_threat_level(score: int) -> Tuple[str, str]:
    """
    Quy đổi điểm rủi ro (0 - 100) thành:
    - threat_level: 'An toàn' | 'Đáng ngờ' | 'Nguy cơ cao'
    - status_label: Nhãn hiển thị có icon
    """
    score = max(0, min(100, int(score)))

    if score >= 70:
        return "Nguy cơ cao", "🚨 Nguy cơ cao"
    elif score >= 40:
        return "Đáng ngờ", "⚠️ Đáng ngờ"
    else:
        return "An toàn", "✅ An toàn"


def should_trigger_emergency_alert(score: int) -> bool:
    """Kiểm tra có cần kích hoạt còi báo động khẩn cấp và popup Giờ Vàng hay không"""
    return int(score) >= 85
