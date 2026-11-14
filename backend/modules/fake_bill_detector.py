import os
import json
import google.generativeai as genai
from PIL import Image

class FakeBillDetector:
    def __init__(self, api_key: str = None):
        """
        Khởi tạo module kiểm tra bill với Gemini API.
        """
        # Cấu hình API Key (Nếu không truyền vào, nó sẽ tự tìm biến môi trường GEMINI_API_KEY)
        if api_key:
            genai.configure(api_key=api_key)
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Sử dụng Gemini mà API bọn m có, check bằng cách chạy file check_model.py
        self.model = genai.GenerativeModel('gemini-4-hydrogen')
        
    def analyze_bill(self, image_path: str) -> dict:
        """
        Gửi ảnh biên lai lên Gemini và ép nó trả về chuẩn JSON.
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": "Không tìm thấy file ảnh tại đường dẫn này."}

        try:
            # Dùng thư viện Pillow mở ảnh lên
            img = Image.open(image_path)
            
            # Viết Prompt "đặt hàng" Gemini đóng vai chuyên gia điều tra và trả về đúng form JSON
            prompt = """
            Bạn là một chuyên gia điều tra gian lận tài chính. Hãy soi kỹ bức ảnh biên lai chuyển khoản này.
            Nhiệm vụ của bạn là tìm ra các dấu hiệu chỉnh sửa, cắt ghép, làm giả. 
            Hãy chú ý đến: sai font chữ, viền chữ mờ hoặc lem nhem, sai logo/màu sắc ngân hàng, thời gian giao dịch phi lý, khoảng cách chữ không đều, hoặc bố cục bị lệch.
            
            TRẢ VỀ KẾT QUẢ DUY NHẤT DƯỚI DẠNG JSON (Không giải thích lằng nhằng thêm) với cấu trúc chính xác sau:
            {
                "success": true,
                "is_fake": true (nếu nghi ngờ giả mạo) hoặc false (nếu trông bình thường),
                "confidence_score": <nhập 1 số từ 0 đến 100 thể hiện mức độ tự tin của bạn>,
                "suspicious_points": ["liệt kê dấu hiệu 1", "liệt kê dấu hiệu 2", ...],
                "conclusion": "Kết luận ngắn gọn khuyên người dùng nên làm gì"
            }
            """
            
            # Ném cả câu lệnh và bức ảnh cho Gemini xử lý
            response = self.model.generate_content([prompt, img])
            
            # Bóc tách JSON từ kết quả text của Gemini (Đề phòng Gemini bọc kết quả trong thẻ ```json ... ```)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
                
            # Ép kiểu text thành Dictionary của Python
            result_dict = json.loads(response_text)
            return result_dict

        except json.JSONDecodeError:
             return {"success": False, "error": "Lỗi: Gemini không trả về đúng chuẩn JSON."}
        except Exception as e:
            return {"success": False, "error": f"Lỗi hệ thống hoặc gọi API: {str(e)}"}

if __name__ == "__main__":
    # === KHU VỰC TEST NHANH DÀNH CHO BẠN ===
    
    # 1. Điền API Key của bạn vào đây (Nhớ xóa đi trước khi push lên GitHub để khỏi lộ Key)
    TEST_API_KEY = "API KEY cua bon m" 
    
    # 2. Khởi tạo class
    detector = FakeBillDetector(api_key=TEST_API_KEY)
    
    # 3. Chuẩn bị 1 tấm ảnh bill (thật hoặc giả) để cùng thư mục, đổi tên thành test_bill.jpg
    test_image = "test_bill.jpg" 
    
    if os.path.exists(test_image):
        print(f"Đang gửi ảnh {test_image} cho Gemini soi...")
        ket_qua = detector.analyze_bill(test_image)
        
        # In kết quả ra màn hình cho đẹp
        print("\n=== KẾT QUẢ TỪ GEMINI ===")
        print(json.dumps(ket_qua, indent=4, ensure_ascii=False))
    else:
        print(f"Vui lòng copy 1 ảnh bill vào thư mục hiện tại, đặt tên là '{test_image}' để test.")