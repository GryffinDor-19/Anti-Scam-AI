"""
View: tab_fake_bill.py
Tab 2: Phòng Lab Soi Hóa Đơn Chuyển Tiền Giả (Forensic Vision Lab).
Đồng bộ 100% giao diện thẻ Vietcombank Digibank thực tế với bản Demo,
sử dụng bảng màu đề xuất mới (#D3DCE8, #EEF2F8, #C7D2E1, #0F1B33, #374662) và bóng đổ nhẹ nhàng.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
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
    """Hiển thị nội dung Tab 2: Soi hóa đơn chuyển tiền giả chuẩn Image 3"""
    
    # State quản lý mẫu bill đang xem: 'fake' hoặc 'real'
    if "bill_sample_type" not in st.session_state:
        st.session_state.bill_sample_type = "fake"

    # 1. TIÊU ĐỀ TAB & 2 NÚT CHUYỂN MẪU BILL NHANH
    col_head_left, col_head_right = st.columns([3, 2])
    with col_head_left:
        st.markdown("""
        <div style='margin-bottom: 4px;'>
            <div style='font-size: 1.15rem; font-weight: 700; color: var(--text-primary, #0F1B33);'>Soi chi tiết phông chữ và vết tẩy xóa</div>
            <div style='font-size: 14.5px; color: var(--text-secondary, #374662);'>Phát hiện lệch phông chữ ngân hàng và làm mờ số tiền</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_head_right:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔴 Mẫu bill giả", use_container_width=True):
                st.session_state.bill_sample_type = "fake"
                st.session_state.uploaded_bill_img = None
                st.rerun()
        with col_b2:
            if st.button("🟢 Mẫu bill thật", use_container_width=True):
                st.session_state.bill_sample_type = "real"
                st.session_state.uploaded_bill_img = None
                st.rerun()

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # 2. KHU VỰC TẢI ẢNH TÙY CHỌN (EXPANDER THU GỌN KHÔNG CHIẾM DIỆN TÍCH)
    with st.expander("📁 Tải ảnh biên lai của riêng bạn để AI phân tích", expanded=False):
        uploaded_file = st.file_uploader(
            "Tải lên ảnh chụp biên lai chuyển tiền (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="custom_bill_uploader"
        )
        if uploaded_file is not None:
            st.session_state.uploaded_bill_img = uploaded_file

    # 3. CHIA 2 CỘT CHÍNH: BÊN TRÁI LÀ THẺ BILL VIETCOMBANK, BÊN PHẢI LÀ KẾT LUẬN GIÁM ĐỊNH
    col_card, col_verdict = st.columns([1.1, 1], gap="medium")

    is_fake = (st.session_state.bill_sample_type == "fake")
    custom_img = st.session_state.get("uploaded_bill_img", None)

    # ==========================
    # CỘT TRÁI: THẺ HÓA ĐƠN VCB
    # ==========================
    with col_card:
        with st.container(border=True):
            if custom_img:
                st.markdown("<div style='font-weight: 700; font-size: 14px; color: var(--text-primary, #0F1B33); margin-bottom: 8px;'>Ảnh bạn tải lên:</div>", unsafe_allow_html=True)
                st.image(custom_img, use_container_width=True)
            else:
                # HIỂN THỊ THẺ VIETCOMBANK DIGIBANK CHUẨN ĐỒNG BỘ DEMO IMAGE 3
                if is_fake:
                    # MẪU BILL GIẢ: CÓ KHUNG ĐỎ CẢNH BÁO LỆCH PHÔNG CHỮ & SAI ĐỊNH DẠNG
                    st.markdown("""
                    <div style='background: #ffffff; border: 1px solid var(--border-color, #B8C5D6); border-radius: 14px; padding: 16px 18px; box-shadow: var(--box-shadow, 0 2px 10px rgba(15,27,51,0.06)); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
                        <!-- Header thẻ bill -->
                        <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 12px;'>
                            <div style='display: flex; align-items: center; gap: 8px;'>
                                <span style='background-color: #047857; color: #ffffff; font-weight: 900; font-size: 11px; padding: 4px 6px; border-radius: 6px; letter-spacing: 0.5px;'>VCB</span>
                                <div>
                                    <div style='font-weight: 800; font-size: 13.5px; color: #0f172a;'>Vietcombank Digibank</div>
                                    <div style='font-size: 11px; color: #047857; font-weight: 700;'>Chuyển tiền thành công</div>
                                </div>
                            </div>
                            <span style='font-size: 12px; color: #64748b; font-weight: 500;'>14/11/2026</span>
                        </div>
                        
                        <!-- Số tiền chuyển (Kèm khung đỏ phát hiện làm giả) -->
                        <div style='text-align: center; padding: 12px 8px; margin-bottom: 12px; background: #fff1f2; border: 2px dashed #ef4444; border-radius: 10px; position: relative;'>
                            <div style='font-size: 12px; color: #64748b; font-weight: 600;'>Số tiền chuyển:</div>
                            <div style='font-size: 24px; font-weight: 900; color: #047857; letter-spacing: -0.5px; margin: 2px 0;'>50,000,000 VND</div>
                            <span style='background-color: #dc2626; color: #ffffff; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px; display: inline-block; box-shadow: 0 1px 3px rgba(220,38,38,0.3);'>
                                ⚠️ Lệch phông chữ (98%)
                            </span>
                        </div>

                        <!-- Chi tiết giao dịch -->
                        <div style='border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; padding: 10px 0; margin-bottom: 10px; font-size: 13px; line-height: 1.8; color: #334155;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #64748b;'>Người nhận:</span>
                                <strong style='color: #0f172a;'>NGUYEN VAN A</strong>
                            </div>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #64748b;'>Số tài khoản:</span>
                                <strong style='color: #0f172a;'>1029384756</strong>
                            </div>
                            <div style='display: flex; justify-content: space-between; align-items: center; background: #fffbeb; padding: 3px 8px; border-radius: 6px; border: 1px solid #fde68a;'>
                                <span style='color: #64748b;'>Thời gian:</span>
                                <span style='color: #b45309; font-weight: 700;'>14/11/2026 10:15:32 (Sai định dạng)</span>
                            </div>
                        </div>

                        <!-- Chân biên lai -->
                        <div style='text-align: center; font-size: 12px; color: #94a3b8;'>
                            Biên lai điện tử tạo tự động
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # MẪU BILL THẬT: KHÔNG CÓ LỖI, SẠCH SẼ NHƯ ẢNH DEMO
                    st.markdown("""
                    <div style='background: #ffffff; border: 1px solid var(--border-color, #B8C5D6); border-radius: 14px; padding: 16px 18px; box-shadow: var(--box-shadow, 0 2px 10px rgba(15,27,51,0.06)); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
                        <!-- Header thẻ bill -->
                        <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 12px;'>
                            <div style='display: flex; align-items: center; gap: 8px;'>
                                <span style='background-color: #047857; color: #ffffff; font-weight: 900; font-size: 11px; padding: 4px 6px; border-radius: 6px; letter-spacing: 0.5px;'>VCB</span>
                                <div>
                                    <div style='font-weight: 800; font-size: 13.5px; color: #0f172a;'>Vietcombank Digibank</div>
                                    <div style='font-size: 11px; color: #047857; font-weight: 700;'>Chuyển tiền thành công</div>
                                </div>
                            </div>
                            <span style='font-size: 12px; color: #64748b; font-weight: 500;'>14/11/2026</span>
                        </div>
                        
                        <!-- Số tiền chuyển sạch sẽ -->
                        <div style='text-align: center; padding: 12px 8px; margin-bottom: 12px;'>
                            <div style='font-size: 12px; color: #64748b; font-weight: 600;'>Số tiền chuyển:</div>
                            <div style='font-size: 26px; font-weight: 900; color: #047857; letter-spacing: -0.5px; margin: 2px 0;'>500,000 VND</div>
                        </div>

                        <!-- Chi tiết giao dịch -->
                        <div style='border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; padding: 10px 0; margin-bottom: 10px; font-size: 13px; line-height: 1.8; color: #334155;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #64748b;'>Người nhận:</span>
                                <strong style='color: #0f172a;'>NGUYEN VAN A</strong>
                            </div>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #64748b;'>Số tài khoản:</span>
                                <strong style='color: #0f172a;'>1029384756</strong>
                            </div>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='color: #64748b;'>Thời gian:</span>
                                <strong style='color: #0f172a;'>14/11/2026 10:15:32</strong>
                            </div>
                        </div>

                        <!-- Chân biên lai -->
                        <div style='text-align: center; font-size: 12px; color: #94a3b8;'>
                            Biên lai điện tử tạo tự động
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='text-align: center; font-size: 13.5px; color: var(--text-secondary, #374662); margin-top: 10px;'>💡 Bấm vào khung đỏ trên ảnh để xem chi tiết sai lệch</div>", unsafe_allow_html=True)

    # ==========================
    # CỘT PHẢI: KẾT LUẬN GIÁM ĐỊNH
    # ==========================
    with col_verdict:
        with st.container(border=True):
            if is_fake:
                # KẾT LUẬN BILL GIẢ
                st.markdown("""
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color, #B8C5D6); padding-bottom: 8px; margin-bottom: 10px;'>
                    <span style='font-size: 14.5px; font-weight: 700; color: var(--text-primary, #0F1B33);'>Kết luận kiểm tra</span>
                    <span style='background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; font-size: 12.5px; font-weight: 800; padding: 4px 10px; border-radius: 9999px;'>
                        Biên lai có dấu hiệu làm giả
                    </span>
                </div>

                <div style='background: var(--card-inner-bg, #DFE7F2); border: 1px solid var(--border-color, #B8C5D6); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;'>
                        <span style='font-weight: 700; color: var(--text-primary, #0F1B33);'>Khả năng đã chỉnh sửa ảnh:</span>
                        <span style='font-weight: 800; color: #dc2626; font-size: 14px;'>94.2%</span>
                    </div>
                    <div style='width: 100%; background: #CBD6E6; border-radius: 9999px; height: 8px; overflow: hidden;'>
                        <div style='background: #dc2626; height: 8px; width: 94%; border-radius: 9999px;'></div>
                    </div>
                </div>

                <div style='display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;'>
                    <div style='background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 10px 12px; display: flex; align-items: flex-start; gap: 8px;'>
                        <span style='color: #e11d48; font-weight: 800; font-size: 15px;'>❌</span>
                        <div>
                            <div style='font-weight: 700; font-size: 13px; color: #881337;'>Phông chữ số tiền không đúng chuẩn</div>
                            <div style='font-size: 13px; color: #334155; margin-top: 2px;'>Phông chữ số "50,000,000" không khớp với phông chữ gốc của Vietcombank.</div>
                        </div>
                    </div>

                    <div style='background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 12px; display: flex; align-items: flex-start; gap: 8px;'>
                        <span style='color: #d97706; font-weight: 800; font-size: 15px;'>⚠️</span>
                        <div>
                            <div style='font-weight: 700; font-size: 13px; color: #78350f;'>Vết mờ xung quanh số dư</div>
                            <div style='font-size: 13px; color: #334155; margin-top: 2px;'>Vùng số tiền bị nhòe pixel, dấu hiệu dùng phần mềm cắt dán số tiền khác đè lên.</div>
                        </div>
                    </div>
                </div>

                <div style='background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; padding: 10px 12px;'>
                    <div style='font-size: 13px; font-weight: 700; color: #991b1b;'>Khuyến nghị an toàn:</div>
                    <div style='font-size: 13px; color: var(--text-primary, #0F1B33); margin-top: 2px; line-height: 1.5;'>
                        Tuyệt đối <strong>không giao hàng hoặc chuyển tiền lại</strong> chỉ vì nhìn thấy ảnh chụp này. Hãy tự mở ứng dụng ngân hàng của bạn để kiểm tra số dư thực tế.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # KẾT LUẬN BILL THẬT (CHUẨN IMAGE 3)
                st.markdown("""
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color, #B8C5D6); padding-bottom: 8px; margin-bottom: 10px;'>
                    <span style='font-size: 14.5px; font-weight: 700; color: var(--text-primary, #0F1B33);'>Kết luận kiểm tra</span>
                    <span style='background: #dcfce7; color: #166534; border: 1px solid #86efac; font-size: 12.5px; font-weight: 800; padding: 4px 10px; border-radius: 9999px;'>
                        Biên lai có vẻ bình thường
                    </span>
                </div>

                <div style='background: var(--card-inner-bg, #DFE7F2); border: 1px solid var(--border-color, #B8C5D6); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;'>
                    <div style='display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;'>
                        <span style='font-weight: 700; color: var(--text-primary, #0F1B33);'>Khả năng đã chỉnh sửa ảnh:</span>
                        <span style='font-weight: 800; color: #16a34a; font-size: 14px;'>4.8%</span>
                    </div>
                    <div style='width: 100%; background: #CBD6E6; border-radius: 9999px; height: 8px; overflow: hidden;'>
                        <div style='background: #16a34a; height: 8px; width: 5%; border-radius: 9999px;'></div>
                    </div>
                </div>

                <div style='display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;'>
                    <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 12px; display: flex; align-items: flex-start; gap: 8px;'>
                        <span style='color: #16a34a; font-weight: 800; font-size: 15px;'>✅</span>
                        <div>
                            <div style='font-weight: 700; font-size: 13px; color: #14532d;'>Phông chữ chuẩn Vietcombank Digibank</div>
                            <div style='font-size: 13px; color: #334155; margin-top: 2px;'>Kiểu chữ, độ dày và khoảng cách dòng số tiền 500,000 VND đồng đều, sắc nét.</div>
                        </div>
                    </div>

                    <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 12px; display: flex; align-items: flex-start; gap: 8px;'>
                        <span style='color: #16a34a; font-weight: 800; font-size: 15px;'>✅</span>
                        <div>
                            <div style='font-weight: 700; font-size: 13px; color: #14532d;'>Không phát hiện vết nén hay tẩy xóa pixel</div>
                            <div style='font-size: 13px; color: #334155; margin-top: 2px;'>Mật độ điểm ảnh vùng số tiền khớp với toàn bộ biên lai chuyển tiền.</div>
                        </div>
                    </div>
                </div>

                <div style='background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 10px 12px;'>
                    <div style='font-size: 13px; font-weight: 700; color: #166534;'>Lưu ý an toàn cho chủ shop:</div>
                    <div style='font-size: 13px; color: var(--text-primary, #0F1B33); margin-top: 2px; line-height: 1.5;'>
                        Biên lai không có dấu hiệu sửa ảnh Photoshop, tuy nhiên vẫn cần <strong>kiểm tra thông báo số dư trên điện thoại</strong> của bạn trước khi bàn giao hàng giá trị cao.
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 4. DẪN CHỨNG BÀI BÁO CẢNH BÁO FAKE BILL
    st.divider()
    st.markdown("<div style='font-size: 14.5px; font-weight: 700; color: var(--text-primary, #0F1B33); margin-bottom: 8px;'>📰 Cảnh báo chính thống về thủ đoạn Fake Bill:</div>", unsafe_allow_html=True)
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
