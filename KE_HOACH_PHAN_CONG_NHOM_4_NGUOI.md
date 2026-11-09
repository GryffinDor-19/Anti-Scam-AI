# 📋 KẾ HOẠCH & BẢNG PHÂN CÔNG NHIỆM VỤ DỰ ÁN (NHÓM 4 NGƯỜI)
## ĐỀ TÀI: HỆ THỐNG TRỢ LÝ PHÒNG CHỐNG LỪA ĐẢO TRỰC TUYẾN ĐA PHƯƠNG THỨC (ANTI-SCAM AI)
**Môn học:** Trí Tuệ Nhân Tạo (Artificial Intelligence) · **Track:** Application Track  
**Thời gian thực hiện:** 4 tuần (Từ Tuần 9 đến Tuần 13)

---

## 📌 PHẦN 1: BẢNG PHÂN CÔNG NHIỆM VỤ CHI TIẾT THEO THỨ TỰ THỰC HIỆN

| Thành viên & Vai trò | File phụ trách | Thứ tự các bước thực hiện (Theo tiến độ tuần) | Sản phẩm bàn giao cụ thể | Mối quan hệ phối hợp (Bàn giao cho ai) |
| :--- | :--- | :--- | :--- | :--- |
| **THÀNH VIÊN 1**<br>*(Trưởng nhóm / Lõi AI & Backend)* | `modules/semantic_analyzer.py`<br>và `backend.py` | **• Bước 1 (Đầu T9):** Ngồi với TV3 chốt cứng cấu trúc gói tin JSON đầu ra (Mock Data).<br>**• Bước 2 (T9):** Nhận bài báo & dataset từ TV2 $\rightarrow$ Viết Prompt Chain-of-Thought gọi Gemini Flash bóc 5 bẫy tâm lý, chấm Scam Score (0–100%) và cơ chế chống sập (Fallback).<br>**• Bước 3 (Giữa T10):** Nhận các module từ TV2 $\rightarrow$ Viết file tổng `backend.py` làm nhạc trưởng điều phối toàn bộ.<br>**• Bước 4 (T11 - T12):** Hỗ trợ TV4 đo chỉ số F1-Score, tối ưu tốc độ phản hồi < 3s, rà soát code lần cuối. | • File `semantic_analyzer.py` chạy độc lập.<br>• File tổng `backend.py` nhận input và trả về JSON chuẩn xác. | • Chốt chuẩn JSON cho **TV3**.<br>• Nhận dữ liệu từ **TV2**.<br>• Bàn giao backend hoàn chỉnh cho **TV3** và **TV4**. |
| **THÀNH VIÊN 2**<br>*(Kỹ sư Dữ liệu & Hệ thống RAG)* | `modules/rag_case_matcher.py`<br>`modules/fast_filter.py`<br>`modules/fake_bill_detector.py` | **• Bước 1 (2 ngày đầu T9 - ƯU TIÊN SỐ 1):** Thu thập 20 bài báo/cẩm nang Cục ATTT + lập dataset 150 mẫu tin nhắn (lừa/thật) $\rightarrow$ Giao ngay cho TV1 & TV4.<br>**• Bước 2 (T9):** Viết `fast_filter.py` (Lớp 1 lọc nhanh link <1s) và `rag_case_matcher.py` (Cosine Similarity bốc bài báo tương đồng).<br>**• Bước 3 (Giữa T10):** Viết `fake_bill_detector.py` soi bất thường hóa đơn chuyển tiền qua ảnh.<br>**• Bước 4 (T11 - T12):** Hỗ trợ TV4 test các ca ảnh mờ, link lạ; cập nhật thêm bài báo nếu cần. | • Thư mục dữ liệu bài báo đã làm sạch.<br>• File dataset kiểm thử.<br>• 3 file code module: `fast_filter.py`, `rag_case_matcher.py`, `fake_bill_detector.py`. | • Bàn giao bài báo & dataset ngay đầu T9 cho **TV1 & TV4**.<br>• Bàn giao 3 file module cho **TV1** ráp vào `backend.py`. |
| **THÀNH VIÊN 3**<br>*(Frontend & Trải nghiệm Người dùng)* | `app_anti_scam.py`<br>và `modules/emergency_manager.py` | **• Bước 1 (Đầu T9):** Thống nhất JSON với TV1 $\rightarrow$ Lấy mock data để lập trình giao diện độc lập.<br>**• Bước 2 (T9):** Viết `emergency_manager.py` (hotline ngân hàng) + Dựng khung Streamlit `app_anti_scam.py` tĩnh (ô nhập liệu, nút cấp cứu đỏ, nút chữ to cho người già).<br>**• Bước 3 (Cuối T10):** Cắm kết nối trực tiếp với `backend.py` của TV1 $\rightarrow$ Hoàn thiện giao diện sống (đổi màu Xanh/Vàng/Đỏ theo điểm, tự bung popup cấp cứu nếu rủi ro > 85%, nút chia sẻ Zalo).<br>**• Bước 4 (T12):** Cùng TV4 làm kịch bản Live Demo 3 phút và quay 1 video demo dự phòng. | • File `emergency_manager.py`.<br>• Giao diện Web Streamlit hoàn chỉnh `app_anti_scam.py` chạy mượt mà trên trình duyệt. | • Nhận chuẩn JSON từ **TV1**.<br>• Bàn giao app hoàn chỉnh cho **TV4** chạy kiểm thử.<br>• Phối hợp với **TV4** làm kịch bản Demo. |
| **THÀNH VIÊN 4**<br>*(Kiểm thử QA, Đo đạc & Báo cáo)* | Bộ 3 Báo cáo:<br>• `BAO_CAO_SAN_PHAM_1.md`<br>• `BAO_CAO_SAN_PHAM_2.md`<br>• `NHAT_KY_SU_DUNG_AI.md`<br>và Slide Thuyết trình | **• Bước 1 (T9):** Viết trước 70% lý thuyết Báo cáo (Chương 1 đến Chương 4) + Soạn thảo 10 kịch bản kiểm thử (TC-01 đến TC-10).<br>**• Bước 2 (T10):** Nhận dataset từ TV2 để chuẩn bị sẵn bảng đo đạc; cập nhật Nhật ký sử dụng AI.<br>**• Bước 3 (T11 - TRỌNG TÂM):** Cầm app chạy hàng loạt test cases $\rightarrow$ Tính toán chỉ số chính thức: **Accuracy, F1-Score (>85%), Latency** $\rightarrow$ Điền vào Chương 6 Báo cáo.<br>**• Bước 4 (T12):** Hoàn thiện 100% 3 file Báo cáo, thiết kế Slide thuyết trình (Canva/PPT), quay video demo dự phòng, điều phối nhóm tổng duyệt. | • Bảng kịch bản & số liệu kiểm thử thực tế.<br>• Trọn bộ 3 file Báo cáo chuẩn chỉnh theo yêu cầu đề bài.<br>• Bộ Slide thuyết trình và Video demo 3 phút. | • Nhận dataset từ **TV2**.<br>• Nhận app chạy được từ **TV1 & TV3** để test.<br>• Bàn giao slide và báo cáo hoàn chỉnh cho cả nhóm đi nộp. |

---

## 🧠 PHẦN 2: LỘ TRÌNH HUẤN LUYỆN & TINH CHỈNH AI (AI TRAINING ROADMAP)

### 1. Bước 1: Chuẩn bị Dữ liệu (Thời gian: 2 ngày đầu Tuần 9 - TV2)
* Thu thập 20 bài báo cảnh báo chính thức từ VnExpress, Tuổi Trẻ, Cục An toàn thông tin.
* Xây dựng tập dữ liệu kiểm thử gồm 200 mẫu tin nhắn tiếng Việt (120 tin lừa đảo, 80 tin bình thường).
* Chia tập dữ liệu: 80% dùng để tinh chỉnh prompt, 20% dùng làm bài thi kiểm thử độc lập (Test Set).

### 2. Bước 2: Huấn luyện Mô hình Tra cứu Bài báo RAG (Thời gian: 2 ngày giữa Tuần 9 - TV2 & TV1)
* Phân mảnh văn bản (Chunking 400-600 ký tự).
* Xây dựng ma trận không gian vector và đo khoảng cách ngữ nghĩa bằng thuật toán Cosine Similarity.
* Đảm bảo: Khi gõ một câu bất kỳ, hệ thống bốc đúng bài báo tương đồng trong thời gian dưới 0.05 giây.

### 3. Bước 3: Tinh chỉnh Lõi AI (Prompt Engineering / Chain-of-Thought) (Thời gian: 2 ngày cuối Tuần 9 - TV1)
* Tầng 1: Đọc hiểu ý đồ giao tiếp (nhận diện được cả teencode như `c.ọ.c`, `ck`, `stk`).
* Tầng 2: Bóc trần 5 bẫy tâm lý (*Sợ hãi, Gấp gáp, Tham lam, Tình cảm, Niềm tin*).
* Tầng 3: Kết hợp ngữ cảnh bài báo từ RAG để tính ra điểm **Scam Score (0 - 100%)**.
* Tầng 4: Ép đầu ra tuân thủ nghiêm ngặt theo định dạng JSON chuẩn.

### 4. Bước 4: Đánh giá Định lượng & Chốt số liệu (Thời gian: Tuần 11 - TV4 & TV1)
* Đo đạc 4 chỉ số khoa học cốt lõi: Accuracy, Precision, Recall, F1-Score.
* **Chỉ tiêu cam kết đạt được:** F1-Score > 85% và Thời gian phản hồi trung bình < 3 giây.

---

## ⏱️ PHẦN 3: TIMELINE TỔNG THỂ 4 TUẦN ĐẾN HẠN NỘP

* **TUẦN 9:** Hoàn thiện Lõi AI (`semantic_analyzer.py`), RAG bài báo (`rag_case_matcher.py`) và chuẩn bị xong Dataset.
* **TUẦN 10:** Hoàn thiện Giao diện Streamlit (`app_anti_scam.py`), ghép nối toàn bộ Backend - Frontend thành một Web App chạy thông suốt trên trình duyệt.
* **TUẦN 11:** Chạy toàn bộ Test Cases, đo F1-Score thực tế, xử lý các lỗi phát sinh (chống crash khi mất mạng/file rác).
* **TUẦN 12:** Đóng gói Kịch bản Live Demo 3 phút, làm Slide thuyết trình, quay video demo dự phòng và tổng duyệt thuyết trình.
* **TUẦN 13:** Nộp toàn bộ sản phẩm và tự tin bảo vệ trước Hội đồng chấm thi!
