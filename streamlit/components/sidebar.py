"""
Component: sidebar.py
Thanh điều hướng bên trái:
1. Giao diện mặc định: Tối (không còn lựa chọn Dịu / Sáng).
2. Trợ năng màn hình: Công tắc Chữ to dễ đọc có thanh trượt xám sáng / xanh rõ ràng, hiển thị nhãn BẬT / TẮT.
3. Cài đặt nâng cao (Gemini API Key) thu gọn trong Expander.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import streamlit as st


def render_sidebar():
    """Hiển thị Sidebar chuẩn UX tối ưu theo yêu cầu mới nhất"""
    with st.sidebar:
        # 1. GIAO DIỆN TỐI CỐ ĐỊNH (ĐÃ BỎ LỰA CHỌN DỊU / SÁNG)
        st.markdown("### 🌙 Giao Diện Tối")
        st.caption("Chế độ tối mặc định — tối ưu cho mắt.")

        st.markdown("---")

        # 2. CÔNG TẮC CHỮ TO, DỄ ĐỌC (CÓ THANH TRƯỢT TƯƠNG PHẢN CAO & NHÃN BẬT/TẮT)
        st.markdown("### 👓 Trợ Năng Màn Hình")
        current_val = st.session_state.get("elderly_mode", False)
        status_label = "BẬT" if current_val else "TẮT"

        elderly_mode = st.toggle(
            f"Chữ to, dễ đọc: **[{status_label}]**",
            value=current_val,
            key="sidebar_elderly_toggle",
        )
        if elderly_mode != current_val:
            st.session_state.elderly_mode = elderly_mode

        selected_zoom = st.session_state.get("font_zoom_level", "1.45")
        if st.session_state.get("elderly_mode", False):
            zoom_idx = 0 if selected_zoom == "1.40" else (2 if selected_zoom == "1.50" else 1)
            zoom_opt = st.radio(
                "Cỡ chữ phóng đại:",
                options=["140% (Chữ lớn)", "145% (Chữ rất lớn ⭐)", "150% (Chữ siêu lớn)"],
                index=zoom_idx,
                key="sidebar_font_zoom_selector"
            )
            new_zoom = "1.40" if "140%" in zoom_opt else ("1.50" if "150%" in zoom_opt else "1.45")
            if new_zoom != selected_zoom:
                st.session_state.font_zoom_level = new_zoom

            st.caption(f"Đang hiển thị ở mức cỡ chữ **{zoom_opt.split(' ')[0]}** (Mặc định chuẩn là 128%, bố cục giữ nguyên 100%).")

        st.markdown("---")
        
        # 3. CÀI ĐẶT NÂNG CAO CHO GIẢNG VIÊN / DEVELOPER
        with st.expander("⚙️ Cài đặt nâng cao (API Key & Kỹ thuật)", expanded=False):
            st.caption("Dành riêng cho giảng viên chấm đồ án hoặc kết nối trực tiếp mô hình AI đám mây:")
            api_key_val = st.text_input(
                "Khóa Google Gemini API Key:",
                value=st.session_state.get("gemini_api_key", ""),
                type="password",
                placeholder="AIzaSy...",
            )
            if api_key_val and api_key_val.strip() != "":
                st.session_state.gemini_api_key = api_key_val.strip()
                import os
                os.environ["GEMINI_API_KEY"] = api_key_val.strip()
                st.success("✅ Đã kích hoạt Google Gemini AI!")
            else:
                st.caption("⚡ Mặc định: Bộ lọc nhanh & Bộ luật phòng thủ đa tiêu chí động.")

    return st.session_state.get("elderly_mode", False), selected_zoom
