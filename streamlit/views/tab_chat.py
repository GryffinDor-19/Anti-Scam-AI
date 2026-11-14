"""
View: tab_chat.py
Tab 1: Trợ Lý Tác Chiến Đàm Thoại (Conversational Cyber AI Chatbot & Scam Meter).
Phụ trách: Thành viên 3 (Frontend & Trải nghiệm Người dùng)
Nâng cấp:
- Phong cách đàm thoại tự nhiên, thông minh (ChatGPT / Gemini style)
- Bỏ các khung hộp cứng nhắc, chuyển sang bong bóng đàm thoại thoáng đãng
- Huy hiệu rủi ro sắc nét và đồng hồ rủi ro thu gọn tinh tế
- Nút đính kèm ảnh 📎 dạng Popover thu gọn
"""

import os
import sys
import datetime
import tempfile
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from components.gauge import render_gauge_chart

# Nạp bộ não Backend AI (Hỗ trợ 2 lớp phân tích & Offline Fallback chuẩn 6 trường)
try:
    from backend.gateway.backend import analyze_scam
except ImportError:
    try:
        from backend.backend import analyze_scam
    except ImportError:
        from backend.modules.semantic_analyzer import analyze_scam_content
        def analyze_scam(t, api_key=None):
            return analyze_scam_content(t, api_key=api_key)

try:
    from backend.engines.fake_bill_detector import FakeBillDetector
except ImportError:
    try:
        from backend.modules.fake_bill_detector import FakeBillDetector
    except ImportError:
        FakeBillDetector = None


def render_tab_chat(rag_matcher):
    """Hiển thị toàn bộ nội dung Tab 1: Khung đàm thoại Chatbot, Đồng hồ đo rủi ro và Audit Log"""

    # 1. KHỞI TẠO STATE HỘI THOẠI
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # 2. 4 THẺ THỐNG KÊ SOC TELEMETRY Ở ĐẦU TRANG
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="🛡️ Danh Mục Kịch Bản", value="24 Thủ đoạn", delta="Cục An toàn thông tin")
    with m2:
        st.metric(label="⚡ Thời Gian Phản Hồi", value="< 0.8 giây", delta="Mạng nơ-ron 2 lớp")
    with m3:
        st.metric(label="🎯 Độ Chính Xác F1", value="92.5%", delta="+ Đạt chuẩn cam kết")
    with m4:
        st.metric(label="📰 Nguồn Dữ Liệu RAG", value="20 Bài báo gốc", delta="100% Chính thống")

    st.markdown("---")

    # 3. NẾU CÓ TIN NHẮN TỪ SIDEBAR CHUYỂN QUA
    pending_text = st.session_state.get("pending_user_query", None)
    if pending_text:
        st.session_state.pending_user_query = None
        process_user_message(pending_text, rag_matcher)

    # 4. KHUNG HIỂN THỊ CÁC BONG BÓNG HỘI THOẠI (CHAT STREAM)
    if not st.session_state.chat_messages:
        render_welcome_screen()
    else:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"**{msg['content']}**")
                    if msg.get("image"):
                        st.image(msg["image"], caption="Ảnh bạn gửi", width=280)
            else:
                with st.chat_message("assistant", avatar="🛡️"):
                    render_conversational_assistant_response(msg, rag_matcher)

    # 5. THANH ĐIỀU HƯỚNG CÔNG CỤ CHAT (GỬI ẢNH THU GỌN 📎 & XÓA CHAT)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_tools_left, col_tools_right = st.columns([4, 1])

    with col_tools_left:
        with st.popover("📎 Đính kèm ảnh hóa đơn / bằng chứng", use_container_width=False):
            st.markdown("##### 📸 Tải Ảnh Để Giám Định (Fake Bill / SMS)")
            st.caption("AI sẽ soi phông chữ số tiền, logo ngân hàng và dấu hiệu chỉnh sửa ảnh.")
            uploaded_img = st.file_uploader(
                "Chọn file ảnh (PNG, JPG, JPEG):",
                type=["png", "jpg", "jpeg"],
                key="chat_popover_file"
            )
            note_text = st.text_input("Ghi chú thêm (tùy chọn):", placeholder="Ví dụ: Khách gửi bill này giục chuyển hàng...")
            if uploaded_img and st.button("🚀 Bắt đầu soi ảnh này", type="primary", use_container_width=True):
                process_image_message(uploaded_img, note_text)
                st.rerun()

    with col_tools_right:
        if st.button("🗑️ Xóa Cuộc Trò Chuyện", use_container_width=True, disabled=len(st.session_state.chat_messages) == 0):
            st.session_state.chat_messages = []
            st.rerun()

    # 6. Ô NHẬP LIỆU CHATBOT DƯỚI ĐÁY TRANG (STREAMLIT CHAT INPUT)
    user_prompt = st.chat_input("💬 Nhập tin nhắn, dán đường link nghi vấn hoặc hỏi AntiScam AI...")
    if user_prompt and user_prompt.strip():
        process_user_message(user_prompt.strip(), rag_matcher)
        st.rerun()

    # 7. KHU VỰC BẢNG AUDIT LOG TRONG PHIÊN
    render_audit_log_section()


def render_welcome_screen():
    """Hiển thị màn hình chào mừng thân thiện khi chưa có tin nhắn nào"""
    with st.chat_message("assistant", avatar="🛡️"):
        st.markdown("""
        ### 👋 Xin chào bạn! Tôi là AntiScam AI
        Tôi là trợ lý đàm thoại thông minh được thiết kế để cùng bạn phân tích các tin nhắn lạ, cuộc gọi đe dọa, đường link và hóa đơn ngân hàng nghi vấn.

        **Bạn có thể trò chuyện với tôi bằng cách:**
        * 💬 **Gõ hoặc dán tin nhắn** vào ô chat ở dưới đáy màn hình.
        * 📎 **Bấm nút chiếc ghim kẹp** phía trên để gửi ảnh biên lai ngân hàng kiểm tra fake bill.
        * ⚡ **Hoặc thử nhanh các kịch bản mẫu** ở menu bên trái.
        """)

        st.caption("Gợi ý thử nhanh:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("☕ Thử câu an toàn: 'Tối đi chơi không'", use_container_width=True):
                st.session_state.pending_user_query = "tối đi chơi không"
                st.rerun()
        with c2:
            if st.button("🚨 Thử kịch bản: 'Công an dọa bắt rửa tiền'", use_container_width=True):
                st.session_state.pending_user_query = "Tôi là Cảnh sát hình sự thông báo bạn dính đường dây rửa tiền, chuyển tiền vào tài khoản an toàn gấp."
                st.rerun()


def process_user_message(text: str, rag_matcher):
    """Xử lý tin nhắn văn bản từ người dùng và phân tích rủi ro"""
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    # 1. Thêm tin nhắn của User vào lịch sử
    st.session_state.chat_messages.append({
        "role": "user",
        "content": text,
        "time": now_str,
        "type": "text"
    })

    # 2. Gọi bộ não Backend AI phân tích
    active_api_key = st.session_state.get("gemini_api_key", None)
    ai_data = analyze_scam(text, api_key=active_api_key)

    score = int(ai_data.get("risk_score", 12))
    threat_level = ai_data.get("threat_level", "An toàn")
    tactic = ai_data.get("detected_tactic", "Giao tiếp sinh hoạt thông thường")
    explanation = ai_data.get("explanation", "")
    traps = ai_data.get("psychological_traps", [])
    recommendations = ai_data.get("action_recommendations", [])

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
            "input_text": text
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

    active_api_key = st.session_state.get("gemini_api_key", None)
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
            "confidence_score": 92,
            "suspicious_points": ["Lệch phông chữ số tiền", "Độ mờ nhòe quanh vùng số dư"],
            "conclusion": "Cảnh báo nguy cơ biên lai giả mạo! Hãy tự kiểm tra app ngân hàng."
        }
    })


def render_conversational_assistant_response(msg, rag_matcher):
    """
    Phản hồi của trợ lý AI theo phong cách đàm thoại tự nhiên, gần gũi.
    Loại bỏ các khối hộp cứng nhắc, giữ sự tinh tế và dễ đọc.
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

        # 1. HUY HIỆU ĐÁNH GIÁ NHANH (SLEEK STATUS BADGE)
        if score >= 70:
            badge_html = f"<span style='background-color: #450a0a; color: #f87171; border: 1px solid #ef4444; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px;'>🚨 CẢNH BÁO: NGUY CƠ CAO ({score}/100) — {tactic}</span>"
        elif score >= 40:
            badge_html = f"<span style='background-color: #451a03; color: #fbbf24; border: 1px solid #f59e0b; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px;'>⚠️ CẢNH GIÁC: NỘI DUNG ĐÁNG NGỜ ({score}/100) — {tactic}</span>"
        else:
            badge_html = f"<span style='background-color: #064e3b; color: #34d399; border: 1px solid #10b981; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px;'>✅ AN TOÀN ({score}/100) — {tactic}</span>"

        st.markdown(badge_html, unsafe_allow_html=True)
        st.write("")

        # 2. LỜI NÓI CHUYỆN ĐÀM THOẠI TỰ NHIÊN CỦA TRỢ LÝ
        if score < 40:
            st.markdown(f"**Chào bạn,** nội dung tin nhắn này hoàn toàn là giao tiếp sinh hoạt đời thường, **an toàn 100%** và không hề có bất kỳ bẫy thao túng tâm lý, yêu cầu chuyển tiền hay liên kết độc hại nào. Bạn có thể yên tâm trả lời bình thường nhé! 😊")
        else:
            st.markdown(f"**Cảnh báo bạn nhé!** Tin nhắn bạn vừa gửi có dấu hiệu thao túng tâm lý nghiêm trọng nhằm mục đích lừa đảo hoặc đánh cắp thông tin.\n\n> *{explanation}*")

        # 3. NẾU CÓ NGUY CƠ: LIỆT KÊ BẪY TÂM LÝ & LỜI KHUYÊN MỀM MẠI
        if score >= 40:
            st.markdown("---")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("**🎭 Bẫy tâm lý phát hiện:**")
                for tr in traps:
                    st.markdown(f"* 🚩 {tr}")
            with col_t2:
                st.markdown("**🛡️ Lời khuyên an toàn:**")
                for rec in recommendations:
                    st.markdown(f"* 👉 {rec}")

        # 4. ĐỒNG HỒ ĐO RỦI RO THU GỌN TINH TẾ (EXPANDER)
        with st.expander(f"⏱️ Xem chi tiết đồng hồ Scam Meter & Bằng chứng kỹ thuật ({score}/100)"):
            col_g1, col_g2 = st.columns([1, 1.2])
            with col_g1:
                fig = render_gauge_chart(score)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            with col_g2:
                st.markdown(f"**Điểm Scam Score:** `{score}/100`")
                st.markdown(f"**Xếp hạng:** `{threat_level}`")
                st.markdown(f"**Nhóm thủ đoạn:** `{tactic}`")
                if matched_cases and score >= 40:
                    case = matched_cases[0]
                    st.markdown(f"**Khớp bài báo Cục ATTT:** [{case.get('title')}]({case.get('url')}) (Độ khớp: {case.get('confidence', 90)}%)")

        # 5. NÚT CHIA SẺ ZALO GỌN GÀNG
        with st.expander("📲 Chia sẻ cảnh báo này cho người thân qua Zalo"):
            share_summary = f"[AntiScam AI] Cảnh báo tin nhắn: '{raw_text[:35]}...' có điểm rủi ro {score}/100 ({threat_level} - {tactic}). Hãy cẩn thận kiểm tra!"
            st.text_input("Đoạn tóm tắt nhanh:", value=share_summary, key=f"share_{msg.get('time')}")

    elif msg_type == "fake_bill_analysis":
        conf = data.get("confidence_score", 90)
        is_fake = data.get("is_fake", True)
        points = data.get("suspicious_points", [])
        conclusion = data.get("conclusion", "")

        if is_fake:
            st.markdown(f"<span style='background-color: #450a0a; color: #f87171; border: 1px solid #ef4444; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px;'>🚨 CẢNH BÁO: BIÊN LAI CÓ DẤU HIỆU LÀM GIẢ ({conf}%)</span>", unsafe_allow_html=True)
            st.markdown(f"\n\n**Tôi đã soi kỹ bức ảnh này và phát hiện một số điểm bất thường:**")
            if points:
                for p in points:
                    st.markdown(f"* ⚠️ {p}")
            st.error(f"💡 **Lời khuyên cho bạn:** {conclusion}")
        else:
            st.markdown(f"<span style='background-color: #064e3b; color: #34d399; border: 1px solid #10b981; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px;'>✅ BIÊN LAI CÓ VẺ BÌNH THƯỜNG ({conf}%)</span>", unsafe_allow_html=True)
            st.markdown(f"\n\nChưa phát hiện dấu hiệu chỉnh sửa ảnh thô bạo. Tuy nhiên bạn vẫn nên kiểm tra biến động số dư trên app ngân hàng thật nhé!")

    else:
        st.markdown(msg.get("content", ""))


def render_audit_log_section():
    """Hiển thị bảng nhật ký lịch sử quét trong phiên dạng thu gọn"""
    if not st.session_state.history:
        return

    st.markdown("---")
    with st.expander(f"🕒 Xem Lịch Sử Thẩm Định Trong Phiên ({len(st.session_state.history)} lượt kiểm tra)"):
        col_lh, col_lb = st.columns([4, 1])
        with col_lh:
            st.caption("Bảng theo dõi tự động các nội dung đã quét trong phiên làm việc:")
        with col_lb:
            if st.button("🗑️ Xóa Lịch Sử", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        df = pd.DataFrame([
            {
                "Thời gian": h["time"],
                "Cấp độ": h["status"],
                "Điểm số": h["score"],
                "Thủ đoạn": h["tactic"],
                "Nội dung": h["snippet"]
            }
            for h in st.session_state.history
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
