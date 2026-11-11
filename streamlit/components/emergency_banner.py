"""
Component: emergency_banner.py
Tiêu đề Cyber SOC và khu vực Cấp cứu khẩn cấp Giờ Vàng (Hotlines 1-chạm).
"""

import streamlit as st

try:
    from modules.emergency_manager import EmergencyManager
except ImportError:
    from backend.modules.emergency_manager import EmergencyManager


def render_header_and_emergency():
    """Hiển thị Header và khu vực Cấp cứu khẩn cấp nếu được kích hoạt"""
    col_hdr_left, col_hdr_right = st.columns([3, 1])

    with col_hdr_left:
        st.title("🛡️ ANTISCAM AI — CYBER SOC COMMAND")
        st.caption("🟢 **THREAT MONITORING ACTIVE** · 🤖 **CONVERSATIONAL AI ASSISTANT v3.5**")

    with col_hdr_right:
        st.write("")
        if st.button("🚨 TÔI ĐÃ LỠ BỊ LỪA / CẦN CỨU NGUY", type="primary", use_container_width=True):
            st.session_state.show_emergency = not st.session_state.show_emergency

    # Khu vực hiển thị bảng cấp cứu
    if st.session_state.show_emergency:
        emergency_data = EmergencyManager.get_emergency_payload()

        st.error(f"### {emergency_data['title']}\n\n**{emergency_data['subtitle']}**")

        col_em1, col_em2 = st.columns([3, 2])
        with col_em1:
            st.subheader("⚡ 3 Hành Động Cứu Tiền Tức Thì:")
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

                st.divider()
                st.warning(f"🏛️ **Hotline Cục An ninh mạng A05 (Bộ Công an):** `{emergency_data['police_hotline']}`")

        st.divider()
