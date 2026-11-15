"""
Script: Omni-Channel AI Knowledge Trainer (Học từ Văn bản, Link, Hình ảnh)
Phụ trách: TV1 - Tự động hóa quá trình mở rộng kho RAG đa phương thức
"""

import os
import sys
import json
import urllib.request

# Cài đặt thêm thư viện nếu thiếu: pip install pillow requests
try:
    from PIL import Image
    import requests
    from google import genai
    from google.genai import types
except ImportError:
    print("⚠️ Thiếu thư viện. Hãy mở Terminal gõ: pip install pillow requests")
    sys.exit()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
KNOWLEDGE_PATH = os.path.join(BACKEND_DIR, "data", "scam_knowledge.json")

def fetch_content_from_url(url: str) -> str:
    """Hàm cào dữ liệu thô từ một đường link bài báo"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # Trả về khoảng 3000 ký tự đầu tiên để AI đọc (tránh quá tải)
        return response.text[:3000] 
    except Exception as e:
        return f"[Không thể đọc link: {e}]"

def train_and_save_to_json(input_type: str, input_data: str, api_key: str):
    print("\n⏳ AI đang phân tích và chiết xuất dữ liệu...")
    client = genai.Client(api_key=api_key)
    
    # Chuẩn bị nội dung đưa vào AI tùy theo loại dữ liệu
    contents_to_send = []
    
    prompt = """
    Đóng vai chuyên gia phân tích dữ liệu tội phạm mạng. 
    Hãy phân tích thông tin tôi cung cấp (có thể là chữ, ảnh hoặc bài báo) và trích xuất kịch bản lừa đảo.
    
    YÊU CẦU TRẢ VỀ DUY NHẤT ĐỊNH DẠNG JSON SAU:
    {
        "title": "<Tự đặt tiêu đề cảnh báo ngắn gọn>",
        "source": "<Nguồn học: Hình ảnh / Bài báo / Tin nhắn thô>",
        "url": "<Để trống nếu không có, hoặc điền link nếu nguồn là bài báo>",
        "category_name": "<Phân loại thủ đoạn>",
        "summary": "<Tóm tắt thủ đoạn này trong 1-2 câu>",
        "keywords": ["<từ khóa 1>", "<từ khóa 2>", "<từ khóa 3>", "<từ khóa 4>"]
    }
    """
    
    # Xử lý theo từng nguồn
    if input_type == "text":
        contents_to_send = [f"Nội dung thô: {input_data}", prompt]
    elif input_type == "link":
        print("🔗 Đang cào dữ liệu từ website...")
        web_text = fetch_content_from_url(input_data)
        contents_to_send = [f"Dữ liệu cào từ website ({input_data}):\n{web_text}", prompt]
    elif input_type == "image":
        print("📸 Đang đọc hình ảnh...")
        try:
            img = Image.open(input_data)
            contents_to_send = [img, "Ảnh chụp màn hình vụ lừa đảo.", prompt]
        except Exception as e:
            print(f"❌ Lỗi đọc ảnh: {e}")
            return

    try:
        # Gọi Gemini đa phương thức
        response = client.models.generate_content(
            model="gemini-1.5-flash", # Dùng 1.5-flash vì nó cân được cả ảnh, text và code
            contents=contents_to_send,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        new_knowledge = json.loads(response.text)
        
        # --- BƯỚC LƯU VÀO FILE JSON ---
        if os.path.exists(KNOWLEDGE_PATH):
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                try:
                    knowledge_base = json.load(f)
                except:
                    knowledge_base = []
        else:
            knowledge_base = []
            
        new_knowledge["id"] = len(knowledge_base) + 1
        knowledge_base.append(new_knowledge)
        
        with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
            json.dump(knowledge_base, f, ensure_ascii=False, indent=4)
            
        print(f"✅ ĐÃ HỌC XONG! Đã nạp kịch bản '{new_knowledge['title']}' vào kho RAG.")
        
    except Exception as e:
        print(f"❌ Quá trình Train thất bại: {e}")

if __name__ == "__main__":
    print("=" * 65)
    print("🧠 AI KNOWLEDGE TRAINER (HỖ TRỢ ĐA PHƯƠNG THỨC: TEXT, LINK, ẢNH)")
    print("=" * 65)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Vui lòng set biến môi trường GEMINI_API_KEY trước khi chạy!")
        sys.exit()
        
    while True:
        print("\nChọn nguồn dữ liệu muốn AI học:")
        print("1. Chữ / Tin nhắn thô")
        print("2. Đường link (URL bài báo)")
        print("3. Hình ảnh (Đường dẫn tới file ảnh)")
        print("0. Thoát")
        
        choice = input("👉 Nhập lựa chọn (0-3): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            data = input("📝 Dán nội dung tin nhắn vào đây: ").strip()
            if data: train_and_save_to_json("text", data, api_key)
        elif choice == '2':
            data = input("🔗 Dán link bài báo (VD: https://dantri...): ").strip()
            if data: train_and_save_to_json("link", data, api_key)
        elif choice == '3':
            data = input("📸 Nhập đường dẫn ảnh (VD: D:/anh_lua_dao.jpg): ").strip()
            if data: train_and_save_to_json("image", data, api_key)
        else:
            print("⚠️ Lựa chọn không hợp lệ.")