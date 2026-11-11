"""
Module: styles.py
Quản lý giao diện CSS Dark Cyber SOC & Trợ năng phóng to cho người lớn tuổi.
"""

BASE_CSS = """<style>
/* Nền không gian tối chuẩn SOC Cyber */
.stApp {
    background-color: #060913 !important;
    color: #e2e8f0 !important;
}

/* Thẻ Container bo góc và viền phát sáng nhẹ */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(13, 21, 39, 0.75) !important;
    border: 1px solid rgba(56, 189, 248, 0.22) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
}

/* Nút bấm phong cách Cyber */
button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    border: 1px solid #38bdf8 !important;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}

button[kind="secondary"] {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #cbd5e1 !important;
}

/* Hiệu ứng nhấp nháy đèn đỏ cấp cứu */
@keyframes pulse-red-glow {
    0%, 100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.9); }
}

.panic-btn-glow {
    animation: pulse-red-glow 2s infinite ease-in-out;
}

/* Tabs giao diện tối */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0b1120 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #1e293b !important;
}

.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    color: #38bdf8 !important;
    background-color: #1e293b !important;
    border-radius: 8px !important;
}

/* Thanh nhập chat */
[data-testid="stChatInput"] {
    border-color: rgba(56, 189, 248, 0.5) !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
}
</style>"""


def get_elderly_css(zoom_level: str = "1.20") -> str:
    """Trả về CSS phóng đại theo tỷ lệ cân đối cho người cao tuổi"""
    return f"""<style>
html, body, .stApp {{
    zoom: {zoom_level} !important;
}}
button p {{
    font-weight: 700 !important;
}}
</style>"""
