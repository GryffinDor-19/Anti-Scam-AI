"""
Component: emergency_banner.py
Tiêu đề ứng dụng & Nút Cấp Cứu Giờ Vàng:
- Hàng đầu CHỈ CÒN 2 thứ: Tiêu đề bên trái và Nút cấp cứu đỏ rực bên phải.
- Nút cấp cứu đọc trọn vẹn câu: "🚨 Tôi lỡ bị lừa!", không bị co cụm, không bị cắt chữ.
- Bảng cấp cứu khẩn cấp: Tương phản cao vượt trội (>= 10:1), toàn bộ dòng hướng dẫn
  dùng chữ xanh đen đậm #0F1B33 và đỏ sẫm #7F1D1D trên nền thẻ trắng/hồng nhạt, cực kỳ dễ đọc.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import streamlit as st

try:
    from backend.emergency.emergency_manager import EmergencyManager
except ImportError:
    try:
        from emergency.emergency_manager import EmergencyManager
    except ImportError:
        try:
            from modules.emergency_manager import EmergencyManager
        except ImportError:
            from backend.modules.emergency_manager import EmergencyManager


def render_header_and_emergency():
    """Hiển thị Header chuẩn UX: Hàng đầu CHỈ CÒN Tiêu đề và Nút Cấp Cứu đỏ rực"""

    # 1. HÀNG ĐẦU: TIÊU ĐỀ BÊN TRÁI + NÚT CẤP CỨU BÊN PHẢI (CHỈ 2 THỨ, RỘNG RÃI, KHÔNG BỊ CẮT CHỮ)
    col_hdr_left, col_hdr_right = st.columns([3.6, 1.4], vertical_alignment="center")

    is_dark = (st.session_state.get("theme_mode", "Dịu") == "Tối")
    hdr_card_bg = "#1C2541" if is_dark else "var(--card-bg, #EEF2F8)"
    hdr_border = "#3A506B" if is_dark else "var(--border-color, #B8C5D6)"
    hdr_title_color = "#F8FAFC" if is_dark else "var(--text-primary, #0F1B33)"
    hdr_sub_color = "#CBD5E1" if is_dark else "#374662"

    with col_hdr_left:
        st.markdown(f"""
        <div style='background: {hdr_card_bg}; border: 1.5px solid {hdr_border}; border-radius: 16px; padding: 12px 20px; box-shadow: var(--box-shadow, 0 2px 10px rgba(15,27,51,0.06));'>
            <div style='display: flex; align-items: center; gap: 14px;'>
                <div style='width: 44px; height: 44px; border-radius: 12px; background-color: #2563eb; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; flex-shrink: 0; box-shadow: 0 3px 8px rgba(37,99,235,0.3);'>
                    🛡️
                </div>
                <div>
                    <div style='font-size: 1.35rem; font-weight: 800; color: {hdr_title_color}; line-height: 1.25; white-space: nowrap;'>Hệ thống hỗ trợ chống lừa đảo online</div>
                    <div style='font-size: 14px; font-weight: 600; color: {hdr_sub_color}; margin-top: 2px;'>Trợ lý nhận diện thủ đoạn thao túng tâm lý, đường link lạ và hóa đơn giả mạo</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_hdr_right:
        st.markdown('<div id="fixed-emergency-btn-anchor"></div>', unsafe_allow_html=True)
        if st.button("🚨 Tôi lỡ bị lừa!", key="btn_corner_emergency", type="primary", use_container_width=True, help="Bấm để xem ngay 3 việc cần làm trong 15 phút đầu"):
            st.session_state.show_emergency = not st.session_state.get("show_emergency", False)
            st.rerun()

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 2. KHU VỰC BẢNG CẤP CỨU KHẨN CẤP GIỜ VÀNG (15 PHÚT ĐẦU TIÊN) - TƯƠNG PHẢN CAO TRÊN CẢ SÁNG/DỊU VÀ TỐI
    if st.session_state.get("show_emergency", False):
        emergency_data = EmergencyManager.get_emergency_payload()
        is_dark = (st.session_state.get("theme_mode", "Dịu") == "Tối")

        # CẤU HÌNH BẢNG MÀU TỰ ĐỘNG THÍCH ỨNG THEO THEME (KHÔNG BAO GIỜ BỊ TRÙNG MÀU NỀN)
        if is_dark:
            # Chế độ Tối: Nền đỏ sẫm sang trọng, chữ trắng tinh / hồng sáng, tương phản vượt trội >= 12:1
            em_banner_bg = "#2A0A0E"
            em_banner_border = "#EF4444"
            em_title_color = "#FECACA"
            em_subtitle_bg = "#450A0A"
            em_subtitle_color = "#FFFFFF"
            em_subtitle_border = "#EF4444"
            em_heading_color = "#F8FAFC"
            em_caption_color = "#CBD5E1"
            em_card_bg = "#1C2541"
            em_card_border = "#DC2626"
            em_step_title_color = "#FCA5A5"
            em_priority_bg = "#7F1D1D"
            em_priority_color = "#FECACA"
            em_priority_border = "#DC2626"
            em_body_text = "#F1F5F9"
            em_tag_bg = "#DC2626"
            em_tag_color = "#FFFFFF"
            em_hotline_card_bg = "#1C2541"
            em_hotline_card_border = "#3A506B"
            em_bank_name_color = "#F8FAFC"
            em_bank_desc_color = "#CBD5E1"
            em_hotline_badge_bg = "#7F1D1D"
            em_hotline_badge_color = "#FECACA"
            em_hotline_badge_border = "1px solid #DC2626"
            em_police_card_bg = "#2A0A0E"
            em_police_card_border = "#EF4444"
            em_police_title_color = "#FECACA"
        else:
            # Chế độ Dịu / Sáng: Nền hồng sáng, chữ xanh đen #0F1B33, dải hướng dẫn #7F1D1D tương phản >= 10:1
            em_banner_bg = "#FFF1F2"
            em_banner_border = "#EF4444"
            em_title_color = "#991B1B"
            em_subtitle_bg = "#FEE2E2"
            em_subtitle_color = "#7F1D1D"
            em_subtitle_border = "#DC2626"
            em_heading_color = "#0F1B33"
            em_caption_color = "#374662"
            em_card_bg = "#FFFFFF"
            em_card_border = "#FCA5A5"
            em_step_title_color = "#991B1B"
            em_priority_bg = "#FEE2E2"
            em_priority_color = "#991B1B"
            em_priority_border = "#FCA5A5"
            em_body_text = "#0F1B33"
            em_tag_bg = "#FEE2E2"
            em_tag_color = "#DC2626"
            em_hotline_card_bg = "#FFFFFF"
            em_hotline_card_border = "#CBD6E6"
            em_bank_name_color = "#0F1B33"
            em_bank_desc_color = "#374662"
            em_hotline_badge_bg = "#FEE2E2"
            em_hotline_badge_color = "#DC2626"
            em_hotline_badge_border = "none"
            em_police_card_bg = "#FEF2F2"
            em_police_card_border = "#FCA5A5"
            em_police_title_color = "#991B1B"

        # BANNER TIÊU ĐỀ CẤP CỨU VỚI DÒNG HƯỚNG DẪN TƯƠNG PHẢN CAO RÕ NÉT
        st.markdown(f"""
        <div style='background-color: {em_banner_bg}; border: 2px solid {em_banner_border}; border-radius: 16px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(239,68,68,0.22);'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>
                <span style='font-size: 26px;'>🚨</span>
                <span style='font-size: 1.25rem; font-weight: 800; color: {em_title_color};'>{emergency_data['title']}</span>
            </div>
            <div style='font-size: 15px; font-weight: 700; color: {em_subtitle_color}; line-height: 1.55; padding: 10px 14px; background: {em_subtitle_bg}; border-radius: 10px; border-left: 4px solid {em_subtitle_border};'>
                💡 {emergency_data['subtitle']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_em1, col_em2 = st.columns([1.12, 1], gap="medium")
        
        # CỘT TRÁI: 3 BƯỚC HÀNH ĐỘNG KHẨN CẤP
        with col_em1:
            st.markdown(f"<div style='font-size: 1.15rem; font-weight: 800; color: {em_heading_color}; margin-bottom: 8px;'>⚡ 3 Việc Cần Làm Ngay Lập Tức:</div>", unsafe_allow_html=True)
            for item in emergency_data["checklist"]:
                # Làm nổi bật các cụm từ hành động quyết định
                action_text = item['action']
                action_text = action_text.replace("BẬT NGAY CHẾ ĐỘ MÁY BAY", f"<strong style='color: {em_tag_color}; background: {em_tag_bg}; padding: 2px 6px; border-radius: 4px;'>BẬT NGAY CHẾ ĐỘ MÁY BAY</strong>")
                action_text = action_text.replace("TẮT NGUỒN ĐIỆN THOẠI", f"<strong style='color: {em_tag_color}; background: {em_tag_bg}; padding: 2px 6px; border-radius: 4px;'>TẮT NGUỒN ĐIỆN THOẠI</strong>")
                action_text = action_text.replace("khóa thẻ và tạm dừng mọi giao dịch khẩn cấp", f"<strong style='color: {em_tag_color}; background: {em_tag_bg}; padding: 2px 6px; border-radius: 4px;'>khóa thẻ và tạm dừng mọi giao dịch khẩn cấp</strong>")
                link_color = "#60A5FA" if is_dark else "#2563EB"
                action_text = action_text.replace("chụp ngay", f"<strong style='color: {link_color};'>chụp ngay</strong>")

                st.markdown(f"""
                <div style='background: {em_card_bg}; border: 1.5px solid {em_card_border}; border-radius: 12px; padding: 11px 14px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);'>
                    <!-- Hàng 1: Tiêu đề bước trải rộng trọn vẹn, không bị ép dọc chữ -->
                    <div style='font-size: 14.5px; font-weight: 800; color: {em_step_title_color}; line-height: 1.35; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;'>
                        <span>{item['icon']}</span>
                        <span>{item['step']}</span>
                    </div>

                    <!-- Hàng 2: Huy hiệu thời gian / ưu tiên tách riêng gọn gàng -->
                    <div style='margin-bottom: 6px;'>
                        <span style='background: {em_priority_bg}; color: {em_priority_color}; font-size: 11.5px; font-weight: 700; padding: 2px 8px; border-radius: 5px; border: 1px solid {em_priority_border}; display: inline-flex; align-items: center; gap: 4px;'>
                            ⏱️ {item['priority']}
                        </span>
                    </div>

                    <!-- Hàng 3: Nội dung hành động khẩn cấp -->
                    <div style='font-size: 13.5px; line-height: 1.5; color: {em_body_text}; font-weight: 500;'>
                        {action_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # CỘT PHẢI: HOTLINE KHÓA TÀI KHOẢN 1-CHẠM (ĐÓNG KHUNG GỌN GÀNG, KHÔNG BỊ TRÀN CHỮ)
        with col_em2:
            st.markdown(f"<div style='font-size: 1.15rem; font-weight: 800; color: {em_heading_color}; margin-bottom: 4px;'>📞 Hotline Khóa Tài Khoản 1-Chạm:</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 13px; font-weight: 500; color: {em_caption_color}; margin-bottom: 10px;'>Bấm gọi ngay để tổng đài ngân hàng phong tỏa tài khoản / thẻ:</div>", unsafe_allow_html=True)

            for bank in emergency_data["hotlines"][:5]:
                st.markdown(f"""
                <div style='background: {em_hotline_card_bg}; border: 1.5px solid {em_hotline_card_border}; border-radius: 12px; padding: 10px 14px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);'>
                    <!-- Hàng trên: Tên ngân hàng bên trái + Nút Gọi nhỏ gọn bên phải -->
                    <div style='display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 5px;'>
                        <div style='font-size: 14.5px; font-weight: 800; color: {em_bank_name_color}; display: flex; align-items: center; gap: 6px; white-space: nowrap;'>
                            <span>🏦</span>
                            <span>{bank['bank']}</span>
                        </div>
                        <a href="tel:{bank['hotline']}" class="em-call-btn" style='display: inline-flex; align-items: center; justify-content: center; gap: 4px; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: #FFFFFF !important; font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-decoration: none; white-space: nowrap; box-shadow: 0 1px 3px rgba(37,99,235,0.3); flex-shrink: 0; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s ease;'>
                            <span>📞</span>
                            <span style='color: #FFFFFF !important;'>Gọi ngay</span>
                        </a>
                    </div>
                    <!-- Hàng dưới: Số hotline nổi bật + Hướng dẫn bấm phím -->
                    <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                        <span style='background: {em_hotline_badge_bg}; color: {em_hotline_badge_color}; border: {em_hotline_badge_border}; font-size: 12px; font-weight: 800; padding: 1px 6px; border-radius: 5px; font-family: monospace;'>
                            {bank['hotline']}
                        </span>
                        <span style='font-size: 12px; font-weight: 500; color: {em_bank_desc_color}; line-height: 1.3;'>
                            {bank['desc']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ĐƯỜNG DÂY NÓNG CỤC A05 (BỘ CÔNG AN)
            st.markdown(f"""
            <div style='background: {em_police_card_bg}; border: 1.5px solid {em_police_card_border}; border-radius: 12px; padding: 10px 14px; margin-top: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);'>
                <!-- Hàng trên: Tên cơ quan + Nút Gọi -->
                <div style='display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 5px;'>
                    <div style='font-size: 14px; font-weight: 800; color: {em_police_title_color}; display: flex; align-items: center; gap: 6px; white-space: nowrap;'>
                        <span>🛡️</span>
                        <span>Cục An ninh mạng A05</span>
                    </div>
                    <a href="tel:0692348560" class="em-call-btn" style='display: inline-flex; align-items: center; justify-content: center; gap: 4px; background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); color: #FFFFFF !important; font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-decoration: none; white-space: nowrap; box-shadow: 0 1px 3px rgba(220,38,38,0.4); flex-shrink: 0; border: 1px solid rgba(255,255,255,0.15); transition: all 0.2s ease;'>
                        <span>📞</span>
                        <span style='color: #FFFFFF !important;'>Gọi ngay</span>
                    </a>
                </div>
                <!-- Hàng dưới: Số hotline + Mô tả -->
                <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                    <span style='background: #7F1D1D; color: #FECACA; border: 1px solid #DC2626; font-size: 12px; font-weight: 800; padding: 1px 6px; border-radius: 5px; font-family: monospace;'>
                        069.234.8560
                    </span>
                    <span style='font-size: 12px; font-weight: 500; color: {em_bank_desc_color}; line-height: 1.3;'>
                        Tố giác tội phạm lừa đảo công nghệ cao
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
