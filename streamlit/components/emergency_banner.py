"""
Component: emergency_banner.py
Tiêu đề ứng dụng & Nút Cấp Cứu Giờ Vàng:
- Hàng đầu CHỈ CÒN 2 thứ: Tiêu đề bên trái và Nút cấp cứu đỏ rực bên phải.
- Nút cấp cứu đọc trọn vẹn câu: "🚨 Tôi lỡ bị lừa!", không bị co cụm, không bị cắt chữ.
- Tiêu đề nằm trọn trên 1 dòng, không bị ép xuống dòng.
- Đã dời toàn bộ bộ chọn giao diện và nút chữ to sang thanh bên (Sidebar).
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import streamlit as st

try:
    from modules.emergency_manager import EmergencyManager
except ImportError:
    from backend.modules.emergency_manager import EmergencyManager


def render_header_and_emergency():
    """Hiển thị Header chuẩn UX: Hàng đầu CHỈ CÒN Tiêu đề và Nút Cấp Cứu đỏ rực"""

    # HÀNG ĐẦU: TIÊU ĐỀ BÊN TRÁI + NÚT CẤP CỨU BÊN PHẢI (CHỈ 2 THỨ, RỘNG RÃI, KHÔNG BỊ CẮT CHỮ)
    col_hdr_left, col_hdr_right = st.columns([3.6, 1.4], vertical_alignment="center")

    with col_hdr_left:
        st.markdown("""
        <div style='background: var(--card-bg, #EEF2F8); border: 1.5px solid var(--border-color, #B8C5D6); border-radius: 16px; padding: 12px 20px; box-shadow: var(--box-shadow, 0 2px 10px rgba(15,27,51,0.06));'>
            <div style='display: flex; align-items: center; gap: 14px;'>
                <div style='width: 44px; height: 44px; border-radius: 12px; background-color: #2563eb; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; flex-shrink: 0; box-shadow: 0 3px 8px rgba(37,99,235,0.3);'>
                    🛡️
                </div>
                <div>
                    <div style='font-size: 1.35rem; font-weight: 800; color: var(--text-primary, #0F1B33); line-height: 1.25; white-space: nowrap;'>Hệ thống hỗ trợ chống lừa đảo online</div>
                    <div style='font-size: 13.5px; font-weight: 500; color: var(--text-secondary, #374662); margin-top: 2px;'>Trợ lý nhận diện thủ đoạn thao túng tâm lý, đường link lạ và hóa đơn giả mạo</div>
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

    # KHU VỰC BẢNG CẤP CỨU KHẨN CẤP GIỜ VÀNG (15 PHÚT ĐẦU TIÊN)
    if st.session_state.get("show_emergency", False):
        emergency_data = EmergencyManager.get_emergency_payload()

        st.error(f"### {emergency_data['title']}\n\n**{emergency_data['subtitle']}**")

        col_em1, col_em2 = st.columns([3, 2])
        with col_em1:
            st.subheader("⚡ 3 Việc Cần Làm Ngay Lập Tức:")
            for item in emergency_data["checklist"]:
                with st.container(border=True):
                    st.markdown(f"#### {item['icon']} {item['step']}")
                    st.write(item['action'])
                    st.caption(f"⏱️ **Mức độ ưu tiên:** {item['priority']}")

        with col_em2:
            st.subheader("📞 Hotline Khóa Tài Khoản 1-Chạm:")
            st.caption("Bấm gọi ngay để tổng đài ngân hàng phong tỏa tài khoản / thẻ khẩn cấp:")
            with st.container(border=True):
                for bank in emergency_data["hotlines"][:5]:
                    col_b1, col_b2 = st.columns([2, 1])
                    with col_b1:
                        st.write(f"🏦 **{bank['bank']}**: `{bank['hotline']}`")
                        st.caption(bank['desc'])
                    with col_b2:
                        st.link_button("📞 Gọi ngay", f"tel:{bank['hotline']}", use_container_width=True)
