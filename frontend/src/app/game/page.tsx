"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  Play,
  Shuffle,
  Search,
  Heart,
  Trophy,
  Flag,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  RotateCcw,
} from "lucide-react";
import {
  fetchGameScenariosApi,
  evaluateGameAnswerApi,
  GameScenario,
  EvaluateGameResponse,
} from "@/lib/api";

interface TurnLog {
  stageIndex: number;
  scammerMessage: string;
  evaluation: EvaluateGameResponse;
}

export default function ScamGamePage() {
  const [scenarios, setScenarios] = useState<GameScenario[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCat, setSelectedCat] = useState("Tất cả");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const [activeScenario, setActiveScenario] = useState<GameScenario | null>(null);
  const [stageIdx, setStageIdx] = useState(0);
  const [hp, setHp] = useState(100);
  const [score, setScore] = useState(0);
  const [logs, setLogs] = useState<TurnLog[]>([]);
  const [selectedOpt, setSelectedOpt] = useState<number | null>(null);
  const [freeText, setFreeText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [finished, setFinished] = useState(false);

  const [bestScore, setBestScore] = useState(0);
  const [completedIds, setCompletedIds] = useState<string[]>([]);

  // Nạp tiến độ Đấu trường từ localStorage (không mất khi chuyển trang hoặc F5)
  useEffect(() => {
    try {
      const saved = localStorage.getItem("lachanso_game_progress");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.bestScore === "number") setBestScore(parsed.bestScore);
        if (Array.isArray(parsed.completedIds)) setCompletedIds(parsed.completedIds);
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(
        "lachanso_game_progress",
        JSON.stringify({ bestScore, completedIds })
      );
    } catch {
      // ignore
    }
  }, [bestScore, completedIds]);

  useEffect(() => {
    fetchGameScenariosApi()
      .then((data) => {
        setScenarios(data.scenarios);
        setCategories(data.categories);
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredScenarios = useMemo(() => {
    return scenarios.filter((s) => {
      const cat = s.category_name || s.category || "";
      const matchCat = selectedCat === "Tất cả" || cat === selectedCat;
      const q = searchQuery.trim().toLowerCase();
      const desc = s.brief || s.subtitle || s.context || s.description || "";
      const matchQ =
        !q ||
        s.title.toLowerCase().includes(q) ||
        cat.toLowerCase().includes(q) ||
        desc.toLowerCase().includes(q);
      return matchCat && matchQ;
    });
  }, [scenarios, selectedCat, searchQuery]);

  const startScenario = (sc: GameScenario) => {
    setActiveScenario(sc);
    setStageIdx(0);
    setHp(100);
    setScore(0);
    setLogs([]);
    setSelectedOpt(null);
    setFreeText("");
    setFinished(false);
  };

  const startRandom = () => {
    if (!scenarios.length) return;
    startScenario(scenarios[Math.floor(Math.random() * scenarios.length)]);
  };

  const handleSubmitTurn = async () => {
    if (!activeScenario || submitting) return;
    if (selectedOpt === null && !freeText.trim()) return;

    const currentStage = activeScenario.stages[stageIdx];
    setSubmitting(true);
    try {
      const res = await evaluateGameAnswerApi({
        scenario_id: activeScenario.id,
        stage_index: stageIdx,
        option_index: selectedOpt !== null ? selectedOpt : undefined,
        free_text: selectedOpt === null ? freeText.trim() : undefined,
      });

      const nextHp = Math.max(0, hp + res.hp_delta);
      const nextScore = score + res.score_delta;
      setHp(nextHp);
      setScore(nextScore);
      setLogs((prev) => [
        ...prev,
        {
          stageIndex: stageIdx,
          scammerMessage: currentStage.scammer || currentStage.scammer_message || "",
          evaluation: res,
        },
      ]);
      setSelectedOpt(null);
      setFreeText("");

      if (res.is_last_stage || nextHp <= 0) {
        setFinished(true);
        setBestScore((prev) => Math.max(prev, nextScore));
        setCompletedIds((prev) =>
          prev.includes(activeScenario.id) ? prev : [...prev, activeScenario.id]
        );
      } else {
        setStageIdx((prev) => prev + 1);
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (activeScenario) {
    const currentStage = activeScenario.stages[stageIdx];
    const maxScore = activeScenario.stages.length * 30;

    return (
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[var(--r-rule)]">
          <button
            type="button"
            onClick={() => setActiveScenario(null)}
            className="ribbon-btn inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-medium cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Quay lại sảnh
          </button>

          <div className="flex items-center gap-2.5 flex-wrap font-mono text-xs">
            <span
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium"
              style={{ backgroundColor: "var(--r-danger-soft)", color: "var(--r-danger)" }}
            >
              <Heart className="w-3.5 h-3.5" />
              {hp}%
            </span>
            <span
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium"
              style={{ backgroundColor: "var(--r-accent-soft)", color: "var(--r-accent)" }}
            >
              <Trophy className="w-3.5 h-3.5" />
              {score}/{maxScore}
            </span>
            <span className="ribbon-recessed inline-flex items-center gap-1.5 px-3 py-1.5 text-[var(--r-ink-2)]">
              <Flag className="w-3.5 h-3.5" />
              Lượt {Math.min(stageIdx + 1, activeScenario.stages.length)}/{activeScenario.stages.length}
            </span>
          </div>
        </div>

        <div className="ribbon-panel p-4">
          <div className="text-xs font-mono" style={{ color: "var(--r-accent)" }}>
            {activeScenario.category_name || activeScenario.category}
          </div>
          <h1 className="text-lg font-medium text-[var(--r-ink)] mt-0.5">
            {activeScenario.icon ? `${activeScenario.icon} ` : ""}
            {activeScenario.title}
          </h1>
          {(activeScenario.brief || activeScenario.subtitle) && (
            <p className="text-xs sm:text-sm text-[var(--r-muted)] mt-1">
              {activeScenario.brief || activeScenario.subtitle}
            </p>
          )}
        </div>

        {logs.map((log, i) => {
          const ev = log.evaluation;
          const isSafe = ev.level === "safe";
          const isRisky = ev.level === "risky";
          const evColor = isSafe ? "var(--r-safe)" : isRisky ? "var(--r-danger)" : "var(--r-warn)";
          const evBg = isSafe
            ? "var(--r-safe-soft)"
            : isRisky
            ? "var(--r-danger-soft)"
            : "var(--r-warn-soft)";
          return (
            <div key={i} className="space-y-3">
              <div className="ribbon-recessed p-4">
                <div className="text-[11px] font-medium text-[var(--r-muted)] mb-1">
                  Đối tượng nghi vấn · Lượt {log.stageIndex + 1}
                </div>
                <p className="text-sm text-[var(--r-ink)]">{log.scammerMessage}</p>
              </div>

              <div className="flex justify-end">
                <div
                  className="max-w-[80%] rounded-2xl px-4 py-2.5 text-sm text-[var(--r-ink)] border"
                  style={{
                    backgroundColor: "var(--r-user-bubble)",
                    borderColor: "var(--r-user-border)",
                  }}
                >
                  {ev.user_reply}
                </div>
              </div>

              <div
                className="rounded-xl p-4 border space-y-1.5"
                style={{ backgroundColor: evBg, borderColor: evColor }}
              >
                <div
                  className="text-xs font-semibold flex items-center gap-1.5"
                  style={{ color: evColor }}
                >
                  {isSafe ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : isRisky ? (
                    <ShieldAlert className="w-4 h-4" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  Trọng tài AI · {ev.title} (+{ev.score_delta} điểm)
                </div>
                <p className="text-xs sm:text-sm text-[var(--r-ink)] leading-relaxed">
                  {ev.feedback}
                </p>
                {ev.red_flag && (
                  <div className="text-xs text-[var(--r-ink-2)] pt-1">
                    <strong>Dấu hiệu cần nhớ:</strong> {ev.red_flag}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {!finished && currentStage ? (
          <div className="ribbon-panel p-5 space-y-4">
            <div className="ribbon-recessed p-4">
              <div className="text-xs font-medium mb-1" style={{ color: "var(--r-danger)" }}>
                {activeScenario.persona_avatar || "🎭"}{" "}
                {activeScenario.persona || "Đối tượng nghi vấn"} · Lượt {stageIdx + 1}/
                {activeScenario.stages.length}
              </div>
              <p className="text-sm sm:text-base text-[var(--r-ink)] leading-relaxed">
                &ldquo;{currentStage.scammer || currentStage.scammer_message}&rdquo;
              </p>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-medium text-[var(--r-muted)]">
                Chọn cách phản ứng của bạn
              </div>
              {currentStage.options.map((opt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setSelectedOpt(idx);
                    setFreeText("");
                  }}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm transition cursor-pointer ${
                    selectedOpt === idx
                      ? "ribbon-part text-[var(--r-ink)] font-medium"
                      : "ribbon-recessed text-[var(--r-ink-2)] hover:text-[var(--r-ink)]"
                  }`}
                  style={selectedOpt === idx ? { borderColor: "var(--r-accent)" } : undefined}
                >
                  <span className="font-mono font-semibold mr-2" style={{ color: "var(--r-accent)" }}>
                    {String.fromCharCode(65 + idx)}.
                  </span>
                  {opt.text}
                </button>
              ))}
            </div>

            <div className="space-y-1.5 pt-1">
              <label className="text-xs text-[var(--r-muted)]">
                Hoặc tự nhập câu trả lời của bạn
              </label>
              <input
                type="text"
                value={freeText}
                onChange={(e) => {
                  setFreeText(e.target.value);
                  if (e.target.value.trim()) setSelectedOpt(null);
                }}
                placeholder="Nhập phản hồi của bạn..."
                className="ribbon-recessed w-full px-3.5 py-2.5 text-sm text-[var(--r-ink)] placeholder-[var(--r-muted)] focus:outline-none focus:border-[var(--r-accent)]"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                disabled={submitting || (selectedOpt === null && !freeText.trim())}
                onClick={handleSubmitTurn}
                className="ribbon-btn-accent inline-flex items-center gap-2 px-5 py-2.5 rounded-xl disabled:opacity-40 text-sm font-semibold cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                Xác nhận câu trả lời
              </button>
            </div>
          </div>
        ) : (
          <div className="ribbon-panel p-6 text-center space-y-4">
            <h2 className="text-xl font-medium text-[var(--r-ink)]">
              Hoàn thành tình huống · Điểm cảnh giác: {score}/{maxScore}
            </h2>
            <p className="text-sm text-[var(--r-muted)] max-w-xl mx-auto">
              {score >= maxScore * 0.8
                ? "Xuất sắc! Bạn đã nhận diện chính xác các chiêu trò thao túng và giữ an toàn tuyệt đối."
                : "Bạn đã hoàn thành bài luyện tập. Hãy ghi nhớ các dấu hiệu cảnh báo từ Trọng tài AI để phản xạ tốt hơn."}
            </p>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => startScenario(activeScenario)}
                className="ribbon-btn inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-medium cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
                Chơi lại
              </button>
              <button
                type="button"
                onClick={() => setActiveScenario(null)}
                className="ribbon-btn-accent inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer"
              >
                Chọn tình huống khác
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3 pb-4 border-b border-[var(--r-rule)]">
        <div>
          <h1 className="text-2xl sm:text-[1.75rem] font-semibold tracking-tight text-[var(--r-ink)] leading-tight">
            Đấu trường lừa đảo
          </h1>
          <p className="text-sm text-[var(--r-ink-2)] mt-1">
            Thực hành đối thoại 3 lượt với bot lừa đảo để rèn phản xạ phòng vệ trước các kịch bản thực tế
          </p>
        </div>
        <button
          type="button"
          onClick={startRandom}
          className="ribbon-btn-accent game-random-btn inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer"
        >
          <Shuffle className="w-4 h-4" />
          Chơi ngẫu nhiên
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="ribbon-panel p-4">
          <div className="text-xs text-[var(--r-muted)]">Tổng tình huống</div>
          <div className="text-2xl font-mono font-medium text-[var(--r-ink)] mt-1 tabular-nums">
            {scenarios.length}
          </div>
        </div>
        <div className="ribbon-panel p-4">
          <div className="text-xs text-[var(--r-muted)]">Đã hoàn thành</div>
          <div
            className="text-2xl font-mono font-medium mt-1 tabular-nums"
            style={{ color: "var(--r-safe)" }}
          >
            {completedIds.length}/{scenarios.length}
          </div>
        </div>
        <div className="ribbon-panel p-4">
          <div className="text-xs text-[var(--r-muted)]">Điểm cao nhất</div>
          <div
            className="text-2xl font-mono font-medium mt-1 tabular-nums"
            style={{ color: "var(--r-accent)" }}
          >
            {bestScore}/90
          </div>
        </div>
        <div className="ribbon-panel p-4">
          <div className="text-xs text-[var(--r-muted)]">Số nhóm thủ đoạn</div>
          <div className="text-2xl font-mono font-medium text-[var(--r-ink)] mt-1 tabular-nums">
            {categories.length}
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-[var(--r-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm tình huống..."
            className="ribbon-recessed w-full pl-10 pr-4 py-2.5 text-sm text-[var(--r-ink)] placeholder-[var(--r-muted)] focus:outline-none focus:border-[var(--r-accent)]"
          />
        </div>
        <select
          value={selectedCat}
          onChange={(e) => setSelectedCat(e.target.value)}
          className="ribbon-recessed px-3.5 py-2.5 text-sm text-[var(--r-ink)] focus:outline-none focus:border-[var(--r-accent)]"
        >
          <option value="Tất cả">Tất cả nhóm thủ đoạn</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-[var(--r-muted)] text-sm">
          Đang tải danh sách tình huống...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {filteredScenarios.map((sc) => {
            const done = completedIds.includes(sc.id);
            return (
              <div
                key={sc.id}
                className="ribbon-panel p-4 flex flex-col justify-between gap-3 transition hover:border-[var(--r-accent)]"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className="text-[11px] font-medium px-2 py-0.5 rounded-md truncate"
                      style={{
                        backgroundColor: "var(--r-accent-soft)",
                        color: "var(--r-accent)",
                      }}
                    >
                      {sc.category_name || sc.category || "Tình huống thực tế"}
                    </span>
                    {done && (
                      <span className="text-[11px] font-medium flex-shrink-0" style={{ color: "var(--r-safe)" }}>
                        Đã chơi
                      </span>
                    )}
                  </div>
                  <h3 className="font-medium text-sm sm:text-[15px] text-[var(--r-ink)] leading-snug">
                    {sc.icon ? `${sc.icon} ` : ""}
                    {sc.title}
                  </h3>
                  <p className="text-xs text-[var(--r-muted)] line-clamp-2">
                    {sc.brief || sc.subtitle || "Tình huống đối thoại 3 lượt thực tế."}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => startScenario(sc)}
                  className="ribbon-btn game-play-btn w-full py-2 px-3 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5" style={{ color: "var(--r-accent)" }} />
                  Chơi ngay
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
