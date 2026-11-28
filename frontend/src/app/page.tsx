"use client";

import React, { useRef, useState } from "react";
import {
  Send,
  Paperclip,
  Trash2,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  X,
  Link2,
  Brain,
  CheckCircle2,
  Loader2,
  ClipboardPaste,
  Copy,
  Check,
} from "lucide-react";
import { useAppContext, ChatMessage } from "@/context/AppContext";
import { analyzeMessageApi, AnalyzeResult } from "@/lib/api";
import { RiskGauge } from "@/components/RiskGauge";

const SAMPLE_SCENARIOS = [
  {
    label: "Giả danh ngân hàng khóa thẻ",
    tag: "Phishing",
    tone: "danger",
    text: "Tài khoản ngân hàng của bạn có dấu hiệu bất thường và sắp bị khóa. Vui lòng truy cập http://vcb-xacthuc-24h.xyz để xác minh thông tin trong vòng 10 phút.",
  },
  {
    label: "Giả danh công an cài VNeID",
    tag: "Nguy cơ cao",
    tone: "danger",
    text: "Tôi là cán bộ Công an, CCCD của bạn liên quan đường dây rửa tiền 40 tỷ. Yêu cầu giữ bí mật tuyệt đối, tải app VNeID dịch vụ công qua file APK và chuyển tiền vào tài khoản an toàn để xác minh.",
  },
  {
    label: "Tuyển CTV chốt đơn Shopee",
    tag: "CTV lừa đảo",
    tone: "danger",
    text: "Tuyển cộng tác viên chốt đơn Shopee tại nhà, mỗi ngày chỉ cần 30 phút làm nhiệm vụ nạp tiền nhận hoa hồng 20% thanh toán ngay lập tức.",
  },
  {
    label: "Giả danh shipper thu phí COD",
    tag: "Đáng ngờ",
    tone: "warn",
    text: "Anh là shipper giao đơn hàng 280k nhưng em không nghe máy, em chuyển khoản trước 35k phí lưu kho vào STK 1903888999 để anh giao lại nhé.",
  },
  {
    label: "Phạt nguội CSGT giả mạo",
    tag: "Nguy cơ cao",
    tone: "danger",
    text: "Cục CSGT thông báo phương tiện của bạn bị phạt nguội vi phạm tốc độ. Truy cập tra-cuu-phat-nguoi.top và cung cấp mã OTP để nộp phạt ngay.",
  },
  {
    label: "Tin nhắn sinh hoạt an toàn",
    tag: "An toàn",
    tone: "safe",
    text: "Chiều nay 5h tan làm nhớ ghé siêu thị mua thêm sữa và rau rồi về ăn cơm nhé!",
  },
];

const QUICK_INPUT_HINTS = [
  {
    chip: "Nhận được link lạ",
    keywords: ["link", "http", "web", "truy cập", "bấm vào", "xác minh", "đường dẫn"],
    text: "Tôi nhận được tin nhắn yêu cầu bấm vào đường link lạ để xác minh tài khoản: ",
  },
  {
    chip: "Xưng công an / VNeID",
    keywords: ["công an", "cảnh sát", "vneid", "cccd", "rửa tiền", "lệnh bắt", "apk"],
    text: "Có người gọi điện tự xưng cán bộ công an báo CCCD liên quan vụ án và yêu cầu cài app VNeID qua file APK.",
  },
  {
    chip: "Ngân hàng báo khóa thẻ",
    keywords: ["ngân hàng", "khóa", "thẻ", "tài khoản", "otp", "vcb", "mb", "bidv"],
    text: "Tài khoản ngân hàng của bạn có dấu hiệu bất thường và sắp bị khóa, yêu cầu nhập mã OTP để xác minh.",
  },
  {
    chip: "Shipper đòi chuyển khoản",
    keywords: ["ship", "giao hàng", "cod", "đơn hàng", "phí", "stk"],
    text: "Có người tự xưng shipper báo giao hàng nhưng yêu cầu chuyển khoản trước phí ship vào số tài khoản lạ.",
  },
  {
    chip: "Người thân mượn tiền Zalo",
    keywords: ["zalo", "mượn tiền", "vay", "người thân", "gấp", "chuyển khoản", "bạn"],
    text: "Tài khoản Zalo người thân nhắn tin hỏi mượn tiền gấp và nhờ chuyển vào số tài khoản tên người khác.",
  },
  {
    chip: "Tuyển CTV chốt đơn",
    keywords: ["ctv", "shopee", "hoa hồng", "nhiệm vụ", "việc nhẹ", "nạp tiền", "lương"],
    text: "Có tin nhắn tuyển cộng tác viên chốt đơn Shopee tại nhà, yêu cầu nạp tiền làm nhiệm vụ để nhận hoa hồng 20%.",
  },
  {
    chip: "Phạt nguội CSGT",
    keywords: ["phạt", "csgt", "tốc độ", "giao thông", "vi phạm", "biển số"],
    text: "Nhận được thông báo phạt nguội giao thông yêu cầu truy cập website lạ và cung cấp mã OTP để nộp phạt.",
  },
];

const DANGER_KEYWORDS = [
  "rửa tiền",
  "công an",
  "cảnh sát hình sự",
  "bắt tạm giam",
  "tài khoản an toàn",
  "chuyển tiền",
  "giữ bí mật",
  "lệnh bắt",
  "viện kiểm sát",
  "nạp tiền",
  "hoa hồng",
  "nhiệm vụ",
  "phạt nguội",
  "mã otp",
  "csgt",
  "khóa thẻ",
  "bị khóa",
  "xác minh",
  "file apk",
];

function highlightKeywords(text: string): React.ReactNode {
  const regex = new RegExp(`(${DANGER_KEYWORDS.join("|")})`, "gi");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    DANGER_KEYWORDS.some((kw) => kw.toLowerCase() === part.toLowerCase()) ? (
      <mark key={i} className="kw-danger">
        {part}
      </mark>
    ) : (
      <React.Fragment key={i}>{part}</React.Fragment>
    )
  );
}

function buildShareSummary(res: AnalyzeResult): string {
  const recs = res.action_recommendations.map((r) => `- ${r}`).join("\n");
  return `[Cảnh báo từ Lá Chắn Số]
Mức độ rủi ro: ${res.risk_score}/100 (${res.threat_level})
Thủ đoạn: ${res.detected_tactic}
Nhận định: ${res.explanation}
Khuyến nghị:
${recs}`;
}

export default function ChatCheckPage() {
  const {
    geminiApiKey,
    setEmergencyOpen,
    chatMessages,
    setChatMessages,
    clearChatMessages,
  } = useAppContext();

  const [inputText, setInputText] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [attachedPreview, setAttachedPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [pasteHint, setPasteHint] = useState<string | null>(null);
  const [inputFocused, setInputFocused] = useState(false);

  const matchedHints = React.useMemo(() => {
    const q = inputText.trim().toLowerCase();
    if (q.length < 2) return [];
    return QUICK_INPUT_HINTS.filter(
      (h) =>
        h.text.toLowerCase() !== q &&
        (h.chip.toLowerCase().includes(q) ||
          h.text.toLowerCase().includes(q) ||
          h.keywords.some((kw) => kw.includes(q) || q.includes(kw)))
    ).slice(0, 3);
  }, [inputText]);

  const applyHint = (hintText: string) => {
    setInputText(hintText);
    setInputFocused(false);
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
        const len = hintText.length;
        inputRef.current.setSelectionRange(len, len);
      }
    }, 0);
  };

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const latestResponseRef = useRef<HTMLDivElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAttachedFile(file);
    setAttachedPreview(URL.createObjectURL(file));
  };

  const clearAttachment = () => {
    setAttachedFile(null);
    if (attachedPreview) URL.revokeObjectURL(attachedPreview);
    setAttachedPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleQuickPaste = async () => {
    try {
      const clip = await navigator.clipboard.readText();
      if (clip && clip.trim()) {
        setInputText(clip.trim());
        inputRef.current?.focus();
      } else {
        setPasteHint("Bộ nhớ tạm đang trống");
        setTimeout(() => setPasteHint(null), 2000);
      }
    } catch {
      setPasteHint("Nhấn Ctrl+V vào ô nhập để dán");
      inputRef.current?.focus();
      setTimeout(() => setPasteHint(null), 2500);
    }
  };

  const handleCopyAlert = async (msgId: string, res: AnalyzeResult) => {
    try {
      await navigator.clipboard.writeText(buildShareSummary(res));
      setCopiedId(msgId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // ignore
    }
  };

  const submitAnalysis = async (customText?: string) => {
    const textToSend = (customText ?? inputText).trim();
    const fileToSend = customText ? null : attachedFile;
    const previewToKeep = customText ? undefined : attachedPreview || undefined;

    if (!textToSend && !fileToSend) return;
    if (loading) return;

    const now = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: textToSend || "(Đính kèm ảnh biên lai / chụp màn hình cần phân tích)",
      imagePreview: previewToKeep,
      timestamp: now,
    };

    setChatMessages((prev) => [...prev, userMsg]);
    if (!customText) {
      setInputText("");
      setAttachedFile(null);
      setAttachedPreview(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
    setLoading(true);

    try {
      const result = await analyzeMessageApi({
        text: textToSend,
        apiKey: geminiApiKey,
        image: fileToSend,
      });

      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: result.explanation,
        result,
        timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      };

      setChatMessages((prev) => [...prev, assistantMsg]);
      setTimeout(() => {
        latestResponseRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "assistant",
        content: "",
        error: err instanceof Error ? err.message : "Không thể kết nối máy chủ AI.",
        timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      };
      setChatMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const inputBar = (
    <div className="ribbon-panel chat-input-box p-2.5 space-y-2 transition-colors">
      {attachedPreview && (
        <div className="flex items-center gap-3 px-2 pt-1">
          <img
            src={attachedPreview}
            alt="Xem trước ảnh đính kèm"
            className="w-12 h-12 rounded-lg object-cover border border-[var(--r-rule-2)]"
          />
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-[var(--r-ink)] truncate">
              {attachedFile?.name}
            </div>
            <div className="text-[11px] text-[var(--r-muted)]">
              Ảnh đính kèm sẽ được phân tích cùng tin nhắn
            </div>
          </div>
          <button
            type="button"
            onClick={clearAttachment}
            className="p-1.5 rounded-lg text-[var(--r-muted)] hover:text-[var(--r-ink)] cursor-pointer"
            aria-label="Gỡ ảnh đính kèm"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submitAnalysis();
        }}
        className="flex flex-col sm:flex-row sm:items-center gap-2"
      >
        <input
          id="chat-file-input"
          name="attachment"
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={handleFileChange}
          className="hidden"
        />

        <input
          id="chat-message-input"
          name="message"
          aria-label="Nhập tin nhắn nghi ngờ hoặc đường link lạ cần kiểm tra"
          ref={inputRef}
          type="text"
          value={inputText}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setTimeout(() => setInputFocused(false), 160)}
          onKeyDown={(e) => {
            if (e.key === "Tab" && matchedHints.length > 0) {
              e.preventDefault();
              applyHint(matchedHints[0].text);
            }
          }}
          onChange={(e) => {
            setInputText(e.target.value);
            setInputFocused(true);
          }}
          placeholder="Dán tin nhắn nghi ngờ hoặc đường link lạ cần kiểm tra..."
          className="order-1 sm:order-2 flex-1 w-full bg-transparent px-2.5 py-2 text-[0.9375rem] sm:text-base text-[var(--r-ink)] placeholder-[var(--r-muted)] focus:outline-none min-w-0"
        />

        <div className="order-2 sm:order-1 flex items-center justify-between sm:justify-start gap-2 flex-shrink-0">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="ribbon-btn inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-2 sm:py-2.5 text-sm font-medium cursor-pointer flex-shrink-0"
              title="Đính kèm ảnh biên lai hoặc ảnh chụp màn hình"
            >
              <Paperclip className="w-4 h-4" style={{ color: "var(--r-accent)" }} />
              <span>Tải ảnh bill</span>
            </button>

            <button
              type="button"
              onClick={handleQuickPaste}
              className="ribbon-btn inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-2 sm:py-2.5 text-sm font-medium cursor-pointer flex-shrink-0"
              title="Dán nhanh tin nhắn từ bộ nhớ tạm"
            >
              <ClipboardPaste className="w-4 h-4 text-[var(--r-ink-2)]" />
              <span className="sm:hidden md:inline">Dán nhanh</span>
            </button>
          </div>

          <button
            type="submit"
            disabled={loading || (!inputText.trim() && !attachedFile)}
            className="sm:hidden ribbon-btn-accent inline-flex items-center gap-1.5 px-4 py-2 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-semibold cursor-pointer flex-shrink-0"
          >
            <span>Phân tích</span>
            <Send className="w-4 h-4" />
          </button>
        </div>

        <button
          type="submit"
          disabled={loading || (!inputText.trim() && !attachedFile)}
          className="hidden sm:inline-flex order-3 ribbon-btn-accent items-center gap-1.5 px-4 py-2.5 disabled:opacity-40 disabled:cursor-not-allowed text-sm sm:text-[0.9375rem] font-semibold cursor-pointer flex-shrink-0"
        >
          <span>Phân tích</span>
          <Send className="w-4 h-4" />
        </button>
      </form>

      {/* Danh sách gợi ý tự động khi đang gõ (nhấn Tab hoặc bấm để điền nhanh) */}
      {inputFocused && matchedHints.length > 0 && (
        <div className="border-t border-[var(--r-rule)] pt-2 space-y-1">
          <div className="flex items-center justify-between px-2 text-xs text-[var(--r-muted)]">
            <span>Gợi ý nhập nhanh</span>
            <span className="hidden sm:inline font-mono">Nhấn Tab để chọn dòng đầu</span>
          </div>
          {matchedHints.map((hint, i) => (
            <button
              key={i}
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                applyHint(hint.text);
              }}
              className="w-full text-left px-2.5 py-2 rounded-md text-sm text-[var(--r-ink-2)] hover:bg-[var(--r-paper-3)] hover:text-[var(--r-ink)] transition-colors flex items-center justify-between gap-2 cursor-pointer"
            >
              <span className="truncate">{hint.text}</span>
              <span
                className="text-xs font-medium flex-shrink-0"
                style={{ color: "var(--r-accent)" }}
              >
                Chọn
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Dải chip gợi ý 1-chạm khi chưa có hội thoại và ô nhập đang trống */}
      {chatMessages.length === 0 && !inputText.trim() && (
        <div className="flex items-center gap-2 flex-wrap px-1 pt-1">
          <span className="text-sm sm:text-[0.9375rem] font-medium text-[var(--r-muted)] mr-0.5">
            Gợi ý nhanh:
          </span>
          {QUICK_INPUT_HINTS.slice(0, 5).map((hint, i) => (
            <button
              key={i}
              type="button"
              onClick={() => applyHint(hint.text)}
              className="px-3.5 py-1.5 rounded-md text-sm sm:text-[0.9375rem] font-medium bg-[var(--r-paper)] hover:bg-[var(--r-paper-3)] text-[var(--r-ink-2)] hover:text-[var(--r-ink)] border border-[var(--r-rule)] transition-colors cursor-pointer"
            >
              + {hint.chip}
            </button>
          ))}
        </div>
      )}

      {pasteHint && (
        <div className="px-2 text-xs text-[var(--r-muted)]">{pasteHint}</div>
      )}
    </div>
  );

  return (
    <div className="flex flex-col min-h-[calc(100vh-3.5rem)] gap-5">
      {/* Header trang */}
      <div className="flex flex-wrap items-end justify-between gap-3 pb-4 border-b border-[var(--r-rule)]">
        <div>
          <h1 className="text-2xl sm:text-[1.85rem] font-semibold tracking-tight text-[var(--r-ink)] leading-tight">
            Kiểm tra tin nhắn và đường link
          </h1>
          <p className="text-base sm:text-[1.0625rem] text-[var(--r-ink-2)] mt-1.5 leading-relaxed">
            Dán tin nhắn SMS, Zalo, đường link lạ hoặc ảnh chụp màn hình để thẩm định dấu hiệu lừa đảo
          </p>
        </div>

        {chatMessages.length > 0 && (
          <button
            type="button"
            onClick={clearChatMessages}
            className="ribbon-btn inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium cursor-pointer"
          >
            <Trash2 className="w-4 h-4 text-[var(--r-muted)]" />
            <span>Xóa đoạn chat</span>
          </button>
        )}
      </div>

      {/* Vùng nội dung chính */}
      <div className="flex-1 space-y-5">
        {chatMessages.length === 0 ? (
          <div className="space-y-6 pb-6">
            {/* Khi chưa có tin nhắn: đưa ô nhập lên ngay trên đầu để thao tác tức thì */}
            {inputBar}

            <div className="space-y-4">
              <div className="text-lg sm:text-[1.1875rem] font-semibold text-[var(--r-ink-2)]">
                Hoặc chọn nhanh một tình huống mẫu để kiểm thử:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {SAMPLE_SCENARIOS.map((sc, idx) => {
                  const tagColor =
                    sc.tone === "danger"
                      ? "var(--r-danger)"
                      : sc.tone === "warn"
                      ? "var(--r-warn)"
                      : "var(--r-safe)";
                  const tagBg =
                    sc.tone === "danger"
                      ? "var(--r-danger-soft)"
                      : sc.tone === "warn"
                      ? "var(--r-warn-soft)"
                      : "var(--r-safe-soft)";
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => submitAnalysis(sc.text)}
                      className="ribbon-panel text-left p-5 space-y-3 cursor-pointer transition-colors hover:bg-[var(--r-paper-3)] hover:border-[var(--r-rule-2)]"
                    >
                      <div className="flex items-start justify-between gap-2.5">
                        <span className="font-semibold text-lg sm:text-[1.1875rem] text-[var(--r-ink)] leading-snug">
                          {sc.label}
                        </span>
                        <span
                          className="text-[0.9375rem] font-medium px-2.5 py-1 rounded flex-shrink-0"
                          style={{ backgroundColor: tagBg, color: tagColor }}
                        >
                          {sc.tag}
                        </span>
                      </div>
                      <p className="text-[1.0625rem] sm:text-lg text-[var(--r-ink-2)] line-clamp-3 leading-relaxed">
                        &ldquo;{sc.text}&rdquo;
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-5 pb-4">
            {chatMessages.map((msg, idx) => {
              const isLatestAssistant =
                msg.role === "assistant" && idx === chatMessages.length - 1;

              if (msg.role === "user") {
                return (
                  <div key={msg.id} className="flex justify-end">
                    <div
                      className="max-w-[85%] sm:max-w-[75%] rounded-lg px-4 py-3 space-y-2 border"
                      style={{
                        backgroundColor: "var(--r-user-bubble)",
                        borderColor: "var(--r-user-border)",
                      }}
                    >
                      <div className="text-base sm:text-[1.0625rem] text-[var(--r-ink)] leading-relaxed">
                        {highlightKeywords(msg.content)}
                      </div>
                      {msg.imagePreview && (
                        <img
                          src={msg.imagePreview}
                          alt="Ảnh đính kèm"
                          className="max-h-56 rounded-lg border border-[var(--r-rule-2)] object-contain"
                        />
                      )}
                      <div className="text-xs font-mono text-[var(--r-muted)] text-right">
                        {msg.timestamp}
                      </div>
                    </div>
                  </div>
                );
              }

              if (msg.error) {
                return (
                  <div
                    key={msg.id}
                    ref={isLatestAssistant ? latestResponseRef : null}
                    className="ribbon-panel p-4 text-base flex items-center gap-3"
                    style={{ borderColor: "var(--r-danger)", color: "var(--r-danger)" }}
                  >
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                    <span>{msg.error}</span>
                  </div>
                );
              }

              const res = msg.result!;
              const isHigh = res.risk_score >= 65 || res.threat_level === "Nguy cơ cao";
              const isSafe = res.risk_score < 35 && res.threat_level === "An toàn";

              return (
                <div
                  key={msg.id}
                  ref={isLatestAssistant ? latestResponseRef : null}
                  className="ribbon-panel p-5 space-y-4 scroll-mt-20 lg:scroll-mt-6"
                >
                  <div className="flex flex-col sm:flex-row items-stretch sm:items-start gap-4">
                    <RiskGauge score={res.risk_score} threatLevel={res.threat_level} />
                    <div className="flex-1 space-y-2.5 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className="inline-flex items-center gap-1.5 text-sm font-medium px-3 py-1 rounded-md"
                          style={{
                            backgroundColor: isSafe
                              ? "var(--r-safe-soft)"
                              : "var(--r-accent-soft)",
                            color: isSafe ? "var(--r-safe)" : "var(--r-accent)",
                          }}
                        >
                          {isSafe ? (
                            <ShieldCheck className="w-4 h-4" />
                          ) : (
                            <ShieldAlert className="w-4 h-4" />
                          )}
                          {res.detected_tactic}
                        </span>

                        <div className="ml-auto flex items-center gap-2.5">
                          <button
                            type="button"
                            onClick={() => handleCopyAlert(msg.id, res)}
                            className="ribbon-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium cursor-pointer"
                            title="Sao chép tóm tắt kết quả để gửi cho người thân"
                          >
                            {copiedId === msg.id ? (
                              <>
                                <Check className="w-4 h-4" style={{ color: "var(--r-safe)" }} />
                                <span>Đã chép</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-4 h-4 text-[var(--r-muted)]" />
                                <span>{isSafe ? "Sao chép kết quả" : "Sao chép cảnh báo"}</span>
                              </>
                            )}
                          </button>
                          <span className="text-xs font-mono text-[var(--r-muted)]">
                            {msg.timestamp}
                          </span>
                        </div>
                      </div>
                      <p className="text-base sm:text-[1.0625rem] text-[var(--r-ink)] leading-relaxed">
                        {res.explanation}
                      </p>
                    </div>
                  </div>

                  {res.url_analysis && res.url_analysis.warnings.length > 0 && (
                    <div
                      className="rounded-lg p-4 space-y-2 border"
                      style={{
                        backgroundColor: "var(--r-warn-soft)",
                        borderColor: "var(--r-warn)",
                      }}
                    >
                      <div
                        className="text-sm sm:text-[0.9375rem] font-semibold flex items-center gap-1.5"
                        style={{ color: "var(--r-warn)" }}
                      >
                        <Link2 className="w-4 h-4" />
                        Cảnh báo kỹ thuật về đường link và tên miền
                      </div>
                      <ul className="text-[0.9375rem] sm:text-base text-[var(--r-ink)] space-y-1.5 list-disc list-inside leading-relaxed">
                        {res.url_analysis.warnings.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div
                    className="rounded-lg p-4.5 space-y-2.5 border"
                    style={{
                      backgroundColor: isHigh
                        ? "var(--r-danger-soft)"
                        : isSafe
                        ? "var(--r-safe-soft)"
                        : "var(--r-warn-soft)",
                      borderColor: isHigh
                        ? "var(--r-danger)"
                        : isSafe
                        ? "var(--r-safe)"
                        : "var(--r-warn)",
                    }}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div
                        className="text-[0.9375rem] sm:text-base font-semibold flex items-center gap-1.5"
                        style={{
                          color: isHigh
                            ? "var(--r-danger)"
                            : isSafe
                            ? "var(--r-safe)"
                            : "var(--r-warn)",
                        }}
                      >
                        <CheckCircle2 className="w-4.5 h-4.5" />
                        {isHigh ? "Việc bạn cần làm ngay lập tức" : "Khuyến nghị an toàn"}
                      </div>
                      {isHigh && (
                        <button
                          type="button"
                          onClick={() => setEmergencyOpen(true)}
                          className="ribbon-btn-sos text-sm font-semibold px-3.5 py-1.5 cursor-pointer"
                        >
                          Mở quy trình cấp cứu 15 phút
                        </button>
                      )}
                    </div>
                    <ul className="space-y-2 text-base sm:text-[1.0625rem] text-[var(--r-ink)] leading-relaxed">
                      {res.action_recommendations.map((rec, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span style={{ color: "var(--r-accent)" }}>•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    <div
                      className={`ribbon-recessed p-4 space-y-2 ${
                        !res.matched_article ? "md:col-span-2" : ""
                      }`}
                    >
                      <div
                        className="text-sm sm:text-[0.9375rem] font-semibold flex items-center gap-1.5"
                        style={{ color: "var(--r-accent)" }}
                      >
                        <Brain className="w-4 h-4" />
                        Dấu hiệu và bẫy tâm lý
                      </div>
                      <ul className="space-y-1.5 text-[0.9375rem] sm:text-base text-[var(--r-ink-2)] leading-relaxed">
                        {res.psychological_traps.map((trap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-[var(--r-muted)]">▸</span>
                            <span>{trap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {res.matched_article && (
                      <div className="ribbon-recessed p-4 space-y-2">
                        <div className="text-sm font-medium text-[var(--r-muted)]">
                          Đối chiếu cảnh báo (RAG)
                        </div>
                        <div className="text-base font-medium text-[var(--r-ink)] leading-snug">
                          {res.matched_article.title}
                        </div>
                        <div className="text-sm text-[var(--r-muted)]">
                          Nguồn: {res.matched_article.source}
                        </div>
                        {res.matched_article.url &&
                          res.matched_article.url.startsWith("http") &&
                          !(res.matched_article.source || "").toLowerCase().includes("omni-learn") &&
                          !(res.matched_article.source || "").toLowerCase().includes("tự học") && (
                            <a
                              href={res.matched_article.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 text-sm font-medium hover:underline"
                              style={{ color: "var(--r-accent)" }}
                            >
                              Đọc bài báo gốc <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="ribbon-panel p-4 flex items-center gap-3 text-base text-[var(--r-ink-2)]">
                <Loader2 className="w-5 h-5 animate-spin" style={{ color: "var(--r-accent)" }} />
                <span>Đang phân tích URL, đối soát kho RAG và thẩm định bẫy tâm lý...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Khi đã có hội thoại mới ghim khung nhập liệu xuống đáy */}
      {chatMessages.length > 0 && (
        <div className="sticky bottom-0 z-20 bg-[var(--r-paper)] pt-2 pb-3">
          {inputBar}
        </div>
      )}
    </div>
  );
}
