"""
View: tab_library.py
Tab 3: Cẩm Nang & Thư Viện 20 Bài Báo Cảnh Báo Chính Thống Cục An Toàn Thông Tin.
"""

import streamlit as st


def render_tab_library(rag_matcher):
    """Hiển thị toàn bộ nội dung Tab 3: Thư viện 20 bài báo chính thống & Tra cứu"""
    st.subheader("📚 Thư Viện 20 Bài Báo Cảnh Báo Chính Thống & Hotline")
    st.caption("Bộ dữ liệu RAG Grounding đối soát được thu thập từ Cục An toàn thông tin (Bộ TT&TT), Bộ Công an và các Cơ quan báo chí chính thống:")

    # KHỐI HOTLINE & NGUYÊN TẮC VÀNG
    col_hl1, col_hl2 = st.columns(2)
    with col_hl1:
        with st.container(border=True):
            st.markdown("### 🚨 Tổng Đài Tiếp Nhận Phản Ánh:")
            st.markdown("• **Tổng đài 156 (hoặc 5656):** Tiếp nhận phản ánh cuộc gọi rác, tin nhắn rác, lừa đảo (miễn phí).")
            st.markdown("• **Cục An ninh mạng A05 (Bộ Công an):** Hotline `069.234.8560`.")
            st.markdown("• **Cổng Không gian mạng Quốc gia:** `https://canhbao.khonggianmang.vn`.")
    with col_hl2:
        with st.container(border=True):
            st.markdown("### 🛑 4 Nguyên Tắc Vàng Dành Cho Người Dân:")
            st.markdown("1. **Không có Công an nào làm việc qua điện thoại hay Zalo** hoặc đòi chuyển tiền vào tài khoản an toàn.")
            st.markdown("2. **Không một nhân viên ngân hàng nào được phép hỏi mã OTP** của khách hàng.")
            st.markdown("3. **Không chuyển tiền khi có tin nhắn giục gấp của người thân** mà chưa gọi điện thoại nghe trực tiếp giọng nói.")
            st.markdown("4. **Không tin vào bất kỳ công việc 'việc nhẹ lương cao'** hay làm nhiệm vụ nạp tiền nhận hoa hồng.")

    st.markdown("---")
    st.subheader("📑 Danh Mục Toàn Văn 20 Bài Báo Cảnh Báo (Được sắp xếp theo Thủ Đoạn)")

    all_cases = rag_matcher.get_all_cases()

    # Thanh tìm kiếm và bộ lọc nhóm
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_kw = st.text_input("🔍 Tìm kiếm theo từ khóa (ví dụ: công an, shopee, tinder, vneid, bill...):", value="")
    with col_filter:
        categories = ["Tất cả danh mục"] + sorted(list(set([c.get("category_name", "") for c in all_cases if c.get("category_name")])))
        selected_cat = st.selectbox("Lọc theo nhóm thủ đoạn:", categories)

    # Lọc danh sách
    filtered_cases = all_cases
    if selected_cat != "Tất cả danh mục":
        filtered_cases = [c for c in filtered_cases if c.get("category_name") == selected_cat]

    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered_cases = [
            c for c in filtered_cases
            if kw in c.get("title", "").lower() or kw in c.get("summary", "").lower() or any(kw in k.lower() for k in c.get("keywords", []))
        ]

    st.caption(f"Đang hiển thị **{len(filtered_cases)} / {len(all_cases)}** bài báo cảnh báo chính thống:")

    for case in filtered_cases:
        with st.expander(f"📌 [{case.get('id')}] {case.get('title')} — {case.get('source')}"):
            st.markdown(f"**Nhóm thủ đoạn:** `{case.get('category_name')}`")
            st.markdown(f"**Nguồn bài viết:** *{case.get('source')}*")
            st.write(case.get('summary'))
            st.markdown(f"**Từ khóa nhận diện:** `{'`, `'.join(case.get('keywords', []))}`")
            st.link_button("👉 Mở bài báo gốc trên báo chí chính thống để đọc", case.get('url'), use_container_width=True)
