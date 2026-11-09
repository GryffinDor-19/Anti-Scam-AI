# 🛡️ AntiScam AI — Hệ Thống Trợ Lý Phòng Chống Lừa Đảo Trực Tuyến Đa Phương Thức

> **Bài tập lớn môn Trí tuệ Nhân tạo (INT3401)**  
> **Phân ban:** Track 1.1 Application Track  
> **Mục tiêu:** Bảo vệ người dân và người cao tuổi trước các thủ đoạn lừa đảo tinh vi trên không gian mạng bằng mô hình suy luận đa phương thức và đối soát dữ liệu thực tế.

---

## 🌟 Tính Năng Nổi Bật

1. **🔍 Thẩm định Tin nhắn & Phân tích Bẫy Tâm lý:**
   - Đánh giá mức độ rủi ro trên thang điểm 0–100 bằng **Đồng hồ Bán nguyệt (Speedometer Gauge)** trực quan.
   - Bóc trần các bẫy thao túng: Dọa dẫm uy quyền, ép buộc thời gian, cô lập nạn nhân.
2. **📰 RAG Grounding (Đối chiếu Dẫn chứng Thực tế):**
   - Tự động đối soát nội dung nghi vấn với kho tri thức **20 bài báo cảnh báo chính thống** từ *Cục An toàn thông tin (Bộ TT&TT)*, *Bộ Công an*, *Báo Chính phủ*, *Tuổi Trẻ*, *Thanh Niên*, *VnExpress*...
   - Cung cấp link gốc để người dùng kiểm chứng bài báo thực tế tức thì.
3. **🧾 Giám định Hóa đơn Chuyển tiền Giả (Fake Bill):**
   - Hỗ trợ chủ shop và người bán hàng online phát hiện biên lai chuyển khoản giả mạo (lệch phông chữ, mờ nhòe số tiền, sai chu kỳ mã giao dịch).
4. **🚨 Chế độ Cấp cứu Khẩn cấp (Thời điểm vàng):**
   - 3 bước hành động khẩn cấp cứu tiền.
   - Hotline khóa tài khoản/thẻ ngân hàng 1-chạm (Vietcombank, BIDV, Techcombank, Agribank, ACB, VPBank, MBBank) & Cục An ninh mạng A05.
5. **👵 Chế độ Người lớn tuổi (Elderly Accessibility):**
   - Phóng to toàn bộ giao diện 1.45 lần bằng chuẩn CSS Zoom, cỡ chữ to rõ, độ tương phản cao.
6. **🕒 Bảng Lịch sử Thẩm định Trong Phiên (Session Audit Log):**
   - Tự động ghi nhật ký và thống kê tỷ lệ lừa đảo của các lượt quét trong phiên làm việc.

---

## 📁 Cấu Trúc Dự Án (Phân Tách Module Chuẩn)

```text
Anti-Scam-AI/
├── streamlit/                      # [Frontend - TV3] Toàn bộ mã nguồn giao diện Streamlit
│   └── app_anti_scam.py            # Giao diện chính (Đồng hồ rủi ro, Fake Bill, Lịch sử)
│
├── backend/                        # [Backend & AI - TV1 & TV2] Module AI, RAG & Dữ liệu
│   ├── data/
│   │   └── scam_knowledge.json     # Kho tri thức 20 bài báo cảnh báo chính thống
│   └── modules/
│       ├── __init__.py
│       ├── emergency_manager.py    # Quản lý danh bạ hotline & quy trình cấp cứu
│       └── rag_case_matcher.py     # Module RAG đối soát từ khóa và bài báo tương đồng
│
├── requirements.txt                # Danh sách thư viện phụ thuộc
├── .gitignore                      # Cấu hình bỏ qua file tạm, bytecode
└── README.md                       # Tài liệu hướng dẫn dự án
```

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
