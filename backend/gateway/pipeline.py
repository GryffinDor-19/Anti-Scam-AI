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
            if full_url.startswith('http://'):  # Kiểm tra link có thiếu chứng chỉ bảo mật HTTPS không
                warnings.append(f"Link {domain} không có bảo mật HTTPS")  # Thêm cảnh báo thiếu HTTPS

    return {"urls": urls, "domains": list(set(domains)), "warnings": warnings}  # Trả về link, tên miền không trùng và cảnh báo


# 1. Nạp Lớp RAG: Knowledge Retriever (TV2)
try:  # Thử import hàm tìm kiếm bài báo RAG theo đường dẫn ngắn
    from knowledge.retriever import find_matching_article  # Nạp hàm đối soát kho dữ liệu RAG
except ImportError:  # Nếu lỗi đường dẫn thì thử nạp từ thư mục gốc
    from backend.knowledge.retriever import find_matching_article  # Nạp hàm đối soát RAG từ backend

# 2. Nạp Lớp AI: Semantic Analyzer (TV1 - Gemini)
try:  # Thử import hàm phân tích ngữ nghĩa Gemini theo đường dẫn ngắn
    from modules.semantic_analyzer import analyze_scam_content  # Nạp hàm gọi Gemini AI
except ImportError:  # Nếu lỗi đường dẫn thì thử nạp từ thư mục gốc
    from backend.modules.semantic_analyzer import analyze_scam_content  # Nạp hàm gọi Gemini AI từ backend

# 3. Nạp bộ chuẩn hóa Response Formatter
from .response_formatter import format_scam_response  # Nạp hàm đóng gói JSON chuẩn 6 trường


class AntiScamPipeline:  # Lớp điều phối chính của hệ thống (đã gỡ bỏ Fast Filter)
    """
    Chuỗi xử lý phòng thủ AI trực tiếp:
    Bước 1: Quét & phân tích cấu trúc URL
    Bước 2: RAG Retriever - Bốc bài báo chính thống từ Cục ATTT
    Bước 3: Semantic LLM - Gemini bóc bẫy tâm lý chuyên sâu
    Bước 4: Auto-Learn - Tự động học kịch bản & tên miền mới
    """

    def __init__(self):  # Hàm khởi tạo Pipeline
        pass  # Không còn khởi tạo FastFilter nữa

    def execute(self, user_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:  # Hàm thực thi chuỗi phân tích
        clean_text = (user_text or "").strip()  # Làm sạch khoảng trắng thừa và chống lỗi None
        if not clean_text:  # Kiểm tra nếu người dùng không nhập nội dung gì
            return format_scam_response({  # Trả về phản hồi an toàn mặc định
                "risk_score": 0,  # Điểm rủi ro bằng 0
                "threat_level": "An toàn",  # Mức độ an toàn
                "detected_tactic": "Không có nội dung",  # Nhóm thủ đoạn trống
                "explanation": "Vui lòng nhập nội dung cần kiểm tra.",  # Thông báo nhắc nhập liệu
                "psychological_traps": ["Không phát hiện dấu hiệu thao túng tâm lý"],  # Không có bẫy tâm lý
                "action_recommendations": ["Nhập nội dung tin nhắn hoặc đường link nghi vấn để thẩm định."]  # Khuyến nghị hành động
            })

        # BƯỚC 1: QUÉT & PHÂN TÍCH CẤU TRÚC LINK
        url_info = extract_and_analyze_urls(clean_text)  # Tách link, tên miền và cảnh báo kỹ thuật ngay từ đầu

        # BƯỚC 2: ĐỐI SOÁT BÀI BÁO CHÍNH THỐNG (RAG Retriever)
        matched_article = find_matching_article(clean_text)  # Tìm bài báo cảnh báo khớp trong kho RAG

        # MỚM CẢNH BÁO LINK CHO GEMINI
        enriched_text = clean_text  # Tạo bản sao nội dung để gửi sang Gemini
        if url_info["warnings"]:  # Nếu phát hiện link có đuôi lạ, rút gọn hoặc thiếu HTTPS
            hint = " | ".join(url_info["warnings"])  # Nối các cảnh báo thành một chuỗi ngắn gọn
            enriched_text = f"{clean_text}\n[Cảnh báo kỹ thuật từ hệ thống: {hint}]"  # Đính kèm cảnh báo vào cuối tin nhắn

        # BƯỚC 3: PHÂN TÍCH NGỮ NGHĨA & CHẤM ĐIỂM RỦI RO (GEMINI)
        ai_result = analyze_scam_content(  # Gọi thẳng Gemini AI phân tích chuyên sâu
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

                new_item = {  # Tạo khối dữ liệu kiến thức mới
                    "id": len(db) + 1,  # Tự động tăng ID
                    "title": f"{prefix}: {final_response.get('detected_tactic', 'Phân tích mới')}",  # Tiêu đề kèm nhãn phân loại
                    "source": "Hệ thống tự học toàn diện (Omni-Learn)",  # Ghi nhận nguồn tự học
                    "url": url_info["urls"][0] if url_info["urls"] else "",  # Lưu đường link đầu tiên nếu có
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