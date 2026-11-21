import html  # Thư viện giải mã các ký tự đặc biệt trong HTML (như &amp;, &quot;...)
import json  # Thư viện xử lý và chuyển đổi dữ liệu định dạng JSON
import os  # Thư viện đọc biến môi trường từ hệ thống
import re  # Thư viện Regex để tìm đường link, bóc tách thẻ HTML và khối JSON
import ssl  # Thư viện xử lý kết nối bảo mật HTTPS khi đọc nhanh nội dung trang web
import urllib.request  # Thư viện có sẵn của Python để gửi yêu cầu HTTP lấy mã nguồn trang web
from concurrent.futures import ThreadPoolExecutor, as_completed  # Thư viện chạy đa luồng để đua song song nhiều model

try:  # Thử nạp thư viện đọc file .env
    from dotenv import load_dotenv  # Import hàm load_dotenv từ gói python-dotenv
    load_dotenv()  # Tự động đọc các biến môi trường (như GEMINI_API_KEY) từ file .env ở thư mục gốc
except ImportError:  # Nếu máy chưa cài python-dotenv thì bỏ qua để không bị sập chương trình
    pass  # Không làm gì cả và tiếp tục chạy

try:
    from backend.engines.dynamic_scorer import calculate_dynamic_risk
except ImportError:
    try:
        from engines.dynamic_scorer import calculate_dynamic_risk
    except ImportError:
        calculate_dynamic_risk = None


def local_fallback_6_fields(user_text: str, rag_article: dict = None) -> dict:  # Hàm dự phòng chuẩn 6 trường khi không có API key hoặc Gemini gián đoạn
    if calculate_dynamic_risk:
        return calculate_dynamic_risk(user_text, rag_article)

    text_lower = user_text.lower()  # Chuyển tin nhắn về chữ thường để dò từ khóa
    traps = []  # Khởi tạo danh sách bẫy tâm lý
    score = 20  # Điểm rủi ro mặc định ban đầu
    tactic = rag_article["category_name"] if rag_article else "Chưa xác định rõ thủ đoạn"  # Lấy tên thủ đoạn từ RAG nếu có

    if any(k in text_lower for k in ["shipper", "nhận hàng", "giao hàng", "shopee", "bến xe", "chuyển tiền hộ"]):
        score = 80
        tactic = rag_article["category_name"] if rag_article else "Mạo Danh Người Thân & Shipper Giả"
        traps.append("Thao túng niềm tin: Giả danh shipper báo giao đơn hàng hoặc nhờ chuyển khoản hộ")
        traps.append("Ép thời gian: Hối thúc chuyển tiền nhanh khi nạn nhân chưa kịp kiểm tra đơn hàng")
    elif any(k in text_lower for k in ["công an", "vneid", "tòa án", "định danh", "khóa tài khoản", "rửa tiền"]):
        score = 95
        tactic = rag_article["category_name"] if rag_article else "Giả Danh Cơ Quan Công Quyền"
        traps.append("Uy quyền / Sợ hãi: Mạo danh cơ quan nhà nước báo lỗi hoặc dọa khóa tài khoản")
        traps.append("Ép thời gian: Yêu cầu thao tác cập nhật/chuyển khoản gấp")
    elif any(k in text_lower for k in ["cộng tác viên", "hoa hồng", "nhiệm vụ", "cọc", "việc nhẹ", "thưởng", "iphone"]):
        score = 85
        tactic = rag_article["category_name"] if rag_article else "Tuyển CTV Việc Nhẹ Lương Cao"
        traps.append("Hám lợi: Dụ dỗ nhận hoa hồng cao hoặc trúng thưởng lớn")
        traps.append("Mua chuộc niềm tin: Yêu cầu đóng phí hoặc nạp tiền cọc trước để nhận tiền")

    level = "An toàn" if score < 40 else ("Đáng ngờ" if score < 70 else "Nguy cơ cao")
    rag_note = f" (Trùng khớp cảnh báo: {rag_article['title']} - {rag_article['source']})" if rag_article else ""

    return {
        "risk_score": score,
        "threat_level": level,
        "detected_tactic": tactic,
        "explanation": f"Phát hiện kịch bản thao túng tâm lý yêu cầu chuyển tiền hoặc cung cấp thông tin trái phép.{rag_note}",
        "psychological_traps": traps if traps else ["Đánh vào sự mất cảnh giác của người dùng"],
        "action_recommendations": [
            "Tuyệt đối không chuyển tiền và không bấm vào đường link lạ.",
            "Kiểm tra lại thông tin trực tiếp trên ứng dụng chính thức hoặc gọi xác minh.",
            "Chặn số liên lạc và trình báo cơ quan chức năng nếu bị đe dọa."
        ]
    }


_CACHED_CLIENT = None  # Biến toàn cục giữ kết nối mạng tới Google để không phải khởi tạo lại
_CACHED_KEY = None  # Biến lưu API Key tương ứng với kết nối hiện tại


def get_gemini_client(api_key: str):  # Hàm lấy hoặc khởi tạo kết nối Gemini có giới hạn thời gian chờ
    global _CACHED_CLIENT, _CACHED_KEY  # Khai báo sử dụng 2 biến toàn cục
    if _CACHED_CLIENT is not None and _CACHED_KEY == api_key:  # Nếu đã có kết nối sẵn và đúng API Key hiện tại
        return _CACHED_CLIENT  # Trả về ngay kết nối mạng cũ để gọi API nhanh hơn
    from google import genai  # Import SDK google-genai mới
    _CACHED_CLIENT = genai.Client(  # Tạo kết nối mới tới Google AI Studio
        api_key=api_key,  # Truyền API Key hợp lệ
        http_options={"timeout": 10000}  # Giới hạn thời gian chờ tối đa 10 giây (10000ms) cho mỗi model
    )
    _CACHED_KEY = api_key  # Cập nhật lại API Key đã lưu
    return _CACHED_CLIENT  # Trả về đối tượng Client vừa khởi tạo


def fetch_live_url_preview(user_text: str) -> str:  # Hàm đọc nhanh nội dung thực tế đang hiển thị trên trang web (nếu tin nhắn có link)
    url_match = re.search(r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+)', user_text, re.IGNORECASE)  # Tìm đường link đầu tiên trong nội dung người dùng gửi
    if not url_match:  # Nếu tin nhắn không chứa đường link nào
        return "Không có đường link trong nội dung."  # Trả về thông báo không có link

    target_url = url_match.group(0).rstrip(".,);!?")  # Lấy đường link và cắt bỏ dấu câu thừa ở cuối
    if target_url.lower().startswith("www."):  # Nếu link bắt đầu bằng www. mà thiếu http/https
        target_url = "https://" + target_url  # Tự động bổ sung giao thức https:// để kết nối

    try:  # Bọc try-except để không làm gián đoạn chương trình nếu trang web chết hoặc chặn truy cập
        req = urllib.request.Request(  # Tạo yêu cầu HTTP giả lập trình duyệt thông thường
            target_url,  # Đường link cần kiểm tra
            headers={  # Khai báo Header để tránh bị trang web chặn bot cơ bản
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",  # Giả lập trình duyệt Chrome trên Windows
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"  # Ưu tiên nhận nội dung tiếng Việt nếu có
            }
        )
        ctx = ssl.create_default_context()  # Tạo ngữ cảnh SSL cho kết nối HTTPS
        ctx.check_hostname = False  # Tắt kiểm tra nghiêm ngặt tên miền SSL để vẫn đọc được web lừa đảo dùng chứng chỉ lỗi
        ctx.verify_mode = ssl.CERT_NONE  # Bỏ qua lỗi chứng chỉ tự ký để không bị văng lỗi khi soi web độc hại

        with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:  # Mở kết nối với thời gian chờ tối đa 3 giây
            final_url = resp.geturl()  # Lấy đường link cuối cùng sau khi bị chuyển hướng (redirect) nếu có
            raw_bytes = resp.read(35000)  # Chỉ tải tối đa 35KB đầu tiên cho nhanh và an toàn
            html_text = raw_bytes.decode("utf-8", errors="ignore")  # Giải mã dữ liệu sang chuỗi UTF-8, bỏ qua ký tự lỗi

        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)  # Bóc tách nội dung thẻ <title>
        title = html.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip()) if title_match else "Không có tiêu đề"  # Làm sạch khoảng trắng và giải mã HTML

        desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html_text, re.IGNORECASE | re.DOTALL)  # Bóc tách thẻ meta description
        desc = html.unescape(re.sub(r'\s+', ' ', desc_match.group(1)).strip()) if desc_match else ""  # Làm sạch nội dung mô tả nếu có

        clean_body = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', html_text, flags=re.IGNORECASE | re.DOTALL)  # Xóa bỏ toàn bộ mã JS và CSS
        clean_body = html.unescape(re.sub(r'<[^>]+>', ' ', clean_body))  # Xóa bỏ các thẻ HTML để chỉ giữ lại chữ hiển thị
        clean_body = re.sub(r'\s+', ' ', clean_body).strip()[:450]  # Cắt gọn còn 450 ký tự đầu tiên cho Prompt nhẹ

        print(f"[WEB-SCAN] 🌐 Đã đọc nhanh {target_url} -> Title: {title[:60]}")  # In log ra Terminal để biết đã quét thành công
        return f"URL gốc: {target_url} | URL cuối cùng: {final_url} | Tiêu đề trang: {title} | Mô tả: {desc} | Chữ hiển thị trên trang: {clean_body}"  # Trả về dữ liệu thực tế cho Gemini
    except Exception as e:  # Nếu trang web không truy cập được, hết thời gian 3 giây hoặc bị chặn
        print(f"[WEB-SCAN] ⚠️ Không thể đọc trực tiếp {target_url}: {e}")  # In cảnh báo ra Terminal
        return f"URL: {target_url} | Trạng thái: Không thể truy cập trực tiếp (lỗi: {e})"  # Báo lại trạng thái thực tế cho Gemini


def ai_error_response(error_detail: str) -> dict:  # Hàm trả về thông báo lỗi rõ ràng đúng 6 trường khi không gọi được AI
    return {  # Trả về cấu trúc 6 trường để giao diện Streamlit không bị sập
        "risk_score": 0,  # Đặt điểm về 0 vì AI chưa phân tích được
        "threat_level": "Đáng ngờ",  # Gán mức cảnh báo trung lập để người dùng tự cẩn trọng
        "detected_tactic": "Lỗi kết nối AI",  # Báo rõ trạng thái lỗi thay vì bịa tên thủ đoạn
        "explanation": f"Không thể kết nối tới Google Gemini AI để phân tích nội dung này. Chi tiết: {error_detail}",  # Hiển thị nguyên nhân lỗi thực tế
        "psychological_traps": ["Chưa có dữ liệu phân tích từ AI"],  # Ghi rõ chưa có dữ liệu
        "action_recommendations": [  # Khuyến nghị cơ bản khi AI tạm gián đoạn
            "Kiểm tra lại kết nối mạng hoặc GEMINI_API_KEY trong file .env.",  # Khuyến nghị 1
            "Thử gửi lại yêu cầu sau vài giây.",  # Khuyến nghị 2
            "Không bấm vào link lạ khi chưa được xác minh."  # Khuyến nghị 3
        ]
    }


def _call_single_model(ai_client, model_name: str, prompt: str, gen_config) -> dict:  # Hàm phụ gọi riêng 1 model để chạy trong luồng song song
    response = ai_client.models.generate_content(  # Gửi yêu cầu phân tích trực tiếp tới 1 model cụ thể
        model=model_name,  # Tên model cần gọi
        contents=prompt,  # Nội dung Prompt phân tích
        config=gen_config  # Cấu hình JSON và giới hạn token
    )
    raw_text = (response.text or "").strip()  # Lấy chuỗi phản hồi từ AI, phòng trường hợp trả về None
    if not raw_text:  # Nếu model trả về chuỗi rỗng
        raise ValueError(f"{model_name} trả về rỗng")  # Báo lỗi để luồng đua bỏ qua model này
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)  # Bóc tách khối JSON chuẩn {...}
    return json.loads(json_match.group(0)) if json_match else json.loads(raw_text)  # Chuyển chuỗi JSON sang dict Python và trả về


def analyze_scam_content(user_text: str, rag_article: dict = None, api_key: str = None) -> dict:  # Hàm chính gọi thẳng Gemini AI phân tích mới 100%
    valid_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()  # Ưu tiên lấy API Key truyền vào, nếu không có thì đọc từ biến môi trường
    if not valid_key or valid_key.startswith("YOUR_") or "YOUR_API" in valid_key:  # Kiểm tra nếu thiếu key hoặc vẫn đang để key mẫu
        print("[GEMINI] ℹ️ Không phát hiện GEMINI_API_KEY hợp lệ, chuyển sang cơ chế phân tích đa nhân tố ngoại tuyến.")
        return local_fallback_6_fields(user_text, rag_article)

    try:  # Bọc try-except để bắt lỗi khi nạp thư viện hoặc khởi tạo kết nối Google
        from google.genai import types  # Import module cấu hình kiểu dữ liệu
        ai_client = get_gemini_client(valid_key)  # Lấy đối tượng Client kết nối Google AI Studio
    except Exception as e:  # Nếu khởi tạo kết nối thất bại
        print(f"[GEMINI] ⚠️ Lỗi khởi tạo Client ({e}), chuyển sang cơ chế ngoại tuyến.")
        return local_fallback_6_fields(user_text, rag_article)

    live_web_context = fetch_live_url_preview(user_text)  # Quét nhanh nội dung thực tế đang hiển thị trên trang web (nếu có link)

    rag_context = "Không có."  # Giá trị mặc định khi RAG không tìm thấy bài báo khớp
    if rag_article:  # Nếu có bài báo khớp từ kho scam_knowledge.json
        rag_context = f"{rag_article.get('title')} ({rag_article.get('source')}) | {rag_article.get('category_name')} | {rag_article.get('summary')}"  # Gom thông tin bài báo đưa vào Prompt

    prompt = f"""
    Bạn là chuyên gia an ninh mạng tại Việt Nam. Hãy phân tích trực tiếp nội dung/đường link sau:
    - Nội dung người dùng gửi: "{user_text}"
    - Dữ liệu thực tế vừa quét trực tiếp từ trang web: "{live_web_context}"
    - Dữ liệu tham khảo RAG: "{rag_context}"

    Quy tắc bắt buộc:
    1. ƯU TIÊN TUYỆT ĐỐI dữ liệu thực tế vừa quét từ trang web hơn trí nhớ cũ của bạn. Nếu tên miền cũ là thương hiệu hợp pháp nhưng nội dung thực tế hiện tại đã bị đổi sang web bóng đá lậu, cá độ, cờ bạc, nhà cái, hoặc phishing -> BẮT BUỘC cảnh báo Nguy cơ cao (75-95 điểm) và chỉ rõ thủ đoạn chiếm dụng/mua lại tên miền cũ.
    2. Trong "explanation", nêu rõ trang web hiện tại thực chất là gì, của ai/tổ chức nào, hoặc có dấu hiệu bất thường gì.
    3. Trang chính thống (.gov.vn, .edu.vn, thương hiệu lớn uy tín có nội dung khớp) chấm 0-10 điểm (An toàn).
    4. CHỈ trả về JSON đúng 6 trường sau:
    {{
        "risk_score": <số nguyên 0-100>,
        "threat_level": "<An toàn | Đáng ngờ | Nguy cơ cao>",
        "detected_tactic": "<tên thủ đoạn AI phát hiện hoặc 'Tên miền chính thống'>",
        "explanation": "<phân tích chi tiết của AI trong 2-3 câu>",
        "psychological_traps": ["<bẫy tâm lý 1>", "<bẫy tâm lý 2>"],
        "action_recommendations": ["<lời khuyên 1>", "<lời khuyên 2>", "<lời khuyên 3>"]
    }}
    """  # Kết thúc chuỗi Prompt

    gen_config = types.GenerateContentConfig(  # Tạo cấu hình gọi API dùng chung cho các model
        response_mime_type="application/json",  # Ép AI chỉ trả về chuỗi JSON thuần
        temperature=0.2,  # Độ linh hoạt nhẹ để AI phân tích tự nhiên, không rập khuôn
        max_output_tokens=1500  # Đủ không gian để AI trả lời trọn vẹn không bị cắt cụt JSON
    )  # Kết thúc cấu hình

    race_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.5-flash"]  # Đua song song các model để lấy kết quả phân tích thật nhanh nhất
    executor = ThreadPoolExecutor(max_workers=len(race_models))  # Tạo nhóm luồng chạy song song
    futures = {  # Ánh xạ từng luồng đang chạy với tên model tương ứng
        executor.submit(_call_single_model, ai_client, m, prompt, gen_config): m  # Bắn yêu cầu đồng thời tới cả các model
        for m in race_models  # Duyệt qua danh sách model
    }  # Kết thúc tạo danh sách luồng

    last_error = "Tất cả model đều quá tải hoặc hết thời gian chờ."  # Biến lưu lỗi cuối cùng nếu tất cả model đều thất bại
    for future in as_completed(futures):  # Lắng nghe ngay khi bất kỳ model nào phân tích xong trước
        model_name = futures[future]  # Lấy tên model vừa hoàn thành
        try:  # Kiểm tra kết quả từ model vừa xong
            result = future.result()  # Lấy dict JSON kết quả AI vừa phân tích
            print(f"[GEMINI] 🏆 AI phân tích trực tiếp bởi: {model_name}")  # In tên model thắng cuộc ra Terminal
            executor.shutdown(wait=False, cancel_futures=True)  # Ngắt ngay không chờ các model còn lại
            return result  # Trả thẳng kết quả AI phân tích về giao diện web
        except Exception as e:  # Nếu model này gặp lỗi
            last_error = str(e)  # Lưu lại thông tin lỗi
            print(f"[GEMINI] ⚠️ {model_name} lỗi: {e}")  # In lỗi ra Terminal và tiếp tục chờ model khác

    executor.shutdown(wait=False)  # Dọn dẹp nhóm luồng nếu tất cả đều lỗi
    print(f"[GEMINI] ⚠️ Các model đều gián đoạn ({last_error}), tự động chuyển sang phân tích ngoại tuyến.")
    return local_fallback_6_fields(user_text, rag_article)
