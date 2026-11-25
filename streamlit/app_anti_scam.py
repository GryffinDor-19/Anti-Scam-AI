"""
AntiScam AI - Hệ Thống Trợ Lý Tác Chiến Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức
Phiên bản: Giao diện Sáng / Dịu / Tối, Tabs bo tròn hình Pill, Nút cấp cứu đỏ rực ghim góc (v5.0)
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import os
import sys
import importlib
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Thêm các thư mục liên quan vào system path để import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

for p in [backend_dir, root_dir, current_dir]:
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

try:
    from backend.engines.rag_case_matcher import RAGCaseMatcher
except ImportError:
    try:
        from engines.rag_case_matcher import RAGCaseMatcher
    except ImportError:
        try:
            from modules.rag_case_matcher import RAGCaseMatcher
        except ImportError:
            from backend.modules.rag_case_matcher import RAGCaseMatcher

# =============================================================================
# NẠP CÁC MODULE GIAO DIỆN & TỐI ƯU HIỆU NĂNG TỐI ĐA (ZERO-DELAY)
# =============================================================================
import styles
from styles import get_theme_css, get_elderly_css, BASE_CSS
from components.sidebar import render_sidebar
from components.emergency_banner import render_header_and_emergency
from views.tab_chat import render_tab_chat
from views.tab_fake_bill import render_tab_fake_bill
from views.tab_scam_game import render_tab_scam_game
from views.tab_library import render_tab_library

# Khởi tạo RAG Matcher với Cache bộ nhớ để tăng tốc tối đa
@st.cache_resource
def get_rag_matcher():
    return RAGCaseMatcher()

rag_matcher = get_rag_matcher()

# Cấu hình trang Streamlit: Căn giữa đối xứng, thu gọn sidebar mặc định
st.set_page_config(
    page_title="Hệ thống hỗ trợ chống lừa đảo online",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Khởi tạo trạng thái phiên làm việc (Session State)
for key, default in [
    ("theme_mode", "Tối"),           # Mặc định giao diện "Tối" (#0B132B)
    ("input_text", ""),
    ("show_emergency", False),
    ("elderly_mode", False),
    ("font_zoom_level", "1.45"),
    ("has_analyzed", False),
    ("demo_fake_bill", True),
    ("history", []),
    ("trigger_animation", False),
    ("chat_history", [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Đồng bộ theme — chỉ dùng "Tối" (đã bỏ Dịu & Sáng)
pill_sel = st.session_state.get("sidebar_theme_pill_selector")
if pill_sel:
    if "Tối" in pill_sel:
        st.session_state["theme_mode"] = "Tối"

if st.session_state.get("theme_mode") not in ["Tối"]:
    st.session_state["theme_mode"] = "Tối"

# 1. Áp dụng CSS Giao diện theo Theme Tối & Chế độ Chữ to
active_theme = st.session_state.get("theme_mode", "Tối")
st.markdown(get_theme_css(active_theme), unsafe_allow_html=True)
if st.session_state.get("elderly_mode", False):
    font_zoom = st.session_state.get("font_zoom_level", "1.45")
    st.markdown(get_elderly_css(font_zoom), unsafe_allow_html=True)

# 2. Hiển thị Sidebar rút gọn (Đã loại bỏ trùng lặp kịch bản mẫu)
render_sidebar()

# 3. Hiển thị Header chuẩn UX (Logo + Tiêu đề + Nút cấp cứu đỏ rực + Bộ chọn theme)
render_header_and_emergency()

# 4. Hiển thị 4 Tabs chức năng chính dạng nút Pill bo tròn chuẩn Image 3
tab_chat, tab_bill, tab_game, tab_guide = st.tabs([
    "Kiểm tra tin nhắn",
    "Soi bill giả",
    "Đấu trường lừa đảo",
    "Thư viện cảnh báo"
])

with tab_chat:
    render_tab_chat(rag_matcher)

with tab_bill:
    render_tab_fake_bill()

with tab_game:
    render_tab_scam_game(rag_matcher)

with tab_guide:
    render_tab_library(rag_matcher)
