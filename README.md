# 🛡️ Lá Chắn Số (AntiScam AI) — Hệ Thống Trợ Lý Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức

> **Bài tập lớn môn Trí tuệ Nhân tạo (INT3401)**  
> **Phân ban:** Track 1.1 Application Track  
> **Repository:** [GryffinDor-19/Anti-Scam-AI](https://github.com/GryffinDor-19/Anti-Scam-AI)  
> **Mục tiêu:** Bảo vệ người dân và người cao tuổi trước các thủ đoạn lừa đảo tinh vi trên không gian mạng bằng mô hình suy luận đa phương thức, đối soát vector thực tế (RAG), giám định biên lai 2 lớp và mô phỏng tình huống tương tác trên giao diện web hiện đại.

---

## 🌟 Tính Năng Nổi Bật (Khớp 100% Mã Nguồn Hiện Tại)

1. **💬 Màn hình 1 — Kiểm tra tin nhắn và đường link (`/`, `frontend/src/app/page.tsx`):**
   - Khung nhập tin nhắn đặt ngay trên đầu khi trang trống, tích hợp **nút Dán nhanh** (1 chạm từ clipboard), **gợi ý nhập nhanh thông minh** (tự động lọc câu mẫu khi đang gõ + nhấn `Tab` chọn nhanh + dải chip gợi ý 1-chạm) và **tải ảnh đính kèm**.
   - Đánh giá mức độ rủi ro trên thang điểm **0–100** bằng **Đồng hồ bán nguyệt SVG (`RiskGauge.tsx`)** trực quan, tô sáng từ khóa nguy hiểm (`highlightKeywords`), cảnh báo kỹ thuật URL (đuôi tên miền lạ, link rút gọn, thiếu HTTPS).
   - Bóc trần các bẫy tâm lý, đưa ra khuyến nghị hành động rõ ràng kèm **nút Sao chép cảnh báo** để gửi nhanh cho người thân qua Zalo/SMS và đối chiếu bài báo chính thống (RAG).
   - Lưu lịch sử phiên kiểm tra tự động trong `sessionStorage` (`AppContext.tsx`) giúp chuyển trang không bị mất kết quả.
   - Kết nối lõi AI backend chạy **đua đa luồng 3 mô hình Gemini** (`gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.7-flash`) qua `ThreadPoolExecutor` và tự động fallback sang bộ chấm điểm cục bộ (`Dynamic Scorer`) khi offline hoặc thiếu API key.

2. **🧾 Màn hình 2 — Kiểm tra biên lai chuyển khoản (`/fake-bill`, `frontend/src/app/fake-bill/page.tsx`):**
   - **Lớp 1 (Thị giác và phông chữ):** Kiểm tra bố cục ngân hàng, phông chữ số tiền, căn lề và tính hợp lệ ngày giao dịch.
   - **Lớp 2 (Pixel, ELA và metadata):** Trích xuất EXIF, quét chữ ký nhị phân phát hiện dấu vết phần mềm/AI tạo sinh (`C2PA`, `ChatGPT`, `OpenAI`, `Photoshop`, `Canva`, `Picsart`), kiểm tra tỷ lệ khung hình (`> 0.58`) và cường độ cạnh nét / độ bão hòa màu HSV; kết hợp gọi tuần tự **Gemini Vision** (`gemini-3.8-flash` → `3.5-flash-lite`) và tự động fallback về bộ pháp y số heuristic cục bộ.
   - Tích hợp sẵn mẫu **bill giả** (`fake_bill.jpg`), **bill thật** (`test_bill.jpg`), kéo-thả ảnh tải lên và **Lightbox phóng to ảnh** để tự đối chiếu chi tiết.

3. **🎮 Màn hình 3 — Đấu trường lừa đảo (`/game`, `frontend/src/app/game/page.tsx`):**
   - **15 tình huống lừa đảo thực tế** thuộc **13 nhóm thủ đoạn** (`scam_scenarios.json`), mỗi tình huống gồm **3 lượt đối thoại** tương tác liên tiếp.
   - Hỗ trợ **chọn phương án phản ứng nhanh** hoặc **tự gõ câu trả lời** (chấm điểm theo từ khóa tiếng Việt có dấu & không dấu qua API `POST /api/game/evaluate`).
   - **Trọng tài AI** chấm điểm theo 3 mức: **Phản xạ an toàn** (`+30 điểm`), **Chưa dứt khoát** (`+10 điểm, -10 HP`), **Đã sập bẫy** (`0 điểm, -35 HP`), tổng kết dấu hiệu nhận diện và tự động lưu tiến độ + điểm cao nhất vào `localStorage`.

4. **📚 Màn hình 4 — Thư viện cảnh báo và hotline (`/library`, `frontend/src/app/library/page.tsx`):**
   - Tách bạch rõ nguồn dữ liệu **Bài báo chính thống (20 bài)** từ Cục An toàn thông tin, Bộ Công an, VnExpress, Tuổi Trẻ... và **AI tự học (Omni-Learn)** (loại bỏ các mẫu an toàn khỏi danh sách cảnh báo).
   - Hỗ trợ tìm kiếm trực tiếp theo từ khóa (live search), lọc theo nhóm thủ đoạn, kèm **Tổng đài 156/5656**, **Hotline Cục A05 (`069.234.8560`)**, **Cổng không gian mạng quốc gia** và **4 nguyên tắc vàng**.

5. **🚨 Cấp cứu Giờ Vàng (`EmergencyDrawer.tsx` & `emergency_manager.py`):**
   - Nút đỏ **Tôi lỡ bị lừa** ghim cố định ngay đầu Sidebar trái (và topbar mobile), mở modal 2 cột gồm **3 bước xử lý trong 15 phút đầu** cùng **7 hotline ngân hàng lớn** (`Vietcombank`, `Techcombank`, `MB Bank`, `VietinBank`, `BIDV`, `VPBank`, `Agribank`) và **Cục A05** gắn sẵn liên kết `tel:` gọi 1 chạm.

6. **🌓 Giao diện Next.js hiện đại, Light/Dark mode & Trợ năng người cao tuổi (`AppShell.tsx`, `globals.css`):**
   - Thiết kế phẳng tối giản (không gradient, không glow, chuẩn **sentence case**) với logo khiên 2 mảng riêng (`BrandMark.tsx`) và Sidebar điều hướng cố định bên trái (tự động chuyển thành Drawer trượt trên mobile).
   - **Chế độ tối / sáng (`Warm Charcoal` & `Furrow Stone`):** Tự động nhận diện theo hệ điều hành lần đầu (`prefers-color-scheme`), có công tắc chuyển đổi tức thì, lưu vào `localStorage` và chèn script khởi tạo sớm trong `<head>` để **không nháy màn hình (Zero-FOUC)**.
   - **Trợ năng chữ to, dễ đọc:** Bật/tắt phản hồi **tức thì 0ms** với 3 mức phóng đại **115%**, **130%** và **145%**, giữ nguyên bố cục không tràn ngang.

---

## 🏗️ Kiến Trúc Hệ Thống & Cấu Trúc Dự Án Thực Tế

Hệ thống áp dụng kiến trúc tách biệt **Client–Server**:
- **Frontend (`frontend/`, cổng `3000`):** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4, Lucide Icons.
- **API Layer (`backend/api/server.py`, cổng `8000`):** Starlette + Uvicorn ASGI REST API với 8 endpoints (`/api/health`, `/api/analyze`, `/api/fake-bill/analyze`, `/api/fake-bill/sample/{sample_type}`, `/api/emergency`, `/api/library`, `/api/game/scenarios`, `/api/game/evaluate`).
- **AI Core (`backend/`):** Toàn bộ lõi suy luận Python (`AntiScamPipeline`, `FakeBillDetector`, `RAGCaseMatcher`, `Dynamic Scorer`, `EmergencyManager`).

```text
AntiScam_AI/
├── .gitignore                              # Chặn file tạm, .env, node_modules/, .next/, hallmark/
├── anti_scam_core.py                       # Lõi tương thích AntiScam Core
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.md      # Kế hoạch phân công nhiệm vụ theo tuần (TV1–TV4)
├── KE_HOACH_PHAN_CONG_NHOM_4_NGUOI.html    # Bản trình bày HTML kế hoạch phân công nhóm
├── HUONG_DAN_THUYET_TRINH_NHOM.md          # Phân công nội dung ôn tập & hỏi đáp bảo vệ cho 4 thành viên
├── README.md                               # Tài liệu tổng quan & kiến trúc khớp mã nguồn Git
├── requirements.txt                        # Danh sách thư viện Python phụ thuộc (AI + Starlette/Uvicorn)
├── so_do_tuong_tac_tinh_gian.png           # Sơ đồ luồng tương tác hệ thống
│
├── backend/                                # [Backend, REST API & AI Engines]
│   ├── backend.py                          # Cổng tương thích tầng Backend
│   ├── api/                                # [REST API Layer - Cầu nối cho Next.js]
│   │   ├── __init__.py
│   │   └── server.py                       # ASGI Server (Starlette + Uvicorn, CORS, 8 REST endpoints)
│   ├── data/
│   │   ├── mock_response.json              # Hợp đồng JSON chuẩn 6 trường đầu ra
│   │   ├── scam_knowledge.json             # Kho tri thức RAG (20 bài báo chính thống + Omni-Learn)
│   │   ├── scam_learned_cache.json         # Bộ nhớ đệm mẫu đã học
│   │   └── scam_scenarios.json             # 15 tình huống Đấu trường lừa đảo (3 lượt/tình huống)
│   ├── emergency/
│   │   └── emergency_manager.py            # Danh bạ Hotline ngân hàng & quy trình cấp cứu 15 phút
│   ├── engines/                            # Các động cơ AI & xử lý lõi (TV1 & TV2)
│   │   ├── dynamic_scorer.py               # Thuật toán chấm điểm rủi ro đa tiêu chí (hỗ trợ teencode/không dấu)
│   │   ├── fake_bill_detector.py           # Giám định bill 2 lớp (EXIF/C2PA/Pixel + Gemini Vision)
│   │   ├── fast_filter.py                  # Bộ lọc từ khóa/link nhanh (kế thừa)
│   │   ├── llm_analyzer.py                 # Giao tiếp mô hình Gemini LLM
│   │   ├── rag_case_matcher.py             # Đối soát vector FAISS + MiniLM & fallback từ khóa
│   │   └── semantic_analyzer.py            # Live URL Preview + Đua đa luồng 3 Gemini + Fallback Scorer
│   ├── gateway/                            # Điều phối Pipeline & Kiểm thử (TV1 & TV4)
│   │   ├── backend.py                      # Gateway tiếp nhận
│   │   ├── batch_test.py                   # Script chạy kiểm thử hàng loạt
│   │   ├── cli_test.py                     # Trình chạy kiểm thử dòng lệnh (CLI)
│   │   ├── knowledge_trainer.py            # Công cụ hỗ trợ huấn luyện dữ liệu RAG
│   │   ├── pipeline.py                     # Nhạc trưởng điều phối (URL -> RAG -> Gemini Racing -> Format -> Omni-Learn)
│   │   ├── response_formatter.py           # Chuẩn hóa đầu ra JSON 6 trường
│   │   ├── test_report.json                # Kết quả chạy kiểm thử mẫu
│   │   └── threat_classifier.py            # Phân loại mức độ đe dọa & thủ đoạn
│   ├── knowledge/
│   │   └── retriever.py                    # Truy xuất bài báo chính thống (lọc stopwords & bỏ mẫu an toàn)
│   └── modules/                            # Lớp tương thích ngược & ảnh mẫu kiểm thử
│       ├── check_model.py                  # Kiểm tra danh sách model Gemini khả dụng
│       ├── fake_bill.jpg                   # Ảnh hóa đơn giả mẫu
│       ├── test_bill.jpg                   # Ảnh hóa đơn thật mẫu (Vietcombank)
│       └── ...
│
└── frontend/                               # [Frontend Next.js 15 & UX - TV3]
    ├── package.json                        # Next.js 15, React 19, TypeScript, Tailwind CSS v4, Lucide
    ├── next.config.ts                      # Cấu hình Next.js
    ├── postcss.config.mjs                  # Cấu hình Tailwind CSS v4 PostCSS
    ├── tsconfig.json                       # Cấu hình TypeScript
    └── src/
        ├── lib/
        │   └── api.ts                      # Client gọi 8 endpoints REST API & định nghĩa TypeScript types
        ├── context/
        │   └── AppContext.tsx              # Quản lý Light/Dark mode, Chữ to, API Key & lịch sử chat
        ├── components/
        │   ├── AppShell.tsx                # Khung Sidebar trái cố định + Mobile Drawer + công tắc trợ năng
        │   ├── BrandMark.tsx               # Logo khiên 2 mảng Lá Chắn Số (SVG phẳng)
        │   ├── EmergencyDrawer.tsx         # Modal Cấp cứu Giờ Vàng 2 cột (thích ứng Light/Dark)
        │   ├── ApiKeyModal.tsx             # Modal cài đặt Google Gemini API key
        │   └── RiskGauge.tsx               # Đồng hồ bán nguyệt SVG đo điểm rủi ro (0–100)
        └── app/
            ├── globals.css                 # Hệ biến màu Warm Charcoal (Dark) & Furrow Stone (Light)
            ├── layout.tsx                  # Root layout + script chống nháy sáng/tối (Zero-FOUC)
            ├── icon.svg                    # Favicon đồng bộ logo Lá Chắn Số
            ├── page.tsx                    # Màn hình 1: Kiểm tra tin nhắn, link, ảnh & gợi ý nhập nhanh
            ├── fake-bill/page.tsx          # Màn hình 2: Kiểm tra biên lai 2 lớp & Lightbox phóng to
            ├── game/page.tsx               # Màn hình 3: Đấu trường lừa đảo (15 tình huống, lưu tiến độ)
            └── library/page.tsx            # Màn hình 4: Thư viện cảnh báo (tách nguồn) & Hotline
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Cài đặt thư viện phụ thuộc
**Backend (Python 3.10+):**
```bash
pip install -r requirements.txt
```

**Frontend (Node.js 18+):**
```bash
npm install --prefix frontend
```

### 2. Cấu hình Gemini API Key (khuyến nghị)
Tạo file `.env` ở thư mục gốc dự án hoặc nhập trực tiếp trong **Sidebar → Cài đặt API key** trên giao diện web:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Nếu không nhập API Key, hệ thống vẫn chạy ổn định ở chế độ dự phòng cục bộ với `Dynamic Scorer`, `FAISS/Keyword RAG` và `Heuristic Forensics`.)*

### 3. Khởi chạy hệ thống (2 Terminal)

**Terminal 1 — Khởi chạy Backend REST API (`http://localhost:8000`):**
```bash
python -m uvicorn backend.api.server:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Build & khởi chạy Frontend Next.js (`http://localhost:3000`):**
```bash
# Chế độ phát triển (dev):
npm run dev --prefix frontend

# Hoặc chế độ sản phẩm (production - khuyến nghị khi demo bảo vệ):
npm run build --prefix frontend
npm run start --prefix frontend
```

Mở trình duyệt truy cập: **`http://localhost:3000`**.
