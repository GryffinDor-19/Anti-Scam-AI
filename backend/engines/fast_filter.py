"""
Lớp 1: Fast Filter - Bộ lọc phản xạ siêu tốc (<0.05s)
Phụ trách: Thành viên 2 (Dữ liệu & Lọc thô)
"""

import re
import unicodedata
from typing import Dict, Any


class FastFilter:
    def __init__(self):
        self.emergency_keywords = [
            "chuyển tiền để xác minh",
            "chuyển tiền vào tài khoản an toàn",
            "chuyển tiền để phục vụ điều tra",
            "chuyển tiền để tránh bị bắt",
            "cung cấp mã otp",
            "gửi mã otp",
            "đọc mã otp",
            "cung cấp mật khẩu",
            "nộp phí nhận thưởng",
            "đóng phí nhận quà",
            "đóng thuế nhận thưởng",
            "nạp tiền làm nhiệm vụ",
            "ứng tiền để chốt đơn",
            "nạp thêm tiền để hoàn thành nhiệm vụ",
            "nộp phí để rút tiền",
            "đóng thuế để rút tiền",
            "chuyển tiền để giải ngân",
            "phí mở khóa khoản vay",
            "đặt cọc để lấy lại tiền",
            "đóng phí thu hồi tiền"
        ]

        self.emergency_keywords = [self.normalize_text(kw) for kw in self.emergency_keywords]

        self.url_pattern = re.compile(
            r"""https?://[^\s<>"']+|(?<![\w@.-])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}\b(?::\d{1,5})?(?:[/?#][^\s<>"']*)?""",
            re.IGNORECASE
        )

    @staticmethod
    def normalize_text(text: str) -> str:
        """Chuẩn hóa NFC, chữ thường và gom khoảng trắng."""
        text = unicodedata.normalize("NFC", text or "").lower()
        return " ".join(text.split())

    def check(self, text: str) -> Dict[str, Any]:
        """Kiểm tra phản xạ nhanh từ khóa nóng và đường link lạ."""
        if not text or not text.strip():
            return {"is_urgent": False, "matched_keyword": None, "has_link": False}

        normalized = self.normalize_text(text)
        found_kw = next((kw for kw in self.emergency_keywords if kw in normalized), None)
        has_link = bool(self.url_pattern.search(normalized))

        return {
            "is_urgent": found_kw is not None or has_link,
            "matched_keyword": found_kw,
            "has_link": has_link
        }
