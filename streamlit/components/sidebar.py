"""
Component: sidebar.py
Thanh điều hướng bên trái: Cấu hình Trợ năng Người lớn tuổi & Kịch bản thử nghiệm nhanh.
"""

import streamlit as st


def render_sidebar():
    """Hiển thị Sidebar và trả về (elderly_mode, selected_zoom)"""
    with st.sidebar:
        st.markdown("### ⚙️ Trợ Năng & Giám Sát")
        elderly_mode = st.toggle("👵 Chế độ Người Lớn Tuổi (Trợ năng)", value=False)
        selected_zoom = "1.20"

        if elderly_mode:
            zoom_opt = st.radio(
                "Mức độ phóng đại:",
                options=["115% (Vừa vặn)", "120% (Cân bằng ⭐ Khuyên dùng)", "128% (Chữ lớn)"],
                index=1
            )
            if "115%" in zoom_opt:
                selected_zoom = "1.15"
            elif "128%" in zoom_opt:
                selected_zoom = "1.28"
            else:
                selected_zoom = "1.20"

            st.caption(f"👓 Đang hiển thị ở mức phóng to **{zoom_opt.split(' ')[0]}**.")

        st.markdown("### 🔑 Cấu Hình Mô Hình AI")
        with st.expander("Gemini API Key (Tùy chọn)", expanded=False):
            api_key_val = st.text_input(
                "Nhập Gemini API Key:",
                value=st.session_state.get("gemini_api_key", ""),
                type="password",
                placeholder="Dán AI Studio Key (AIzaSy...)",
                help="Dùng để kết nối trực tiếp mô hình gemini-3.8-flash & gemini-4 của nhóm"
            )
            if api_key_val and api_key_val.strip() != "":
                st.session_state.gemini_api_key = api_key_val.strip()
                import os
                os.environ["GEMINI_API_KEY"] = api_key_val.strip()
                st.success("✅ Đã kích hoạt Gemini 3.8 Flash & Gemini 4!")
            else:
                st.caption("⚡ Mặc định: Bộ tính điểm rủi ro hành vi đa tiêu chí động.")

        st.markdown("---")
        st.markdown("### ⚡ Kịch Bản Thử Nghiệm Nhanh")
        st.caption("Bấm chọn kịch bản để bắn trực tiếp vào khung đàm thoại AI:")

        sample_scenarios = {
            "🚨 Giả danh Công an dọa bắt": (
                "Tôi là Đại úy Nguyễn Văn Hùng, Cán bộ Điều tra Cục Cảnh sát Hình sự. "
                "Hiện tài khoản ngân hàng của anh/chị đang dính líu vào đường dây rửa tiền xuyên quốc gia trị giá 40 tỷ đồng. "
                "Yêu cầu anh/chị giữ bí mật tuyệt đối trong vòng 24h, ngay lập tức chuyển toàn bộ số dư 150 triệu vào số tài khoản an toàn "
                "của Cơ quan Điều tra để tiến hành thanh tra tài chính, nếu không chấp hành sẽ có lệnh bắt tạm giam ngay trong chiều nay!"
            ),
            "💼 Tuyển CTV Shopee hoa hồng 40%": (
                "Chào bạn! Bên mình đang cần tuyển gấp 5 bạn làm Cộng tác viên đánh giá sản phẩm Shopee/TikTok tại nhà. "
                "Công việc rất nhẹ nhàng, chỉ cần xem video bấm like nhận hoa hồng 30% - 50% mỗi ngày, kiếm 500k - 1 triệu. "
                "Số lượng có hạn, bạn chỉ cần nạp 200k tiền cọc kích hoạt nhiệm vụ đầu tiên để rút ngay 350k tiền lãi về tài khoản. "
                "Nhấn vào nhóm Telegram: https://t.me/tuyen-dung-shopee-vip để nhận việc ngay!"
            ),
            "🚗 Phạt nguội CSGT dán link độc": (
                "CUC CSGT THONG BAO: Phuong tien BKS 29A-888.88 da vi pham Chay qua toc do vao ngay 15/10 tai Km45 Cao toc. "
                "Yeu cau chu phuong tien truy cap ngay vao cong thong tin: http://tra-cuu-phat-nguoi.csgt-online.xyz "
                "de nop phat trong ngay hom nay, qua han se tien hanh huy dang kiem va tuoc giay phep lai xe vinh vien."
            ),
            "🏦 Bẫy khóa tài khoản đòi mã OTP": (
                "[VIETCOMBANK CANH BAO]: Phat hien giao dich bat thuong 25,000,000 VND luc 02:15. "
                "Tai khoan cua quy khach tam thoi bi khoa de bao ve. "
                "De mo khoa va xac thuc sinh trac hoc khan cap, vui long truy cap: http://vietcombank-xac-thuc.top "
                "va nhap ma OTP duoc gui ve dien thoai cua ban."
            ),
            "☕ Tin nhắn bạn bè bình thường": (
                "Alo mày ơi, tối nay tầm 7h rảnh không tao với mấy đứa qua quán cà phê Acoustic ở đường Nguyễn Trãi ngồi tí nhé. "
                "Hôm nay tao vừa nhận lương xong, để tao bao chầu này nhé, nhớ qua sớm giữ bàn nha!"
            )
        }

        for label, text_content in sample_scenarios.items():
            if st.button(label, use_container_width=True):
                st.session_state.input_text = text_content
                st.session_state.has_analyzed = True
                st.session_state.trigger_animation = True

    return elderly_mode, selected_zoom
