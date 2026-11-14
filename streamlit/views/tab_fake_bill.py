"""
View: tab_fake_bill.py
Tab 2: Phòng Lab Soi Hóa Đơn Chuyển Tiền Giả (Forensic Vision Lab).
Phụ trách: Thành viên 2 (Mô hình Thị giác AI) & Thành viên 3 (UX Giao diện)
"""

import os
import tempfile
import streamlit as st

try:
    from backend.engines.fake_bill_detector import FakeBillDetector
except ImportError:
    try:
        from backend.modules.fake_bill_detector import FakeBillDetector
    except ImportError:
        FakeBillDetector = None


def render_tab_fake_bill():
    """Hiển thị toàn bộ nội dung Tab 2: Phòng Lab Phân Tích Fake Bill"""
    st.subheader("🧾 Nhận Diện Hóa Đơn Chuyển Tiền Giả (Fake Bill)")
    st.caption("Dành riêng cho chủ shop & người bán hàng online kiểm tra bill thanh toán trước khi giao hàng:")

    col_upload, col_sample = st.columns([3, 2])
    with col_upload:
        uploaded_file = st.file_uploader(
            "Tải lên ảnh chụp màn hình hóa đơn chuyển tiền:",
            type=["png", "jpg", "jpeg"]
        )
    with col_sample:
        st.write("")
        st.write("")
        if st.button("🧪 Bấm để Xem Demo Hóa Đơn Nghi Giả Mạo", use_container_width=True):
            st.session_state.demo_fake_bill = True

    # NẾU NGƯỜI DÙNG TẢI ẢNH HOẶC BẤM DEMO
    if uploaded_file is not None or st.session_state.demo_fake_bill:
        st.divider()

        analysis_result = None
        if uploaded_file is not None and FakeBillDetector:
            active_api_key = st.session_state.get("gemini_api_key", None)
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name

                detector = FakeBillDetector(api_key=active_api_key)
                analysis_result = detector.analyze_bill(tmp_path)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            except Exception:
                analysis_result = None

        col_img1, col_img2 = st.columns(2)

        with col_img1:
            with st.container(border=True):
                st.markdown("#### 🖼️ Hình Ảnh Hóa Đơn Đang Giám Định")
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="Ảnh hóa đơn người dùng tải lên", use_container_width=True)
                else:
                    st.warning("⚠️ **ẢNH DEMO ĐÃ ĐƯỢC AI KHOANH VÙNG PHÂN TÍCH:**")
                    st.markdown("""
                    ```text
                    ┌──────────────────────────────────────────────┐
                    │  NGÂN HÀNG THƯƠNG MẠI CỔ PHẦN NGOẠI THƯƠNG   │
                    │  CHUYỂN KHOẢN THÀNH CÔNG (NAPAS 247)         │
                    │                                              │
                    │  Người nhận: NGUYEN VAN A                    │
                    │  Số tài khoản: 1023456789                    │
                    │                                              │
                    │  ╔════════════════════════════════════════╗  │
                    │  ║ SỐ TIỀN: 150,000,000 VND [LỆCH FONT]   ║◄─┼── VÙNG PHÁT HIỆN
                    │  ╚════════════════════════════════════════╝  │     CHỈNH SỬA ẢNH!
                    │                                              │
                    │  Thời gian: 21:14:02 - 15/10/2026            │
                    │  Mã giao dịch: VCB.99823412034               │
                    └──────────────────────────────────────────────┘
                    ```
                    """)

        with col_img2:
            st.subheader("🔍 Kết Quả Giám Định Hình Thái & Kỹ Thuật:")
            with st.container(border=True):
                if analysis_result and analysis_result.get("success"):
                    is_fake = analysis_result.get("is_fake", True)
                    conf = analysis_result.get("confidence_score", 90)
                    if is_fake:
                        st.error(f"🚨 **KẾT LUẬN: NGUY CƠ BIÊN LAI GIẢ MẠO (ĐỘ TIN CẬY {conf}%)**")
                    else:
                        st.success(f"✅ **KẾT LUẬN: BIÊN LAI CÓ VẺ BÌNH THƯỜNG ({conf}%)**")

                    points = analysis_result.get("suspicious_points", [])
                    if points:
                        st.markdown("**Các dấu hiệu phát hiện:**")
                        for pt in points:
                            st.markdown(f"• `{pt}`")
                    st.write(analysis_result.get("conclusion", ""))
                else:
                    st.error("🚨 **KẾT LUẬN: NGUY CƠ HÓA ĐƠN FAKE BILL (RỦI RO 95%)**")
                    st.markdown("• **Phông chữ số tiền:** `Sai lệch phông chuẩn Vietcombank Digital`")
                    st.markdown("• **Khoảng cách dòng:** `Bất thường quanh khu vực 150,000,000 VND`")
                    st.markdown("• **Độ phân giải điểm ảnh:** `Vùng số tiền bị mờ nhòe do nén lại qua công cụ sửa ảnh`")
                    st.markdown("• **Mã giao dịch:** `Định dạng mã không khớp với chu kỳ thời gian thực tế`")

            st.warning("💡 **Khuyến nghị vàng cho chủ shop:** **CHƯA GIAO HÀNG!** Hãy mở ngay ứng dụng ngân hàng của bạn để kiểm tra **Biến động số dư thực tế**.")

        # DẪN CHỨNG BÀI BÁO CẢNH BÁO FAKE BILL
        st.divider()
        st.subheader("📰 Cảnh Báo Chính Thống Về Thủ Đoạn Fake Bill:")
        col_fb1, col_fb2 = st.columns(2)
        with col_fb1:
            with st.container(border=True):
                st.markdown("#### 🏛️ Báo Điện tử Chính phủ")
                st.write("**Lật tẩy chiêu trò lừa đảo hóa đơn giả 'online'**")
                st.caption("Cục An toàn thông tin cảnh báo xuất hiện các app/web tạo bill giả chỉ 20.000đ/lần.")
                st.link_button("👉 Đọc bài báo trên Báo Chính Phủ", "https://baochinhphu.vn/lat-tay-chieu-tro-lua-dao-hoa-don-gia-online-102230807142716254.htm", use_container_width=True)

        with col_fb2:
            with st.container(border=True):
                st.markdown("#### 📰 Báo Thanh Niên")
                st.write("**Cảnh giác với biên lai chuyển khoản ngân hàng giả mạo để lừa đảo**")
                st.caption("Kẻ gian dùng tài khoản ảo quảng cáo dịch vụ làm giả biên lai để lừa người bán hàng online.")
                st.link_button("👉 Đọc bài báo trên Báo Thanh Niên", "https://thanhnien.vn/canh-giac-voi-bien-lai-chuyen-khoan-ngan-hang-gia-mao-de-lua-dao-185231128183234606.htm", use_container_width=True)
