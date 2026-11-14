"""
Module Ứng Phó Khẩn Cấp: Emergency Manager - Quy trình Giờ Vàng & Hotline cứu nguy 1-chạm.
Phụ trách: Thành viên 3 (Frontend & Cấp cứu khẩn cấp)
"""

from typing import Dict, Any, List


class EmergencyManager:
    """Quản trị danh bạ tổng đài ngân hàng phong tỏa thẻ khẩn cấp và A05"""

    HOTLINES: List[Dict[str, str]] = [
        {"bank": "Vietcombank", "hotline": "1900545413", "desc": "Khóa thẻ khẩn cấp & đóng dịch vụ VCB Digibank"},
        {"bank": "BIDV", "hotline": "19009247", "desc": "Khóa tài khoản và hỗ trợ tra soát giao dịch gian lận"},
        {"bank": "VietinBank", "hotline": "1900558868", "desc": "Khóa thẻ tức thì và chặn giao dịch Internet Banking"},
        {"bank": "Techcombank", "hotline": "1800588822", "desc": "Hỗ trợ bảo mật và khóa khẩn cấp ứng dụng Techcombank"},
        {"bank": "MB Bank", "hotline": "1900545426", "desc": "Khóa App MB Bank và ngừng mọi giao dịch thanh toán"}
    ]

    POLICE_HOTLINE: str = "069.234.8560"  # Cục An ninh mạng A05 (Bộ Công an)
    PORTAL_SPAM: str = "156"  # Tổng đài phản ánh tin nhắn rác & cuộc gọi lừa đảo

    @classmethod
    def get_emergency_payload(cls) -> Dict[str, Any]:
        """Trả về dữ liệu hiển thị cho Banner Cấp Cứu Giờ Vàng trên Streamlit"""
        return {
            "title": "🚨 QUY TRÌNH CỨU NGUY KHẨN CẤP (THỜI ĐIỂM VÀNG 15 PHÚT ĐẦU)",
            "subtitle": "Nếu bạn vừa lỡ chuyển tiền hoặc cung cấp mã OTP cho kẻ lạ, hãy thực hiện ngay 3 bước sau:",
            "checklist": [
                {
                    "step": "BƯỚC 1: KHÓA TÀI KHOẢN & THẺ NGÂN HÀNG NGAY LẬP TỨC",
                    "action": "Gọi ngay hotline ngân hàng của bạn bên dưới hoặc vào ứng dụng bấm 'Khóa thẻ khẩn cấp' để ngăn tiền tiếp tục bị chuyển đi.",
                    "priority": "Khẩn cấp số 1 (Trong 5 phút đầu)",
                    "icon": "⚡"
                },
                {
                    "step": "BƯỚC 2: CHỤP ẢNH MÀN HÌNH LƯU TOÀN BỘ BẰNG CHỨNG",
                    "action": "Lưu lại toàn bộ tin nhắn, số điện thoại, số tài khoản nhận tiền, tên ngân hàng và biên lai giao dịch.",
                    "priority": "Quan trọng",
                    "icon": "📸"
                },
                {
                    "step": "BƯỚC 3: TRÌNH BÁO CƠ QUAN CÔNG AN & TỔNG ĐÀI 156",
                    "action": "Gọi Tổng đài 156 hoặc liên hệ Công an phường/xã gần nhất để làm đơn tố giác tội phạm.",
                    "priority": "Cần thiết",
                    "icon": "🏛️"
                }
            ],
            "hotlines": cls.HOTLINES,
            "police_hotline": cls.POLICE_HOTLINE,
            "spam_hotline": cls.PORTAL_SPAM
        }
