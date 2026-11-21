"""
AntiScam Pipeline: Nhạc trưởng điều phối chuỗi phòng thủ AI (Bỏ Fast Filter, chạy thẳng RAG + Gemini).
Phụ trách: Mảng 2 - Cổng điều phối & Chuẩn hóa (TV1)
"""

import os  # Thư viện thao tác hệ thống và đường dẫn thư mục
import sys  # Thư viện quản lý đường dẫn import module của Python
import re  # Thư viện biểu thức chính quy (Regex) để tìm kiếm đường link trong văn bản
import json  # Thư viện đọc và ghi file dữ liệu JSON
from urllib.parse import urlparse  # Hàm tách tên miền (domain) từ đường link
from typing import Dict, Any, Optional  # Khai báo kiểu dữ liệu cho các tham số và giá trị trả về

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn thư mục hiện tại (gateway)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)  # Lấy đường dẫn thư mục backend
ROOT_DIR = os.path.dirname(BACKEND_DIR)  # Lấy đường dẫn thư mục gốc dự án

for p in [CURRENT_DIR, BACKEND_DIR, ROOT_DIR]:  # Duyệt qua 3 thư mục cốt lõi
    if p not in sys.path:  # Kiểm tra nếu thư mục chưa có trong đường dẫn tìm kiếm
        sys.path.insert(0, p)  # Thêm vào đầu sys.path để tránh lỗi ImportError


def extract_and_analyze_urls(text: str) -> dict:  # Định nghĩa hàm quét và phân tích dấu hiệu rủi ro của đường link
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|\b[a-zA-Z0-9-]+\.(?:com|vn|net|org|xyz|top|vip|cc|tk|ml|ga|cf|info|click|online)\b[^\s]*)'  # Regex bắt cả link có http/www lẫn tên miền trần như q66kpa.top
    urls = re.findall(url_pattern, text)  # Trích xuất danh sách tất cả đường link có trong tin nhắn

    domains = []  # Tạo danh sách rỗng để lưu các tên miền tách được
    warnings = []  # Tạo danh sách rỗng để lưu các cảnh báo kỹ thuật về link
    suspicious_tlds = ('.xyz', '.top', '.vip', '.cc', '.tk', '.ml', '.ga', '.cf')  # Các đuôi tên miền giá rẻ hay dùng để lừa đảo
    shorteners = ('bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'shorturl.at')  # Các dịch vụ rút gọn link hay dùng để che giấu đích đến

    for url in urls:  # Lặp qua từng đường link tìm được
        full_url = url if url.startswith('http') else f'http://{url}'  # Bổ sung http:// nếu link chỉ bắt đầu bằng www.
        parsed = urlparse(full_url)  # Phân tách cấu trúc URL thành giao thức, tên miền, đường dẫn
        domain = parsed.netloc.lower()  # Lấy tên miền chính và chuyển thành chữ thường

        if domain:  # Kiểm tra nếu tách được tên miền hợp lệ
            domains.append(domain)  # Lưu tên miền để đưa vào từ khóa cho RAG học
            if any(domain.endswith(tld) for tld in suspicious_tlds):  # Kiểm tra tên miền có dùng đuôi lạ không
                warnings.append(f"Tên miền {domain} dùng đuôi lạ, hay gặp trong lừa đảo")  # Thêm cảnh báo đuôi tên miền
            if any(short in domain for short in shorteners):  # Kiểm tra có phải link rút gọn không
                warnings.append(f"Link rút gọn ({domain}) có nguy cơ che giấu trang độc hại")  # Thêm cảnh báo link rút gọn
            if full_url.startswith('http://'):  # Kiểm tra xem đường link có dùng giao thức cũ không bảo mật không
                warnings.append(f"Đường link {domain} không có bảo mật HTTPS")  # Thêm cảnh báo thiếu HTTPS

    return {  # Trả về kết quả phân tích link
        "has_url": len(urls) > 0,  # Có chứa đường link hay không (True/False)
        "urls": urls,  # Danh sách các link nguyên gốc
        "domains": list(set(domains)),  # Danh sách tên miền duy nhất (đã loại bỏ trùng lặp)
        "warnings": warnings  # Danh sách các dấu hiệu đáng ngờ của đường link
    }


# 2. Nạp Lớp RAG Retriever (TV2)
try:
    from knowledge.retriever import find_matching_article  # Thử nạp hàm tìm kiếm bài báo RAG
except ImportError:
    try:
        from backend.knowledge.retriever import find_matching_article  # Thử nạp với tiền tố backend
    except ImportError:
        def find_matching_article(text): return None  # Hàm giả lập trả về rỗng nếu không nạp được module RAG

# 3. Nạp Lớp Semantic Analyzer (TV1 - Gemini AI)
try:
    from modules.semantic_analyzer import analyze_scam_content  # Thử nạp hàm gọi Gemini AI
except ImportError:
    try:
        from backend.modules.semantic_analyzer import analyze_scam_content  # Thử nạp với tiền tố backend
    except ImportError:
        from modules.semantic_analyzer import local_fallback_6_fields as analyze_scam_content  # Dùng hàm dự phòng nếu không nạp được

# 4. Nạp bộ chuẩn hóa Response Formatter (TV1)
from .response_formatter import format_scam_response  # Nạp hàm ép chuẩn 6 trường JSON


class AntiScamPipeline:  # Lớp điều phối chuỗi xử lý phòng thủ
    """
    Chuỗi xử lý tinh gọn:
    - Bỏ Fast Filter để AI tự phân tích và chấm điểm
    - Trích xuất và mớm cảnh báo về link (domain lạ, rút gọn, thiếu HTTPS) cho Gemini
    - Đối soát kho tri thức RAG (Cục ATTT)
    - Gọi Gemini AI phân tích chuyên sâu
    """

    def __init__(self):  # Hàm khởi tạo
        pass  # Không cần khởi tạo Fast Filter nữa

    def execute(self, user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:  # Hàm thực thi chính của pipeline
        clean_text = (user_text or "").strip()  # Làm sạch khoảng trắng ở hai đầu tin nhắn
        if not clean_text:  # Nếu người dùng để trống tin nhắn
            return format_scam_response({  # Trả về ngay kết quả rỗng hợp lệ
                "risk_score": 0,
                "threat_level": "An toàn",
                "detected_tactic": "Không có nội dung",
                "explanation": "Vui lòng nhập nội dung cần kiểm tra.",
                "psychological_traps": ["Không phát hiện dấu hiệu thao túng tâm lý"],
                "action_recommendations": ["Nhập nội dung tin nhắn hoặc đường link nghi vấn để thẩm định."]
            })

        # BƯỚC 1: TRÍCH XUẤT & PHÂN TÍCH LINK
        url_info = extract_and_analyze_urls(clean_text)  # Quét và kiểm tra các đường link có trong văn bản

        # BƯỚC 2: ĐỐI SOÁT BÀI BÁO CHÍNH THỐNG (RAG Retriever)
        matched_article = find_matching_article(clean_text)  # Tìm bài báo cảnh báo khớp trong kho RAG

        # MỚM CẢNH BÁO LINK CHO GEMINI
        enriched_text = clean_text  # Tạo bản sao nội dung để gửi sang Gemini
        if url_info["warnings"]:  # Nếu phát hiện link có đuôi lạ, rút gọn hoặc thiếu HTTPS
            hint = " | ".join(url_info["warnings"])  # Nối các cảnh báo thành một chuỗi ngắn gọn
            enriched_text = f"{clean_text}\n[Cảnh báo kỹ thuật từ hệ thống: {hint}]"  # Đính kèm cảnh báo vào cuối tin nhắn

        # BƯỚC 3: PHÂN TÍCH NGỮ NGHĨA & CHẤM ĐIỂM RỦI RO (GEMINI / MULTI-FACTOR ENGINE)
        ai_result = analyze_scam_content(  # Phân tích chuyên sâu
            user_text=enriched_text,  # Truyền nội dung đã đính kèm cảnh báo link
            rag_article=matched_article,  # Truyền bài báo RAG đối chiếu (nếu có)
            api_key=api_key  # Truyền khóa API Gemini
        )

        # BƯỚC 4: ĐÓNG GÓI CHUẨN HÓA 6 TRƯỜNG DỮ LIỆU
        final_response = format_scam_response(ai_result)  # Chuẩn hóa kết quả đầu ra theo hợp đồng JSON

        # BƯỚC 5 (BỌC THÉP): TỰ ĐỘNG HỌC MỌI THỨ CHƯA BIẾT (OMNI-LEARNING)
        if not matched_article:  # Chỉ lưu học mới khi kho RAG chưa có kịch bản này
            try:  # Bọc try-except để lỗi ghi file không làm sập giao diện web
                data_dir = os.path.join(BACKEND_DIR, "data")  # Xác định đường dẫn thư mục data
                knowledge_path = os.path.join(data_dir, "scam_knowledge.json")  # Xác định đường dẫn file JSON tri thức

                if not os.path.exists(data_dir):  # Kiểm tra nếu thư mục data chưa tồn tại
                    os.makedirs(data_dir)  # Tự động tạo mới thư mục data

                db = []  # Khởi tạo danh sách dữ liệu cũ
                if os.path.exists(knowledge_path):  # Nếu file JSON đã tồn tại
                    with open(knowledge_path, "r", encoding="utf-8") as f:  # Mở file ở chế độ đọc UTF-8
                        try:  # Thử đọc dữ liệu JSON
                            db = json.load(f)  # Nạp toàn bộ danh sách bài báo hiện có
                        except Exception:  # Nếu file rỗng hoặc lỗi cấu trúc
                            db = []  # Khởi tạo lại danh sách rỗng

                is_scam = final_response.get("risk_score", 0) >= 50  # Xác định mẫu là lừa đảo nếu điểm >= 50
                prefix = "🚨 Mẫu lừa đảo" if is_scam else "✅ Mẫu an toàn"  # Gắn nhãn tiền tố tương ứng

                text_keywords = [w for w in clean_text.lower().split() if len(w) > 3][:8]  # Tách tối đa 8 từ khóa từ clean_text
                combined_keywords = list(set(text_keywords + url_info["domains"]))  # Gộp từ khóa chữ với tên miền link và lọc trùng

                safe_url = url_info["urls"][0] if url_info["urls"] else "https://canhbao.khonggianmang.vn"

                new_item = {  # Tạo khối dữ liệu kiến thức mới
                    "id": len(db) + 1,  # Tự động tăng ID
                    "title": f"{prefix}: {final_response.get('detected_tactic', 'Phân tích mới')}",  # Tiêu đề kèm nhãn phân loại
                    "source": "Hệ thống tự học toàn diện (Omni-Learn)",  # Ghi nhận nguồn tự học
                    "url": safe_url,  # Lưu đường link an toàn
                    "category_name": final_response.get('detected_tactic', 'Giao tiếp thông thường'),  # Lưu tên nhóm thủ đoạn
                    "summary": final_response.get('explanation', ''),  # Lưu phần giải thích chi tiết của AI
                    "keywords": combined_keywords  # Lưu danh sách từ khóa đã bao gồm tên miền (domain)
                }

                db.append(new_item)  # Thêm bản ghi mới vào cuối danh sách

                with open(knowledge_path, "w", encoding="utf-8") as f:  # Mở file JSON ở chế độ ghi đè
                    json.dump(db, f, ensure_ascii=False, indent=4)  # Lưu lại toàn bộ dữ liệu giữ nguyên tiếng Việt

                print(f"\n[AUTO-LEARN] ✅ Đã học kịch bản mới và lưu vào: {knowledge_path}\n")  # In thông báo thành công ra Terminal

            except Exception as e:  # Nếu có lỗi trong quá trình lưu dữ liệu
                print(f"\n[AUTO-LEARN] ❌ LỖI LƯU DATA: {e}\n")  # In chi tiết lỗi ra Terminal để dễ kiểm tra

        # BƯỚC 6: TRẢ KẾT QUẢ VỀ CHO WEB
        return final_response  # Trả về kết quả JSON chuẩn cho giao diện Streamlit


pipeline_instance = AntiScamPipeline()  # Khởi tạo sẵn 1 thực thể Pipeline dùng chung (Singleton)


def run_pipeline(user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:  # Hàm tiện ích gọi nhanh từ bên ngoài
    """Hàm tiện ích gọi nhanh pipeline"""
    return pipeline_instance.execute(user_text, api_key=api_key)  # Thực thi phân tích và trả kết quả
