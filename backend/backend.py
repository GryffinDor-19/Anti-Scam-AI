import os  # Thư viện xử lý đường dẫn hệ thống
import json  # Thư viện đọc và in định dạng JSON
from modules.semantic_analyzer import analyze_scam_content  # Nạp hàm phân tích AI từ module semantic_analyzer

# Xác định đường dẫn tới file backend/data/scam_knowledge.json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa file backend.py hiện tại
KNOWLEDGE_PATH = os.path.join(CURRENT_DIR, "data", "scam_knowledge.json")  # Đường dẫn tới file scam_knowledge.json

def find_matching_article(user_text: str) -> dict:  # Hàm tìm bài báo khớp nhất trong scam_knowledge.json
    try:  # Mở và đọc file dữ liệu 20 bài báo
        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:  # Đọc file với bảng mã tiếng Việt UTF-8
            articles = json.load(f)  # Nạp danh sách 20 bài báo vào biến articles
    except Exception:  # Nếu không tìm thấy file
        return None  # Trả về None để AI tự phân tích

    text_lower = user_text.lower()  # Chuyển tin nhắn cần kiểm tra về chữ thường
    best_article = None  # Lưu bài báo khớp nhất
    max_score = 0  # Lưu điểm khớp từ khóa cao nhất

    for article in articles:  # Duyệt qua từng bài báo trong kho (từ id 1 đến id 20)
        score = 0  # Điểm khớp của bài báo hiện tại
        for kw in article.get("keywords", []):  # Duyệt qua từng từ khóa của bài báo
            kw_lower = kw.lower()  # Chuyển từ khóa về chữ thường
            if kw_lower in text_lower:  # Nếu cả cụm từ khóa nằm trong tin nhắn người dùng
                score += 3  # Cộng 3 điểm ưu tiên
            else:  # Kiểm tra từng từ đơn quan trọng trong từ khóa
                for word in kw_lower.split():  # Tách các từ đơn
                    if len(word) >= 4 and word in text_lower:  # Nếu từ đơn dài từ 4 ký tự trở lên xuất hiện trong tin nhắn
                        score += 1  # Cộng 1 điểm phụ

        if score > max_score:  # Nếu bài báo này có điểm khớp cao hơn các bài trước
            max_score = score  # Cập nhật điểm cao nhất
            best_article = article  # Chọn bài báo này

    return best_article if max_score >= 2 else None  # Chỉ trả về bài báo nếu đạt từ 2 điểm khớp trở lên

def analyze_scam(user_text: str) -> dict:  # Hàm chuẩn tên gọi analyze_scam(user_text: str) chốt với Frontend
    matched_article = find_matching_article(user_text)  # Bước 1: Tìm bài báo khớp trong scam_knowledge.json
    ai_result = analyze_scam_content(user_text=user_text, rag_article=matched_article)  # Bước 2: Gọi AI phân tích
    
    # Bước 3: Đóng gói trả về đúng 6 trường theo cấu trúc file mock_response
    return {  # Trả về dict gồm đúng 6 trường
        "risk_score": int(ai_result.get("risk_score", 50)),  # 1. Số nguyên 0 - 100 để vẽ đồng hồ đo rủi ro
        "threat_level": ai_result.get("threat_level", "Đáng ngờ"),  # 2. Chuỗi: "An toàn", "Đáng ngờ", hoặc "Nguy cơ cao"
        "detected_tactic": ai_result.get("detected_tactic", "Chưa xác định"),  # 3. Tên thủ đoạn lừa đảo mà AI phát hiện
        "explanation": ai_result.get("explanation", "Cần cảnh giác khi giao dịch trực tuyến."),  # 4. Lời giải thích ngắn gọn của AI
        "psychological_traps": ai_result.get("psychological_traps", []),  # 5. Danh sách các bẫy tâm lý phát hiện
        "action_recommendations": ai_result.get("action_recommendations", [])  # 6. Danh sách lời khuyên hành động cho người dùng
    }

# --- KHỐI CHẠY TƯƠNG TÁC TRÊN TERMINAL (IN RA ĐÚNG ĐỊNH DẠNG FILE MOCK) ---
if __name__ == "__main__":  # Chạy khi gọi lệnh python backend/backend.py
    print("=" * 65)  # In đường kẻ phân cách
    print("🤖 TEST BACKEND ANTI-SCAM (IN RA ĐÚNG CHUẨN FILE MOCK 6 TRƯỜNG)")  # Tiêu đề mới
    print("Nhập tin nhắn cần kiểm tra. Gõ 'exit' hoặc 'quit' để thoát.")  # Hướng dẫn thoát
    print("=" * 65)  # In đường kẻ phân cách
    
    while True:  # Vòng lặp nhập tin nhắn liên tục
        try:  # Nhận nội dung từ bàn phím
            user_input = input("\n💬 Bạn nhập tin nhắn cần check: ").strip()  # Đọc chuỗi nhập vào
            if user_input.lower() in ["exit", "quit"]:  # Nếu gõ exit hoặc quit
                print("👋 Đã thoát chương trình.")  # Thông báo thoát
                break  # Dừng vòng lặp
            if not user_input:  # Nếu bấm Enter trống
                continue  # Yêu cầu nhập lại
                
            result = analyze_scam(user_input)  # Gọi hàm xử lý chính
            
            # In trực tiếp gói JSON 6 trường giống hệt cấu trúc file mock_response.json
            print(json.dumps(result, ensure_ascii=False, indent=2))  # In ra định dạng JSON chuẩn với thụt lề 2 khoảng trắng
            
        except KeyboardInterrupt:  # Bắt tổ hợp phím Ctrl + C
            print("\n👋 Đã thoát chương trình.")  # Thông báo thoát
            break  # Dừng vòng lặp