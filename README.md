# 🛡️ AntiScam AI — Hệ Thống Trợ Lý Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức

> **Bài tập lớn môn Trí tuệ Nhân tạo (INT3401)**  
> **Phân ban:** Track 1.1 Application Track  
> **Repository:** [GryffinDor-19/Anti-Scam-AI](https://github.com/GryffinDor-19/Anti-Scam-AI)  
> **Mục tiêu:** Bảo vệ người dân và người cao tuổi trước các thủ đoạn lừa đảo tinh vi trên không gian mạng bằng mô hình suy luận đa phương thức, đối soát vector thực tế (RAG) và mô phỏng tình huống tương tác.

---

## 🌟 Tính Năng Nổi Bật (Khớp 100% Mã Nguồn Hiện Tại)

1. **🔍 Tab 1 — Kiểm Tra Tin Nhắn, Link & Ảnh Đa Phương Thức (`tab_chat.py`):**
   - Đánh giá mức độ rủi ro trên thang điểm **0–100** bằng **Đồng hồ Bán nguyệt (Speedometer Gauge)** trực quan.
   - Bóc trần các bẫy tâm lý (đe dọa uy quyền, ép thời gian, mồi chài hoa hồng/việc nhẹ lương cao, chiếm đoạt OTP/tài sản) và đưa ra khuyến nghị hành động sát ngữ cảnh.
   - Hỗ trợ phân tích **văn bản, đường link (tự động quét tiêu đề/nội dung web thực tế) và hình ảnh đính kèm** (ảnh chụp tin nhắn, mã QR, bill chuyển khoản).
   - Tích hợp **đua đa luồng 3 mô hình Gemini** (`gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.7-flash`) qua `ThreadPoolExecutor` — mô hình nào trả JSON hợp lệ nhanh nhất sẽ được ưu tiên phản hồi ngay; tự động chuyển sang bộ chấm điểm nội bộ (`Dynamic Scorer`) khi offline hoặc thiếu API Key.

2. **🧾 Tab 2 — Soi Bill Giả / Giám Định Hóa Đơn 2 Lớp (`tab_fake_bill.py`):**
   - **Lớp 1 (Pháp y số & Pixel cục bộ):** Trích xuất EXIF, quét chữ ký nhị phân phát hiện dấu vết phần mềm/AI tạo sinh (`C2PA`, `ChatGPT`, `OpenAI`, `Photoshop`, `Canva`, `Picsart`), kiểm tra bất thường tỷ lệ khung hình (`> 0.58`) và đo cường độ cạnh nét / độ bão hòa màu HSV.
   - **Lớp 2 (Gemini Vision ưu tiên tuần tự):** Gọi lần lượt từ model thị giác mạnh nhất xuống nhẹ hơn (`gemini-3.8-flash` → `3.7-flash` → `3.6-flash` → `3.5-flash` → `3.1-pro-preview` → `3.5-flash-lite`), tự động fallback về bộ pháp y số heuristic nội bộ nếu không có mạng/API Key.
   - Tích hợp sẵn ảnh mẫu **bill giả** (`fake_bill.jpg`), **bill thật** (`test_bill.jpg`) và hỗ trợ tải ảnh bất kỳ từ người dùng.

3. **🎮 Tab 3 — Đấu Trường Lừa Đảo (`tab_scam_game.py`):**
   - **15 tình huống lừa đảo thực tế** (`scam_scenarios.json`), mỗi tình huống gồm **3 lượt đối thoại** tương tác liên tiếp với bot đóng vai kẻ lừa đảo.
   - Người chơi có thể **chọn phương án phản ứng nhanh** hoặc **tự gõ câu trả lời** (hệ thống tự chấm theo từ khóa tiếng Việt có dấu & không dấu).
   - Chấm điểm theo 3 mức: **An toàn** (`+30 điểm`), **Chưa dứt khoát** (`+10 điểm, -10 HP`), **Dính bẫy** (`0 điểm, -35 HP`), tổng kết dấu hiệu nhận diện và trích dẫn bài báo gốc.
   - Giao diện sử dụng 100% thành phần gốc của Streamlit (không nhúng HTML thô), hiển thị sạch sẽ trên mọi kích thước chữ.

4. **📚 Tab 4 — Thư Viện Cảnh Báo & RAG Grounding (`tab_library.py`):**
   - Đối soát ngữ nghĩa bằng **FAISS Vector Search** (`IndexFlatIP` + `paraphrase-multilingual-MiniLM-L12-v2`, ngưỡng `>= 0.55`) kết hợp fallback từ khóa.
   - Kho tri thức `scam_knowledge.json` hiện có **37 bản ghi** (gồm **20 bài báo cảnh báo chính thống** từ Cục An toàn thông tin, Bộ Công an, VnExpress, Tuổi Trẻ... và **17 mẫu tự học Omni-Learn**).
   - Hỗ trợ tìm kiếm theo từ khóa, lọc theo nhóm thủ đoạn, kèm **Tổng đài 156**, **Hotline A05 (`069.234.8560`)** và **4 Nguyên tắc vàng**.

5. **🚨 Chế Độ Cấp Cứu Khẩn Cấp (`emergency_banner.py` & `emergency_manager.py`):**
   - Nút cấp cứu ghim nổi bật ở đầu trang, mở nhanh quy trình xử lý khẩn cấp và danh bạ hotline khóa thẻ/tài khoản các ngân hàng lớn (`Vietcombank`, `BIDV`, `Techcombank`, `Agribank`, `ACB`, `VPBank`, `MBBank`) cùng Cục An ninh mạng A05.

6. **🌙 Giao Diện Tối Mặc Định & Trợ Năng Cỡ Chữ Lớn (`styles.py` & `sidebar.py`):**
   - Thiết kế **Giao diện Tối (`#0B132B`) mặc định** (đã loại bỏ chế độ Sáng/Dịu để đồng nhất độ tương phản và bảo vệ mắt).
   - **Cỡ chữ mặc định 128%** rõ ràng ngay khi mở ứng dụng.
   - **Chế độ Trợ năng cho người lớn tuổi** với 3 mức phóng đại tùy chọn: **140%**, **145% (mặc định)** và **150%**.

---

## 📁 Cấu Trúc Dự Án Thực Tế

```text
AntiScam_AI/
├── .gitignore                              # Cấu hình bỏ qua file tạm, môi trường, bytecode
├── anti_scam_core.py                       # Lõi tương thích AntiScam Core
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.md      # Kế hoạch phân công nhiệm vụ theo tuần (TV1–TV4)
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.html    # Bản trình bày HTML kế hoạch phân công nhóm
├── HUONG_DAN_THUYET_TRINH_NHOM.md          # Phân công nội dung ôn tập & hỏi đáp bảo vệ cho 4 thành viên
├── README.md                               # Tài liệu tổng quan & kiến trúc khớp mã nguồn Git
├── requirements.txt                        # Danh sách thư viện Python phụ thuộc
├── so_do_tuong_tac_tinh_gian.png           # Sơ đồ luồng tương tác hệ thống
│
├── backend/                                # [Backend & AI Engines]
│   ├── backend.py                          # Cổng tương thích tầng Backend
│   ├── data/
│   │   ├── mock_response.json              # Hợp đồng JSON chuẩn 6 trường đầu ra
│   │   ├── scam_knowledge.json             # Kho tri thức RAG (37 bản ghi: 20 gốc + 17 Omni-Learn)
│   │   ├── scam_learned_cache.json         # Bộ nhớ đệm mẫu đã học
│   │   └── scam_scenarios.json             # 15 tình huống Đấu trường lừa đảo (3 lượt/tình huống)
│   ├── emergency/
│   │   └── emergency_manager.py            # Danh bạ Hotline ngân hàng & quy trình cấp cứu
│   ├── engines/                            # Các động cơ AI & xử lý lõi (TV1 & TV2)
│   │   ├── dynamic_scorer.py               # Thuật toán chấm điểm rủi ro đa tiêu chí (hỗ trợ teencode/không dấu)
│   │   ├── fake_bill_detector.py           # Giám định bill 2 lớp (EXIF/C2PA/Pixel + Gemini Vision)
│   │   ├── fast_filter.py                  # Bộ lọc từ khóa/link nhanh (kế thừa)
│   │   ├── llm_analyzer.py                 # Giao tiếp mô hình Gemini LLM
│   │   ├── rag_case_matcher.py             # Đối soát vector FAISS + MiniLM & fallback từ khóa
│   │   └── semantic_analyzer.py            # Live URL Preview + Đua đa luồng 3 Gemini + Fallback Scorer
│   ├── gateway/                            # Điều phối Pipeline & Kiểm thử (TV1 & TV4)
│   │   ├── backend.py                      # Gateway tiếp nhận từ Frontend
│   │   ├── batch_test.py                   # Script chạy kiểm thử hàng loạt
│   │   ├── cli_test.py                     # Trình chạy kiểm thử dòng lệnh (CLI)
│   │   ├── knowledge_trainer.py            # Công cụ hỗ trợ huấn luyện dữ liệu RAG
│   │   ├── pipeline.py                     # Nhạc trưởng điều phối (URL -> RAG -> Gemini Racing -> Format -> Omni-Learn)
│   │   ├── response_formatter.py           # Chuẩn hóa đầu ra JSON 6 trường
│   │   ├── test_report.json                # Kết quả chạy kiểm thử mẫu
│   │   └── threat_classifier.py            # Phân loại mức độ đe dọa & thủ đoạn
│   ├── knowledge/
│   │   └── retriever.py                    # Tầng truy xuất bài báo chính thống
│   └── modules/                            # Lớp tương thích ngược (Compatibility Layer) & ảnh mẫu test
│       ├── check_model.py                  # Kiểm tra danh sách model Gemini khả dụng
│       ├── fake_bill.jpg                   # Ảnh hóa đơn giả mẫu
│       ├── test_bill.jpg                   # Ảnh hóa đơn thật mẫu (Vietcombank)
│       └── ...                             # Các wrapper trỏ về backend/engines/ & backend/emergency/
│
└── streamlit/                              # [Frontend & UX - TV3]
    ├── app_anti_scam.py                    # Điểm khởi chạy chính Streamlit (Theme Tối mặc định, 4 Tab)
    ├── styles.py                           # Hệ thống CSS (Theme Tối, chữ mặc định 128%, trợ năng 140–150%)
    ├── .streamlit/
    │   └── config.toml                     # Cấu hình nền tối (#0B132B) & server
    ├── components/
    │   ├── emergency_banner.py             # Banner & nút cấp cứu khẩn cấp
    │   ├── gauge.py                        # Đồng hồ bán nguyệt đo điểm rủi ro (0–100)
    │   └── sidebar.py                      # Thanh bên: Trạng thái Giao diện Tối, Trợ năng 140–150%, API Key
    └── views/                              # 4 Tab chức năng theo đúng thứ tự hiển thị
        ├── tab_chat.py                     # Tab 1: Kiểm tra tin nhắn (Chat + Upload ảnh + Lịch sử)
        ├── tab_fake_bill.py                # Tab 2: Soi bill giả (2 lớp giám định)
        ├── tab_scam_game.py                # Tab 3: Đấu trường lừa đảo (15 tình huống, 3 lượt)
        └── tab_library.py                  # Tab 4: Thư viện cảnh báo (37 bản ghi + Hotline)
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Gemini API Key (khuyến nghị)
Tạo file `.env` ở thư mục gốc dự án hoặc nhập trực tiếp trong **Sidebar → Cài đặt nâng cao** trên web:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Nếu không nhập API Key, hệ thống vẫn chạy ổn định ở chế độ dự phòng cục bộ với `Dynamic Scorer`, `FAISS/Keyword RAG` và `Heuristic Forensics`.)*

### 3. Khởi chạy ứng dụng
```bash
streamlit run streamlit/app_anti_scam.py
```
Ứng dụng mở tại địa chỉ: `http://localhost:8501`.
