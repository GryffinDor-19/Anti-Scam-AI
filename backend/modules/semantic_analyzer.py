import json  # Thư viện xử lý dữ liệu định dạng JSON
from google import genai  # Nạp thư viện Google GenAI thế hệ mới
from google.genai import types  # Nạp bộ công cụ cấu hình tham số cho AI

import os
# Xóa key thật đi, thay bằng biến môi trường
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))

def local_fallback_6_fields(user_text: str, rag_article: dict = None) -> dict:  # Hàm dự phòng trả về đúng 6 trường của file mock
    text_lower = user_text.lower()  # Chuyển tin nhắn về chữ thường để dò từ khóa
    traps = []  # Khởi tạo danh sách bẫy tâm lý
    score = 20  # Điểm rủi ro mặc định ban đầu
    tactic = rag_article["category_name"] if rag_article else "Chưa xác định rõ thủ đoạn"  # Lấy tên thủ đoạn từ RAG nếu có

    if any(k in text_lower for k in ["shipper", "nhận hàng", "giao hàng", "shopee", "bến xe", "chuyển tiền hộ"]):  # Dò nhóm giao hàng/shipper
        score = 80  # Điểm rủi ro cao
        tactic = rag_article["category_name"] if rag_article else "Mạo Danh Người Thân & Shipper Giả"  # Gán tên thủ đoạn
        traps.append("Thao túng niềm tin: Giả danh shipper báo giao đơn hàng hoặc nhờ chuyển khoản hộ")  # Thêm bẫy tâm lý
        traps.append("Ép thời gian: Hối thúc chuyển tiền nhanh khi nạn nhân chưa kịp kiểm tra đơn hàng")  # Thêm bẫy tâm lý
    elif any(k in text_lower for k in ["công an", "vneid", "tòa án", "định danh", "khóa tài khoản", "rửa tiền"]):  # Dò nhóm công quyền
        score = 95  # Điểm nguy hiểm tối đa
        tactic = rag_article["category_name"] if rag_article else "Giả Danh Cơ Quan Công Quyền"  # Gán tên thủ đoạn
        traps.append("Uy quyền / Sợ hãi: Mạo danh cơ quan nhà nước báo lỗi hoặc dọa khóa tài khoản")  # Thêm bẫy uy quyền
        traps.append("Ép thời gian: Yêu cầu thao tác cập nhật/chuyển khoản gấp")  # Thêm bẫy thời gian
    elif any(k in text_lower for k in ["cộng tác viên", "hoa hồng", "nhiệm vụ", "cọc", "việc nhẹ", "thưởng", "iphone"]):  # Dò nhóm việc làm/trúng thưởng
        score = 85  # Điểm nguy hiểm cao
        tactic = rag_article["category_name"] if rag_article else "Tuyển CTV Việc Nhẹ Lương Cao"  # Gán tên thủ đoạn
        traps.append("Hám lợi: Dụ dỗ nhận hoa hồng cao hoặc trúng thưởng lớn")  # Thêm bẫy hám lợi
        traps.append("Mua chuộc niềm tin: Yêu cầu đóng phí hoặc nạp tiền cọc trước để nhận tiền")  # Thêm bẫy niềm tin

    level = "An toàn" if score < 30 else ("Đáng ngờ" if score <= 70 else "Nguy cơ cao")  # Quy đổi đúng 3 mức của file mock
    rag_note = f" (Trùng khớp cảnh báo: {rag_article['title']} - {rag_article['source']})" if rag_article else ""  # Ghép nguồn báo nếu có

    return {  # Trả về đúng 6 trường theo chuẩn mock_response
        "risk_score": score,  # 1. Số nguyên 0 - 100 để vẽ đồng hồ đo rủi ro
        "threat_level": level,  # 2. Chuỗi: "An toàn", "Đáng ngờ", hoặc "Nguy cơ cao"
        "detected_tactic": tactic,  # 3. Tên thủ đoạn lừa đảo mà AI phát hiện
        "explanation": f"Phát hiện kịch bản thao túng tâm lý yêu cầu chuyển tiền hoặc cung cấp thông tin trái phép.{rag_note}",  # 4. Lời giải thích ngắn gọn
        "psychological_traps": traps if traps else ["Đánh vào sự mất cảnh giác của người dùng"],  # 5. Danh sách các bẫy tâm lý
        "action_recommendations": [  # 6. Danh sách lời khuyên hành động cho người dùng
            "Tuyệt đối không chuyển tiền và không bấm vào đường link lạ.",  # Lời khuyên 1
            "Kiểm tra lại thông tin trực tiếp trên ứng dụng chính thức hoặc gọi xác minh.",  # Lời khuyên 2
            "Chặn số liên lạc và trình báo cơ quan chức năng nếu bị đe dọa."  # Lời khuyên 3
        ]
    }

def analyze_scam_content(user_text: str, rag_article: dict = None) -> dict:  # Hàm phân tích chính gọi AI Gemini
    rag_context = "Không có bài báo đối chiếu trực tiếp."  # Mặc định khi không khớp từ khóa nào trong kho
    if rag_article:  # Nếu tìm thấy bài báo khớp trong scam_knowledge.json
        rag_context = f"Tiêu đề: {rag_article.get('title')} ({rag_article.get('source')}) | Thủ đoạn: {rag_article.get('category_name')} | Tóm tắt: {rag_article.get('summary')}"  # Đưa bài báo đúng vào Prompt

    prompt = f"""
    Bạn là chuyên gia phân tích lừa đảo trực tuyến tại Việt Nam.
    Hãy phân tích tin nhắn sau và tham khảo dữ liệu cảnh báo (nếu phù hợp):
    - Tin nhắn người dùng: "{user_text}"
    - Dữ liệu cảnh báo từ kho RAG: "{rag_context}"

    BẮT BUỘC trả về đúng định dạng JSON gồm đúng 6 trường như file mock sau đây:
    {{
        "risk_score": <số nguyên từ 0 đến 100>,
        "threat_level": "<chỉ chọn 1 trong 3 giá trị: An toàn | Đáng ngờ | Nguy cơ cao>",
        "detected_tactic": "<tên thủ đoạn lừa đảo mà AI phát hiện>",
        "explanation": "<lời giải thích, nhận định ngắn gọn của AI (kết hợp dẫn chứng từ dữ liệu RAG nếu khớp)>",
        "psychological_traps": [
            "<bẫy tâm lý 1: uy quyền, ép thời gian, hám lợi...>",
            "<bẫy tâm lý 2>"
        ],
        "action_recommendations": [
            "<lời khuyên hành động 1>",
            "<lời khuyên hành động 2>",
            "<lời khuyên hành động 3>"
        ]
    }}
    """  # Kết thúc chuỗi Prompt chuẩn 6 trường

    model_list = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]  # Danh sách model xoay vòng
    for model_name in model_list:  # Duyệt qua từng model
        try:  # Gửi yêu cầu lên Google Gemini
            response = client.models.generate_content(  # Gọi hàm sinh phản hồi
                model=model_name,  # Tên model
                contents=prompt,  # Nội dung Prompt
                config=types.GenerateContentConfig(  # Cấu hình ép kiểu JSON
                    response_mime_type="application/json",  # Bắt buộc trả về JSON thuần
                    temperature=0.1  # Giữ nhiệt độ thấp để kết quả chuẩn xác
                )
            )
            return json.loads(response.text)  # Chuyển chuỗi JSON của AI sang dict và trả về ngay
        except Exception:  # Nếu model bị bận 503 hoặc lỗi
            continue  # Thử model tiếp theo

    return local_fallback_6_fields(user_text, rag_article)  # Nếu server Google bận thì chạy hàm dự phòng chuẩn 6 trường