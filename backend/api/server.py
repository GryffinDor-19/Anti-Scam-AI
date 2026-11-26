"""
ASGI REST API Server cho AntiScam AI (Next.js Frontend <-> Python AI Backend).
Chạy trực tiếp trên Starlette + Uvicorn (đã có sẵn trong môi trường Python).
Bọc toàn bộ lõi AI: AntiScamPipeline, FakeBillDetector, EmergencyManager, RAGCaseMatcher và Đấu trường lừa đảo.
"""

import os
import sys
import json
import tempfile
import unicodedata
from typing import Optional, List, Dict, Any

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Thiết lập sys.path để import ổn định các module trong backend/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

for p in [BACKEND_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.gateway.pipeline import run_pipeline, extract_and_analyze_urls
from backend.engines.fake_bill_detector import FakeBillDetector
from backend.engines.rag_case_matcher import RAGCaseMatcher
from backend.emergency.emergency_manager import EmergencyManager
from backend.knowledge.retriever import find_matching_article

_rag_matcher: Optional[RAGCaseMatcher] = None


def get_rag_matcher() -> RAGCaseMatcher:
    global _rag_matcher
    if _rag_matcher is None:
        _rag_matcher = RAGCaseMatcher()
    return _rag_matcher


def _load_scenarios() -> List[Dict[str, Any]]:
    path = os.path.join(BACKEND_DIR, "data", "scam_scenarios.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("scenarios", [])
    except Exception:
        return []


def _norm_vn(text: str) -> str:
    text = (text or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _classify_library_item(item: Dict[str, Any]) -> str:
    title = (item.get("title") or "").lower()
    source = (item.get("source") or "").lower()
    if "mẫu an toàn" in title:
        return "safe_sample"
    if "omni-learn" in source or "tự học" in source:
        return "learned"
    return "official"


SAMPLE_FILES = {
    "fake": os.path.join(BACKEND_DIR, "modules", "fake_bill.jpg"),
    "real": os.path.join(BACKEND_DIR, "modules", "test_bill.jpg"),
}

LEVEL_META = {
    "safe": {"label": "An toàn", "score": 30, "hp": 0, "title": "Phản xạ an toàn"},
    "neutral": {"label": "Chưa dứt khoát", "score": 10, "hp": -10, "title": "Chưa dứt khoát"},
    "risky": {"label": "Dính bẫy", "score": 0, "hp": -35, "title": "Đã sập bẫy"},
}


# =============================================================================
# 1. HEALTH CHECK
# =============================================================================

async def health_check(request: Request):
    return JSONResponse({
        "status": "ok",
        "service": "AntiScam AI Backend",
        "pipeline_ready": True,
        "has_env_gemini_key": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
    })


# =============================================================================
# 2. KIỂM TRA TIN NHẮN, LINK & ẢNH ĐÍNH KÈM
# =============================================================================

async def analyze_message(request: Request):
    form = await request.form()
    clean_text = str(form.get("text") or "").strip()
    api_key = str(form.get("api_key") or "").strip()
    image_file = form.get("image")

    image_bytes: Optional[bytes] = None
    image_mime = "image/jpeg"

    if image_file is not None and hasattr(image_file, "read"):
        image_bytes = await image_file.read()
        image_mime = getattr(image_file, "content_type", None) or "image/jpeg"

    if not clean_text and not image_bytes:
        return JSONResponse(
            {"detail": "Vui lòng nhập nội dung tin nhắn hoặc tải ảnh cần kiểm tra."},
            status_code=400,
        )

    active_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip() or None

    result = run_pipeline(
        user_text=clean_text,
        api_key=active_key,
        image_bytes=image_bytes,
        image_mime=image_mime,
    )

    url_info = extract_and_analyze_urls(clean_text) if clean_text else {"urls": [], "domains": [], "warnings": []}
    matched_article = find_matching_article(clean_text) if clean_text else None

    return JSONResponse({
        **result,
        "url_analysis": url_info,
        "matched_article": matched_article,
    })


# =============================================================================
# 3. SOI BILL CHUYỂN KHOẢN GIẢ (FORENSIC VISION LAB)
# =============================================================================

async def get_sample_bill_image(request: Request):
    sample_type = request.path_params.get("sample_type", "")
    if sample_type not in SAMPLE_FILES:
        return JSONResponse({"detail": "Không tìm thấy mẫu bill yêu cầu."}, status_code=404)
    file_path = SAMPLE_FILES[sample_type]
    if not os.path.exists(file_path):
        return JSONResponse({"detail": "Tệp ảnh mẫu chưa tồn tại trên máy chủ."}, status_code=404)
    return FileResponse(file_path, media_type="image/jpeg")


async def analyze_fake_bill(request: Request):
    form = await request.form()
    sample_type = str(form.get("sample_type") or "").strip()
    api_key = str(form.get("api_key") or "").strip()
    image_file = form.get("image")

    active_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip() or ""
    detector = FakeBillDetector(api_key=active_key)

    if sample_type in SAMPLE_FILES:
        file_path = SAMPLE_FILES[sample_type]
        if not os.path.exists(file_path):
            return JSONResponse({"detail": "Không tìm thấy tệp ảnh mẫu."}, status_code=404)
        return JSONResponse(detector.analyze_bill(file_path))

    if image_file is None or not hasattr(image_file, "read"):
        return JSONResponse({"detail": "Vui lòng tải ảnh biên lai hoặc chọn mẫu demo."}, status_code=400)

    filename = getattr(image_file, "filename", "bill.jpg") or "bill.jpg"
    suffix = os.path.splitext(filename)[1] or ".jpg"
    data = await image_file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        return JSONResponse(detector.analyze_bill(tmp_path))
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# =============================================================================
# 4. CẤP CỨU GIỜ VÀNG (EMERGENCY MANAGER)
# =============================================================================

async def get_emergency_guide(request: Request):
    payload = EmergencyManager.get_emergency_payload()
    clean_title = payload.get("title", "").lstrip("🚨 ").strip()
    return JSONResponse({
        **payload,
        "title": clean_title,
        "police": {
            "name": "Cục An ninh mạng A05 (Bộ Công an)",
            "hotline": "0692348560",
            "display": "069.234.8560",
            "desc": "Tố giác tội phạm lừa đảo công nghệ cao 24/7",
        },
        "spam_portal": {
            "name": "Tổng đài 156 / 5656",
            "hotline": "156",
            "desc": "Phản ánh cuộc gọi rác, tin nhắn rác & lừa đảo (miễn phí)",
            "portal_url": "https://canhbao.khonggianmang.vn",
        },
    })


# =============================================================================
# 5. THƯ VIỆN CẢNH BÁO & HOTLINE
# =============================================================================

async def get_library_cases(request: Request):
    source_type = request.query_params.get("source_type", "all")
    category = request.query_params.get("category", "")
    q = request.query_params.get("q", "")

    matcher = get_rag_matcher()
    cases = matcher._load_knowledge() if hasattr(matcher, "_load_knowledge") else matcher.get_all_cases()

    enriched: List[Dict[str, Any]] = []
    official_count = 0
    learned_count = 0

    for c in cases:
        s_type = _classify_library_item(c)
        if s_type == "safe_sample":
            continue
        if s_type == "official":
            official_count += 1
        else:
            learned_count += 1
        enriched.append({**c, "source_type": s_type})

    categories = sorted(list({c.get("category_name", "") for c in enriched if c.get("category_name")}))

    filtered = enriched
    if source_type in ("official", "learned"):
        filtered = [c for c in filtered if c["source_type"] == source_type]
    if category and category != "Tất cả":
        filtered = [c for c in filtered if c.get("category_name") == category]
    if q.strip():
        kw = q.strip().lower()
        filtered = [
            c for c in filtered
            if kw in (c.get("title") or "").lower()
            or kw in (c.get("summary") or "").lower()
            or any(kw in k.lower() for k in c.get("keywords", []))
        ]

    return JSONResponse({
        "total": len(enriched),
        "official_count": official_count,
        "learned_count": learned_count,
        "filtered_count": len(filtered),
        "categories": categories,
        "items": filtered,
    })


# =============================================================================
# 6. ĐẤU TRƯỜNG LỪA ĐẢO (SCAM TRAINER GAME)
# =============================================================================

async def get_game_scenarios(request: Request):
    scenarios = _load_scenarios()
    categories = sorted(list({
        (s.get("category_name") or s.get("category") or "")
        for s in scenarios
        if (s.get("category_name") or s.get("category"))
    }))
    return JSONResponse({
        "total": len(scenarios),
        "categories": categories,
        "scenarios": scenarios,
    })


async def evaluate_game_answer(request: Request):
    body = await request.json()
    scenario_id = str(body.get("scenario_id") or "")
    stage_index = int(body.get("stage_index", 0))
    option_index = body.get("option_index", None)
    free_text = body.get("free_text", None)

    scenarios = _load_scenarios()
    scenario = next((s for s in scenarios if str(s.get("id")) == scenario_id), None)
    if not scenario:
        return JSONResponse({"detail": "Không tìm thấy tình huống."}, status_code=404)

    stages = scenario.get("stages", [])
    if stage_index < 0 or stage_index >= len(stages):
        return JSONResponse({"detail": "Lượt đối thoại không hợp lệ."}, status_code=400)

    stage = stages[stage_index]
    options = stage.get("options", [])

    if option_index is not None and 0 <= int(option_index) < len(options):
        chosen = options[int(option_index)]
        level = chosen.get("level", "neutral")
        user_reply = chosen.get("text", "")
        feedback = chosen.get("feedback", "")
        red_flag = chosen.get("red_flag") or stage.get("red_flag", "")
    elif free_text and str(free_text).strip():
        t = _norm_vn(str(free_text))
        safe_hits = [k for k in stage.get("safe_keywords", []) if _norm_vn(k) in t]
        risky_hits = [k for k in stage.get("risky_keywords", []) if _norm_vn(k) in t]
        safe_w = sum(len(_norm_vn(k)) for k in safe_hits)
        risky_w = sum(len(_norm_vn(k)) for k in risky_hits)
        level = "safe" if safe_w > risky_w else ("risky" if risky_w > safe_w else "neutral")
        matched_opt = next((o for o in options if o.get("level") == level), options[0] if options else {})
        user_reply = str(free_text).strip()
        feedback = matched_opt.get("feedback", "")
        red_flag = matched_opt.get("red_flag") or stage.get("red_flag", "")
    else:
        return JSONResponse({"detail": "Vui lòng chọn phương án hoặc nhập câu trả lời."}, status_code=400)

    meta = LEVEL_META.get(level, LEVEL_META["neutral"])
    return JSONResponse({
        "level": level,
        "label": meta["label"],
        "title": meta["title"],
        "score_delta": meta["score"],
        "hp_delta": meta["hp"],
        "user_reply": user_reply,
        "feedback": feedback,
        "red_flag": red_flag,
        "is_last_stage": stage_index >= len(stages) - 1,
    })


routes = [
    Route("/api/health", health_check, methods=["GET"]),
    Route("/api/analyze", analyze_message, methods=["POST"]),
    Route("/api/fake-bill/sample/{sample_type}", get_sample_bill_image, methods=["GET"]),
    Route("/api/fake-bill/analyze", analyze_fake_bill, methods=["POST"]),
    Route("/api/emergency", get_emergency_guide, methods=["GET"]),
    Route("/api/library", get_library_cases, methods=["GET"]),
    Route("/api/game/scenarios", get_game_scenarios, methods=["GET"]),
    Route("/api/game/evaluate", evaluate_game_answer, methods=["POST"]),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=False, routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.server:app", host="0.0.0.0", port=8000, reload=True)
