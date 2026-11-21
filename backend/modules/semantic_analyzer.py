import html  # Thư viện giải mã các ký tự đặc biệt trong HTML (như &amp;, &quot;...)
import json  # Thư viện xử lý và chuyển đổi dữ liệu định dạng JSON
import os  # Thư viện đọc biến môi trường từ hệ thống
import re  # Thư viện Regex để tìm đường link, bóc tách thẻ HTML và khối JSON
import ssl  # Thư viện xử lý kết nối bảo mật HTTPS khi đọc nhanh nội dung trang web
import urllib.request  # Thư viện có sẵn của Python để gửi yêu cầu HTTP lấy mã nguồn trang web
from concurrent.futures import ThreadPoolExecutor, as_completed  # Thư viện chạy đa luồng để đua song song 3 model

try:  # Thử nạp thư viện đọc file .env
    from dotenv import load_dotenv  # Import hàm load_dotenv từ gói python-dotenv
    load_dotenv()  # Tự động đọc các biến môi trường (như GEMINI_API_KEY) từ file .env ở thư mục gốc
except ImportError:  # Nếu máy chưa cài python-dotenv thì bỏ qua để không bị sập chương trình
    pass  # Không làm gì cả và tiếp tục chạy

_CACHED_CLIENT = None  # Biến toàn cục giữ kết nối mạng tới Google để không phải khởi tạo lại
_CACHED_KEY = None  # Biến lưu API Key tương ứng với kết nối hiện tại


def get_gemini_client(api_key: str):  # Hàm lấy hoặc khởi tạo kết nối Gemini (không ép deadline cứng lên server Google)
    global _CACHED_CLIENT, _CACHED_KEY  # Khai báo sử dụng 2 biến toàn cục
    if _CACHED_CLIENT is not None and _CACHED_KEY == api_key:  # Nếu đã có kết nối sẵn và đúng API Key hiện tại
        return _CACHED_CLIENT  # Trả về ngay kết nối mạng cũ để gọi API nhanh hơn
    from google import genai  # Import SDK google-genai mới
    _CACHED_CLIENT = genai.Client(api_key=api_key)  # Tạo kết nối mới tới Google AI Studio
    _CACHED_KEY = api_key  # Cập nhật lại API Key đã lưu
    return _CACHED_CLIENT  # Trả về đối tượng Client vừa khởi tạo


def fetch_live_url_preview(user_text: str) -> str:  # Hàm đọc nhanh nội dung thực tế đang hiển thị trên trang web (kể cả tên miền trần)
    url_match = re.search(  # Tìm đường link đầy đủ hoặc tên miền trần đầu tiên trong nội dung người dùng gửi
        r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+|\b[a-zA-Z0-9-]+\.(?:com|vn|net|org|xyz|top|vip|cc|tk|info|online)\b[^\s<>"\']*)',  # Regex bắt cả link có http/www lẫn tên miền trần
        user_text,  # Chuỗi nội dung cần tìm link
        re.IGNORECASE  # Không phân biệt chữ hoa hay chữ thường
    )
    if not url_match:  # Nếu tin nhắn không chứa đường link hoặc tên miền nào
        return "Không có đường link trong nội dung."  # Trả về thông báo không có link

    target_url = url_match.group(0).rstrip(".,);!?")  # Lấy đường link và cắt bỏ dấu câu thừa ở cuối
    if not target_url.lower().startswith(("http://", "https://")):  # Nếu link chưa có giao thức http/https (gồm cả www. và tên miền trần)
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


def ai_error_response(error_detail: str) -> dict:  # Hàm trả về thông báo lỗi thân thiện đúng 6 trường khi không gọi được AI
    return {  # Trả về cấu trúc 6 trường chuẩn cho giao diện Streamlit
        "risk_score": 50,  # Đặt 50 điểm (mức vàng Đáng ngờ) thay vì 0 để giao diện KHÔNG hiện màu xanh "Nguy cơ thấp"
        "threat_level": "Đáng ngờ",  # Mức cảnh báo trung lập để người dùng không chủ quan
        "detected_tactic": "Hệ thống AI đang bận",  # Nhãn thân thiện thay vì thông báo lỗi kỹ thuật
        "explanation": "Hệ thống AI hiện đang quá tải nên chưa thể phân tích ngay lúc này. Bạn vui lòng chờ vài giây rồi gửi lại, và tuyệt đối không chuyển tiền hay bấm vào link lạ khi chưa xác minh.",  # Ẩn mã lỗi JSON thô khỏi người dùng
        "psychological_traps": ["Chưa hoàn tất phân tích do kết nối gián đoạn"],  # Ghi chú ngắn gọn
        "action_recommendations": [  # Khuyến nghị an toàn tạm thời
            "Thử gửi lại nội dung sau 5-10 giây.",  # Khuyến nghị 1
            "Không chuyển tiền hoặc cung cấp mã OTP khi chưa gọi xác nhận trực tiếp.",  # Khuyến nghị 2
            "Không bấm vào các đường link lạ."  # Khuyến nghị 3
        ]
    }


def _call_single_model(ai_client, model_name: str, contents, gen_config) -> dict:  # Hàm phụ gọi riêng 1 model hỗ trợ cả chữ lẫn ảnh
    response = ai_client.models.generate_content(  # Gửi yêu cầu phân tích trực tiếp tới 1 model cụ thể
        model=model_name,  # Tên model cần gọi
        contents=contents,  # Truyền danh sách nội dung gồm Prompt chữ và Ảnh (nếu có)
        config=gen_config  # Cấu hình JSON và giới hạn token
    )
    raw_text = (response.text or "").strip()  # Lấy chuỗi phản hồi từ AI, phòng trường hợp trả về None
    if not raw_text:  # Nếu model trả về chuỗi rỗng
        raise ValueError(f"{model_name} trả về rỗng")  # Báo lỗi để luồng đua bỏ qua model này
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)  # Bóc tách khối JSON chuẩn {...}
    return json.loads(json_match.group(0)) if json_match else json.loads(raw_text)  # Chuyển chuỗi JSON sang dict Python và trả về


def analyze_scam_content(
    user_text: str = "",  # Nội dung tin nhắn hoặc đường link người dùng nhập (có thể rỗng nếu chỉ gửi ảnh)
    rag_article: dict = None,  # Bài báo cảnh báo đối chiếu từ kho RAG (nếu có)
    api_key: str = None,  # Khóa API Gemini truyền vào (nếu có)
    image_bytes: bytes = None,  # Dữ liệu nhị phân của ảnh người dùng tải lên (bill, ảnh chụp màn hình...)
    image_mime: str = "image/jpeg"  # Định dạng ảnh (mặc định image/jpeg hoặc image/png)
) -> dict:  # Hàm chính gọi thẳng Gemini AI phân tích đa phương thức mới 100%
    valid_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()  # Ưu tiên lấy API Key truyền vào, nếu không có thì đọc từ biến môi trường
    if not valid_key or valid_key.startswith("YOUR_"):  # Kiểm tra nếu thiếu key hoặc vẫn đang để key mẫu
        print("[GEMINI] ❌ Thiếu GEMINI_API_KEY hợp lệ.")  # In báo lỗi ra Terminal
        return ai_error_response("Thiếu GEMINI_API_KEY hợp lệ trong file .env.")  # Trả về thông báo lỗi thân thiện

    try:  # Bọc try-except để bắt lỗi khi nạp thư viện hoặc khởi tạo kết nối Google
        from google.genai import types  # Import module cấu hình kiểu dữ liệu và đóng gói ảnh
        ai_client = get_gemini_client(valid_key)  # Lấy đối tượng Client kết nối Google AI Studio
    except Exception as e:  # Nếu khởi tạo kết nối thất bại
        print(f"[GEMINI] ❌ Lỗi khởi tạo Client: {e}")  # In chi tiết lỗi ra Terminal
        return ai_error_response(str(e))  # Trả về thông báo lỗi thân thiện

    clean_text = (user_text or "").strip()  # Làm sạch chuỗi văn bản đầu vào
    live_web_context = fetch_live_url_preview(clean_text) if clean_text else "Không có đường link."  # Quét nhanh nội dung web nếu có link

    rag_context = "Không có."  # Giá trị mặc định khi RAG không tìm thấy bài báo khớp
    if rag_article:  # Nếu có bài báo khớp từ kho scam_knowledge.json
        rag_context = f"{rag_article.get('title')} ({rag_article.get('source')}) | {rag_article.get('category_name')} | {rag_article.get('summary')}"  # Gom thông tin bài báo đưa vào Prompt

    has_image_note = "Có đính kèm hình ảnh (hãy đọc toàn bộ chữ, chi tiết, dấu hiệu chỉnh sửa/làm giả trong ảnh)." if image_bytes else "Không có hình ảnh."  # Báo cho AI biết có ảnh đính kèm không

    prompt = f"""  # Tạo chuỗi Prompt đa phương thức bằng ngôn ngữ đời thường, không tự suy diễn
    Bạn là trợ lý chống lừa đảo thân thiện tại Việt Nam. Hãy phân tích nội dung sau bằng ngôn ngữ đời thường, dễ hiểu cho mọi lứa tuổi:
    - Tin nhắn/Link người dùng gửi: "{clean_text or '(Người dùng chỉ gửi hình ảnh)'}"
    - Hình ảnh đính kèm: {has_image_note}
    - Dữ liệu thực tế vừa quét từ trang web: "{live_web_context}"
    - Dữ liệu tham khảo RAG: "{rag_context}"

    Quy tắc bắt buộc:
    1. NGÔN NGỮ ĐỜI THƯỜNG, DỄ HIỂU: Giải thích ngắn gọn, trực quan, phù hợp mọi đối tượng. TUYỆT ĐỐI KHÔNG dùng thuật ngữ kỹ thuật (HTTPS, SSL, giao thức, URL gốc/cuối, dữ liệu quét, RAG) và KHÔNG nhắc lại dòng "[Cảnh báo kỹ thuật...]".
    2. KHÔNG TỰ SUY DIỄN THÔNG TIN CHƯA CÓ: Nếu người dùng chỉ dán tin nhắn mượn tiền mà chưa nói rõ ai gửi (số lạ hay danh bạ) và chưa rõ số tài khoản có quen hay không -> TUYỆT ĐỐI KHÔNG kết luận là "giả mạo" hay "số tài khoản lạ". Chỉ chấm mức "Đáng ngờ" (45-65 điểm), đặt "detected_tactic" là "Cần xác minh người gửi", và đặt thêm 1 câu hỏi ngắn trong "explanation" để người dùng tự đối chiếu.
    3. XỬ LÝ ĐA DẠNG TÌNH HUỐNG:
       - Nếu có ẢNH BILL CHUYỂN KHOẢN: Soi kỹ lỗi phông chữ, căn lề, sai chính tả, thời gian, mã giao dịch bất thường; nhắc người dùng chỉ tin khi tiền đã thực sự vào tài khoản ngân hàng của mình.
       - Nếu có ẢNH CHỤP TIN NHẮN / CÔNG VĂN / MÃ QR: Đọc nội dung trong ảnh để phân tích thủ đoạn.
       - Nếu có LINK: Ưu tiên tuyệt đối dữ liệu vừa quét từ trang web. Nếu tên miền cũ bị đổi sang web bóng đá lậu, cá độ, cờ bạc, phishing -> BẮT BUỘC chấm Nguy cơ cao (75-95 điểm).
    4. LỜI KHUYÊN SÁT NGỮ CẢNH: Không khuyên "không bấm link lạ" nếu không có link; không khuyên "gọi cơ quan chức năng" nếu chỉ là tin nhắn hỏi mượn tiền thông thường.
    5. Trang chính thống (.gov.vn, .edu.vn, thương hiệu lớn uy tín khớp nội dung) chấm 0-10 điểm (An toàn).
    6. CHỈ trả về JSON đúng 6 trường sau:
    {{
        "risk_score": <số nguyên 0-100>,
        "threat_level": "<An toàn | Đáng ngờ | Nguy cơ cao>",
        "detected_tactic": "<tên thủ đoạn ngắn gọn dễ hiểu hoặc 'Cần xác minh người gửi' / 'Trang web chính thức'>",
        "explanation": "<giải thích khách quan, dễ hiểu trong 2-3 câu>",
        "psychological_traps": ["<dấu hiệu/bẫy tâm lý 1>", "<dấu hiệu/bẫy tâm lý 2>"],
        "action_recommendations": ["<lời khuyên sát thực tế 1>", "<lời khuyên 2>", "<lời khuyên 3>"]
    }}
    """  # Kết thúc chuỗi Prompt

    contents = [prompt]  # Khởi tạo danh sách nội dung gửi lên Gemini, bắt đầu bằng Prompt chữ
    if image_bytes:  # Nếu người dùng có tải ảnh lên
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))  # Đính kèm trực tiếp ảnh vào yêu cầu gửi lên Gemini

    gen_config = types.GenerateContentConfig(  # Tạo cấu hình gọi API tối ưu tốc độ
        response_mime_type="application/json",  # Ép AI chỉ trả về chuỗi JSON thuần
        temperature=0.2,  # Độ linh hoạt nhẹ để AI phân tích tự nhiên, không rập khuôn
        max_output_tokens=1000,  # Vừa đủ không gian cho 6 trường JSON
        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Tắt bước suy luận ngầm để AI trả lời nhanh trong 1-3 giây
    )  # Kết thúc cấu hình

    race_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]  # Giữ nguyên 3 model ổn định nhất để đua song song
    executor = ThreadPoolExecutor(max_workers=len(race_models))  # Tạo nhóm luồng chạy song song cho đúng 3 model
    futures = {  # Ánh xạ từng luồng đang chạy với tên model tương ứng
        executor.submit(_call_single_model, ai_client, m, contents, gen_config): m  # Bắn yêu cầu đa phương thức đồng thời tới 3 model
        for m in race_models  # Duyệt qua danh sách 3 model
    }  # Kết thúc tạo danh sách luồng

    last_error = "Tất cả model đều quá tải hoặc hết thời gian chờ."  # Biến lưu lỗi cuối cùng nếu cả 3 model đều thất bại
    try:  # Chờ kết quả với giới hạn 25 giây ở phía Python
        for future in as_completed(futures, timeout=25):  # Lắng nghe ngay khi bất kỳ model nào phân tích xong trước
            model_name = futures[future]  # Lấy tên model vừa hoàn thành
            try:  # Kiểm tra kết quả từ model vừa xong
                result = future.result()  # Lấy dict JSON kết quả AI vừa phân tích
                print(f"[GEMINI] 🏆 AI phân tích trực tiếp bởi: {model_name}")  # In tên model thắng cuộc ra Terminal
                executor.shutdown(wait=False, cancel_futures=True)  # Ngắt ngay không chờ 2 model chậm còn lại
                return result  # Trả thẳng kết quả AI phân tích về giao diện web
            except Exception as e:  # Nếu model này gặp lỗi
                last_error = str(e)  # Lưu lại thông tin lỗi
                print(f"[GEMINI] ⚠️ {model_name} lỗi: {e}")  # In lỗi ra Terminal và tiếp tục chờ model khác
    except TimeoutError:  # Nếu quá 25 giây chưa có model nào về đích
        last_error = "Quá thời gian chờ 25 giây."  # Cập nhật thông báo timeout
        print("[GEMINI] ⏱️ Hết thời gian chờ 25s.")  # In log ra Terminal

    executor.shutdown(wait=False)  # Dọn dẹp nhóm luồng nếu cả 3 đều lỗi
    print("[GEMINI] ❌ Cả 3 model đều thất bại.")  # Thông báo ra Terminal
    return ai_error_response(last_error)  # Trả về thông báo lỗi thân thiện (không dùng kịch bản cứng)