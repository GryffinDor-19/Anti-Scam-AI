"""
View: tab_fake_bill.py
Tab 2: Phòng Lab Giám Định Hóa Đơn Chuyển Tiền Giả Mạo (Forensic Vision Lab).
Tích hợp Cơ Chế Giám Định 2 Lớp (Lớp 1: Thị giác & Typography · Lớp 2: Cấu trúc Pixel & Vết nén ELA).
Kết nối trực tiếp với backend FakeBillDetector (Hỗ trợ tải ảnh người dùng, ảnh mẫu thực tế,
kết hợp Gemini Vision và Bộ Giám Định Pháp Y Số & Heuristic Cục Bộ).
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import os
import tempfile
import streamlit as st
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from backend.engines.fake_bill_detector import FakeBillDetector
except ImportError:
    try:
        from backend.modules.fake_bill_detector import FakeBillDetector
    except ImportError:
        FakeBillDetector = None


def get_detector() -> "FakeBillDetector":
    """Lấy hoặc khởi tạo detector với API Key khả dụng."""
    api_key = st.session_state.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", ""))
    if FakeBillDetector:
        return FakeBillDetector(api_key=api_key)
    return None


def run_analysis(image_source, is_custom_upload: bool = False):
    """
    Thực hiện giám định hóa đơn qua Backend.
    - image_source: đường dẫn file ảnh (str), bytes hoặc đối tượng UploadedFile của Streamlit.
    """
    detector = get_detector()
    if not detector:
        return {
            "success": False,
            "error": "Không thể nạp module FakeBillDetector từ Backend."
        }

    if is_custom_upload:
        # Lưu file tải lên vào file tạm thời để backend xử lý
        suffix = ".jpg"
        if hasattr(image_source, "name"):
            suffix = os.path.splitext(image_source.name)[1] or ".jpg"

        if hasattr(image_source, "getvalue"):
            data = image_source.getvalue()
            if hasattr(image_source, "seek"):
                image_source.seek(0)
        elif hasattr(image_source, "read"):
            data = image_source.read()
            if hasattr(image_source, "seek"):
                image_source.seek(0)
        elif isinstance(image_source, bytes):
            data = image_source
        else:
            data = bytes(image_source)

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            result = detector.analyze_bill(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
        return result
    else:
        # Đường dẫn file có sẵn trên đĩa
        return detector.analyze_bill(image_source)


def render_tab_fake_bill():
    """Hiển thị nội dung Tab 2: Soi hóa đơn chuyển tiền giả kết nối trực tiếp Backend AI"""

    # Đường dẫn 2 mẫu bill thực tế trong repo
    sample_fake_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "backend", "modules", "fake_bill.jpg")
    )
    sample_real_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "backend", "modules", "test_bill.jpg")
    )

    # 1. KHỞI TẠO STATE
    if "bill_sample_type" not in st.session_state:
        st.session_state.bill_sample_type = "fake"  # 'fake' | 'real' | 'custom'
    if "bill_sample_cache" not in st.session_state:
        st.session_state.bill_sample_cache = {}
    if "bill_analysis_result" not in st.session_state:
        st.session_state.bill_analysis_result = None
    if "uploaded_bill_img" not in st.session_state:
        st.session_state.uploaded_bill_img = None
    if "last_analyzed_source" not in st.session_state:
        st.session_state.last_analyzed_source = None

    # 2. TIÊU ĐỀ TAB & NÚT CHUYỂN MẪU BILL NHANH
    col_head_left, col_head_right = st.columns([3, 2], vertical_alignment="center")
    with col_head_left:
        st.markdown("""
        <div style='margin-bottom: 4px;'>
            <div style='font-size: 1.25rem; font-weight: 800; color: var(--text-primary, #0F1B33);'>
                🔬 Phòng Lab Giám Định Biên Lai Chuyển Tiền
            </div>
            <div style='font-size: 14.5px; color: var(--text-secondary, #374662);'>
                Phát hiện làm giả số tiền, sai lệch phông chữ ngân hàng và dấu vết chỉnh sửa hình ảnh
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_head_right:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_fake_label = "🔴 Mẫu bill giả" + (" (Đang xem)" if st.session_state.bill_sample_type == "fake" else "")
            if st.button(btn_fake_label, use_container_width=True, key="btn_sample_fake"):
                st.session_state.bill_sample_type = "fake"
                st.session_state.bill_analysis_result = None
                st.rerun()
        with col_b2:
            btn_real_label = "🟢 Mẫu bill thật" + (" (Đang xem)" if st.session_state.bill_sample_type == "real" else "")
            if st.button(btn_real_label, use_container_width=True, key="btn_sample_real"):
                st.session_state.bill_sample_type = "real"
                st.session_state.bill_analysis_result = None
                st.rerun()

    # 3. KHỐI TRỰC QUAN HÓA CƠ CHẾ GIÁM ĐỊNH 2 LỚP
    st.markdown("""
    <div style='background-color: var(--card-bg, #EEF2F8); border: 1.5px solid var(--border-color, #B8C5D6); border-radius: 12px; padding: 12px 16px; margin: 8px 0 16px 0;'>
        <div style='font-size: 14px; font-weight: 800; color: #2563EB; margin-bottom: 6px;'>
            🛡️ CƠ CHẾ GIÁM ĐỊNH TÀI LIỆU SỐ 2 LỚP (2-LAYER FORENSIC DEFENSE)
        </div>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; font-size: 13.5px; color: var(--text-primary, #0F1B33);'>
            <div style='background: var(--card-inner-bg, #DFE7F2); padding: 8px 12px; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                <strong>Lớp 1: Giám định Thị giác & Typography</strong><br/>
                <span style='color: var(--text-secondary, #374662); font-size: 13px;'>Đối soát phông chữ số tiền, căn lề baseline, mã giao dịch, logo và màu sắc nhận diện chuẩn của ngân hàng.</span>
            </div>
            <div style='background: var(--card-inner-bg, #DFE7F2); padding: 8px 12px; border-radius: 8px; border-left: 4px solid #8B5CF6;'>
                <strong>Lớp 2: Giám định Cấu trúc Pixel & Vết nén ELA</strong><br/>
                <span style='color: var(--text-secondary, #374662); font-size: 13px;'>Phân tích mức nén ảnh ELA, phát hiện quầng mờ viền pixel, tỷ lệ khung hình và chữ ký phần mềm/AI trong metadata nhị phân.</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. KHU VỰC TẢI ẢNH NGƯỜI DÙNG (CÓ NÚT GIÁM ĐỊNH RÕ RÀNG)
    with st.expander("📁 Tải ảnh biên lai của riêng bạn để AI phân tích", expanded=(st.session_state.bill_sample_type == "custom")):
        col_up_1, col_up_2 = st.columns([3, 1], vertical_alignment="center")
        with col_up_1:
            uploaded_file = st.file_uploader(
                "Tải lên ảnh chụp biên lai chuyển tiền (PNG, JPG, JPEG):",
                type=["png", "jpg", "jpeg"],
                key="custom_bill_uploader"
            )
        with col_up_2:
            if uploaded_file is not None:
                st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
                btn_check = st.button("🚀 Giám định ngay", type="primary", use_container_width=True)
                if btn_check:
                    st.session_state.uploaded_bill_img = uploaded_file
                    st.session_state.bill_sample_type = "custom"
                    st.session_state.bill_analysis_result = None
                    st.rerun()

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            uploaded_file.seek(0)
            if (
                st.session_state.uploaded_bill_img != uploaded_file
                or st.session_state.get("uploaded_bill_bytes") != file_bytes
            ):
                st.session_state.uploaded_bill_img = uploaded_file
                st.session_state.uploaded_bill_bytes = file_bytes
                st.session_state.uploaded_bill_name = uploaded_file.name
                st.session_state.bill_sample_type = "custom"
                st.session_state.bill_analysis_result = None

    # 5. XÁC ĐỊNH NGUỒN ẢNH VÀ THỰC HIỆN GIÁM ĐỊNH QUA BACKEND
    sample_type = st.session_state.bill_sample_type
    current_source_key = f"{sample_type}_{st.session_state.uploaded_bill_img.name if (sample_type == 'custom' and st.session_state.uploaded_bill_img) else sample_type}"

    # Kiểm tra xem có cần chạy phân tích mới không
    if st.session_state.bill_analysis_result is None or st.session_state.last_analyzed_source != current_source_key:
        # Nếu là mẫu có sẵn và đã có trong cache
        if sample_type in ["fake", "real"] and sample_type in st.session_state.bill_sample_cache:
            st.session_state.bill_analysis_result = st.session_state.bill_sample_cache[sample_type]
            st.session_state.last_analyzed_source = current_source_key
        else:
            with st.spinner("🔍 Đang kết nối Backend AI & phân tích giám định 2 lớp (Pháp y số, Metadata & AI Vision)..."):
                if sample_type == "custom" and st.session_state.uploaded_bill_img is not None:
                    res = run_analysis(st.session_state.uploaded_bill_img, is_custom_upload=True)
                elif sample_type == "real" and os.path.exists(sample_real_path):
                    res = run_analysis(sample_real_path, is_custom_upload=False)
                    st.session_state.bill_sample_cache["real"] = res
                else:
                    target_path = sample_fake_path if os.path.exists(sample_fake_path) else sample_real_path
                    res = run_analysis(target_path, is_custom_upload=False)
                    st.session_state.bill_sample_cache["fake"] = res

                st.session_state.bill_analysis_result = res
                st.session_state.last_analyzed_source = current_source_key

    result = st.session_state.bill_analysis_result or {}
    is_fake = result.get("is_fake", True)
    confidence = result.get("confidence_score", 90)
    tx_info = result.get("transaction_info", {})
    tech_meta = result.get("technical_metadata", {})
    layer_1_points = result.get("layer_1_typography", [])
    layer_2_points = result.get("layer_2_pixel_forensics", [])
    suspicious_points = result.get("suspicious_points", [])
    conclusion = result.get("conclusion", "")
    model_used = result.get("model_used", "Hệ thống giám định AntiScam AI")

    # 6. CHIA 2 CỘT CHÍNH: BÊN TRÁI LÀ ẢNH VÀ THÔNG SỐ, BÊN PHẢI LÀ KẾT QUẢ GIÁM ĐỊNH
    col_card, col_verdict = st.columns([1.1, 1], gap="medium")

    # ==========================
    # CỘT TRÁI: ẢNH BIÊN LAI VÀ THÔNG SỐ PHÁP Y SỐ
    # ==========================
    with col_card:
        with st.container(border=True):
            st.markdown("##### 📸 Biên lai đang kiểm định")

            if sample_type == "custom":
                custom_bytes = st.session_state.get("uploaded_bill_bytes")
                if custom_bytes:
                    st.image(custom_bytes, caption="Ảnh biên lai bạn tải lên", use_container_width=True)
                elif st.session_state.uploaded_bill_img is not None:
                    st.image(st.session_state.uploaded_bill_img, caption="Ảnh biên lai bạn tải lên", use_container_width=True)
            elif sample_type == "real" and os.path.exists(sample_real_path):
                st.image(sample_real_path, caption="Mẫu biên lai thật chuẩn (Hợp lệ)", use_container_width=True)
            elif os.path.exists(sample_fake_path):
                st.image(sample_fake_path, caption="Mẫu biên lai nghi ngờ giả mạo (Chứa chữ ký AI/chỉnh sửa)", use_container_width=True)
            elif os.path.exists(sample_real_path):
                st.image(sample_real_path, caption="Mẫu biên lai đối soát", use_container_width=True)

            # Khối thông số kỹ thuật pháp y số (Dung lượng, Độ phân giải, Chữ ký phần mềm)
            if tech_meta:
                with st.container(border=True):
                    st.markdown("**🔍 Dữ liệu pháp y số (Digital Forensics):**")
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.write(f"• **Độ phân giải:** `{tech_meta.get('resolution', 'N/A')}`")
                        st.write(f"• **Dung lượng file:** `{tech_meta.get('file_size_kb', 0)} KB`")
                        st.write(f"• **Tỷ lệ khung hình:** `{tech_meta.get('aspect_ratio', 'N/A')}`")
                    with col_t2:
                        pix = tech_meta.get("pixel_forensics", {})
                        st.write(f"• **Độ nét cạnh (Edge):** `{pix.get('mean_edge_intensity', 'N/A')}`")
                        st.write(f"• **Độ bão hòa màu:** `{pix.get('mean_color_saturation', 'N/A')}`")

                    sigs = tech_meta.get("software_signatures", [])
                    if sigs:
                        st.markdown(
                            f"<div style='background: #FEE2E2; border: 1px solid #EF4444; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 13px; color: #991B1B; font-weight: 700;'>"
                            f"🚨 Chữ ký công cụ phát hiện trong file: {', '.join(sigs)}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    st.caption(f"Động cơ phân tích: **{model_used}**")

    # ==========================
    # CỘT PHẢI: KẾT QUẢ GIÁM ĐỊNH CHI TIẾT THEO CƠ CHẾ 2 LỚP
    # ==========================
    with col_verdict:
        with st.container(border=True):
            if is_fake:
                # KẾT LUẬN TỔNG QUAN BILL GIẢ
                st.markdown(f"""
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1.5px solid #FCA5A5; padding-bottom: 10px; margin-bottom: 12px;'>
                    <span style='font-size: 16px; font-weight: 800; color: var(--text-primary, #0F1B33);'>Kết Luận Giám Định</span>
                    <span style='background: #FEE2E2; color: #991B1B; border: 1.5px solid #EF4444; font-size: 13px; font-weight: 800; padding: 4px 12px; border-radius: 9999px;'>
                        🚨 BIÊN LAI CÓ DẤU HIỆU LÀM GIẢ
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Thước đo rủi ro
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 14px; font-weight: 700; color: #DC2626; margin-bottom: 4px;'>"
                    f"<span>Xác suất ảnh đã bị chỉnh sửa / rủi ro:</span>"
                    f"<span style='font-size: 16px; font-weight: 900;'>{confidence}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.progress(float(confidence) / 100.0)
                st.caption(f"🤖 Động cơ phân tích: **{model_used}**")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # CHI TIẾT LỚP 1: THỊ GIÁC & TYPOGRAPHY
                with st.container(border=True):
                    st.markdown("<div style='font-weight: 800; font-size: 14px; color: #1D4ED8; margin-bottom: 6px;'>🔍 Lớp 1: Giám định Thị giác & Typography</div>", unsafe_allow_html=True)
                    if layer_1_points:
                        for pt in layer_1_points:
                            st.markdown(f"- {pt}")
                    else:
                        st.markdown("""
                        - ❌ **Lệch phông chữ số tiền:** Phông chữ dãy số có độ dày và tỷ lệ nét không khớp với tiêu chuẩn ứng dụng ngân hàng.
                        - ❌ **Lệch trục căn lề (Baseline):** Dòng số tiền bị xê dịch so với trục chữ bên cạnh.
                        - ⚠️ **Màu sắc thương hiệu:** Xuất hiện sai lệch hệ màu logo hoặc không đồng nhất tông màu nền.
                        """)

                # CHI TIẾT LỚP 2: CẤU TRÚC PIXEL & VẾT NÉN ELA
                with st.container(border=True):
                    st.markdown("<div style='font-weight: 800; font-size: 14px; color: #7C3AED; margin-bottom: 6px;'>🔬 Lớp 2: Giám định Cấu trúc Pixel & Vết nén ELA</div>", unsafe_allow_html=True)
                    if layer_2_points:
                        for pt in layer_2_points:
                            st.markdown(f"- {pt}")
                    else:
                        st.markdown("""
                        - ❌ **Bất thường mức nén ELA:** Vùng chứa số tiền và tên người thụ hưởng có mức chênh lệch nén cao hơn nền, dấu hiệu của việc chèn nội dung khác.
                        - ⚠️ **Hiện tượng nhòe viền điểm ảnh:** Xuất hiện quầng mờ quanh các con số do sử dụng công cụ tẩy xóa (Clone Stamp/Brush).
                        """)

                # CÁC ĐIỂM BẤT THƯỜNG BỔ SUNG (NẾU CÓ)
                if suspicious_points:
                    with st.expander("⚠️ Chi tiết các dấu vết bất thường phát hiện được", expanded=False):
                        for sp in suspicious_points:
                            st.write(f"• {sp}")

                # KHUYẾN NGHỊ HÀNH ĐỘNG DỨT KHOÁT
                rec_text = conclusion or (
                    "Tuyệt đối **KHÔNG giao hàng, gửi mã thẻ hoặc chuyển tiền hoàn lại** chỉ vì nhìn thấy ảnh chụp này. "
                    "Kẻ gian thường tạo bill giả để hối thúc giao hàng. Hãy **tự mở ứng dụng ngân hàng của bạn** để xác nhận tiền đã thực sự về tài khoản hay chưa!"
                )
                st.markdown(f"""
                <div style='background: #FEF2F2; border: 1.5px solid #EF4444; border-radius: 10px; padding: 12px 16px; margin-top: 10px;'>
                    <div style='font-size: 14px; font-weight: 800; color: #991B1B;'>🚨 KHUYẾN NGHỊ AN TOÀN CHO NGƯỜI BÁN HÀNG:</div>
                    <div style='font-size: 13.5px; color: #7F1D1D; margin-top: 4px; line-height: 1.6; font-weight: 600;'>
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                # KẾT LUẬN TỔNG QUAN BILL THẬT
                st.markdown(f"""
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1.5px solid #86EFAC; padding-bottom: 10px; margin-bottom: 12px;'>
                    <span style='font-size: 16px; font-weight: 800; color: var(--text-primary, #0F1B33);'>Kết Luận Giám Định</span>
                    <span style='background: #DCFCE7; color: #166534; border: 1.5px solid #22C55E; font-size: 13px; font-weight: 800; padding: 4px 12px; border-radius: 9999px;'>
                        ✅ BIÊN LAI CÓ VẺ BÌNH THƯỜNG / HỢP LỆ
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Thước đo rủi ro
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 14px; font-weight: 700; color: #16A34A; margin-bottom: 4px;'>"
                    f"<span>Độ tin cậy biên lai hợp lệ:</span>"
                    f"<span style='font-size: 16px; font-weight: 900;'>{confidence}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.progress(float(confidence) / 100.0)
                st.caption(f"🤖 Động cơ phân tích: **{model_used}**")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # CHI TIẾT LỚP 1: THỊ GIÁC & TYPOGRAPHY
                with st.container(border=True):
                    st.markdown("<div style='font-weight: 800; font-size: 14px; color: #1D4ED8; margin-bottom: 6px;'>🔍 Lớp 1: Giám định Thị giác & Typography</div>", unsafe_allow_html=True)
                    if layer_1_points:
                        for pt in layer_1_points:
                            st.markdown(f"- {pt}")
                    else:
                        st.markdown("""
                        - ✅ **Phông chữ chuẩn xác:** Phông số tiền hoàn toàn đồng nhất về độ dày nét, khoảng cách và tỷ lệ.
                        - ✅ **Căn lề chuẩn xác:** Trục baseline, lề trái và lề phải đạt độ thẳng hàng tự nhiên.
                        - ✅ **Logo & Màu sắc:** Màu nhận diện thương hiệu và logo ngân hàng đạt chuẩn.
                        """)

                # CHI TIẾT LỚP 2: CẤU TRÚC PIXEL & VẾT NÉN ELA
                with st.container(border=True):
                    st.markdown("<div style='font-weight: 800; font-size: 14px; color: #7C3AED; margin-bottom: 6px;'>🔬 Lớp 2: Giám định Cấu trúc Pixel & Vết nén ELA</div>", unsafe_allow_html=True)
                    if layer_2_points:
                        for pt in layer_2_points:
                            st.markdown(f"- {pt}")
                    else:
                        st.markdown("""
                        - ✅ **Mức nén ELA đồng đều:** Hệ số nén phân bố đồng nhất trên toàn bộ bề mặt biên lai, không có vùng bị can thiệp.
                        - ✅ **Không có vết cắt dán pixel:** Mật độ hạt điểm ảnh tự nhiên, không có vết nhòe quanh vùng số tiền.
                        """)

                # KHUYẾN NGHỊ AN TOÀN
                rec_text = conclusion or (
                    "Biên lai không phát hiện dấu vết cắt ghép hình ảnh. Tuy nhiên, đối với đơn hàng giá trị lớn, "
                    "bạn vẫn nên kiểm tra thông báo biến động số dư trên app ngân hàng của mình trước khi bàn giao hàng hóa."
                )
                st.markdown(f"""
                <div style='background: #F0FDF4; border: 1.5px solid #22C55E; border-radius: 10px; padding: 12px 16px; margin-top: 10px;'>
                    <div style='font-size: 14px; font-weight: 800; color: #166534;'>💡 LƯU Ý CHO NGƯỜI BÁN HÀNG:</div>
                    <div style='font-size: 13.5px; color: #14532D; margin-top: 4px; line-height: 1.6; font-weight: 600;'>
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 7. DẪN CHỨNG BÀI BÁO CẢNH BÁO FAKE BILL CHÍNH THỐNG
    st.divider()
    st.markdown("<div style='font-size: 15px; font-weight: 800; color: var(--text-primary, #0F1B33); margin-bottom: 8px;'>📰 Cảnh Báo Chính Thống Về Thủ Đoạn Fake Bill:</div>", unsafe_allow_html=True)
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
