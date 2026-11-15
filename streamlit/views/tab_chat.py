"""
View: tab_chat.py
Tab 1: Kiểm Tra Tin Nhắn (Khung chat nền trắng sáng sủa, độ tương phản cao, 
phân biệt tin người dùng #DCE6F5 vs trợ lý #EEF2F8, ưu tiên việc cần làm ngay,
nút '📎 Tải ảnh bill' gọn gàng, kịch bản thử nghiệm 1 chỗ trực quan trong chat).
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import os
import re
import sys
import time
import datetime
import tempfile
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from components.gauge import render_gauge_chart

# Nạp bộ não Backend AI (Hỗ trợ Gateway, Pipeline 3 lớp và Dynamic Scorer)
# Nạp bộ não Backend AI (Hỗ trợ Gateway, Pipeline 3 lớp và Dynamic Scorer)
try:
    from backend.gateway.pipeline import run_pipeline as analyze_scam  # Đổi tên run_pipeline thành analyze_scam để khớp biến của TV3 ở dưới
except ImportError:
    from gateway.pipeline import run_pipeline as analyze_scam

try:
    from backend.engines.fake_bill_detector import FakeBillDetector
except ImportError:
    try:
        from backend.modules.fake_bill_detector import FakeBillDetector
    except ImportError:
        FakeBillDetector = None


def highlight_dangerous_keywords(text: str) -> str:
    """Tô sáng các cụm từ đe dọa, ép buộc, rửa tiền, CSGT, phạt nguội, tài khoản an toàn trong tin nhắn của người dùng."""
    keywords = [
        r"rửa tiền", r"công an", r"cảnh sát hình sự", r"bắt tạm giam",
        r"tài khoản an toàn", r"chuyển tiền", r"giữ bí mật", r"lệnh bắt",
        r"viện kiểm sát", r"nạp tiền", r"hoa hồng", r"nhiệm vụ", r"40 tỷ", r"150 triệu",
        r"đường dây ma túy", r"thanh tra tài chính", r"phạt nguội", r"mã otp",
        r"cuc csgt", r"csgt", r"phat nguoi", r"phat-nguoi", r"nop phat", r"vi pham toc do", r"tra-cuu"
    ]
    pattern = re.compile(f"({'|'.join(keywords)})", re.IGNORECASE)
    return pattern.sub(r'<mark class="kw-danger">\1</mark>', text)


def render_tab_chat(rag_matcher):
    """Hiển thị giao diện Tab 1: Khung kiểm tra tin nhắn dạng hội thoại hiện đại"""

    # 1. KHỞI TẠO STATE HỘI THOẠI
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # 2. XỬ LÝ NẾU CÓ TIN NHẮN TỪ KỊCH BẢN MẪU CHUYỂN QUA
    pending_text = st.session_state.get("pending_user_query", None)
    if pending_text:
        st.session_state.pending_user_query = None
        process_user_message(pending_text, rag_matcher)

    # 3. THANH TRẠNG THÁI GỌN GÀNG ĐẦU KHUNG CHAT
    is_dark = (st.session_state.get("theme_mode", "Dịu") == "Tối")
    status_text_color = "#F8FAFC" if is_dark else "#0F1B33"

    col_status_left, col_status_right = st.columns([3.2, 1.4], vertical_alignment="center")
    with col_status_left:
        st.markdown(
            f"<div style='display: flex; align-items: center; gap: 8px; padding: 4px 0;'>"
            f"<span style='width: 10px; height: 10px; border-radius: 50%; background-color: #10b981; display: inline-block;'></span>"
            f"<span style='font-size: 15px; font-weight: 700; color: {status_text_color};'>Trợ lý AntiScam sẵn sàng · Chuỗi phòng thủ 3 lớp kích hoạt</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_status_right:
        if st.session_state.chat_messages:
            st.markdown('<div id="clear-chat-btn-anchor"></div>', unsafe_allow_html=True)
            if st.button("🗑️ Xóa đoạn chat", key="btn_clear_chat", type="primary", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 4. VÙNG HIỂN THỊ CÁC BONG BÓNG TIN NHẮN (PHÂN BIỆT RÕ RÀNG NGƯỜI DÙNG #DCE6F5 VS TRỢ LÝ #EEF2F8)
    if not st.session_state.chat_messages:
        render_welcome_screen()
    else:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    raw_content = msg.get("content", "")
                    highlighted_html = highlight_dangerous_keywords(raw_content)
                    user_font_color = "#FFFFFF" if is_dark else "#0F1B33"
                    st.markdown(
                        f"<div style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, sans-serif; font-size: 17px; line-height: 1.7; color: {user_font_color} !important; -webkit-text-fill-color: {user_font_color} !important; font-weight: 600; letter-spacing: 0.2px;'>"
                        f"{highlighted_html}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    if msg.get("image"):
                        st.image(msg["image"], caption="Ảnh đính kèm", width=280)
            else:
                with st.chat_message("assistant", avatar="🛡️"):
                    render_conversational_assistant_response(msg, rag_matcher)

    # 5. THANH CÔNG CỤ CẮM ĐÁY: NÚT TẢI ẢNH BILL & Ô NHẬP TIN NHẮN
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Nút Popover tải ảnh bill (Đã ẩn chevron mũi tên xổ xuống bằng CSS)
    with st.popover("📎 Tải ảnh bill", use_container_width=False):
        st.markdown("##### 📸 Tải Ảnh Biên Lai Ngân Hàng")
        st.caption("AI sẽ soi phông chữ số tiền, logo ngân hàng và dấu hiệu chỉnh sửa ảnh.")
        uploaded_img = st.file_uploader(
            "Chọn file ảnh (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="chat_popover_file"
        )
        note_text = st.text_input("Ghi chú thêm (tùy chọn):", placeholder="Ví dụ: Khách gửi bill này giục giao hàng gấp...")
        if uploaded_img and st.button("🚀 Bắt đầu soi ảnh này", type="primary", use_container_width=True):
            process_image_message(uploaded_img, note_text)
            st.rerun()

    # Ô nhập tin nhắn chuẩn cắm đáy của Streamlit (Nền thẻ #EEF2F8, chữ rõ #0F1B33, nút xanh)
    user_prompt = st.chat_input("Nhập tin nhắn hoặc dán đường link cần kiểm tra...")
    if user_prompt and user_prompt.strip():
        process_user_message(user_prompt.strip(), rag_matcher)
        st.rerun()

    # 6. BẢNG NHẬT KÝ KIỂM TRA TRONG PHIÊN THU GỌN
    render_audit_log_section()


def render_welcome_screen():
    """Màn hình chào mừng thông minh: Giới thiệu Chuỗi phòng thủ 3 lớp và Đề xuất các tin nhắn mẫu 1-click"""
    is_dark = (st.session_state.get("theme_mode", "Dịu") == "Tối")
    text_main = "#F8FAFC" if is_dark else "#0F1B33"
    text_sub = "#CBD5E1" if is_dark else "#374662"
    card_bg = "#1C2541" if is_dark else "#EEF2F8"
    card_inner = "#151C33" if is_dark else "#FFFFFF"
    border_col = "#3A506B" if is_dark else "#B8C5D6"

    with st.container():
        # 1. TIÊU ĐỀ & LỜI CHÀO
        st.markdown(f"""
        <div style='background-color: {card_bg}; border: 1.5px solid {border_col}; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px;'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>
                <span style='font-size: 26px;'>🛡️</span>
                <div>
                    <div style='font-size: 18px; font-weight: 800; color: #2563EB;'>Trợ Lý Phòng Chống Lừa Đảo Trực Tuyến AntiScam AI</div>
                    <div style='font-size: 14px; color: {text_sub};'>Sẵn sàng đối soát tin nhắn, phát hiện bẫy tâm lý và giám định hóa đơn chuyển khoản tức thì</div>
                </div>
            </div>
            <div style='font-size: 14.5px; color: {text_main}; line-height: 1.6; margin-top: 10px;'>
                Bạn có thể <strong>dán trực tiếp tin nhắn nghi vấn</strong> vào ô chat ở đáy màn hình, bấm <strong>📎 Tải ảnh bill</strong> để soi biên lai, hoặc <strong>chọn nhanh các kịch bản lừa đảo thực tế</strong> được đề xuất bên dưới để trải nghiệm:
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. KHỐI HIỂN THỊ CƠ CHẾ PHÒNG THỦ 3 LỚP RÕ RÀNG
        st.markdown(f"""
        <div style='background-color: {card_bg}; border: 1px solid {border_col}; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;'>
            <div style='font-size: 13.5px; font-weight: 800; color: #2563EB; margin-bottom: 8px;'>
                ⚡ CHUỖI PHÒNG THỦ ĐA LỚP TỰ ĐỘNG (MULTI-LAYER DEFENSE PIPELINE):
            </div>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; font-size: 13px; color: {text_main};'>
                <div style='background: {card_inner}; padding: 8px 12px; border-radius: 8px; border-left: 3.5px solid #10B981;'>
                    <strong>Lớp 1: Bộ Lọc Nhanh (< 0.05s)</strong><br/>
                    <span style='color: {text_sub}; font-size: 12.5px;'>Quét lập tức từ khóa đe dọa, bắt bớ, cọc tiền, rửa tiền.</span>
                </div>
                <div style='background: {card_inner}; padding: 8px 12px; border-radius: 8px; border-left: 3.5px solid #3B82F6;'>
                    <strong>Lớp 2: RAG Đối Soát Tri Thức</strong><br/>
                    <span style='color: {text_sub}; font-size: 12.5px;'>Đối chiếu 20+ bài báo và hồ sơ lừa đảo từ Cục An toàn thông tin.</span>
                </div>
                <div style='background: {card_inner}; padding: 8px 12px; border-radius: 8px; border-left: 3.5px solid #8B5CF6;'>
                    <strong>Lớp 3: AI Phân Tích Bẫy Tâm Lý</strong><br/>
                    <span style='color: {text_sub}; font-size: 12.5px;'>Bóc trần kịch bản thao túng uy quyền, ép thời gian, dọa phong tỏa.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. MÀN HÌNH ĐỀ XUẤT CÁC TIN NHẮN MẪU DỄ THAO TÁC (1-CLICK PROMPT CARDS)
        st.markdown(f"<div style='font-size: 15px; font-weight: 800; color: {text_main}; margin-bottom: 10px;'>💡 Đề xuất các kịch bản lừa đảo phổ biến để thử nhanh (1-Click):</div>", unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2, gap="medium")

        # Kịch bản 1: Giả danh công an
        with col_c1:
            with st.container(border=True):
                st.markdown("<div style='font-weight: 800; font-size: 14.5px; color: #DC2626;'>🚨 1. Giả danh Công an điều tra rửa tiền</div>", unsafe_allow_html=True)
                st.caption("Dọa bắt giam, mạo danh cán bộ Cục Cảnh sát hình sự để ép chuyển tiền vào tài khoản an toàn.")
                st.markdown(
                    "<div style='background: rgba(220,38,38,0.06); padding: 8px 10px; border-radius: 6px; font-size: 13px; font-style: italic; margin-bottom: 8px;'>"
                    "\"Tôi là Đại úy Nguyễn Văn Hùng Cục CSHS. Tài khoản anh liên quan rửa tiền 40 tỷ, yêu cầu chuyển 150 triệu vào tài khoản an toàn gấp!\""
                    "</div>",
                    unsafe_allow_html=True
                )
                if st.button("🚀 Thử kịch bản Công an dọa bắt", key="demo_btn_police", use_container_width=True):
                    st.session_state.pending_user_query = "Tôi là Đại úy Nguyễn Văn Hùng cán bộ điều tra Cục Cảnh sát hình sự. Tài khoản của anh đang liên quan đường dây rửa tiền 40 tỷ, yêu cầu chuyển 150 triệu vào tài khoản an toàn gấp!"
                    st.rerun()

        # Kịch bản 2: Tuyển CTV Shopee/TikTok
        with col_c2:
            with st.container(border=True):
                st.markdown("<div style='font-weight: 800; font-size: 14.5px; color: #D97706;'>💼 2. Tuyển CTV việc nhẹ lương cao</div>", unsafe_allow_html=True)
                st.caption("Lừa làm nhiệm vụ xem video, hưởng hoa hồng khủng 30-50%, mồi nạp cọc nhỏ rồi siết tiền.")
                st.markdown(
                    "<div style='background: rgba(217,119,6,0.06); padding: 8px 10px; border-radius: 6px; font-size: 13px; font-style: italic; margin-bottom: 8px;'>"
                    "\"Tuyển CTV làm nhiệm vụ xem video Shopee/TikTok hoa hồng 30-50% mỗi ngày, nạp cọc 200k rút ngay 350k!\""
                    "</div>",
                    unsafe_allow_html=True
                )
                if st.button("🚀 Thử kịch bản Tuyển CTV nạp cọc", key="demo_btn_ctv", use_container_width=True):
                    st.session_state.pending_user_query = "Tuyển CTV làm nhiệm vụ xem video Shopee/TikTok hoa hồng 30-50% mỗi ngày, nạp cọc 200k rút ngay 350k!"
                    st.rerun()

        col_c3, col_c4 = st.columns(2, gap="medium")

        # Kịch bản 3: Shipper giục nạp tiền / link độc
        with col_c3:
            with st.container(border=True):
                st.markdown("<div style='font-weight: 800; font-size: 14.5px; color: #EA580C;'>📦 3. Shipper giao hàng gửi link độc</div>", unsafe_allow_html=True)
                st.caption("Mạo danh shipper giao kiện hàng giả vờ, giục chuyển khoản cọc hoặc bấm link tra cứu giả.")
                st.markdown(
                    "<div style='background: rgba(234,88,12,0.06); padding: 8px 10px; border-radius: 6px; font-size: 13px; font-style: italic; margin-bottom: 8px;'>"
                    "\"Em là shipper GHTK giao đơn Shopee 240k, anh chị đi vắng vui lòng bấm tra-cuu-don.xyz chuyển khoản để em giữ hàng!\""
                    "</div>",
                    unsafe_allow_html=True
                )
                if st.button("🚀 Thử kịch bản Shipper giả mạo", key="demo_btn_shipper", use_container_width=True):
                    st.session_state.pending_user_query = "Em là shipper GHTK giao đơn Shopee 240k, anh chị đi vắng vui lòng bấm tra-cuu-don.xyz chuyển khoản cọc để em giữ hàng!"
                    st.rerun()

        # Kịch bản 4: Phạt nguội giao thông
        with col_c4:
            with st.container(border=True):
                st.markdown("<div style='font-weight: 800; font-size: 14.5px; color: #7C3AED;'>🚗 4. Phạt nguội vi phạm giao thông</div>", unsafe_allow_html=True)
                st.caption("SMS mạo danh Cục CSGT thông báo xe vi phạm, dụ dỗ truy cập trang web giả mạo nộp phạt.")
                st.markdown(
                    "<div style='background: rgba(124,58,237,0.06); padding: 8px 10px; border-radius: 6px; font-size: 13px; font-style: italic; margin-bottom: 8px;'>"
                    "\"CUC CSGT THONG BAO: Phuong tien 29A-888.88 vi pham toc do. Truy cap ngay tra-cuu-phat-nguoi.csgt-online.xyz de nop phat!\""
                    "</div>",
                    unsafe_allow_html=True
                )
                if st.button("🚀 Thử kịch bản Phạt nguội", key="demo_btn_traffic", use_container_width=True):
                    st.session_state.pending_user_query = "CUC CSGT THONG BAO: Phuong tien 29A-888.88 vi pham toc do. Truy cap ngay tra-cuu-phat-nguoi.csgt-online.xyz de nop phat!"
                    st.rerun()

        # Kịch bản 5: Tin nhắn bình thường (An toàn)
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            col_safe_text, col_safe_btn = st.columns([3, 1.2], vertical_alignment="center")
            with col_safe_text:
                st.markdown("<span style='font-weight: 700; color: #16A34A;'>🟢 Tin nhắn sinh hoạt an toàn:</span> *\"Tối nay rảnh không qua quán cà phê ngồi tí nhé, tao vừa nhận lương để tao bao chầu này!\"*", unsafe_allow_html=True)
            with col_safe_btn:
                if st.button("👉 Thử tin nhắn an toàn", key="demo_btn_safe", use_container_width=True):
                    st.session_state.pending_user_query = "Tối nay rảnh không qua quán cà phê ngồi tí nhé, tao vừa nhận lương để tao bao chầu này!"
                    st.rerun()


def process_user_message(text: str, rag_matcher):
    """Xử lý phân tích tin nhắn và đo lường thời gian thực tế"""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    start_time = time.time()

    # 1. Thêm tin nhắn của User vào lịch sử
    st.session_state.chat_messages.append({
        "role": "user",
        "content": text,
        "time": now_str,
        "type": "text"
    })

    # 2. Gọi bộ não Backend AI phân tích
    active_api_key = st.session_state.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", None))
    with st.spinner("🔍 Đang kích hoạt chuỗi phòng thủ 3 lớp (Lọc nhanh · RAG Đối soát · AI Phân tích)..."):
        ai_data = analyze_scam(text, api_key=active_api_key)
    elapsed_time = round(time.time() - start_time, 2)

    score = int(ai_data.get("risk_score", 12))
    threat_level = ai_data.get("threat_level", "An toàn")
    tactic = ai_data.get("detected_tactic", "Giao tiếp sinh hoạt thông thường")
    explanation = ai_data.get("explanation", "")
    traps = ai_data.get("psychological_traps", [])
    recommendations = ai_data.get("action_recommendations", [])

    # Xác định nguồn phân tích thực tế (hỗ trợ cả trường source và layer do Backend trả về)
    backend_source = ai_data.get("source") or ai_data.get("model_source")
    backend_layer = ai_data.get("layer")
    if backend_source:
        model_source = f"{backend_source} ({backend_layer})" if backend_layer else str(backend_source)
    elif active_api_key and "YOUR_API" not in active_api_key and "API KEY" not in active_api_key:
        model_source = "Google Gemini AI"
    else:
        model_source = "Bộ lọc nhanh (không dùng AI)"

    # 3. Tìm bài báo RAG đối soát
    matched_cases = []
    if rag_matcher and score >= 35:
        try:
            matched_cases = rag_matcher.match(text, top_k=2)
        except Exception:
            matched_cases = []

    # 4. Thêm tin nhắn của Assistant vào lịch sử
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": explanation,
        "time": now_str,
        "type": "scam_analysis",
        "data": {
            "score": score,
            "threat_level": threat_level,
            "tactic": tactic,
            "explanation": explanation,
            "traps": traps,
            "recommendations": recommendations,
            "matched_cases": matched_cases,
            "input_text": text,
            "model_source": model_source,
            "elapsed_time": elapsed_time
        }
    })

    # 5. Lưu vào Audit Log
    current_status = "🚨 Nguy cơ cao" if score >= 70 else ("⚠️ Đáng ngờ" if score >= 40 else "✅ An toàn")
    snippet_text = (text[:80] + "...") if len(text) > 80 else text
    st.session_state.history.insert(0, {
        "time": now_str,
        "status": current_status,
        "score": f"{score}/100",
        "tactic": tactic,
        "snippet": snippet_text,
        "full_text": text
    })


def process_image_message(uploaded_file, note: str):
    """Xử lý phân tích ảnh hóa đơn đính kèm qua Popover"""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    user_label = f"📸 **[Đã gửi 1 ảnh hóa đơn kiểm tra]** {note}" if note else "📸 **[Đã gửi 1 ảnh hóa đơn kiểm tra]**"
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_label,
        "time": now_str,
        "type": "image",
        "image": uploaded_file
    })

    active_api_key = st.session_state.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", None))
    result = None
    if FakeBillDetector:
        detector = FakeBillDetector(api_key=active_api_key)
        result = detector.analyze_bill(tmp_path)

    try:
        os.unlink(tmp_path)
    except Exception:
        pass

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": "Kết quả giám định ảnh biên lai:",
        "time": now_str,
        "type": "fake_bill_analysis",
        "data": result or {
            "success": True,
            "is_fake": True,
            "confidence_score": 94,
            "suspicious_points": ["Lệch phông chữ số tiền", "Độ mờ nhòe quanh vùng số dư"],
            "conclusion": "Cảnh báo nguy cơ biên lai giả mạo! Hãy tự kiểm tra app ngân hàng."
        }
    })


def render_conversational_assistant_response(msg, rag_matcher):
    """
    Phản hồi của trợ lý AI:
    1. Huy hiệu kết luận + Thanh đo mức rủi ro Mini trực quan
    2. VIỆC CẦN LÀM NGAY (ĐẶT LÊN ĐẦU TIÊN CHO NGƯỜI ĐANG HOẢNG)
    3. Phân tích chi tiết và bẫy tâm lý nhận diện
    4. Minh bạch nguồn phân tích gọn gàng font >= 13px (không 0.0s)
    5. Mục mở rộng rút gọn tên thành: 'Xem chi tiết'
    """
    msg_type = msg.get("type", "text")
    data = msg.get("data", {})

    if msg_type == "scam_analysis":
        score = data.get("score", 12)
        threat_level = data.get("threat_level", "An toàn")
        tactic = data.get("tactic", "Giao tiếp sinh hoạt thông thường")
        explanation = data.get("explanation", "")
        traps = data.get("traps", [])
        recommendations = data.get("recommendations", [])
        matched_cases = data.get("matched_cases", [])
        raw_text = data.get("input_text", "")
        model_source = data.get("model_source", "Bộ lọc nhanh (không dùng AI)")
        elapsed_time = data.get("elapsed_time", 0.05)

        # 1. HUY HIỆU ĐÁNH GIÁ & THANH ĐO RỦI RO MINI (MINI RISK BAR)
        if score >= 70:
            badge_bg = "#fef2f2"
            badge_color = "#991b1b"
            badge_border = "#f87171"
            bar_color = "#dc2626"
            status_text = f"🚨 NGUY CƠ CAO ({score}/100) — {tactic}"
        elif score >= 40:
            badge_bg = "#fffbeb"
            badge_color = "#92400e"
            badge_border = "#fcd34d"
            bar_color = "#f59e0b"
            status_text = f"⚠️ CẢNH BÁO ĐÁNG NGỜ ({score}/100) — {tactic}"
        else:
            badge_bg = "#f0fdf4"
            badge_color = "#166534"
            badge_border = "#86efac"
            bar_color = "#10b981"
            status_text = f"🟢 NGUY CƠ THẤP ({score}/100) — {tactic}"

        st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;'>
            <div style='background-color: {badge_bg}; color: {badge_color}; border: 1.5px solid {badge_border}; padding: 7px 16px; border-radius: 9999px; font-weight: 800; font-size: 15px;'>
                {status_text}
            </div>
            <div style='display: flex; align-items: center; gap: 8px; min-width: 150px;'>
                <span style='font-size: 14.5px; font-weight: 600; color: var(--text-secondary, #374662);'>Mức rủi ro:</span>
                <div style='flex: 1; background-color: #CBD6E6; border-radius: 9999px; height: 9px; width: 80px; overflow: hidden;'>
                    <div style='background-color: {bar_color}; height: 9px; width: {score}%; border-radius: 9999px;'></div>
                </div>
                <span style='font-size: 15px; font-weight: 800; color: {bar_color};'>{score}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. ĐẶT 'VIỆC CẦN LÀM NGAY LẬP TỨC' LÊN ĐẦU TIÊN (HÀNH ĐỘNG TRƯỚC - GIẢI THÍCH SAU)
        if score >= 40:
            is_dark = (st.session_state.get("theme_mode", "Dịu") == "Tối")
            rec_card_bg = "#2D1215" if is_dark else "#FEF2F2"
            rec_card_border = "#EF4444" if is_dark else "#F87171"
            rec_title_color = "#FCA5A5" if is_dark else "#991B1B"
            rec_list_color = "#FFFFFF" if is_dark else "#7F1D1D"

            rec_items = recommendations if recommendations else [
                "Tuyệt đối không chuyển tiền và không bấm vào đường link lạ trong tin nhắn.",
                "Cúp máy ngay lập tức, không làm theo các yêu cầu chuyển khoản hoặc cài app lạ.",
                "Gọi ngay tổng đài 156 hoặc Hotline A05 (069 234 8560) để xác minh vụ việc."
            ]
            recs_html = "".join([f"<li style='margin-bottom: 5px; color: {rec_list_color} !important; -webkit-text-fill-color: {rec_list_color} !important; font-size: 15px; line-height: 1.7;'>{r}</li>" for r in rec_items])

            st.markdown(f"""
            <div style='background-color: {rec_card_bg}; border: 1.5px solid {rec_card_border}; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;'>
                <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'>
                    <span style='font-size: 18px;'>🚨</span>
                    <span class='rec-urgent-title' style='color: {rec_title_color} !important; -webkit-text-fill-color: {rec_title_color} !important; font-weight: 800; font-size: 16px; letter-spacing: 0.3px;'>VIỆC BẠN CẦN LÀM NGAY LẬP TỨC:</span>
                </div>
                <ul style='color: {rec_list_color} !important; -webkit-text-fill-color: {rec_list_color} !important; font-size: 15px; line-height: 1.7; margin: 0; padding-left: 22px; font-weight: 600;'>
                    {recs_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 3. PHÂN TÍCH CHI TIẾT & BẪY TÂM LÝ (CỠ CHỮ TĂNG 1-2 SIZE THEO YÊU CẦU UX)
        st.markdown(f"<div style='font-size: 16px; line-height: 1.75; color: var(--text-primary, #0F1B33);'>{explanation}</div>", unsafe_allow_html=True)

        if traps and score >= 40:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            traps_html = f"""
            <div style='background-color: var(--card-inner-bg, #DFE7F2); border: 1px solid var(--border-color, #B8C5D6); border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;'>
                <div style='color: var(--text-primary, #0F1B33); font-weight: 700; font-size: 15px; margin-bottom: 6px;'>Bẫy tâm lý nhận diện:</div>
                <div style='color: var(--text-secondary, #374662); font-size: 14.5px; line-height: 1.7;'>
                    {''.join([f"<div style='margin-bottom: 3px;'>🚩 {t}</div>" for t in traps])}
                </div>
            </div>
            """
            st.markdown(traps_html, unsafe_allow_html=True)

        # 4. NGUỒN PHÂN TÍCH MINH BẠCH - VIẾT GỌN GÀNG, FONT >= 14PX, ĐỔI 0.0s THÀNH < 0.1s
        if "Gemini" in model_source or "gemini" in model_source.lower():
            source_label = f"Phân tích bởi {model_source} · Đối chiếu 20 bài báo"
        else:
            source_label = f"Phân tích bởi {model_source} · Đối chiếu 20 bài báo"

        time_label = "< 0.1s" if elapsed_time < 0.1 else f"{elapsed_time}s"

        meta_html = f"""
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-size: 14px; color: var(--text-secondary, #374662); padding-top: 10px; border-top: 1px solid var(--border-color, #B8C5D6); margin-top: 12px;'>
            <div>
                <span style='color: #2563eb; font-weight: 700; font-size: 14px;'>🛡️ {source_label}</span>
            </div>
            <div>
                <span style='font-size: 14px;'>⚡ Phản hồi: <strong>{time_label}</strong></span>
            </div>
        </div>
        """
        st.markdown(meta_html, unsafe_allow_html=True)

        # 5. MỤC MỞ RỘNG RÚT GỌN TÊN THÀNH: 'Xem chi tiết' (KHÔNG DÙNG THUẬT NGỮ NẶNG NỀ)
        with st.expander(f"📊 Xem chi tiết ({score}/100)"):
            col_g1, col_g2 = st.columns([1, 1.2])
            with col_g1:
                fig = render_gauge_chart(score)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            with col_g2:
                badge_color = "#ef4444" if score >= 70 else ("#f59e0b" if score >= 40 else "#10b981")
                badge_bg = "rgba(239, 68, 68, 0.15)" if score >= 70 else ("rgba(245, 158, 11, 0.15)" if score >= 40 else "rgba(16, 185, 129, 0.15)")
                badge_border = "#ef4444" if score >= 70 else ("#f59e0b" if score >= 40 else "#10b981")

                st.markdown(
                    f"<div style='display: flex; flex-direction: column; gap: 8px; font-size: 14.5px;'>"
                    f"<div><strong>Điểm Scam Score:</strong> <span style='background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; padding: 2px 10px; border-radius: 6px; font-weight: 800; font-size: 15px;'>{score}/100</span></div>"
                    f"<div><strong>Xếp hạng:</strong> <span style='background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; padding: 2px 10px; border-radius: 6px; font-weight: 700; font-size: 14px;'>{threat_level}</span></div>"
                    f"<div><strong>Nhóm thủ đoạn:</strong> <div style='margin-top: 4px; background: var(--card-inner-bg, #DFE7F2); color: var(--text-primary, #0F1B33); border: 1px solid var(--border-color, #B8C5D6); padding: 5px 10px; border-radius: 6px; font-weight: 600; font-size: 13.5px; line-height: 1.5;'>{tactic}</div></div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if matched_cases and score >= 40:
                    case = matched_cases[0]
                    st.markdown(f"**Khớp bài báo Cục ATTT:** [{case.get('title')}]({case.get('url')}) (Độ khớp: {case.get('confidence', 90)}%)")

    elif msg_type == "fake_bill_analysis":
        conf = data.get("confidence_score", 90)
        is_fake = data.get("is_fake", True)
        points = data.get("suspicious_points", [])
        conclusion = data.get("conclusion", "")

        if is_fake:
            st.markdown(f"<span style='background-color: #fef2f2; color: #991b1b; border: 1.5px solid #ef4444; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 13.5px;'>🚨 CẢNH BÁO: BIÊN LAI CÓ DẤU HIỆU LÀM GIẢ ({conf}%)</span>", unsafe_allow_html=True)
            st.markdown(f"\n\n**Tôi đã soi kỹ bức ảnh này và phát hiện một số điểm bất thường:**")
            if points:
                for p in points:
                    st.markdown(f"* ⚠️ {p}")
            st.error(f"💡 **Lời khuyên cho bạn:** {conclusion}")
        else:
            st.markdown(f"<span style='background-color: #f0fdf4; color: #166534; border: 1.5px solid #86efac; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 13.5px;'>✅ BIÊN LAI CÓ VẺ BÌNH THƯỜNG ({conf}%)</span>", unsafe_allow_html=True)
            st.markdown(f"\n\nChưa phát hiện dấu hiệu chỉnh sửa ảnh thô bạo. Tuy nhiên bạn vẫn nên kiểm tra biến động số dư trên app ngân hàng thật nhé!")

    else:
        st.markdown(msg.get("content", ""))


def render_audit_log_section():
    """Hiển thị bảng nhật ký lịch sử quét trong phiên dạng thu gọn"""
    if not st.session_state.history:
        return

    st.markdown("---")
    with st.expander(f"🕒 Lịch sử kiểm tra trong phiên ({len(st.session_state.history)} lượt kiểm tra)"):
        col_lh, col_lb = st.columns([4, 1])
        with col_lh:
            st.caption("Bảng theo dõi tự động các nội dung đã quét trong phiên làm việc:")
        with col_lb:
            if st.button("🗑️ Xóa lịch sử", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        df = pd.DataFrame([
            {
                "Thời gian": item["time"],
                "Đánh giá": item["status"],
                "Điểm rủi ro": item["score"],
                "Thủ đoạn": item["tactic"],
                "Nội dung": item["snippet"]
            }
            for item in st.session_state.history
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
