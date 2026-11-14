"""
LLM Analyzer Module: Gửi Prompt phân tích chuyên sâu lên Gemini 3.8 Flash & Gemini 4.
Phụ trách: Thành viên 1 (Lõi AI & Prompt Engineering)
"""

import json
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


def call_gemini_semantic_analysis(
    user_text: str,
    rag_context: str,
    api_key: str
) -> Optional[Dict[str, Any]]:
    """Gửi Prompt lên Gemini 3.8 Flash & Gemini 4 và trả về dict 6 trường."""
    if not HAS_GENAI or not api_key:
        return None

    prompt = f"""
    Bạn là chuyên gia phân tích lừa đảo trực tuyến tại Việt Nam.
    Hãy phân tích tin nhắn sau và tham khảo dữ liệu cảnh báo (nếu phù hợp):
    - Tin nhắn người dùng: "{user_text}"
    - Dữ liệu cảnh báo từ kho RAG: "{rag_context}"

    BẮT BUỘC trả về đúng định dạng JSON gồm đúng 6 trường sau:
    {{
        "risk_score": <số nguyên từ 0 đến 100 thể hiện mức độ rủi ro. Nếu là tin nhắn chào hỏi, sinh hoạt thường ngày, không lừa đảo thì chấm điểm thấp từ 5 đến 20>,
        "threat_level": "<chỉ chọn 1 trong 3 giá trị: An toàn | Đáng ngờ | Nguy cơ cao. Với trò chuyện sinh hoạt thông thường hãy chọn An toàn>",
        "detected_tactic": "<nếu là lừa đảo ghi tên thủ đoạn; nếu là trò chuyện bình thường ghi: Giao tiếp sinh hoạt thông thường>",
        "explanation": "<lời giải thích, nhận định ngắn gọn, khách quan và chính xác của AI>",
        "psychological_traps": [
            "<bẫy tâm lý nếu có; nếu an toàn hãy ghi: Không phát hiện dấu hiệu thao túng tâm lý>"
        ],
        "action_recommendations": [
            "<lời khuyên hành động phù hợp, nếu an toàn hãy khuyên trò chuyện bình thường>"
        ]
    }}
    """

    model_list = [
        "gemini-3.8-flash",
        "gemini-4",
        "gemini-4-hydrogen",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    try:
        client = genai.Client(api_key=api_key.strip())
        for model_name in model_list:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                parsed = json.loads(response.text)
                if isinstance(parsed, dict) and "risk_score" in parsed:
                    return parsed
            except Exception:
                continue
    except Exception:
        pass

    return None
