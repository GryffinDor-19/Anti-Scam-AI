"""
Dynamic Scorer Module: Thuật toán chấm điểm rủi ro đa tiêu chí động (Multi-Factor Scoring).
Phân tích sắc thái ngôn từ, bẫy uy quyền, ép thời gian, link lạ, teencode / không dấu.
"""

import re
import unicodedata
from typing import Dict, Any, Optional


def remove_diacritics(input_str: str) -> str:
    """Loại bỏ dấu tiếng Việt để xử lý teencode và tin nhắn không dấu."""
    nfkd = unicodedata.normalize('NFD', input_str or "")
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def calculate_dynamic_risk(user_text: str, rag_article: Optional[dict] = None) -> Dict[str, Any]:
    """Tính toán Scam Score (0 - 100) dựa trên 5 chiều phân tích hành vi và tâm lý."""
    text_lower = (user_text or "").lower()
    text_unaccented = remove_diacritics(text_lower)
    traps = []
    tactic = rag_article["category_name"] if rag_article else "Giao tiếp sinh hoạt thông thường"
    score = 12

    # 1. BẪY UY QUYỀN & ĐE DỌA CÔNG QUYỀN (+18 đến +35 điểm)
    authority_kw = [
        "công an", "vneid", "tòa án", "cảnh sát", "viện kiểm sát", "bộ công an",
        "csgt", "lệnh bắt", "phạt nguội", "rửa tiền", "khóa thẻ", "khóa cccd",
        "phong tỏa", "bị khởi tố", "định danh điện tử", "cổng dịch vụ công"
    ]
    auth_matches = [
        kw for kw in authority_kw
        if kw in text_lower or remove_diacritics(kw) in text_unaccented
    ]
    if auth_matches:
        score += min(35, 18 + len(auth_matches) * 5)
        traps.append("Bẫy Uy Quyền / Sợ Hãi: Mạo danh cơ quan nhà nước đe dọa bắt giữ hoặc dọa khóa tài khoản/CCCD")
        if not rag_article:
            tactic = "Giả Danh Cơ Quan Công Quyền & Dịch Vụ Công"

    # 2. BẪY CẤP BÁCH & ÉP THỜI GIAN (+14 đến +25 điểm)
    urgency_kw = [
        "15 phút", "24 giờ", "trong ngày", "khẩn cấp", "gấp", "ngay lập tức",
        "khóa ngay", "nếu không sẽ", "hết hạn", "nhanh chóng", "trễ hạn", "tức thì"
    ]
    urg_matches = [
        kw for kw in urgency_kw
        if kw in text_lower or remove_diacritics(kw) in text_unaccented
    ]
    if urg_matches:
        score += min(25, 14 + len(urg_matches) * 4)
        traps.append("Bẫy Ép Thời Gian: Giới hạn thời gian gấp gáp ép nạn nhân hoảng loạn hành động mà không kịp kiểm chứng")

    # 3. BẪY TÀI CHÍNH, CHUYỂN TIỀN, MÃ OTP & HOA HỒNG (+16 đến +30 điểm)
    finance_kw = [
        "chuyển tiền", "tài khoản an toàn", "mã otp", "mật khẩu", "cộng tác viên",
        "hoa hồng", "nạp cọc", "nhiệm vụ", "shopee", "rút tiền", "trúng thưởng",
        "nhận quà", "tiền thưởng", "hoàn tiền", "chốt đơn", "nạp tiền"
    ]
    fin_matches = [
        kw for kw in finance_kw
        if kw in text_lower or remove_diacritics(kw) in text_unaccented
    ]
    if fin_matches:
        score += min(30, 16 + len(fin_matches) * 4)
        if any(k in text_lower or remove_diacritics(k) in text_unaccented for k in ["hoa hồng", "nhiệm vụ", "cộng tác viên", "trúng thưởng", "chốt đơn"]):
            traps.append("Bẫy Hám Lợi: Mồi chài hoa hồng cao hoặc nhận tiền thưởng làm nhiệm vụ ảo")
            if not rag_article:
                tactic = "Tuyển CTV Việc Nhẹ Lương Cao / Làm Nhiệm Vụ Ảo"
        else:
            traps.append("Bẫy Chiếm Đoạt Tài Sản: Yêu cầu chuyển tiền vào tài khoản lạ hoặc đánh cắp mã OTP/mật khẩu")

    # 4. DẤU HIỆU LINK LẠ (+22 điểm)
    has_suspicious_link = bool(re.search(
        r"https?://|[a-z0-9\-]+\.(top|xyz|site|vip|cc|online|work|cfd|click|live|club)",
        text_lower
    ))
    if has_suspicious_link:
        score += 22
        traps.append("Dấu Hiệu Kỹ Thuật: Đính kèm đường link khả nghi hoặc tên miền không chính thống để đánh cắp thông tin")

    # 5. CỘNG HƯỞNG TỪ BÀI BÁO RAG ĐỐI SOÁT
    if rag_article and score > 25:
        rag_conf = int(rag_article.get("confidence", 70))
        score = max(score, min(97, rag_conf + 4))

    score = max(8, min(98, score))

    if score >= 70:
        level = "Nguy cơ cao"
        exp = "Hệ thống phát hiện kịch bản thao túng tâm lý có dấu hiệu nguy cơ cao chiếm đoạt tài sản."
    elif score >= 40:
        level = "Đáng ngờ"
        exp = "Phát hiện một số từ khóa đáng ngờ hoặc có dấu hiệu tạo áp lực, cần kiểm tra thận trọng."
    else:
        level = "An toàn"
        tactic = "Giao tiếp sinh hoạt thông thường"
        traps = ["Không phát hiện dấu hiệu thao túng tâm lý"]
        exp = "Không phát hiện dấu hiệu lừa đảo, đe dọa hay bẫy tài chính. Tin nhắn thuộc giao tiếp sinh hoạt thường ngày."

    rag_note = f" (Trùng khớp cảnh báo: {rag_article['title']} - {rag_article['source']})" if rag_article and level != "An toàn" else ""

    recommendations = [
        "Tuyệt đối không chuyển tiền và không bấm vào đường link lạ trong tin nhắn.",
        "Xác minh trực tiếp qua hotline chính thức của cơ quan hoặc kiểm tra app thật.",
        "Chụp ảnh màn hình lưu bằng chứng và phản ánh đến Tổng đài 156 hoặc Hotline A05."
    ] if level != "An toàn" else [
        "Có thể yên tâm tiếp tục trò chuyện bình thường.",
        "Luôn giữ thói quen bảo mật mã OTP ngân hàng và không chia sẻ cho bất kỳ ai."
    ]

    return {
        "risk_score": score,
        "threat_level": level,
        "detected_tactic": tactic,
        "explanation": f"{exp}{rag_note}",
        "psychological_traps": traps,
        "action_recommendations": recommendations
    }
