"""
View: tab_scam_game.py
Tab 3/4: Đấu Trường Lừa Đảo — Môi trường mô phỏng tương tác với "bot lừa đảo".

Mỗi tình huống gồm 3 lượt đối thoại liên tiếp, dựa trên các bài báo cảnh báo
chính thống trong backend/data/scam_knowledge.json. Giao diện sử dụng 100%
thành phần gốc của Streamlit (không nhúng HTML thô trong tình huống và phản hồi)
để đảm bảo hiển thị sạch sẽ, tương thích mọi cỡ chữ 128%–150% và mọi theme.
Phụ trách: Thành viên 3 (Frontend & UX Developer)
"""

import json
import os
import random
import unicodedata

import streamlit as st


# =============================================================================
# 1. HẰNG SỐ & TIỆN ÍCH
# =============================================================================

LEVEL_META = {
    "safe": {
        "label": "✅ An toàn",
        "score": 30,
        "hp": 0,
        "title": "PHẢN XẠ AN TOÀN",
    },
    "neutral": {
        "label": "⚠️ Chưa dứt khoát",
        "score": 10,
        "hp": -10,
        "title": "CHƯA DỨT KHOÁT",
    },
    "risky": {
        "label": "🚨 Dính bẫy",
        "score": 0,
        "hp": -35,
        "title": "ĐÃ SẬP BẪY",
    },
}

MAX_SCORE_PER_STAGE = 30


def _load_game_data():
    """Nạp bộ tình huống từ backend/data/scam_scenarios.json."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    candidates = [
        os.path.join(root_dir, "backend", "data", "scam_scenarios.json"),
        os.path.join(current_dir, "..", "..", "backend", "data", "scam_scenarios.json"),
        os.path.join(os.getcwd(), "backend", "data", "scam_scenarios.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("scenarios", []), path
            except Exception:
                continue
    return [], ""


def _norm(text: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp câu trả lời tự do linh hoạt hơn."""
    text = (text or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _score_free_text(stage, text: str) -> str:
    """Chấm câu trả lời tự do theo từ khóa; ưu tiên cụm khớp dài hơn."""
    t = _norm(text)
    safe_hits = [k for k in stage.get("safe_keywords", []) if _norm(k) in t]
    risky_hits = [k for k in stage.get("risky_keywords", []) if _norm(k) in t]
    safe_weight = sum(len(_norm(k)) for k in safe_hits)
    risky_weight = sum(len(_norm(k)) for k in risky_hits)
    if safe_weight > risky_weight:
        return "safe"
    if risky_weight > safe_weight:
        return "risky"
    return "neutral"


def _option_by_level(stage, level):
    for opt in stage.get("options", []):
        if opt.get("level") == level:
            return opt
    return {}


def _init_state():
    defaults = {
        "game_scenario_id": None,
        "game_stage": 0,
        "game_hp": 100,
        "game_score": 0,
        "game_history": [],
        "game_flags": [],
        "game_answers": [],
        "game_finished": False,
        "game_best_scores": {},
        "game_played_ids": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _find_scenario(scenarios, scenario_id):
    for sc in scenarios:
        if sc.get("id") == scenario_id:
            return sc
    return None


def _start_game(sc):
    st.session_state.game_scenario_id = sc["id"]
    st.session_state.game_stage = 0
    st.session_state.game_hp = 100
    st.session_state.game_score = 0
    st.session_state.game_flags = []
    st.session_state.game_answers = []
    st.session_state.game_finished = False
    st.session_state.game_history = [
        {"role": "scammer", "text": sc["stages"][0]["scammer"]}
    ]


def _apply_answer(sc, level, answer_text, feedback, red_flag=None):
    """Ghi nhận câu trả lời, trừ HP, cộng điểm và mở lượt kế tiếp."""
    meta = LEVEL_META[level]

    st.session_state.game_hp = max(0, st.session_state.game_hp + meta["hp"])
    st.session_state.game_score += meta["score"]
    st.session_state.game_answers.append(level)

    st.session_state.game_history.append({"role": "user", "text": answer_text})
    st.session_state.game_history.append(
        {
            "role": "coach",
            "text": feedback,
            "level": level,
            "red_flag": red_flag if level == "safe" else None,
        }
    )
    if level == "safe" and red_flag:
        st.session_state.game_flags.append(red_flag)

    next_stage = st.session_state.game_stage + 1
    if st.session_state.game_hp <= 0 or next_stage >= len(sc["stages"]):
        st.session_state.game_finished = True
        best = st.session_state.game_best_scores.get(sc["id"], 0)
        st.session_state.game_best_scores[sc["id"]] = max(best, st.session_state.game_score)
        if sc["id"] not in st.session_state.game_played_ids:
            st.session_state.game_played_ids.append(sc["id"])
    else:
        st.session_state.game_stage = next_stage
        st.session_state.game_history.append(
            {"role": "scammer", "text": sc["stages"][next_stage]["scammer"]}
        )


def _source_cases(rag_matcher, source_ids):
    if not rag_matcher:
        return []
    try:
        cases = rag_matcher.get_all_cases()
    except Exception:
        return []
    wanted = set(source_ids or [])
    return [c for c in cases if c.get("id") in wanted]


# =============================================================================
# 2. RENDER LOBBY THƯ VIỆN TÌNH HUỐNG (100% STREAMLIT NATIVE)
# =============================================================================

def _render_lobby(scenarios):
    with st.container(border=True):
        st.markdown("### 🎮 Đấu Trường Lừa Đảo")
        st.write(
            "Bước vào cuộc trò chuyện với \"bot lừa đảo\" và xem bạn có giữ được bình tĩnh không. "
            "Mỗi tình huống gồm **3 lượt đối thoại**, dựa trên các bài báo cảnh báo chính thống của Cục An toàn thông tin."
        )
        st.caption("💬 3 lượt / tình huống · ❤️ Thanh sinh tồn HP · 🚩 Nhận diện dấu hiệu · 📰 Trích dẫn bài báo gốc")

    best_scores = st.session_state.get("game_best_scores", {})
    best_overall = max(best_scores.values()) if best_scores else 0
    played = len(st.session_state.get("game_played_ids", []))

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    for col, label, num in [
        (col_s1, "Tình huống", len(scenarios)),
        (col_s2, "Đã chơi", played),
        (col_s3, "Điểm cao nhất", f"{best_overall}/90"),
        (col_s4, "Đã hoàn thành", f"{len(best_scores)}/{len(scenarios)}"),
    ]:
        with col:
            with st.container(border=True):
                st.metric(label, num)

    col_filter, col_search, col_random = st.columns([1.3, 1.7, 1], vertical_alignment="bottom")
    categories = ["Tất cả nhóm thủ đoạn"] + sorted(
        {sc.get("category_name", "") for sc in scenarios if sc.get("category_name")}
    )
    with col_filter:
        selected_cat = st.selectbox("Lọc nhóm thủ đoạn:", categories, key="game_filter_cat")
    with col_search:
        keyword = st.text_input(
            "Tìm tình huống:",
            placeholder="ví dụ: công an, OTP, fake bill...",
            key="game_filter_kw",
        )
    with col_random:
        if st.button("🎲 Ngẫu nhiên", use_container_width=True, key="game_btn_random"):
            pool = [sc for sc in scenarios if sc.get("id") != st.session_state.get("game_scenario_id")]
            pick = random.choice(pool or scenarios)
            _start_game(pick)
            st.rerun()

    filtered = scenarios
    if selected_cat != "Tất cả nhóm thủ đoạn":
        filtered = [sc for sc in filtered if sc.get("category_name") == selected_cat]
    if keyword.strip():
        kw = _norm(keyword.strip())
        filtered = [
            sc
            for sc in filtered
            if kw in _norm(sc.get("title", ""))
            or kw in _norm(sc.get("subtitle", ""))
            or kw in _norm(sc.get("category_name", ""))
        ]

    if not filtered:
        st.info("Không tìm thấy tình huống phù hợp. Hãy thử từ khóa khác.")
        return

    st.caption(f"Hiển thị **{len(filtered)} / {len(scenarios)}** tình huống. Chọn một tình huống để bắt đầu:")

    cols = st.columns(3, gap="medium")
    for idx, sc in enumerate(filtered):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"#### {sc.get('icon', '🎭')} {sc.get('title', '')}")
                st.write(sc.get("subtitle", ""))
                st.caption(
                    f"🏷️ {sc.get('category_name', '')} · "
                    f"🎯 {sc.get('difficulty', '')} · "
                    f"📰 {len(sc.get('source_ids', []))} bài báo"
                )
                best = best_scores.get(sc.get("id"))
                if best is not None:
                    st.caption(f"⭐ Điểm cao nhất của bạn: **{best}/90**")
                if st.button(
                    "▶ Chơi ngay",
                    key=f"game_start_{sc['id']}",
                    use_container_width=True,
                ):
                    _start_game(sc)
                    st.rerun()


# =============================================================================
# 3. RENDER MÀN CHƠI (100% STREAMLIT NATIVE, KHÔNG HTML THÔ)
# =============================================================================

def _render_status_bar(sc):
    hp = st.session_state.game_hp
    score = st.session_state.game_score
    stage = st.session_state.game_stage
    total_stages = len(sc["stages"])
    flags = len(st.session_state.game_flags)

    if hp >= 80:
        hp_badge = "🟢 AN TOÀN"
    elif hp >= 40:
        hp_badge = "🟡 CẢNH BÁO"
    else:
        hp_badge = "🔴 NGUY HIỂM"

    col_hp, col_score, col_flags = st.columns([2.2, 1, 1], vertical_alignment="center")
    with col_hp:
        with st.container(border=True):
            st.markdown(
                f"**❤️ Sinh tồn: {hp} HP · {hp_badge}**  \n"
                f"Lượt **{min(stage + 1, total_stages)}/{total_stages}**"
            )
            st.progress(max(0.0, min(1.0, hp / 100.0)))
    with col_score:
        with st.container(border=True):
            st.metric("⭐ Điểm", f"{score}/90")
    with col_flags:
        with st.container(border=True):
            st.metric("🚩 Dấu hiệu", flags)


def _render_history():
    with st.container(border=True):
        for item in st.session_state.game_history:
            role = item.get("role")
            text = (item.get("text") or "").strip()
            if role == "scammer":
                with st.chat_message("assistant", avatar="😈"):
                    st.markdown(f"**KẺ LỪA ĐẢO**\n\n{text}")
            elif role == "user":
                with st.chat_message("user", avatar="🧑"):
                    st.write(text)
            else:
                level = item.get("level", "neutral")
                meta = LEVEL_META.get(level, LEVEL_META["neutral"])
                red_flag = item.get("red_flag")

                coach_lines = [
                    f"**🛡️ TRỌNG TÀI AI · {meta['label'].upper()}**",
                    text,
                ]
                if red_flag:
                    coach_lines.append(f"🚩 **Dấu hiệu nhận diện:** {red_flag}")
                coach_body = "\n\n".join(coach_lines)

                if level == "safe":
                    st.success(coach_body)
                elif level == "risky":
                    st.error(coach_body)
                else:
                    st.warning(coach_body)


def _render_play(sc, rag_matcher):
    stages = sc["stages"]
    stage_index = st.session_state.game_stage
    stage = stages[stage_index]

    col_back, col_title = st.columns([1.3, 4.7], vertical_alignment="center")
    with col_back:
        if st.button("← Quay lại", use_container_width=True, key="game_back"):
            st.session_state.game_scenario_id = None
            st.session_state.game_finished = False
            st.rerun()
    with col_title:
        st.markdown(f"### {sc.get('icon', '🎭')} {sc.get('title', '')}")
        st.caption(f"{sc.get('category_name', '')} · Độ khó: {sc.get('difficulty', '')}")

    _render_status_bar(sc)

    with st.expander("📋 Bối cảnh tình huống", expanded=(stage_index == 0)):
        st.write(sc.get("brief", ""))
        sources = _source_cases(rag_matcher, sc.get("source_ids"))
        if sources:
            st.caption("Dựa trên: " + " · ".join(s.get("title", "") for s in sources))

    _render_history()

    if st.session_state.game_finished:
        _render_result(sc, rag_matcher)
        return

    st.markdown(f"**💬 Lượt {stage_index + 1}/{len(stages)} — Bạn sẽ phản ứng thế nào?**")

    option_labels = [opt.get("text", "") for opt in stage.get("options", [])]
    selected = st.radio(
        "Chọn câu trả lời:",
        option_labels,
        index=None,
        key=f"game_radio_{sc['id']}_{stage_index}",
        label_visibility="collapsed",
    )
    if st.button(
        "✅ Xác nhận câu trả lời",
        type="primary",
        use_container_width=True,
        disabled=selected is None,
        key=f"game_confirm_{sc['id']}_{stage_index}",
    ):
        opt = stage["options"][option_labels.index(selected)]
        _apply_answer(
            sc,
            opt.get("level", "neutral"),
            opt.get("text", ""),
            opt.get("feedback", ""),
            opt.get("red_flag"),
        )
        st.rerun()

    with st.expander("✍️ Hoặc tự gõ câu trả lời của bạn"):
        with st.form(
            key=f"game_free_form_{sc['id']}_{stage_index}",
            clear_on_submit=True,
        ):
            free_text = st.text_input(
                "Câu trả lời tự do:",
                placeholder="Ví dụ: Tôi không chuyển tiền, tôi sẽ gọi lại số cũ để xác minh...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("📨 Gửi câu trả lời", use_container_width=True)
        if submitted:
            if not free_text.strip():
                st.warning("Bạn chưa nhập câu trả lời.")
            else:
                level = _score_free_text(stage, free_text)
                opt = _option_by_level(stage, level)
                feedback = opt.get("feedback", "")
                if level == "neutral":
                    feedback = (
                        "Câu trả lời chưa thể hiện rõ phản xạ an toàn. "
                        + (feedback or "Hãy từ chối dứt khoát và xác minh qua kênh chính thức.")
                    )
                _apply_answer(sc, level, free_text.strip(), feedback, opt.get("red_flag"))
                st.rerun()

    with st.expander("💡 Gợi ý của trọng tài"):
        st.info(stage.get("hint", "Hãy chậm lại, kiểm tra danh tính và không chuyển tiền/OTP cho bất kỳ ai."))


# =============================================================================
# 4. RENDER KẾT QUẢ (100% STREAMLIT NATIVE)
# =============================================================================

def _render_result(sc, rag_matcher):
    hp = st.session_state.game_hp
    score = st.session_state.game_score
    answers = st.session_state.game_answers
    risky_count = answers.count("risky")
    safe_count = answers.count("safe")

    if hp <= 0:
        st.error(
            "### 💀 BẠN ĐÃ SẬP BẪY!\n\n"
            "Bạn đã làm theo hướng dẫn của kẻ lừa đảo. Trong thực tế, tài khoản của bạn đã bị chiếm đoạt."
        )
    elif risky_count == 0 and safe_count == len(answers):
        st.success(
            "### 🏆 XUẤT SẮC! PHẢN XẠ VÀNG\n\n"
            "Bạn nhận diện đúng mọi dấu hiệu và không để kẻ lừa đảo dắt mũi."
        )
    elif risky_count == 0:
        st.warning(
            "### 🛡️ HOÀN THÀNH TỐT\n\n"
            "Bạn không sập bẫy, nhưng vài phản ứng còn chưa dứt khoát. Hãy quyết liệt hơn ở lần sau."
        )
    else:
        st.warning(
            "### ⚠️ HOÀN THÀNH NHƯNG CÒN SƠ HỞ\n\n"
            "Bạn đã trụ được đến cuối, nhưng có lúc suýt sập bẫy. Xem lại các dấu hiệu bên dưới nhé."
        )

    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, num in [
        (col_a, "Tổng điểm", f"{score}/90"),
        (col_b, "Sinh tồn", f"{hp} HP"),
        (col_c, "Lượt an toàn", safe_count),
        (col_d, "Dấu hiệu", len(st.session_state.game_flags)),
    ]:
        with col:
            with st.container(border=True):
                st.metric(label, num)

    if st.session_state.game_flags:
        with st.container(border=True):
            st.markdown("#### 🚩 Các dấu hiệu bạn đã nhận diện đúng")
            for flag in st.session_state.game_flags:
                st.markdown(f"- {flag}")

    with st.container(border=True):
        st.markdown("#### 🧠 Điều cần ghi nhớ")
        st.write(sc.get("debrief", ""))
        if sc.get("golden_rule"):
            st.info(f"**Nguyên tắc vàng:** {sc.get('golden_rule', '')}")

    sources = _source_cases(rag_matcher, sc.get("source_ids"))
    if sources:
        st.markdown("#### 📰 Bài báo gốc trên báo chí chính thống")
        for case in sources:
            with st.container(border=True):
                st.markdown(f"**{case.get('title', '')}**")
                st.caption(f"{case.get('source', '')} · Nhóm: {case.get('category_name', 'Chưa xác định')}")
                st.write(case.get("summary", ""))
                url = (case.get("url") or "").strip()
                if url.startswith(("http://", "https://")):
                    st.link_button("👉 Đọc bài báo gốc", url, use_container_width=True)

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🔁 Chơi lại", use_container_width=True, key="game_replay"):
            _start_game(sc)
            st.rerun()
    with col_r2:
        if st.button("🎲 Tình huống khác", use_container_width=True, key="game_other"):
            st.session_state.game_scenario_id = None
            st.session_state.game_finished = False
            st.rerun()
    with col_r3:
        if st.button("🏠 Về danh sách", use_container_width=True, key="game_home"):
            st.session_state.game_scenario_id = None
            st.session_state.game_finished = False
            st.rerun()


# =============================================================================
# 5. ENTRY POINT
# =============================================================================

def render_tab_scam_game(rag_matcher=None):
    """Hiển thị Tab Đấu trường lừa đảo."""
    _init_state()
    scenarios, _ = _load_game_data()

    if not scenarios:
        st.error(
            "Không tìm thấy dữ liệu tình huống. Vui lòng kiểm tra file "
            "`backend/data/scam_scenarios.json`."
        )
        return

    scenario_id = st.session_state.get("game_scenario_id")
    scenario = _find_scenario(scenarios, scenario_id) if scenario_id else None

    if scenario is None:
        _render_lobby(scenarios)
        return

    _render_play(scenario, rag_matcher)
