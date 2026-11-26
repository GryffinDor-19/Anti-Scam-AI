# 🎤 HƯỚNG DẪN ÔN TẬP & PHÂN CÔNG THUYẾT TRÌNH (NHÓM 4 NGƯỜI)

Tài liệu này tổng hợp **đúng những phần kiến thức, file mã nguồn và câu hỏi phản biện** mà từng thành viên cần nắm vững trước khi bảo vệ đồ án **AntiScam AI** (khớp 100% với nhánh `dev` trên GitHub).

---

## 1️⃣ THÀNH VIÊN 1 — Trưởng nhóm / Lõi AI, Pipeline & Prompt Engineering

### 📂 File cần nắm chắc
* `backend/gateway/pipeline.py` (`AntiScamPipeline`, `run_pipeline`, `extract_and_analyze_urls`)
* `backend/engines/semantic_analyzer.py` (`analyze_scam_content`, `fetch_live_url_preview`, `_call_single_model`)
* `backend/engines/dynamic_scorer.py` (`calculate_dynamic_risk`, `remove_diacritics`)
* `backend/gateway/response_formatter.py` (`format_scam_response`)

### 🧠 Kiến thức cốt lõi phải học để trình bày
1. **Luồng điều phối 5 bước trong `pipeline.py`:**
   * **Bước 1:** Quét URL & tên miền trần bằng Regex (`extract_and_analyze_urls`), bắt đuôi tên miền đáng ngờ (`.xyz`, `.top`, `.vip`, `.cc`, `.tk`...), link rút gọn (`bit.ly`, `tinyurl.com`...) và link thiếu `https://`.
   * **Bước 2:** Gọi RAG Retriever (`find_matching_article`) lấy bài báo cảnh báo liên quan nhất.
   * **Bước 3:** Gọi `analyze_scam_content()` phân tích đa phương thức (chữ + link + ảnh).
   * **Bước 4:** Chuẩn hóa kết quả về **hợp đồng JSON 6 trường** (`risk_score`, `threat_level`, `detected_tactic`, `explanation`, `psychological_traps`, `action_recommendations`).
   * **Bước 5 (Omni-Learn):** Nếu chưa có trong RAG và kết quả rõ ràng (`risk_score <= 15` hoặc `>= 75`, không phải lỗi AI), tự động lưu kịch bản mới vào `backend/data/scam_knowledge.json`.
2. **Cơ chế Live URL Preview & Đua đa luồng (Model Racing):**
   * `fetch_live_url_preview()` tải 6.000 bytes đầu của trang web (timeout 3.5s) lấy `<title>`, `<meta description>`, nội dung đầu trang để phát hiện tên miền cũ bị đổi sang web cờ bạc/phishing.
   * Dùng `ThreadPoolExecutor` chạy song song 3 model: `gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.7-flash`. Dùng `as_completed(timeout=25)` lấy **model đầu tiên trả JSON hợp lệ nhanh nhất**, rồi hủy chờ các model còn lại (`cancel_futures=True`).
3. **Cơ chế Fallback chống sập (Dynamic Scorer):**
   * Khi không có API Key hoặc mạng/Gemini lỗi, tự động chạy `calculate_dynamic_risk()` chấm điểm theo 5 chiều hành vi (uy quyền, gấp gáp, tài chính/OTP, link lạ...) và hỗ trợ bỏ dấu `remove_diacritics()` để bắt từ lóng/teencode/không dấu.

### ❓ Câu hỏi Hội đồng hay hỏi TV1 & Cách trả lời
* **Hỏi:** *Tại sao chạy song song 3 model Gemini thay vì dùng 1 model hay gộp phiếu (voting)?*  
  **Đáp:** Bài toán chống lừa đảo cần phản hồi khẩn cấp cho người dùng. *Model Racing* giảm độ trễ (*latency*) và tránh nghẽn cục bộ khi 1 model bị quá tải; nếu dùng Voting phải chờ model chậm nhất, làm tăng thời gian chờ.
* **Hỏi:** *Mất mạng hoặc hết quota API thì app có bị crash không?*  
  **Đáp:** Không. Hệ thống tự chuyển sang `calculate_dynamic_risk()` cục bộ, vẫn trả đủ 6 trường JSON chuẩn cho Frontend hiển thị.

---

## 2️⃣ THÀNH VIÊN 2 — Kỹ sư Dữ liệu, Hệ thống RAG & Giám định Bill Giả

### 📂 File cần nắm chắc
* `backend/engines/rag_case_matcher.py` (`RAGCaseMatcher`)
* `backend/knowledge/retriever.py` (`find_matching_article`)
* `backend/engines/fake_bill_detector.py` (`FakeBillDetector`)
* `backend/data/scam_knowledge.json` (37 bản ghi: 20 bài báo chính thống + 17 mẫu Omni-Learn)

### 🧠 Kiến thức cốt lõi phải học để trình bày
1. **Hệ thống RAG Vector Search (`rag_case_matcher.py`):**
   * Dùng mô hình embedding đa ngôn ngữ `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` mã hóa tiêu đề + từ khóa + tóm tắt thành vector.
   * Chuẩn hóa vector (`faiss.normalize_L2`) và đưa vào chỉ mục `faiss.IndexFlatIP` (tương đương độ tương đồng Cosine Similarity).
   * Đặt ngưỡng lọc **`score >= 0.55`** để tránh ghép nhầm bài báo không liên quan. Nếu môi trường thiếu thư viện FAISS/Torch, tự động lùi về **so khớp từ khóa có trọng số**.
2. **Giám định Hóa đơn Chuyển tiền Giả 2 Lớp (`fake_bill_detector.py`):**
   * **Lớp 1 (Pháp y số & Pixel cục bộ - `_extract_image_metadata` & `_analyze_pixel_forensics`):**
     * Đọc EXIF & header ảnh.
     * Quét chuỗi nhị phân (bytes) bắt watermark công cụ chỉnh sửa/AI: `C2PA`, `trainedalgorithmicmedia`, `ChatGPT`, `OpenAI`, `Photoshop`, `Canva`, `Picsart`.
     * Bắt lỗi tỷ lệ khung hình bè ngang bất thường (`aspect_ratio > 0.58`, khác màn hình điện thoại chuẩn 0.43–0.56).
     * Dùng `PIL` (`ImageFilter.FIND_EDGES` & hệ màu `HSV`) đo cường độ cạnh nét và độ bão hòa màu để phát hiện ảnh bị AI tái tạo/làm sắc nét đè.
   * **Lớp 2 (Gemini Vision ưu tiên tuần tự - `analyze_bill`):**
     * Không chạy song song như chat mà gọi tuần tự từ model thị giác mạnh nhất: `gemini-3.8-flash` → `3.7-flash` → `3.6-flash` → `3.5-flash` → `3.1-pro-preview` → `3.5-flash-lite` (có retry khi lỗi 503).
     * Nếu API lỗi/offline, kích hoạt `_heuristic_forensic_fallback()` kết luận dựa trên bằng chứng Lớp 1.

### ❓ Câu hỏi Hội đồng hay hỏi TV2 & Cách trả lời
* **Hỏi:** *Tại sao Tab Soi Bill lại gọi tuần tự từ `3.8-flash` xuống, không đua song song như Tab Chat?*  
  **Đáp:** Ảnh biên lai gốc giữ nguyên độ phân giải để soi chi tiết vi mô (font chữ, baseline, logo ngân hàng). Gọi tuần tự giúp ưu tiên mô hình thị giác chính xác nhất (`3.8-flash`), tránh tốn băng thông và tránh vượt hạn mức gửi ảnh đồng thời.
* **Hỏi:** *Làm sao tránh nhận nhầm bill thật có nền 3D hoặc Dark Mode của MB Bank / Techcombank là giả?*  
  **Đáp:** Trong prompt giám định có quy tắc tôn trọng giao diện đặc thù của từng ngân hàng (nền 3D, kính mờ, Dark Mode, ẩn thanh pin/sóng) và chỉ kết luận `is_fake = true` khi có bằng chứng rõ ràng về chữ ký file, lệch font/baseline số tiền, loang nền cục bộ hoặc sai logic ngày giao dịch.

---

## 3️⃣ THÀNH VIÊN 3 — Frontend, Trải nghiệm Người dùng (UX) & Trợ năng

### 📂 File cần nắm chắc
* `streamlit/app_anti_scam.py` (Cấu trúc 4 Tab, khởi tạo Session State, nạp CSS & RAG cache)
* `streamlit/styles.py` & `streamlit/.streamlit/config.toml` (Theme Tối `#0B132B`, cỡ chữ mặc định 128%, trợ năng 140%–150%)
* `streamlit/components/sidebar.py`, `gauge.py`, `emergency_banner.py`
* `streamlit/views/tab_chat.py`, `tab_fake_bill.py`, `tab_scam_game.py`, `tab_library.py`
* `backend/data/scam_scenarios.json` (15 tình huống Đấu trường lừa đảo)

### 🧠 Kiến thức cốt lõi phải học để trình bày
1. **Kiến trúc Giao diện 4 Tab rõ ràng:**
   * **Tab 1 (`tab_chat.py`):** Khung chat phân tích tin nhắn/link/ảnh, hiển thị **Đồng hồ Bán nguyệt (`gauge.py`)**, tô sáng từ khóa nguy hiểm (`highlight_dangerous_keywords`), 4 kịch bản mẫu 1-click và nhật ký lịch sử trong phiên.
   * **Tab 2 (`tab_fake_bill.py`):** Giao diện đối chiếu bill giả (`fake_bill.jpg`), bill thật (`test_bill.jpg`) và upload ảnh người dùng, hiển thị kết quả tách rõ 2 lớp giám định.
   * **Tab 3 (`tab_scam_game.py`):** Đấu trường lừa đảo 15 tình huống × 3 lượt đối thoại, hỗ trợ chọn phương án hoặc tự nhập phản hồi, tính điểm + thanh máu HP, dùng 100% widget gốc của Streamlit (không HTML thô để không bị vỡ giao diện khi phóng to chữ).
   * **Tab 4 (`tab_library.py`):** Tra cứu 37 bản ghi cảnh báo, lọc theo danh mục, tìm từ khóa, kèm Tổng đài 156/A05 và 4 Nguyên tắc vàng.
2. **Thiết kế Trợ năng & Giao diện Tối mặc định:**
   * Nền tối mặc định (`#0B132B`) đồng bộ từ `config.toml` tới `styles.py` giúp giảm chói mắt và tăng độ tương phản.
   * Cỡ chữ mặc định **128%**; bật chế độ **Người lớn tuổi** trong Sidebar có 3 mức phóng to **140% / 145% / 150%** (`get_elderly_css`).
   * Tối ưu tốc độ bằng `@st.cache_resource` cho `RAGCaseMatcher` để không phải nạp lại mô hình embedding mỗi lần bấm nút.

### ❓ Câu hỏi Hội đồng hay hỏi TV3 & Cách trả lời
* **Hỏi:** *Streamlit mặc định mỗi lần bấm nút sẽ chạy lại toàn bộ file từ trên xuống, nhóm xử lý thế nào để không bị chậm khi tải model RAG?*  
  **Đáp:** Nhóm bọc `RAGCaseMatcher()` trong `@st.cache_resource` tại `app_anti_scam.py`, nên mô hình `MiniLM` và `FAISS Index` chỉ nạp đúng 1 lần duy nhất khi khởi động server.
* **Hỏi:** *Vì sao Tab Đấu trường Lừa đảo lại bỏ HTML thô mà dùng thành phần gốc của Streamlit?*  
  **Đáp:** HTML thô dễ xung đột CSS khi người dùng bật chế độ chữ to 140%–150% và dễ bị Markdown hiểu nhầm thành khối code khi thụt lề. Dùng widget gốc (`st.chat_message`, `st.container(border=True)`, `st.metric`, `st.progress`) giúp đồng bộ 100% với Theme Tối và mọi mức phóng đại chữ.

---

## 4️⃣ THÀNH VIÊN 4 — Kiểm thử (QA), Đo đạc Định lượng & Tổng hợp Demo

### 📂 File cần nắm chắc
* `backend/gateway/batch_test.py` & `backend/gateway/cli_test.py`
* `backend/gateway/test_report.json`
* `backend/modules/check_model.py`
* `README.md` & `KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.md`

### 🧠 Kiến thức cốt lõi phải học để trình bày
1. **Quy trình Kiểm thử tự động (`batch_test.py`, `cli_test.py`):**
   * Biết cách chạy test hàng loạt qua CLI/Batch để kiểm tra đầu ra 6 trường JSON của `pipeline.py` (như các ca trong `test_report.json`: tin nhắn bình thường 12 điểm, mượn tiền 74 điểm, VNeID 74 điểm, CTV Shopee 74 điểm, giả công an 83 điểm, link CSGT `.xyz` 98 điểm).
   * Kiểm tra các **ca biên (Edge cases)**: không có API Key (fallback offline), ảnh bill bị chèn chữ ký Photoshop/C2PA (`fake_bill.jpg` vs `test_bill.jpg`), link tên miền trần không có `http://`, tin nhắn teencode/không dấu.
2. **Các chỉ số đánh giá & Kịch bản Live Demo 3 phút:**
   * Nắm rõ công thức & ý nghĩa 4 chỉ số: **Accuracy, Precision, Recall, F1-Score** (đặc biệt vì sao bài toán chống lừa đảo cần **Recall cao** để không bỏ sót tin lừa đảo thật) và **Latency** (thời gian phản hồi).
   * Điều phối **Demo 4 bước trên web (`http://localhost:8501`)**:
     1. *Tab 1:* Bấm thử 1 kịch bản mẫu (ví dụ Phạt nguội CSGT hoặc Giả Công an) → Chỉ vào Đồng hồ rủi ro, bẫy tâm lý & link bài báo RAG.
     2. *Tab 2:* Soi thử `Bill Giả` → Chỉ rõ Lớp 1 (dấu vết AI/tỷ lệ khung hình) & Lớp 2 (Gemini Vision). Chuyển sang `Bill Thật` để chứng minh hệ thống không bắt nhầm.
     3. *Tab 3:* Chơi nhanh 1 lượt Đấu trường lừa đảo + bấm thử **Nút Cấp cứu khẩn cấp** trên đầu trang.
     4. *Sidebar & Tab 4:* Bật công tắc **Chữ to 145%** cho người cao tuổi và lướt nhanh **Thư viện 37 cảnh báo**.

### ❓ Câu hỏi Hội đồng hay hỏi TV4 & Cách trả lời
* **Hỏi:** *Trong bài toán chống lừa đảo, giữa Precision và Recall chỉ số nào quan trọng hơn?*  
  **Đáp:** **Recall** đối với lớp lừa đảo rất quan trọng vì bỏ sót một vụ lừa đảo (False Negative) có thể khiến người dân mất tiền thật; tuy nhiên vẫn cần cân bằng bằng F1-Score và ngưỡng RAG (`>= 0.55`) để không báo nhầm quá nhiều tin nhắn bình thường gây hoang mang.
* **Hỏi:** *Nếu đang demo trực tiếp mà mạng phòng thi yếu hoặc hết quota Gemini thì xử lý sao?*  
  **Đáp:** Hệ thống tự động chuyển về chế độ dự phòng cục bộ (`Dynamic Scorer` + `Heuristic Forensics` + `Keyword RAG`) nên toàn bộ 4 Tab vẫn chạy mượt mà không bị lỗi màn hình đỏ.

---

## ✅ Checklist Chung Trước Giờ Thuyết Trình (Cả 4 Thành Viên)
- [ ] Cài đủ thư viện: `pip install -r requirements.txt`
- [ ] Kiểm tra file `.env` có `GEMINI_API_KEY` còn hạn mức (hoặc chuẩn bị sẵn key dự phòng)
- [ ] Chạy thử trước trên máy trình chiếu: `streamlit run streamlit/app_anti_scam.py`
- [ ] Chuẩn bị sẵn 1 video quay màn hình demo dự phòng (phòng trường hợp sự cố máy chiếu)
