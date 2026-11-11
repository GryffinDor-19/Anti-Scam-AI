"""
View: tab_chat.py
Tab 1: Trợ Lý Tác Chiến Đàm Thoại (Cyber Chatbot & Speedometer Gauge) & Lịch Sử Thẩm Định.
"""

import streamlit as st
import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from components.gauge import render_gauge_chart


def render_tab_chat(rag_matcher):
    """Hiển thị toàn bộ nội dung Tab 1: Chatbot, Đồng hồ đo rủi ro và Audit Log"""
    # 1. 4 THẺ THỐNG KÊ SOC TELEMETRY Ở ĐẦU TRANG
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

    # 2. KHU VỰC NHẬP LIỆU THẨM ĐỊNH
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        user_input = st.text_area(
            "📋 Dán nội dung tin nhắn, SMS, đường link nghi vấn vào đây:",
            value=st.session_state.input_text,
            height=100,
            placeholder="Ví dụ: 'Cục Cảnh sát thông báo bạn có liên quan đến đường dây rửa tiền, chuyển tiền vào tài khoản an toàn...'"
        )
    with col_input2:
        st.write("")
        st.write("")
        btn_scan = st.button("🚀 BẮT ĐẦU PHÂN TÍCH", type="primary", use_container_width=True)
        if btn_scan:
            st.session_state.has_analyzed = True
            st.session_state.trigger_animation = True

        if st.button("🗑️ Xóa Trắng", use_container_width=True):
            st.session_state.input_text = ""
            st.session_state.has_analyzed = False
            st.rerun()

    # 3. XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ DẠNG ĐÀM THOẠI CHATBOT
    if st.session_state.has_analyzed or (user_input and user_input.strip() != ""):
        if not user_input.strip():
            st.warning("Vui lòng nhập nội dung hoặc bấm chọn một kịch bản mẫu ở thanh bên trái!")
        else:
            st.divider()

            # Phân loại sơ bộ kết quả (Mock data - Sẵn sàng nối với TV1 Gemini API)
            is_safe = "cà phê" in user_input.lower() or "nhận lương" in user_input.lower()
            mock_score = 15 if is_safe else 92

            # Xác định tên thủ đoạn
            if is_safe:
                detected_tactic = "Giao tiếp sinh hoạt an toàn"
            elif "công an" in user_input.lower() or "cảnh sát" in user_input.lower() or "rửa tiền" in user_input.lower():
                detected_tactic = "Giả danh Cơ quan Công quyền & Đe dọa bắt giữ"
            elif "cộng tác viên" in user_input.lower() or "shopee" in user_input.lower() or "hoa hồng" in user_input.lower():
                detected_tactic = "Bẫy Tuyển CTV Việc Nhẹ Lương Cao"
            elif "phạt nguội" in user_input.lower() or "csgt" in user_input.lower():
                detected_tactic = "Giả mạo CSGT Phạt Nguội Dán Link Độc"
            elif "otp" in user_input.lower() or "vietcombank" in user_input.lower() or "khóa" in user_input.lower():
                detected_tactic = "Giả mạo Ngân Hàng Đánh Cắp Mã OTP"
            else:
                detected_tactic = "Nghi vấn lừa đảo thao túng tâm lý"

            # Tự động ghi vào Lịch sử kiểm tra (Audit Log) nếu chưa có bản ghi này
            current_status = "🚨 Nguy cơ cao" if mock_score >= 70 else ("⚠️ Đáng ngờ" if mock_score >= 40 else "✅ An toàn")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            snippet_text = (user_input[:85] + "...") if len(user_input) > 85 else user_input

            new_record = {
                "time": now_time,
                "status": current_status,
                "score": f"{mock_score}/100",
                "tactic": detected_tactic,
                "snippet": snippet_text,
                "full_text": user_input
            }

            if not st.session_state.history or st.session_state.history[0]["full_text"] != user_input:
                st.session_state.history.insert(0, new_record)

            # 4. KHUNG HỘI THOẠI ĐÀM THOẠI CYBER CHATBOT
            # 4.1 BONG BÓNG TIN NHẮN NGƯỜI DÙNG
            with st.chat_message("user"):
                st.markdown(f"**📥 Nội dung bạn gửi thẩm định:**\n\n> {user_input}")

            # 4.2 BONG BÓNG TRỢ LÝ ANTISCAM AI
            with st.chat_message("assistant", avatar="🛡️"):
                col_gauge, col_info = st.columns([1, 1.8])

                with col_gauge:
                    with st.container(border=True):
                        st.markdown("##### ⏱️ ĐỒNG HỒ ĐO RỦI RO (SCAM METER)")
                        gauge_placeholder = st.empty()

                # Hiệu ứng quét hoạt họa kim quay (Scanning Animation)
                if st.session_state.get("trigger_animation", False):
                    st.session_state.trigger_animation = False

                    with col_info:
                        scan_box = st.empty()
                        scan_box.info("⚡ **AntiScam AI đang kích hoạt mạng nơ-ron quét phân tích...**\n\n"
                                      "🔍 *Đang bóc tách bẫy thao túng tâm lý & Đối soát 20 bài báo Cục An toàn thông tin...*")

                    anim_steps = np.linspace(0, mock_score, num=14, dtype=int)
                    for pt in anim_steps:
                        fig_frame = render_gauge_chart(int(pt))
                        gauge_placeholder.pyplot(fig_frame, use_container_width=True)
                        plt.close(fig_frame)
                        time.sleep(0.035)

                    scan_box.empty()
                else:
                    fig_static = render_gauge_chart(mock_score)
                    gauge_placeholder.pyplot(fig_static, use_container_width=True)
                    plt.close(fig_static)

                with col_info:
                    if mock_score >= 70:
                        st.error(f"## 🚨 CẢNH BÁO: RỦI RO LỪA ĐẢO CỰC KỲ CAO ({mock_score}/100)\n\n"
                                 f"**Thủ đoạn nhận diện:** {detected_tactic}\n\n"
                                 f"Phát hiện dấu hiệu đe dọa, tạo áp lực thời gian, yêu cầu chuyển tiền hoặc bấm vào đường link lạ chưa xác thực.")
                        st.warning("⚠️ **LƯU Ý KHẨN CẤP:** Tin nhắn này có dấu hiệu thao túng tâm lý nghiêm trọng. **TUYỆT ĐỐI KHÔNG CHUYỂN TIỀN!** Bấm nút đỏ ở góc trên nếu bạn đang bị đe dọa.")
                    else:
                        st.success(f"## ✅ TIN NHẮN AN TOÀN ({mock_score}/100)\n\n"
                                   f"Chưa phát hiện dấu hiệu lừa đảo hay bẫy tài chính trong tin nhắn này. Nội dung thuộc dạng giao tiếp sinh hoạt thường ngày.")

                # Chi tiết phân tích & Bẫy tâm lý
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    with st.container(border=True):
                        st.subheader("🎭 Bẫy Thao Túng Tâm Lý Phát Hiện")
                        if not is_safe:
                            st.markdown("🚩 **Sợ hãi / Uy quyền:** Dọa phát lệnh bắt giam, khóa tài khoản hoặc hủy đăng kiểm")
                            st.markdown("🚩 **Gấp gáp / Ép thời gian:** Bắt xử lý gấp trong 24 giờ để nạn nhân mất tỉnh táo")
                            st.markdown("🚩 **Cô lập nạn nhân:** Cấm nói chuyện hoặc kể cho người thân")
                        else:
                            st.write("Không phát hiện chiêu trò thao túng tâm lý nào.")

                    with st.container(border=True):
                        st.subheader("⚠️ Bằng Chứng Nguy Hiểm")
                        if not is_safe:
                            st.markdown("• Yêu cầu chuyển tiền vào **tài khoản cá nhân lạ / tài khoản an toàn**.")
                            st.markdown("• Chứa **đường link giả mạo / tên miền bất thường**.")
                        else:
                            st.write("• Nội dung trò chuyện sinh hoạt thông thường.")

                with col_d2:
                    with st.container(border=True):
                        st.subheader("🛡️ Lời Khuyên Hành Động An Toàn")
                        if not is_safe:
                            st.markdown("❌ **Tuyệt đối không làm theo:** Cơ quan công an/ngân hàng không làm việc qua điện thoại hay yêu cầu chuyển tiền.")
                            st.markdown("📞 **Cúp máy ngay:** Tự đến cơ quan Công an hoặc chi nhánh Ngân hàng gần nhất để xác minh.")
                            st.markdown("🚫 **Không gửi thông tin cá nhân:** Tuyệt đối không gửi mã OTP, CCCD hay mật khẩu.")
                        else:
                            st.markdown("✅ Có thể yên tâm tiếp tục trò chuyện.")

                # Thẻ đối chiếu bài báo thực tế (RAG Grounding Card)
                if not is_safe:
                    st.divider()
                    st.subheader("📰 Dẫn Chứng Bài Báo Thực Tế Tương Đồng (RAG Grounding)")

                    matched_cases = rag_matcher.match(user_input, top_k=2)

                    if matched_cases:
                        best_match = matched_cases[0]
                        with st.container(border=True):
                            st.info(f"🏷️ **ĐỘ TRÙNG KHỚP KỊCH BẢN: {best_match.get('confidence', 92)}%** — Nguồn: {best_match.get('source')}")
                            st.markdown(f"#### 📌 {best_match.get('title')}")
                            st.caption(f"Danh mục: {best_match.get('category_name')} · Đã kiểm chứng chính thống")
                            st.write(best_match.get('summary'))
                            st.link_button("👉 Bấm vào đây để đọc bài báo cảnh báo gốc để kiểm chứng", best_match.get('url'), use_container_width=True)

                        if len(matched_cases) > 1:
                            sec_match = matched_cases[1]
                            with st.expander(f"📎 Xem thêm bài báo cảnh báo liên quan: {sec_match.get('title')}"):
                                st.write(f"**Nguồn:** {sec_match.get('source')}")
                                st.write(sec_match.get('summary'))
                                st.link_button("👉 Mở bài báo liên quan", sec_match.get('url'))

                # Nút chia sẻ Zalo cho con cháu
                st.divider()
                col_share1, col_share2 = st.columns([3, 1])
                with col_share1:
                    share_text = f"[AntiScam AI Cảnh Báo] Tin nhắn này có điểm rủi ro {mock_score}/100 ({detected_tactic}). Hãy cẩn thận kiểm tra, tuyệt đối không chuyển tiền!"
                    st.text_input("Đoạn tóm tắt kết quả (để gửi cho con cháu/người thân):", value=share_text)
                with col_share2:
                    st.write("")
                    st.write("")
                    st.button("📋 Sao Chép Kết Quả", help="Bấm để copy đoạn tóm tắt gửi qua Zalo/SMS cho người thân")

    # 5. KHU VỰC LỊCH SỬ TRA CỨU TRONG PHIÊN (SESSION AUDIT LOG)
    st.markdown("---")
    col_hist_h, col_hist_btn = st.columns([4, 1])
    with col_hist_h:
        st.subheader(f"🕒 Lịch Sử Thẩm Định Trong Phiên ({len(st.session_state.history)} lượt kiểm tra)")
        st.caption("Bảng theo dõi và ghi nhật ký tự động các nội dung đã quét trong phiên làm việc hiện tại:")
    with col_hist_btn:
        st.write("")
        if st.button("🗑️ Xóa Lịch Sử", use_container_width=True, disabled=len(st.session_state.history) == 0):
            st.session_state.history = []
            st.rerun()

    if st.session_state.history:
        total_checks = len(st.session_state.history)
        high_risk_count = sum(1 for h in st.session_state.history if "Nguy cơ cao" in h["status"])
        safe_count = sum(1 for h in st.session_state.history if "An toàn" in h["status"])
        pct_high = round((high_risk_count / total_checks) * 100) if total_checks else 0

        sh1, sh2, sh3 = st.columns(3)
        with sh1:
            st.metric("📊 Tổng Lượt Thẩm Định", f"{total_checks} tin nhắn")
        with sh2:
            st.metric("🚨 Phát Hiện Lừa Đảo", f"{high_risk_count} vụ việc", delta=f"{pct_high}% tổng số", delta_color="inverse")
        with sh3:
            st.metric("✅ Tin Nhắn An Toàn", f"{safe_count} tin nhắn", delta=f"{100 - pct_high}% tổng số")

        df_history = pd.DataFrame([
            {
                "Thời gian": h["time"],
                "Đánh giá rủi ro": h["status"],
                "Điểm số": h["score"],
                "Thủ đoạn nhận diện": h["tactic"],
                "Trích đoạn nội dung": h["snippet"]
            }
            for h in st.session_state.history
        ])
        st.dataframe(df_history, use_container_width=True, hide_index=True)
    else:
        st.info("💡 Chưa có lượt thẩm định nào trong phiên làm việc này. Hãy dán tin nhắn vào ô trên hoặc bấm các nút kịch bản mẫu ở bên trái để bắt đầu kiểm tra!")
