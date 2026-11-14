"""
AntiScam AI - Hệ Thống Trợ Lý Tác Chiến Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức
Phiên bản: Modular Cyber SOC Command Center & Conversational AI Chatbot (v4.0)
Phụ trách: Thành viên 3 (Frontend & UX Developer)
Cấu trúc module hóa:
- styles.py: Quản lý Dark Cyber Theme & CSS Phóng đại Người lớn tuổi
- components/:
    - gauge.py: Đồng hồ kim quét bán nguyệt Matplotlib Neon
    - sidebar.py: Thanh công cụ trợ năng & kịch bản mẫu
    - emergency_banner.py: Tiêu đề SOC & Nút cấp cứu khẩn cấp 1-chạm
- views/:
    - tab_chat.py: Tab 1 (Chatbot, Gauge, Telemetry, Audit Log)
    - tab_fake_bill.py: Tab 2 (Forensic Vision Lab Fake Bill)
    - tab_library.py: Tab 3 (Thư viện 20 bài báo Cục ATTT & Hotline)
"""

import os
import sys
import streamlit as st

# Thêm các thư mục liên quan vào system path để import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

# Đảm bảo root_dir luôn đứng đầu sys.path để 'backend' được nhận diện chuẩn là package
for p in [backend_dir, current_dir, root_dir]:
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

try:
    from modules.rag_case_matcher import RAGCaseMatcher
except ImportError:
    from backend.modules.rag_case_matcher import RAGCaseMatcher

# Import các components và views được tách module
from styles import BASE_CSS, get_elderly_css
from components.sidebar import render_sidebar
from components.emergency_banner import render_header_and_emergency
from views.tab_chat import render_tab_chat
from views.tab_fake_bill import render_tab_fake_bill
from views.tab_library import render_tab_library

# Khởi tạo RAG Matcher với Cache bộ nhớ để tăng tốc tối đa
@st.cache_resource
def get_rag_matcher():
    return RAGCaseMatcher()

rag_matcher = get_rag_matcher()

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="AntiScam AI - Cyber SOC Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo trạng thái phiên làm việc (Session State)
for key, default in [
    ("input_text", ""),
    ("show_emergency", False),
    ("has_analyzed", False),
    ("demo_fake_bill", False),
    ("history", []),
    ("trigger_animation", False),
    ("chat_history", [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

# 1. Hiển thị Sidebar & lấy cấu hình Trợ năng
elderly_mode, selected_zoom = render_sidebar()

# 2. Áp dụng CSS Cyber SOC & Trợ năng người lớn tuổi
st.markdown(BASE_CSS, unsafe_allow_html=True)
if elderly_mode:
    st.markdown(get_elderly_css(selected_zoom), unsafe_allow_html=True)

# 3. Hiển thị Header & Bảng Cấp cứu khẩn cấp Giờ Vàng
render_header_and_emergency()

# 4. Hiển thị 3 Tabs chức năng chính
tab_chat, tab_bill, tab_guide = st.tabs([
    "💬 1. Trợ Lý Tác Chiến Đàm Thoại (Cyber Chatbot & Gauge)",
    "🧾 2. Phòng Lab Soi Fake Bill (Forensic Vision Lab)",
    "📚 3. Cẩm Nang & Thư Viện 20 Bài Báo Cục ATTT"
])

with tab_chat:
    render_tab_chat(rag_matcher)

with tab_bill:
    render_tab_fake_bill()

with tab_guide:
    render_tab_library(rag_matcher)
