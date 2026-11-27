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

## 3️⃣ THÀNH VIÊN 3 — Frontend Next.js, REST API Bridge, UX & Trợ năng

### 📂 File cần nắm chắc
* `backend/api/server.py` (ASGI REST API trên Starlette + Uvicorn, CORS, 8 endpoints phục vụ Frontend)
* `frontend/src/lib/api.ts` (Tầng gọi REST API & định nghĩa TypeScript interfaces)
* `frontend/src/context/AppContext.tsx` (State toàn cục: Light/Dark mode, Chữ to, API key, lịch sử chat `sessionStorage`)
* `frontend/src/components/AppShell.tsx`, `BrandMark.tsx`, `EmergencyDrawer.tsx`, `ApiKeyModal.tsx`, `RiskGauge.tsx`
* `frontend/src/app/layout.tsx`, `globals.css` (Script chống nháy FOUC & hệ màu Warm Charcoal / Furrow Stone)
* `frontend/src/app/page.tsx`, `fake-bill/page.tsx`, `game/page.tsx`, `library/page.tsx`
* `backend/data/scam_scenarios.json` (15 tình huống Đấu trường lừa đảo)

### 🧠 Kiến thức cốt lõi phải học để trình bày
1. **Kiến trúc tách rời Next.js 15 + Starlette API (`frontend/` ↔ `backend/api/server.py`):**
   * Chuyển từ Streamlit (monolithic, rerun toàn trang mỗi lần bấm nút) sang **Next.js 15 (App Router + TypeScript + Tailwind CSS v4)** giao tiếp qua **8 REST endpoints** của **Starlette + Uvicorn** (`http://localhost:8000`), giữ nguyên 100% lõi AI Python.
   * **Bố cục App Shell Sidebar trái cố định** (tự chuyển thành Drawer trượt trên Mobile `390px`), đặt nút đỏ **Tôi lỡ bị lừa** ở vị trí dễ bấm nhất trên mọi trang.
2. **4 Màn hình chức năng tối ưu trải nghiệm thực tế:**
   * **Màn hình 1 (`page.tsx` — Kiểm tra tin nhắn và đường link):** Đặt khung nhập ngay đầu trang khi trống, có **nút Dán nhanh** (clipboard), **gợi ý nhập nhanh thông minh** (lọc theo từ khóa + nhấn `Tab` + chip 1-chạm), **Đồng hồ SVG (`RiskGauge.tsx`)**, tô sáng từ khóa nguy hiểm, **nút Sao chép cảnh báo** gửi Zalo cho người thân và lưu lịch sử phiên (`sessionStorage`).
   * **Màn hình 2 (`fake-bill/page.tsx` — Kiểm tra biên lai chuyển khoản):** Kéo-thả ảnh, chuyển nhanh *Mẫu bill giả / Mẫu bill thật*, hiển thị 2 lớp giám định và **Lightbox phóng to ảnh** để đối chiếu chi tiết.
   * **Màn hình 3 (`game/page.tsx` — Đấu trường lừa đảo):** 15 tình huống / 13 nhóm thủ đoạn × 3 lượt, Trọng tài AI chấm điểm, hỗ trợ chọn đáp án hoặc nhập tự do, tự lưu điểm cao nhất & tiến độ vào `localStorage`.
   * **Màn hình 4 (`library/page.tsx` — Thư viện cảnh báo và hotline):** Tách rõ tab **Bài báo chính thống (20)** vs **AI tự học**, tìm kiếm trực tiếp (live search), Tổng đài 156/A05 và 4 nguyên tắc vàng.
3. **Thiết kế Light/Dark mode & Trợ năng chuẩn sản phẩm phần mềm:**
   * Tự động nhận diện giao diện hệ điều hành (`prefers-color-scheme`), có công tắc **Chế độ tối / sáng** (`Warm Charcoal` & `Furrow Stone`), lưu `localStorage` và dùng inline script trong `<head>` (`layout.tsx`) để **không bị nháy màn hình (Zero-FOUC)**.
   * Công tắc **Chữ to, dễ đọc (`115% / 130% / 145%`)** thay đổi `html.style.fontSize` phản hồi **tức thì 0ms** không cần tải lại trang; văn bản chuẩn **sentence case**, không dùng gradient/glow gây rối mắt.

### ❓ Câu hỏi Hội đồng hay hỏi TV3 & Cách trả lời
* **Hỏi:** *Vì sao nhóm chuyển Frontend từ Streamlit sang Next.js + Starlette API?*  
  **Đáp:** Streamlit tiện dựng prototype nhanh nhưng bị hạn chế lớn về UX: mỗi tương tác đều rerun toàn bộ script gây trễ 1 nhịp (nhất là nút trợ năng chữ to), khó kiểm soát responsive mobile, và dễ vỡ HTML khi nhúng giao diện phức tạp. Chuyển sang **Next.js + Starlette REST API** tách biệt hoàn toàn giao diện và lõi AI Python, phản hồi mượt tức thì, hỗ trợ Light/Dark mode không nháy, lưu trạng thái trên trình duyệt và dễ mở rộng thành sản phẩm thực tế.
* **Hỏi:** *Làm sao đảm bảo bật/tắt Light/Dark mode không bị nháy trắng (FOUC) khi tải lại trang?*  
  **Đáp:** Nhóm nhúng một đoạn script đồng bộ nhỏ trong `<head>` của `layout.tsx` để đọc `localStorage` (hoặc `prefers-color-scheme` của hệ điều hành nếu chưa chỉnh) và gắn thuộc tính `data-theme` lên `<html>` trước khi trình duyệt render khung hình đầu tiên.
* **Hỏi:** *Chuyển qua lại giữa các trang có bị mất lịch sử kiểm tra hoặc điểm Đấu trường không?*  
  **Đáp:** Không. Lịch sử chat được quản lý trong `AppContext` đồng bộ với `sessionStorage`, còn điểm cao nhất và danh sách tình huống đã hoàn thành ở `/game` được lưu bền vững trong `localStorage`.

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
   * Điều phối **Demo 4 bước trên web Next.js (`http://localhost:3000`, Backend API `:8000`)**:
     1. *Kiểm tra tin nhắn (`/`):* Thử **gợi ý nhập nhanh** (gõ từ khóa + `Tab`) hoặc bấm 1 kịch bản mẫu (Phạt nguội CSGT / Giả ngân hàng) → Chỉ vào Đồng hồ SVG `RiskGauge`, cảnh báo URL, bẫy tâm lý, bài báo RAG và nút **Sao chép cảnh báo**.
     2. *Soi bill giả (`/fake-bill`):* Soi thử `Mẫu bill giả` (bấm **Phóng to** xem chi tiết) → Chỉ rõ Lớp 1 & Lớp 2 (C2PA/AI 96%). Chuyển sang `Mẫu bill thật` (90%) để chứng minh không bắt nhầm.
     3. *Đấu trường (`/game`) & Cấp cứu:* Chơi nhanh 1 lượt Đấu trường lừa đảo (xem Trọng tài AI + lưu điểm) và bấm nút đỏ **Tôi lỡ bị lừa** ở Sidebar mở modal 3 bước + 7 hotline ngân hàng.
     4. *Sidebar & Thư viện (`/library`):* Bấm chuyển **Chế độ tối / sáng**, bật **Chữ to 145%** tức thì cho người cao tuổi và lọc nhanh trong **Thư viện cảnh báo**.

### ❓ Câu hỏi Hội đồng hay hỏi TV4 & Cách trả lời
* **Hỏi:** *Trong bài toán chống lừa đảo, giữa Precision và Recall chỉ số nào quan trọng hơn?*  
  **Đáp:** **Recall** đối với lớp lừa đảo rất quan trọng vì bỏ sót một vụ lừa đảo (False Negative) có thể khiến người dân mất tiền thật; tuy nhiên vẫn cần cân bằng bằng F1-Score và ngưỡng RAG (`>= 0.55`) để không báo nhầm quá nhiều tin nhắn bình thường gây hoang mang.
* **Hỏi:** *Nếu đang demo trực tiếp mà mạng phòng thi yếu hoặc hết quota Gemini thì xử lý sao?*  
  **Đáp:** Hệ thống tự động chuyển về chế độ dự phòng cục bộ (`Dynamic Scorer` + `Heuristic Forensics` + `Keyword RAG`) nên toàn bộ 4 màn hình vẫn chạy mượt mà không bị lỗi.

---

## ✅ Checklist Chung Trước Giờ Thuyết Trình (Cả 4 Thành Viên)
- [ ] Cài đủ thư viện Backend & Frontend: `pip install -r requirements.txt` và `npm install --prefix frontend`
- [ ] Kiểm tra file `.env` có `GEMINI_API_KEY` còn hạn mức (hoặc chuẩn bị sẵn key dự phòng để nhập trong *Cài đặt API key*)
- [ ] Chạy thử trước trên máy trình chiếu (2 terminal):
  - Terminal 1: `python -m uvicorn backend.api.server:app --host 127.0.0.1 --port 8000`
  - Terminal 2: `npm run build --prefix frontend && npm run start --prefix frontend` (mở `http://localhost:3000`)
- [ ] Chuẩn bị sẵn 1 video quay màn hình demo dự phòng (phòng trường hợp sự cố máy chiếu)
