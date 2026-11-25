"""
Module: styles.py
Quản lý hệ thống Theme 3 chế độ (Dịu / Sáng / Tối - Mặc định "Dịu" theo chuẩn đề xuất UX):
- Nền trang: #D3DCE8 (áp dụng triệt để lên stAppViewContainer, section.main, html, body)
- Thẻ chat: #EEF2F8 (áp dụng lên stVerticalBlockBorderWrapper, stChatMessage)
- Thanh bên: #C7D2E1 (áp dụng lên stSidebar, stSidebarContent)
- Chữ chính: #0F1B33 (xanh đen)
- Chữ phụ: #374662 (tương phản cao >= 7:1)
- Nút cấp cứu ĐỎ RỰC đọc trọn chữ không bị cắt, tabs bo tròn hình Pill chuẩn Segmented Control.
- Bộ chọn giao diện 3 viên thuốc nhỏ gọn ở thanh bên; công tắc Chữ to có thanh trượt xám sáng / xanh rõ nét.
- Chế độ Chữ to: GIỮ NGUYÊN 100% GIAO DIỆN / BỐ CỤC, CHỈ PHÓNG TO PHÔNG CHỮ.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

THEMES = {
    "Dịu": {
        "page_bg": "#D3DCE8",             # Nền trang đề xuất chuẩn
        "card_bg": "#EEF2F8",             # Thẻ chat đề xuất chuẩn
        "card_inner_bg": "#DFE7F2",       # Khối bên trong thẻ
        "sidebar_bg": "#C7D2E1",          # Thanh bên đề xuất chuẩn
        "border_color": "#B8C5D6",        # Viền mảnh hài hòa
        "text_primary": "#0F1B33",        # Chữ chính (xanh đen)
        "text_secondary": "#374662",      # Chữ phụ (tương phản >= 7:1)
        "user_bubble_bg": "#DCE6F5",      # Bong bóng người dùng
        "user_bubble_border": "#AEC3DE",  # Viền bong bóng người dùng
        "user_bubble_text": "#0F1B33",
        "assistant_bubble_bg": "#EEF2F8", # Thẻ chat trợ lý
        "assistant_bubble_border": "#B8C5D6",
        "assistant_bubble_text": "#0F1B33",
        "box_shadow": "0 2px 10px rgba(15, 27, 51, 0.08)",
        "box_shadow_hover": "0 4px 16px rgba(15, 27, 51, 0.12)",
        "tab_active_bg": "#2563EB",
        "tab_active_text": "#FFFFFF",
        "chat_input_bg": "#EEF2F8",
    },
    "Sáng": {
        "page_bg": "#E8EEF6",             # Theo bảng màu gợi ý #E8EEF6
        "card_bg": "#FFFFFF",             # Thẻ trắng
        "card_inner_bg": "#F3F6FB",
        "sidebar_bg": "#F3F6FB",          # Thanh bên #F3F6FB
        "border_color": "#CBD6E6",        # Viền #CBD6E6
        "text_primary": "#10203B",        # Chữ chính xanh đen #10203B
        "text_secondary": "#47566F",      # Chữ phụ #47566F
        "user_bubble_bg": "#E3EEFF",
        "user_bubble_border": "#CBD6E6",
        "user_bubble_text": "#10203B",
        "assistant_bubble_bg": "#FFFFFF",
        "assistant_bubble_border": "#CBD6E6",
        "assistant_bubble_text": "#10203B",
        "box_shadow": "0 2px 8px rgba(16, 32, 59, 0.05)",
        "box_shadow_hover": "0 4px 14px rgba(16, 32, 59, 0.08)",
        "tab_active_bg": "#2563EB",
        "tab_active_text": "#FFFFFF",
        "chat_input_bg": "#FFFFFF",
    },
    "Tối": {
        "page_bg": "#0B132B",
        "card_bg": "#1C2541",
        "card_inner_bg": "#151C33",
        "sidebar_bg": "#1C2541",
        "border_color": "#3A506B",
        "text_primary": "#F8FAFC",
        "text_secondary": "#CBD5E1",
        "user_bubble_bg": "#1E3A8A",
        "user_bubble_border": "#3B82F6",
        "user_bubble_text": "#F8FAFC",
        "assistant_bubble_bg": "#1C2541",
        "assistant_bubble_border": "#3A506B",
        "assistant_bubble_text": "#F8FAFC",
        "box_shadow": "0 2px 12px rgba(0, 0, 0, 0.35)",
        "box_shadow_hover": "0 4px 20px rgba(0, 0, 0, 0.5)",
        "tab_active_bg": "#2563EB",
        "tab_active_text": "#FFFFFF",
        "chat_input_bg": "#1C2541",
    }
}


def get_theme_css(theme_mode: str = "Tối") -> str:
    """Sinh CSS động theo chế độ màu được chọn (Mặc định Dịu theo bảng màu đề xuất)"""
    t = THEMES.get(theme_mode, THEMES["Dịu"])
    tab_hover_bg = "rgba(255, 255, 255, 0.12)" if theme_mode == "Tối" else "rgba(255, 255, 255, 0.7)"
    link_hover_color = "#60A5FA" if theme_mode == "Tối" else "#2563EB"

    return f"""<style>
/* =========================================================================
   1. CẤU HÌNH BIẾN MÀU THEME ({theme_mode}) & NỀN TỔNG THỂ
   ========================================================================= */
:root {{
    --page-bg: {t["page_bg"]};
    --card-bg: {t["card_bg"]};
    --card-inner-bg: {t["card_inner_bg"]};
    --sidebar-bg: {t["sidebar_bg"]};
    --border-color: {t["border_color"]};
    --text-primary: {t["text_primary"]};
    --text-secondary: {t["text_secondary"]};
    --user-bubble-bg: {t["user_bubble_bg"]};
    --user-bubble-border: {t["user_bubble_border"]};
    --user-bubble-text: {t["user_bubble_text"]};
    --assistant-bubble-bg: {t["assistant_bubble_bg"]};
    --assistant-bubble-border: {t["assistant_bubble_border"]};
    --assistant-bubble-text: {t["assistant_bubble_text"]};
    --box-shadow: {t["box_shadow"]};
    --box-shadow-hover: {t["box_shadow_hover"]};
    --tab-active-bg: {t["tab_active_bg"]};
    --tab-active-text: {t["tab_active_text"]};
    --chat-input-bg: {t["chat_input_bg"]};
}}

/* ÁP DỤNG MÀU NỀN TRANG TRIỆT ĐỂ LÊN TẤT CẢ CONTAINER CỦA STREAMLIT */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section.main,
section.main,
[data-testid="stMain"],
.main,
.main .block-container,
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {{
    background-color: {t["page_bg"]} !important;
    background: {t["page_bg"]} !important;
    color: {t["text_primary"]} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}}

/* =========================================================================
   2. ẨN HOÀN TOÀN THANH CÔNG CỤ STREAMLIT (DEPLOY, MENU, Ô VUÔNG TỐI LẠC TÔNG)
   ========================================================================= */
header[data-testid="stHeader"],
[data-testid="stHeader"],
header.stAppHeader {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    opacity: 0 !important;
}}

/* =========================================================================
   3. CĂN GIỮA NỘI DUNG CHÍNH (980px), KHÔNG BỊ LỆCH
   ========================================================================= */
.main .block-container {{
    max-width: 980px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
}}

/* =========================================================================
   4. TIÊU ĐỀ VÀ CỠ CHỮ MẶC ĐỊNH 128% (~19.5px - 20px) - ĐỘ TƯƠNG PHẢN CAO
   ========================================================================= */
h1 {{ font-size: 26px !important; color: {t["text_primary"]} !important; font-weight: 800 !important; }}
h2 {{ font-size: 23px !important; color: {t["text_primary"]} !important; font-weight: 800 !important; }}
h3 {{ font-size: 20.5px !important; color: {t["text_primary"]} !important; font-weight: 800 !important; }}
h4, h5, h6 {{ font-size: 18.5px !important; color: {t["text_primary"]} !important; font-weight: 800 !important; }}

p, span, label, div, li {{
    color: {t["text_primary"]};
    font-size: 19.5px;
    line-height: 1.7;
}}

div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span {{
    font-size: 19.5px !important;
    line-height: 1.7 !important;
}}

.stCaption, caption, small, .subtext, div[data-testid="stCaptionContainer"] p {{
    color: {t["text_secondary"]} !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    line-height: 1.55 !important;
}}

/* =========================================================================
   5. BÓNG ĐỔ RẤT NHẸ CHO THẺ THAY VÌ VIỀN ĐẬM - MÀU CARD: {t["card_bg"]}
   ========================================================================= */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background-color: {t["card_bg"]} !important;
    background: {t["card_bg"]} !important;
    border: 1px solid {t["border_color"]} !important;
    border-radius: 16px !important;
    box-shadow: {t["box_shadow"]} !important;
    transition: box-shadow 0.2s ease;
}}

[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    box-shadow: {t["box_shadow_hover"]} !important;
}}

/* =========================================================================
   6. NÚT 'TÔI LỠ BỊ LỪA!' - ĐỎ RỰC, ĐỌC TRỌN VẸN CÂU, KHÔNG BAO GIỜ BỊ CẮT CHỮ
   ========================================================================= */
.st-key-btn_corner_emergency button,
div.st-key-btn_corner_emergency button,
div[data-testid="stElementContainer"]:has(#fixed-emergency-btn-anchor) + div[data-testid="stElementContainer"] button,
div[data-testid="element-container"]:has(#fixed-emergency-btn-anchor) + div[data-testid="element-container"] button,
div.element-container:has(#fixed-emergency-btn-anchor) + div.element-container button,
div:has(> #fixed-emergency-btn-anchor) + div button,
div.stButton:has(button[key="btn_corner_emergency"]) button,
button[key="btn_corner_emergency"],
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"],
button[kind="primary"] {{
    background-color: #dc2626 !important;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    font-size: 14.5px !important;
    font-weight: 800 !important;
    padding: 11px 20px !important;
    border-radius: 9999px !important;
    box-shadow: 0 4px 16px rgba(220, 38, 38, 0.45) !important;
    border: 2px solid #ffffff !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
    min-width: 175px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

.st-key-btn_corner_emergency button *,
div.st-key-btn_corner_emergency button *,
div[data-testid="stElementContainer"]:has(#fixed-emergency-btn-anchor) + div[data-testid="stElementContainer"] button *,
div[data-testid="element-container"]:has(#fixed-emergency-btn-anchor) + div[data-testid="element-container"] button *,
div.element-container:has(#fixed-emergency-btn-anchor) + div.element-container button *,
div:has(> #fixed-emergency-btn-anchor) + div button *,
button[key="btn_corner_emergency"] *,
button[data-testid="stBaseButton-primary"] *,
button[data-testid="baseButton-primary"] *,
button[kind="primary"] * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
}}

.st-key-btn_corner_emergency button:hover,
button[key="btn_corner_emergency"]:hover {{
    background-color: #b91c1c !important;
    background: #b91c1c !important;
    transform: scale(1.03) !important;
    box-shadow: 0 6px 22px rgba(220, 38, 38, 0.6) !important;
}}

/* =========================================================================
   6B. NÚT 'XÓA ĐOẠN CHAT' - DANGER PILL ĐỎ RỰC, CHỮ TRẮNG TINH RÕ NÉT 100%
   ========================================================================= */
.st-key-btn_clear_chat button,
div.st-key-btn_clear_chat button,
div[data-testid="stElementContainer"]:has(#clear-chat-btn-anchor) + div[data-testid="stElementContainer"] button,
div[data-testid="element-container"]:has(#clear-chat-btn-anchor) + div[data-testid="element-container"] button,
div.element-container:has(#clear-chat-btn-anchor) + div.element-container button,
div:has(> #clear-chat-btn-anchor) + div button,
button[key="btn_clear_chat"],
div.stButton:has(button[key="btn_clear_chat"]) button {{
    background-color: #dc2626 !important;
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    padding: 6px 14px !important;
    height: 38px !important;
    min-height: 38px !important;
    max-height: 38px !important;
    min-width: 0 !important;
    border-radius: 9999px !important;
    box-shadow: 0 2px 8px rgba(220, 38, 38, 0.35) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.5) !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

.st-key-btn_clear_chat button *,
div.st-key-btn_clear_chat button *,
.st-key-btn_clear_chat button p,
.st-key-btn_clear_chat button span,
div[data-testid="stElementContainer"]:has(#clear-chat-btn-anchor) + div[data-testid="stElementContainer"] button *,
div[data-testid="element-container"]:has(#clear-chat-btn-anchor) + div[data-testid="element-container"] button *,
div.element-container:has(#clear-chat-btn-anchor) + div.element-container button *,
div:has(> #clear-chat-btn-anchor) + div button *,
button[key="btn_clear_chat"] *,
div.stButton:has(button[key="btn_clear_chat"]) button *,
button[key="btn_clear_chat"] p {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    white-space: nowrap !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.st-key-btn_clear_chat button:hover,
div.st-key-btn_clear_chat button:hover,
div[data-testid="stElementContainer"]:has(#clear-chat-btn-anchor) + div[data-testid="stElementContainer"] button:hover,
button[key="btn_clear_chat"]:hover,
div.stButton:has(button[key="btn_clear_chat"]) button:hover {{
    background-color: #b91c1c !important;
    background: #b91c1c !important;
    box-shadow: 0 4px 14px rgba(220, 38, 38, 0.55) !important;
    transform: translateY(-1px) !important;
}}

/* Nút Gọi Ngay trong thẻ Hotline */
a.em-call-btn,
a.em-call-btn * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-decoration: none !important;
}}

a.em-call-btn:hover {{
    filter: brightness(1.15) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.45) !important;
}}

/* =========================================================================
   7. NÚT BẤM THỨ CẤP & NÚT LIÊN KẾT LINK BUTTON (st.link_button)
   TƯƠNG PHẢN CAO TRÊN CẢ CHẾ ĐỘ SÁNG, DỊU VÀ TỐI (KHÔNG BAO GIỜ BỊ CHỮ TRẮNG TRÊN NỀN TRẮNG)
   ========================================================================= */
button[kind="secondary"],
button[data-testid="stBaseButton-secondary"],
button[data-testid="baseButton-secondary"],
.stButton button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]),
a[data-testid="stBaseButton-secondary"],
a[data-testid="baseButton-secondary"],
a[data-testid="stLinkButton"],
div[data-testid="stLinkButton"] a,
.stLinkButton a,
div.stLinkButton a {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    border: 1.5px solid {t["border_color"]} !important;
    color: {t["text_primary"]} !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    border-radius: 10px !important;
    box-shadow: {t["box_shadow"]} !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    padding: 8px 16px !important;
}}

button[kind="secondary"] *,
button[data-testid="stBaseButton-secondary"] *,
button[data-testid="baseButton-secondary"] *,
.stButton button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]) *,
a[data-testid="stBaseButton-secondary"] *,
a[data-testid="baseButton-secondary"] *,
a[data-testid="stLinkButton"] *,
div[data-testid="stLinkButton"] a *,
.stLinkButton a *,
div.stLinkButton a * {{
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    font-weight: 700 !important;
    font-size: 17px !important;
    text-decoration: none !important;
}}

button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover,
.stButton button:not([kind="primary"]):hover,
a[data-testid="stBaseButton-secondary"]:hover,
a[data-testid="baseButton-secondary"]:hover,
a[data-testid="stLinkButton"]:hover,
div[data-testid="stLinkButton"] a:hover,
.stLinkButton a:hover,
div.stLinkButton a:hover {{
    background-color: {t["card_bg"]} !important;
    background: {t["card_bg"]} !important;
    border-color: {link_hover_color} !important;
    color: {link_hover_color} !important;
    box-shadow: {t["box_shadow_hover"]} !important;
    transform: translateY(-1px) !important;
}}

button[kind="secondary"]:hover *,
button[data-testid="stBaseButton-secondary"]:hover *,
button[data-testid="baseButton-secondary"]:hover *,
.stButton button:not([kind="primary"]):hover *,
a[data-testid="stBaseButton-secondary"]:hover *,
a[data-testid="baseButton-secondary"]:hover *,
a[data-testid="stLinkButton"]:hover *,
div[data-testid="stLinkButton"] a:hover *,
.stLinkButton a:hover *,
div.stLinkButton a:hover * {{
    color: {link_hover_color} !important;
    -webkit-text-fill-color: {link_hover_color} !important;
}}

/* =========================================================================
   7. THANH TABS BO TRÒN HÌNH NÚT PILL CHUẨN SEGMENTED CONTROL (ẢNH 3)
   ========================================================================= */
div[data-testid="stTabs"] {{
    margin-top: 10px !important;
    margin-bottom: 16px !important;
}}

div[data-testid="stTabs"] [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab-list"] {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    border-radius: 9999px !important;
    padding: 5px 6px !important;
    border: 1.5px solid {t["border_color"]} !important;
    box-shadow: 0 2px 8px rgba(15, 27, 51, 0.06) !important;
    gap: 6px !important;
    display: inline-flex !important;
    flex-wrap: wrap !important;
    width: auto !important;
    max-width: 100% !important;
    align-items: center !important;
    border-bottom: none !important;
}}

div[data-testid="stTabs"] button[role="tab"],
.stTabs button[role="tab"],
div[data-testid="stTabs"] button[data-baseweb="tab"],
.stTabs button[data-baseweb="tab"] {{
    color: {t["text_secondary"]} !important;
    font-weight: 700 !important;
    font-size: 16.5px !important;
    border-radius: 9999px !important;
    padding: 8px 16px !important;
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    transition: all 0.2s ease !important;
    outline: none !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
}}

div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[role="tab"] span,
div[data-testid="stTabs"] button[role="tab"] div,
.stTabs button[role="tab"] p,
.stTabs button[role="tab"] span,
.stTabs button[role="tab"] div {{
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
    font-size: 16.5px !important;
    font-weight: 700 !important;
    color: inherit !important;
}}

div[data-testid="stTabs"] button[role="tab"]:not([aria-selected="true"]):hover,
.stTabs button[role="tab"]:not([aria-selected="true"]):hover {{
    background-color: {tab_hover_bg} !important;
    color: {t["text_primary"]} !important;
}}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
.stTabs button[role="tab"][aria-selected="true"],
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
    color: {t["tab_active_text"]} !important;
    background-color: {t["tab_active_bg"]} !important;
    background: {t["tab_active_bg"]} !important;
    border-radius: 9999px !important;
    font-weight: 800 !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
    border: none !important;
    outline: none !important;
}}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {{
    color: {t["tab_active_text"]} !important;
    font-weight: 800 !important;
}}

/* XÓA HOÀN TOÀN VẠCH GẠCH CHÂN ĐỎ / XANH MẶC ĐỊNH */
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-border"],
div[data-testid="stTabs"] [data-baseweb="tab-list"]::after {{
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
}}

/* =========================================================================
   8. CỤM 3 VIÊN THUỐC BỘ CHỌN GIAO DIỆN Ở THANH BÊN (SIDEBAR) - PHÓNG TO & TINH GỌN
   ========================================================================= */
div[data-testid="stSidebar"] div[data-testid="stRadio"]:has(input[name*="sidebar_theme"]) [role="radiogroup"],
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{
    background-color: var(--card-bg, #EEF2F8) !important;
    border: 1.5px solid var(--border-color, #B8C5D6) !important;
    border-radius: 9999px !important;
    padding: 4px !important;
    display: flex !important;
    flex-direction: row !important;
    gap: 4px !important;
    width: 100% !important;
    justify-content: space-between !important;
    box-shadow: 0 2px 6px rgba(15, 27, 51, 0.08) !important;
}}

div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 9999px !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    cursor: pointer !important;
    flex: 1 !important;
    text-align: center !important;
    justify-content: center !important;
    align-items: center !important;
    display: inline-flex !important;
    min-height: 42px !important;
    transition: all 0.2s ease !important;
}}

/* ẨN TRIỆT ĐỂ CHẤM TRÒN RADIO NGUYÊN BẢN ĐỂ KHÔNG BỊ HIỆN 2 CHẤM TRÒN */
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label input,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label input + div,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label > div:first-of-type,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] [data-baseweb="radio"] > div:first-of-type,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label [data-testid="stRadioCircle"] {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}}

div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label div p,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label span {{
    font-size: 15.5px !important;
    font-weight: 800 !important;
    color: var(--text-primary, #0F1B33) !important;
    margin: 0 !important;
    white-space: nowrap !important;
}}

div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {{
    background-color: #2563EB !important;
    box-shadow: 0 3px 10px rgba(37, 99, 235, 0.45) !important;
}}

div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) div p,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) span,
div[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 15.5px !important;
}}

/* =========================================================================
   9. CÔNG TẮC 'CHỮ TO, DỄ ĐỌC' VÀ TRỢ NĂNG THANH BÊN (PHÓNG TO RÕ RÀNG)
   ========================================================================= */
div[data-testid="stSidebar"] div[data-testid="stToggle"] {{
    padding: 4px 0 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"] label {{
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    cursor: pointer !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"] label p,
div[data-testid="stSidebar"] div[data-testid="stToggle"] label span {{
    color: var(--text-primary, #0F1B33) !important;
    -webkit-text-fill-color: var(--text-primary, #0F1B33) !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"] [data-baseweb="checkbox"] > div:first-child {{
    background-color: #64748B !important;
    border: 1.5px solid #475569 !important;
    width: 48px !important;
    height: 26px !important;
    min-width: 48px !important;
    border-radius: 9999px !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"]:has(input:checked) [data-baseweb="checkbox"] > div:first-child,
div[data-testid="stSidebar"] div[data-testid="stToggle"] input:checked + div,
div[data-testid="stSidebar"] div[data-testid="stToggle"] [aria-checked="true"] > div:first-child {{
    background-color: #2563EB !important;
    border-color: #1D4ED8 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stToggle"] [data-baseweb="checkbox"] > div:first-child > div {{
    background-color: #FFFFFF !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3) !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
}}

/* Ẩn triệt để tooltip icon trong thanh bên nếu có để tránh đốm trắng lạ */
div[data-testid="stSidebar"] [data-testid="stTooltipIcon"] {{
    display: none !important;
}}

/* =========================================================================
   10. NÚT 'TẢI ẢNH BILL': ẨN CHEVRON MŨI TÊN XỔ XUỐNG
   ========================================================================= */
div[data-testid="stPopover"] button svg {{
    display: none !important;
}}

div[data-testid="stPopover"] button {{
    background-color: {t["card_bg"]} !important;
    border: 1.5px solid {t["border_color"]} !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    color: {t["text_primary"]} !important;
    box-shadow: 0 1px 4px rgba(15,27,51,0.06) !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stPopover"] button:hover {{
    background-color: {t["card_inner_bg"]} !important;
    border-color: #2563eb !important;
    color: #2563eb !important;
}}

/* =========================================================================
   11. PHÂN BIỆT RÕ RÀNG: TIN NGƯỜI DÙNG ({t["user_bubble_bg"]}) VS TRỢ LÝ ({t["assistant_bubble_bg"]})
   (LOẠI BỎ TRIỆT ĐỂ VIỀN & NỀN LỒNG NHAU / DOUBLE BORDER EFFECT)
   ========================================================================= */
[data-testid="stChatMessage"] {{
    background-color: {t["assistant_bubble_bg"]} !important;
    background: {t["assistant_bubble_bg"]} !important;
    border: 1.5px solid {t["assistant_bubble_border"]} !important;
    border-radius: 16px !important;
    box-shadow: {t["box_shadow"]} !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    font-size: 19.5px !important;
    line-height: 1.75 !important;
}}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {{
    font-size: 19.5px !important;
    line-height: 1.75 !important;
}}

/* Bỏ triệt để viền và nền lồng nhau ở các thẻ div con bên trong stChatMessage */
[data-testid="stChatMessage"] > div,
[data-testid="stChatMessageContent"],
div[data-testid="stChatMessageContent"] {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

/* Bong bóng tin nhắn người dùng: 1 khối mượt mà, không lồng hộp */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    background-color: {t["user_bubble_bg"]} !important;
    background: {t["user_bubble_bg"]} !important;
    border: 1.5px solid {t["user_bubble_border"]} !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 10px rgba(15, 27, 51, 0.12) !important;
}}

div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div,
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {{
    color: {t["user_bubble_text"]} !important;
    -webkit-text-fill-color: {t["user_bubble_text"]} !important;
}}

/* Giữ màu chữ và nền nổi bật cho nhãn nguy hiểm mark.kw-danger trong tin nhắn user */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) mark.kw-danger,
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) mark.kw-danger * {{
    color: #7f1d1d !important;
    -webkit-text-fill-color: #7f1d1d !important;
    background-color: #fee2e2 !important;
}}

/* =========================================================================
   12. TRỊ TRIỆT ĐỂ Ô CHAT INPUT Ở ĐÁY MÀN HÌNH - MÀU {t["chat_input_bg"]}
   ========================================================================= */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {{
    background-color: {t["page_bg"]} !important;
    background: {t["page_bg"]} !important;
}}

div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] [data-baseweb="base-input"],
div[data-testid="stChatInput"] [data-baseweb="textarea"],
div[data-testid="stChatInput"] textarea,
.stChatInput,
.stChatInput > div,
.stChatInput [data-baseweb="base-input"],
.stChatInput [data-baseweb="textarea"],
.stChatInput textarea {{
    background-color: {t["chat_input_bg"]} !important;
    background: {t["chat_input_bg"]} !important;
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    font-size: 18px !important;
    line-height: 1.6 !important;
}}

div[data-testid="stChatInput"],
.stChatInput {{
    border: 1.5px solid {t["border_color"]} !important;
    border-radius: 14px !important;
    box-shadow: {t["box_shadow_hover"]} !important;
}}

div[data-testid="stChatInput"]:focus-within,
.stChatInput:focus-within {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}}

div[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {{
    color: {t["text_secondary"]} !important;
    -webkit-text-fill-color: {t["text_secondary"]} !important;
    font-size: 17.5px !important;
    opacity: 1 !important;
}}

div[data-testid="stChatInputSubmitButton"],
div[data-testid="stChatInput"] button,
.stChatInput button {{
    background-color: #2563eb !important;
    background: #2563eb !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    border: none !important;
    opacity: 1 !important;
}}

div[data-testid="stChatInputSubmitButton"] svg,
div[data-testid="stChatInput"] button svg,
.stChatInput button svg {{
    fill: #ffffff !important;
    color: #ffffff !important;
}}

/* =========================================================================
   13. TÔ SÁNG TỪ KHÓA NGUY HIỂM TRONG TIN NHẮN NGƯỜI DÙNG
   ========================================================================= */
mark.kw-danger {{
    background-color: #fee2e2 !important;
    color: #7f1d1d !important;
    -webkit-text-fill-color: #7f1d1d !important;
    font-weight: 700 !important;
    padding: 1px 6px !important;
    border-radius: 4px !important;
    border: 1px solid #f87171 !important;
    font-size: inherit !important;
    display: inline-block !important;
    line-height: 1.4 !important;
}}

/* =========================================================================
   13B. HỘP CẢNH BÁO VIỆC CẦN LÀM NGAY LẬP TỨC - TƯƠNG PHẢN TUYỆT ĐỐI
   ========================================================================= */
.rec-urgent-title {{
    color: #991b1b !important;
    -webkit-text-fill-color: #991b1b !important;
    font-weight: 800 !important;
    font-size: 16px !important;
    letter-spacing: 0.3px !important;
}}

/* =========================================================================
   14. THANH BÊN (SIDEBAR) RỘNG RÃI & PHÔNG CHỮ TIÊU ĐỀ LỚN
   ========================================================================= */
section[data-testid="stSidebar"],
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
[data-testid="stSidebarCollapseButton"] {{
    background-color: {t["sidebar_bg"]} !important;
    background: {t["sidebar_bg"]} !important;
    border-right: 1.5px solid {t["border_color"]} !important;
}}

section[data-testid="stSidebar"] {{
    min-width: 335px !important;
}}

/* Tiêu đề các mục trong Sidebar: to rõ, đậm nét */
div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3 {{
    font-size: 19px !important;
    font-weight: 800 !important;
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    margin-top: 14px !important;
    margin-bottom: 12px !important;
    letter-spacing: 0.2px !important;
}}

/* =========================================================================
   15. EXPANDER & DETAILS - ĐỒNG BỘ THEME TỐI/SÁNG, HẾT BỊ TRẮNG LÓA
   ========================================================================= */
div[data-testid="stExpander"],
.stExpander,
div[data-testid="stExpander"] details {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    border: 1.5px solid {t["border_color"]} !important;
    border-radius: 14px !important;
    box-shadow: {t["box_shadow"]} !important;
    overflow: hidden !important;
    margin-bottom: 12px !important;
}}

/* Header của Expander (Thanh tiêu đề bấm mở/đóng) */
div[data-testid="stExpander"] summary,
.stExpander summary {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    border-bottom: 1px solid {t["border_color"]} !important;
    color: {t["text_primary"]} !important;
    padding: 12px 18px !important;
    font-weight: 700 !important;
    font-size: 17.5px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stExpander"] summary:hover,
.stExpander summary:hover {{
    background-color: {t["card_bg"]} !important;
    background: {t["card_bg"]} !important;
    color: #2563eb !important;
}}

div[data-testid="stExpander"] summary *,
.stExpander summary *,
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span {{
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    font-weight: 700 !important;
    font-size: 17.5px !important;
}}

div[data-testid="stExpander"] summary svg,
.stExpander summary svg {{
    fill: {t["text_primary"]} !important;
    color: {t["text_primary"]} !important;
}}

/* Expander riêng trong Thanh bên (Sidebar) - Phóng to vừa vặn, sắc nét */
div[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
div[data-testid="stSidebar"] .stExpander summary {{
    padding: 13px 18px !important;
    font-size: 15.5px !important;
    font-weight: 800 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stExpander"] summary p,
div[data-testid="stSidebar"] div[data-testid="stExpander"] summary span {{
    font-size: 15.5px !important;
    font-weight: 800 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
div[data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stExpanderDetails"] span,
div[data-testid="stSidebar"] div[data-testid="stExpander"] [data-testid="stExpanderDetails"] label {{
    font-size: 15px !important;
    line-height: 1.6 !important;
}}

div[data-testid="stSidebar"] div[data-testid="stExpander"] input {{
    font-size: 15px !important;
    padding: 10px 14px !important;
    min-height: 42px !important;
}}

/* Vùng nội dung chi tiết bên trong Expander khi mở ra */
div[data-testid="stExpanderDetails"],
div[data-testid="stExpander"] [data-testid="stExpanderDetails"],
div[data-testid="stExpander"] details > div:last-child {{
    background-color: {t["card_bg"]} !important;
    background: {t["card_bg"]} !important;
    padding: 14px 18px !important;
    color: {t["text_primary"]} !important;
}}

/* =========================================================================
   16. THẺ MÃ CODE INLINE - HÀI HÒA THEME, KHÔNG BỊ TRẮNG LÓA
   ========================================================================= */
code, 
.stMarkdown code, 
span code, 
p code, 
li code {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    border: 1px solid {t["border_color"]} !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    display: inline-block !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
}}

/* =========================================================================
   17. Ô NHẬP LIỆU TEXT INPUT & PASSWORD (SIDEBAR & NỘI DUNG)
   ========================================================================= */
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] [data-baseweb="input"],
div[data-testid="stTextInput"] [data-baseweb="base-input"] {{
    background-color: {t["card_inner_bg"]} !important;
    background: {t["card_inner_bg"]} !important;
    border: 1.5px solid {t["border_color"]} !important;
    color: {t["text_primary"]} !important;
    -webkit-text-fill-color: {t["text_primary"]} !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}}

div[data-testid="stTextInput"] input::placeholder {{
    color: {t["text_secondary"]} !important;
    -webkit-text-fill-color: {t["text_secondary"]} !important;
    opacity: 0.7 !important;
}}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25) !important;
}}

/* Biểu tượng con mắt / nút phụ trong ô mật khẩu */
div[data-testid="stTextInput"] button svg,
div[data-testid="stTextInput"] button {{
    color: {t["text_secondary"]} !important;
    fill: {t["text_secondary"]} !important;
    background: transparent !important;
}}

/* Tooltip trợ giúp (icon hỏi chấm ?) không bị trắng lóa */
div[data-testid="stTooltipIcon"] button svg,
div[data-testid="stTooltipIcon"] svg,
div[data-testid="stTooltipIcon"] button {{
    color: {t["text_secondary"]} !important;
    fill: {t["text_secondary"]} !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
</style>"""


def get_elderly_css(zoom_level: str = "1.45") -> str:
    """
    CSS Chế độ Người lớn tuổi (3 mức phóng đại: 140% / 145% / 150%):
    GIỮ NGUYÊN 100% BỐ CỤC / GIAO DIỆN (KHÔNG DÙNG CSS ZOOM TRÊN KHUNG CHỨA),
    CHỈ PHÓNG TO KÍCH THƯỚC PHÔNG CHỮ SO VỚI MẶC ĐỊNH 128% ĐỂ NGƯỜI LỚN TUỔI ĐỌC DỄ DÀNG.
    """
    level = float(zoom_level) if zoom_level in ["1.40", "1.45", "1.50"] else 1.45

    if level <= 1.40:
        body_font = "22px"
        caption_font = "19px"
        button_font = "19px"
        input_font = "20.5px"
        tab_font = "18.5px"
        h1_font, h2_font, h3_font, h4_font = "29px", "25px", "22px", "20px"
        line_height = "1.75"
    elif level >= 1.50:
        body_font = "24px"
        caption_font = "21px"
        button_font = "21px"
        input_font = "22.5px"
        tab_font = "20.5px"
        h1_font, h2_font, h3_font, h4_font = "33px", "28.5px", "25px", "22.5px"
        line_height = "1.85"
    else:  # 1.45
        body_font = "23px"
        caption_font = "20px"
        button_font = "20px"
        input_font = "21.5px"
        tab_font = "19.5px"
        h1_font, h2_font, h3_font, h4_font = "31px", "27px", "23.5px", "21px"
        line_height = "1.8"

    return f"""<style>
/* =========================================================================
   CHỈ PHÓNG TO PHÔNG CHỮ (140% - 150%) - GIỮ NGUYÊN 100% GIAO DIỆN VÀ KHUNG CHỨA
   KHÔNG SỬ DỤNG 'zoom' TRÊN html/body/.stApp ĐỂ TRÁNH VỠ BỐ CỤC
   ========================================================================= */

/* 1. Phông chữ nội dung bài viết, tin nhắn, đoạn văn, danh sách, radio & cảnh báo */
p, 
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] li,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] li,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span,
label {{
    font-size: {body_font} !important;
    line-height: {line_height} !important;
}}

/* 2. Chữ phụ, caption, hướng dẫn */
.stCaption, 
caption, 
small, 
.subtext,
div[data-testid="stCaptionContainer"] p {{
    font-size: {caption_font} !important;
    line-height: 1.55 !important;
}}

/* 3. Ô nhập văn bản (Chat Input, Text Input, Textarea) */
div[data-testid="stChatInput"] textarea,
.stChatInput textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {{
    font-size: {input_font} !important;
    line-height: 1.55 !important;
}}

div[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {{
    font-size: {input_font} !important;
}}

/* 4. Chữ bên trong các nút bấm và nút liên kết link button */
button p, 
button span, 
div.stButton button p,
div.stButton button span,
a[data-testid="stLinkButton"] p,
a[data-testid="baseButton-secondary"] p,
div[data-testid="stLinkButton"] a p,
.stLinkButton a p {{
    font-size: {button_font} !important;
    font-weight: 700 !important;
}}

/* 5. Chữ bên trong các Tab (giữ nguyên viên thuốc bo tròn của Tab, chỉ chữ to hơn) */
div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[role="tab"] span,
.stTabs button[role="tab"] p {{
    font-size: {tab_font} !important;
    font-weight: 700 !important;
}}

/* 6. Tiêu đề các mục lớn */
h1 {{ font-size: {h1_font} !important; }}
h2 {{ font-size: {h2_font} !important; }}
h3 {{ font-size: {h3_font} !important; }}
h4 {{ font-size: {h4_font} !important; }}
</style>"""

BASE_CSS = get_theme_css("Tối")
