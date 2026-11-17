# 🛡️ AntiScam AI — Hệ Thống Trợ Lý Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức

> **Bài tập lớn môn Trí tuệ Nhân tạo (INT3401)**  
> **Phân ban:** Track 1.1 Application Track  
> **Mục tiêu:** Bảo vệ người dân và người cao tuổi trước các thủ đoạn lừa đảo tinh vi trên không gian mạng bằng mô hình suy luận đa phương thức và đối soát dữ liệu thực tế.

---

## 🌟 Tính Năng Nổi Bật

1. **🔍 Thẩm định Tin nhắn & Phân tích Bẫy Tâm lý (Tab 1):**
   - Đánh giá mức độ rủi ro trên thang điểm 0–100 bằng **Đồng hồ Bán nguyệt (Speedometer Gauge)** trực quan.
   - Bóc trần các bẫy thao túng: Dọa dẫm uy quyền, ép buộc thời gian, cô lập nạn nhân, mồi chài cọc/hoa hồng ảo.
   - Tích hợp 4 kịch bản mẫu 1-click (Phạt nguội CSGT, Giả danh công an, Tuyển CTV Shopee/TikTok, Trúng thưởng) giúp người dùng trải nghiệm nhanh chóng.
2. **📰 RAG Grounding (Đối chiếu Dẫn chứng Thực tế - Tab 3):**
   - Tự động đối soát nội dung nghi vấn với kho tri thức cảnh báo chính thống từ *Cục An toàn thông tin (Bộ TT&TT)*, *Bộ Công an*, *Báo Chính phủ*, *Tuổi Trẻ*, *Thanh Niên*, *VnExpress*...
   - Cung cấp link gốc bài báo để người dùng kiểm chứng nguồn tin thực tế tức thì.
3. **🧾 Giám định Hóa đơn Chuyển tiền Giả 2 Lớp (Tab 2 - Forensic Vision Lab):**
   - **Lớp 1:** Thuật toán thị giác máy tính & Typography phân tích sai lệch phông chữ, phát hiện vết cắt ghép và bất thường nén pixel (< 0.05s).
   - **Lớp 2:** Mô hình đa phương thức Gemini Vision thẩm định chuyên sâu và đưa ra kết luận chi tiết.
   - Hỗ trợ chuyển đổi nhanh giữa mẫu hóa đơn giả và mẫu hóa đơn thật để đối chiếu trực quan.
4. **🚨 Chế độ Cấp cứu Khẩn cấp (Thời điểm vàng):**
   - Nút cấp cứu đỏ rực ghim cố định ở góc trên giao diện, mở ra quy trình 3 bước hành động khẩn cấp bảo vệ tài sản.
   - Hotline khóa tài khoản/thẻ ngân hàng 1-chạm (Vietcombank, BIDV, Techcombank, Agribank, ACB, VPBank, MBBank) & Cục An ninh mạng A05.
5. **🎨 Bộ Chọn Giao Diện 3 Theme (Dịu / Sáng / Tối) & Trợ Năng Màn Hình:**
   - 3 chế độ màu sắc đạt chuẩn tương phản cao (≥ 7:1), chuyển đổi tức thì không gây độ trễ (Zero-delay).
   - Chế độ Trợ năng cho người cao tuổi: Phóng to kích thước phông chữ toàn diện (115% – 128%), bảo toàn nguyên vẹn 100% bố cục giao diện.
6. **🕒 Bảng Lịch sử Thẩm định Trong Phiên (Session Audit Log):**
   - Tự động ghi nhật ký và thống kê các lượt kiểm tra trong phiên làm việc.

---

## 📁 Cấu Trúc Dự Án Thực Tế (Phân Tách Module Chuẩn)

```text
AntiScam_AI/
├── .gitignore                              # Cấu hình bỏ qua file tạm, môi trường, bytecode
├── anti_scam_core.py                       # Lõi xử lý hợp nhất AntiScam Core
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.md      # Kế hoạch & bảng phân công chi tiết nhóm 4 người
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.html    # Bảng phân công nhiệm vụ giao diện HTML trực quan
├── README.md                               # Tài liệu hướng dẫn & kiến trúc hệ thống
├── requirements.txt                        # Danh mục các thư viện phụ thuộc của dự án
├── so_do_tuong_tac_tinh_gian.png           # Sơ đồ luồng tương tác các module hệ thống
│
├── backend/                                # [Backend & AI Engines] - Bộ não phân tích AI & Dữ liệu
│   ├── backend.py                          # Cổng tiếp nhận và điều phối tầng Backend
│   ├── data/                               # Dữ liệu tri thức và cấu trúc phản hồi mẫu
│   │   ├── mock_response.json              # Chuẩn hóa hợp đồng dữ liệu đầu ra 6 trường JSON
│   │   └── scam_knowledge.json             # Kho tri thức cảnh báo lừa đảo (Cục ATTT, Bộ Công an)
│   ├── emergency/                          # Module cấp cứu người dùng
│   │   └── emergency_manager.py            # Danh bạ Hotline ngân hàng & quy trình cấp cứu tài chính
│   ├── engines/                            # Các động cơ phân tích chuyên sâu (TV1 & TV2)
│   │   ├── dynamic_scorer.py               # Thuật toán tính điểm rủi ro đa tiêu chí động (Scam Score)
│   │   ├── fake_bill_detector.py           # Giám định hóa đơn chuyển tiền qua phông chữ & vết nén
│   │   ├── fast_filter.py                  # Bộ lọc phản xạ siêu tốc (< 0.05s) từ khóa nóng & link lạ
│   │   ├── llm_analyzer.py                 # Phân tích ngữ nghĩa chuyên sâu bằng mô hình Google Gemini
│   │   ├── rag_case_matcher.py             # Động cơ RAG đối soát vector bài báo thực tế
│   │   └── semantic_analyzer.py            # Điều phối phân tích ngữ nghĩa kết hợp Fallback nội bộ
│   ├── gateway/                            # Cổng giao tiếp, điều phối Pipeline & Bộ công cụ test (TV1 & TV4)
│   │   ├── backend.py                      # API Gateway chính tiếp nhận yêu cầu từ Frontend
│   │   ├── batch_test.py                   # Script chạy kiểm thử tự động hàng loạt (Batch Testing)
│   │   ├── cli_test.py                     # Giao diện dòng lệnh Terminal CLI Test Runner
│   │   ├── knowledge_trainer.py            # Công cụ trích xuất và huấn luyện dữ liệu RAG
│   │   ├── pipeline.py                     # Nhạc trưởng điều phối chuỗi 3 lớp phòng thủ liên hoàn
│   │   ├── response_formatter.py           # Đóng gói kết quả chuẩn hóa 6 trường dữ liệu
│   │   ├── test_report.json                # Báo cáo số liệu kiểm thử hệ thống
│   │   └── threat_classifier.py            # Bộ phân loại mức độ đe dọa và nhóm thủ đoạn
│   ├── knowledge/                          # Tầng truy xuất tri thức RAG
│   │   └── retriever.py                    # Module tìm kiếm bài báo chính thống theo ngữ cảnh
│   └── modules/                            # Các module đóng gói kế thừa & tương thích ngược
│       ├── check_model.py                  # Script kiểm tra phiên bản Gemini API khả dụng
│       ├── emergency_manager.py            # Module cấp cứu tương thích
│       ├── fake_bill_detector.py           # Module soi bill tương thích
│       ├── fast_filter.py                  # Module lọc nhanh tương thích
│       ├── rag_case_matcher.py             # Module đối soát RAG tương thích
│       ├── semantic_analyzer.py            # Module phân tích ngữ nghĩa tương thích
│       └── test_bill.jpg                   # File ảnh biên lai chuyển tiền Vietcombank phục vụ test
│
└── streamlit/                              # [Frontend & UX - TV3] Toàn bộ mã nguồn giao diện người dùng
    ├── app_anti_scam.py                    # File chạy chính của ứng dụng Web Streamlit
    ├── styles.py                           # Hệ thống CSS Design System (Theme Dịu / Sáng / Tối)
    ├── .streamlit/
    │   └── config.toml                     # File cấu hình Streamlit (Màu sắc, Font chữ, Cổng chạy)
    ├── components/                         # Các linh kiện giao diện tái sử dụng
    │   ├── emergency_banner.py             # Nút cấp cứu đỏ rực ghim góc & Hotline 1-chạm
    │   ├── gauge.py                        # Đồng hồ bán nguyệt đo độ rủi ro (Speedometer Gauge Chart)
    │   └── sidebar.py                      # Thanh bên: Đổi 3 theme tức thì, Trợ năng chữ to, Cài đặt API
    └── views/                              # 3 Tab chức năng chính của giao diện Web
        ├── tab_chat.py                     # Tab 1: Khung chat thẩm định tin nhắn & 4 kịch bản mẫu 1-click
        ├── tab_fake_bill.py                # Tab 2: Phòng Lab Giám định Hóa đơn chuyển tiền 2 lớp
        └── tab_library.py                  # Tab 3: Thư viện tra cứu bài báo cảnh báo chính thống

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng
```bash
streamlit run streamlit/app_anti_scam.py
```
Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.
