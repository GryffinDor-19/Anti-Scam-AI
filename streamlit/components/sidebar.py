"""
Component: sidebar.py
Thanh điều hướng bên trái:
1. Bộ chọn giao diện (Dịu / Sáng / Tối) dạng cụm 3 nút viên thuốc nhỏ gọn.
2. Trợ năng màn hình: Công tắc Chữ to dễ đọc có thanh trượt xám sáng / xanh rõ ràng, hiển thị nhãn BẬT / TẮT.
3. Cài đặt nâng cao (Gemini API Key) thu gọn trong Expander.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import streamlit as st


def render_sidebar():
    """Hiển thị Sidebar chuẩn UX tối ưu theo yêu cầu mới nhất"""
    with st.sidebar:
        # 1. BỘ CHỌN GIAO DIỆN DẠNG CỤM 3 VIÊN THUỐC NHỎ GỌN
        st.markdown("### 🎨 Chế Độ Giao Diện")
        current_theme = st.session_state.get("theme_mode", "Dịu")
        theme_options = ["🔵 Dịu", "⚪ Sáng", "⚫ Tối"]
        theme_index = 0 if current_theme == "Dịu" else (1 if current_theme == "Sáng" else 2)

        selected_theme = st.radio(
            "Chọn giao diện:",
            options=theme_options,
            index=theme_index,
            horizontal=True,
            label_visibility="collapsed",
            key="sidebar_theme_pill_selector"
        )
        new_theme = "Dịu" if "Dịu" in selected_theme else ("Sáng" if "Sáng" in selected_theme else "Tối")
        if new_theme != current_theme:
            st.session_state.theme_mode = new_theme
            st.rerun()

        st.markdown("---")

        # 2. CÔNG TẮC CHỮ TO, DỄ ĐỌC (CÓ THANH TRƯỢT TƯƠNG PHẢN CAO & NHÃN BẬT/TẮT)
        st.markdown("### 👓 Trợ Năng Màn Hình")
        current_val = st.session_state.get("elderly_mode", False)
        status_label = "BẬT" if current_val else "TẮT"

        elderly_mode = st.toggle(
            f"Chữ to, dễ đọc: **[{status_label}]**",
            value=current_val,
            key="sidebar_elderly_toggle",
            help="Phóng to kích thước chữ toàn diện lên >= 18px giúp người cao tuổi dễ đọc"
        )
        if elderly_mode != current_val:
            st.session_state.elderly_mode = elderly_mode
            st.rerun()

        selected_zoom = st.session_state.get("font_zoom_level", "1.20")
        if st.session_state.get("elderly_mode", False):
            zoom_idx = 0 if selected_zoom == "1.15" else (2 if selected_zoom == "1.28" else 1)
            zoom_opt = st.radio(
                "Cỡ chữ phóng đại:",
                options=["115% (Chữ vừa vặn)", "120% (Chữ lớn ⭐)", "128% (Chữ rất lớn)"],
                index=zoom_idx,
                key="sidebar_font_zoom_selector"
            )
            new_zoom = "1.15" if "115%" in zoom_opt else ("1.28" if "128%" in zoom_opt else "1.20")
            if new_zoom != selected_zoom:
                st.session_state.font_zoom_level = new_zoom
                st.rerun()

            st.caption(f"Đang hiển thị ở mức cỡ chữ **{zoom_opt.split(' ')[0]}** (Bố cục giao diện giữ nguyên 100%).")

        st.markdown("---")
        
        # 3. CÀI ĐẶT NÂNG CAO CHO GIẢNG VIÊN / DEVELOPER
        with st.expander("⚙️ Cài đặt nâng cao (API Key & Kỹ thuật)", expanded=False):
            st.caption("Dành riêng cho giảng viên chấm đồ án hoặc kết nối trực tiếp mô hình AI đám mây:")
            api_key_val = st.text_input(
                "Khóa Google Gemini API Key:",
                value=st.session_state.get("gemini_api_key", ""),
                type="password",
                placeholder="AIzaSy...",
                help="Dùng để kết nối trực tiếp mô hình gemini-3.8-flash & gemini-4 của nhóm"
            )
            if api_key_val and api_key_val.strip() != "":
                st.session_state.gemini_api_key = api_key_val.strip()
                import os
                os.environ["GEMINI_API_KEY"] = api_key_val.strip()
                st.success("✅ Đã kích hoạt Google Gemini AI!")
            else:
                st.caption("⚡ Mặc định: Bộ lọc nhanh & Bộ luật phòng thủ đa tiêu chí động.")

    return st.session_state.get("elderly_mode", False), selected_zoom
