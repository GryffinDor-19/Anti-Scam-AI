"""
Lớp 3: Semantic Analyzer Coordinator & Multimodal Engine.
Phụ trách: Thành viên 1 (Lõi AI & Prompt Engineering)
Tích hợp:
- Quét và đọc trước nội dung web thực tế (Live URL Preview).
- Phân tích đa phương thức (Văn bản + Hình ảnh).
- Đua song song 3 mô hình Gemini bằng ThreadPoolExecutor.
- Bộ tính điểm động Fallback nội bộ (Dynamic Scorer) khi offline hoặc không có API key.
"""

import html
import json
import os
import re
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .dynamic_scorer import calculate_dynamic_risk

_CACHED_CLIENT = None
_CACHED_KEY = None


def get_gemini_client(api_key: str):
    """Lấy hoặc khởi tạo kết nối Gemini cached để tối ưu tốc độ."""
    global _CACHED_CLIENT, _CACHED_KEY
    if _CACHED_CLIENT is not None and _CACHED_KEY == api_key:
        return _CACHED_CLIENT
    from google import genai
    _CACHED_CLIENT = genai.Client(api_key=api_key)
    _CACHED_KEY = api_key
    return _CACHED_CLIENT


def fetch_live_url_preview(user_text: str) -> str:
    """Đọc nhanh nội dung thực tế đang hiển thị trên trang web (hỗ trợ cả tên miền trần)."""
    url_match = re.search(
        r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+|\b[a-zA-Z0-9-]+\.(?:com|vn|net|org|xyz|top|vip|cc|tk|info|online)\b[^\s<>"\']*)',
        user_text,
        re.IGNORECASE
    )
    if not url_match:
        return "Không có đường link trong nội dung."

    target_url = url_match.group(0).rstrip(".,);!?")
    if not target_url.lower().startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"
            }
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=3.5, context=ctx) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return f"Đã kết nối trang web {target_url} (Định dạng: {content_type})."

            html_raw = response.read(6000).decode("utf-8", errors="ignore")
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_raw, re.IGNORECASE | re.DOTALL)
            page_title = html.unescape(title_match.group(1).strip()) if title_match else ""

            meta_desc = ""
            desc_match = re.search(r'<meta[^>]+name=[\'"]description[\'"][^>]+content=[\'"](.*?)[\'"]', html_raw, re.IGNORECASE)
            if desc_match:
                meta_desc = html.unescape(desc_match.group(1).strip())

            body_preview = ""
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_raw, re.IGNORECASE | re.DOTALL)
            if body_match:
                clean_body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', body_match.group(1), flags=re.DOTALL | re.IGNORECASE)
                clean_body = re.sub(r'<[^>]+>', ' ', clean_body)
                clean_body = re.sub(r'\s+', ' ', clean_body).strip()
                body_preview = html.unescape(clean_body[:300])

            summary_parts = []
            if page_title:
                summary_parts.append(f"Tiêu đề trang: '{page_title}'")
            if meta_desc:
                summary_parts.append(f"Mô tả: '{meta_desc}'")
            if body_preview and not meta_desc:
                summary_parts.append(f"Nội dung đầu trang: '{body_preview}'")

            return " | ".join(summary_parts) if summary_parts else f"Đã kết nối thành công tới {target_url} nhưng trang không có văn bản tiêu đề."

    except urllib.error.HTTPError as e:
        return f"Trang web {target_url} trả về lỗi HTTP {e.code}."
    except urllib.error.URLError as e:
        return f"Không thể mở trang web {target_url} (Lỗi: {e.reason})."
    except Exception as e:
        return f"Không thể kết nối trang web {target_url}: {str(e)}."


def ai_error_response(err_msg: str) -> dict:
    """Đóng gói phản hồi thân thiện khi AI gặp sự cố."""
    return {
        "risk_score": 50,
        "threat_level": "Đáng ngờ",
        "detected_tactic": "Hệ thống AI đang bận",
        "explanation": "Hệ thống AI hiện đang quá tải nên chưa thể phân tích ngay lúc này. Bạn vui lòng chờ vài giây rồi gửi lại, và tuyệt đối không chuyển tiền hay bấm vào link lạ khi chưa xác minh.",
        "psychological_traps": ["Chưa hoàn tất phân tích do kết nối gián đoạn"],
        "action_recommendations": [
            "Thử gửi lại nội dung sau 5-10 giây.",
            "Không chuyển tiền hoặc cung cấp mã OTP khi chưa gọi xác nhận trực tiếp.",
            "Không bấm vào các đường link lạ."
        ]
    }


def _call_single_model(ai_client, model_name: str, contents, gen_config) -> dict:
    """Hàm phụ gọi riêng 1 model hỗ trợ cả chữ lẫn ảnh."""
    response = ai_client.models.generate_content(
        model=model_name,
        contents=contents,
        config=gen_config
    )
    raw_text = (response.text or "").strip()
    if not raw_text:
        raise ValueError(f"{model_name} trả về rỗng")
    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    return json.loads(json_match.group(0)) if json_match else json.loads(raw_text)


def local_fallback_6_fields(user_text: str, rag_article: Optional[dict] = None) -> Dict[str, Any]:
    """Hàm tính điểm đa tiêu chí động phục vụ tương thích ngược hoặc chế độ offline."""
    return calculate_dynamic_risk(user_text, rag_article)


def analyze_scam_content(
    user_text: str = "",
    rag_article: Optional[dict] = None,
    api_key: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_mime: str = "image/jpeg"
) -> Dict[str, Any]:
    """
    Hàm phân tích chính:
    1. Ưu tiên Gemini AI đa phương thức với Live Web Preview & Model Racing (gemini-3.1-flash-lite, 3.5-flash, 3.7-flash).
    2. Tự động fallback sang dynamic_scorer nội bộ nếu không có API key hoặc lỗi mạng.
    """
    valid_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()

    # Nếu không có API Key và có text, kích hoạt ngay fallback tính điểm đa tiêu chí động offline
    if not valid_key or valid_key.startswith("YOUR_") or "API_KEY" in valid_key:
        if user_text:
            return calculate_dynamic_risk(user_text, rag_article)
        return ai_error_response("Thiếu GEMINI_API_KEY hợp lệ trong file .env.")

    try:
        from google.genai import types
        ai_client = get_gemini_client(valid_key)
    except Exception as e:
        if user_text:
            return calculate_dynamic_risk(user_text, rag_article)
        return ai_error_response(str(e))

    clean_text = (user_text or "").strip()
    live_web_context = fetch_live_url_preview(clean_text) if clean_text else "Không có đường link."

    rag_context = "Không có."
    if rag_article:
        rag_context = f"{rag_article.get('title')} ({rag_article.get('source')}) | {rag_article.get('category_name')} | {rag_article.get('summary')}"

    has_image_note = "Có đính kèm hình ảnh (hãy đọc toàn bộ chữ, chi tiết, dấu hiệu chỉnh sửa/làm giả trong ảnh)." if image_bytes else "Không có hình ảnh."

    prompt = f"""
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
    """

    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))

    gen_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2,
        max_output_tokens=1000,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    race_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]
    executor = ThreadPoolExecutor(max_workers=len(race_models))
    futures = {
        executor.submit(_call_single_model, ai_client, m, contents, gen_config): m
        for m in race_models
    }

    last_error = "Tất cả model đều quá tải hoặc hết thời gian chờ."
    try:
        for future in as_completed(futures, timeout=25):
            model_name = futures[future]
            try:
                result = future.result()
                executor.shutdown(wait=False, cancel_futures=True)
                return result
            except Exception as e:
                last_error = str(e)
    except TimeoutError:
        last_error = "Quá thời gian chờ 25 giây."

    executor.shutdown(wait=False)

    # Nếu AI online thất bại mà có văn bản, thử fallback sang Dynamic Scorer nội bộ
    if clean_text:
        return calculate_dynamic_risk(clean_text, rag_article)

    return ai_error_response(last_error)
