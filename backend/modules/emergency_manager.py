"""
MODULE CẤP CỨU THỜI ĐIỂM VÀNG (EMERGENCY MANAGER)
Phụ trách: Thành viên 3 (Frontend & UX)
Chức năng: Cung cấp danh bạ Hotline khẩn cấp ngân hàng và Checklist 3 bước cứu tiền tức thì.
"""

from typing import Dict, List, Any


class EmergencyManager:
    """Quản lý các kịch bản phản ứng nhanh trong thời điểm vàng khi nạn nhân bị lừa."""

    BANK_HOTLINES = [
        {"bank": "Vietcombank", "hotline": "1900545413", "desc": "Bấm phím 1 để khóa thẻ khẩn cấp"},
        {"bank": "Techcombank", "hotline": "1800588822", "desc": "Tổng đài 24/7 khóa tài khoản tức thì"},
        {"bank": "MB Bank", "hotline": "1900545426", "desc": "Hỗ trợ phong tỏa app và thẻ ngay lập tức"},
        {"bank": "VietinBank", "hotline": "1900558868", "desc": "Khóa dịch vụ ngân hàng điện tử khẩn"},
        {"bank": "BIDV", "hotline": "19009247", "desc": "Hỗ trợ khách hàng và xử lý gian lận 24/7"},
        {"bank": "VPBank", "hotline": "1900545415", "desc": "Tự động khóa thẻ qua tổng đài IVR"},
        {"bank": "Agribank", "hotline": "1900558818", "desc": "Trung tâm chăm sóc khách hàng khẩn cấp"},
    ]

    EMERGENCY_CHECKLIST = [
        {
            "step": "BƯỚC 1: CẮT ĐỨT KẾT NỐI NGAY LẬP TỨC",
            "icon": "✈️",
            "action": "Nếu vừa bấm vào link lạ hoặc tải file `.apk`: Hãy BẬT NGAY CHẾ ĐỘ MÁY BAY (Airplane Mode) hoặc TẮT NGUỒN ĐIỆN THOẠI để ngắt kết nối mạng. Kẻ gian sẽ không thể can thiệp vào máy để đọc mã OTP ngân hàng.",
            "priority": "Khẩn cấp nhất trong 60 giây đầu"
        },
        {
            "step": "BƯỚC 2: GỌI TỔNG ĐÀI NGÂN HÀNG PHONG TỎA DÒNG TIỀN",
            "icon": "📞",
            "action": "Bấm gọi ngay cho hotline ngân hàng của bạn bên dưới. Nói đúng 1 câu với tổng đài viên: 'Tôi vừa bị lừa đảo chuyển tiền/lộ tài khoản, yêu cầu khóa thẻ và tạm dừng mọi giao dịch khẩn cấp!'.",
            "priority": "Thời điểm vàng: Dưới 15 phút"
        },
        {
            "step": "BƯỚC 3: CHỤP MÀN HÌNH LƯU GIỮ 3 BẰNG CHỨNG",
            "icon": "📸",
            "action": "Trước khi kẻ gian kịp thu hồi hoặc xóa đoạn chat, hãy chụp ngay: (1) Số tài khoản và tên người nhận tiền, (2) Mã giao dịch chuyển khoản ngân hàng, (3) Toàn bộ tin nhắn đe dọa hoặc dụ dỗ.",
            "priority": "Dùng để nộp đơn tố giác cho Cơ quan Công an"
        }
    ]

    @classmethod
    def get_emergency_payload(cls) -> Dict[str, Any]:
        return {
            "title": "🚨 QUY TRÌNH CẤP CỨU THỜI ĐIỂM VÀNG (DƯỚI 15 PHÚT)",
            "subtitle": "Bình tĩnh! Lược bỏ lý thuyết, hãy làm đúng theo 3 bước sau để bảo toàn tài sản:",
            "checklist": cls.EMERGENCY_CHECKLIST,
            "hotlines": cls.BANK_HOTLINES,
            "police_hotline": "069.234.8560 (Cục An ninh mạng A05 - Bộ Công an)"
        }
