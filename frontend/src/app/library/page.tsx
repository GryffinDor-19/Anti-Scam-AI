"use client";

import React, { useEffect, useState } from "react";
import {
  Search,
  PhoneCall,
  ShieldCheck,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { fetchLibraryApi, LibraryResponse } from "@/lib/api";

export default function LibraryPage() {
  const [sourceType, setSourceType] = useState<"all" | "official" | "learned">("official");
  const [category, setCategory] = useState("Tất cả");
  const [query, setQuery] = useState("");
  const [data, setData] = useState<LibraryResponse | null>(null);
  const [expandedId, setExpandedId] = useState<string | number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      fetchLibraryApi({
        sourceType,
        category: category === "Tất cả" ? "" : category,
        q: query,
      })
        .then((res) => setData(res))
        .finally(() => setLoading(false));
    }, 150);
    return () => clearTimeout(timer);
  }, [sourceType, category, query]);

  return (
    <div className="space-y-5">
      <div className="pb-4 border-b border-[var(--r-rule)]">
        <h1 className="text-2xl sm:text-[1.75rem] font-semibold tracking-tight text-[var(--r-ink)] leading-tight">
          Thư viện cảnh báo và hotline
        </h1>
        <p className="text-sm text-[var(--r-ink-2)] mt-1">
          Kho dữ liệu cảnh báo từ Cục An toàn thông tin (Bộ TT&TT), Cục A05 (Bộ Công an) và hệ thống phòng thủ AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="ribbon-panel p-5 space-y-3">
          <div className="font-semibold text-sm flex items-center gap-2" style={{ color: "var(--r-danger)" }}>
            <PhoneCall className="w-4 h-4" />
            Tổng đài tiếp nhận phản ánh
          </div>
          <ul className="space-y-2 text-xs sm:text-sm text-[var(--r-ink-2)]">
            <li>
              • <strong className="text-[var(--r-ink)]">Tổng đài 156 (hoặc 5656):</strong> Tiếp nhận phản ánh cuộc gọi rác, tin nhắn rác, lừa đảo (miễn phí).
            </li>
            <li>
              • <strong className="text-[var(--r-ink)]">Cục An ninh mạng A05 (Bộ Công an):</strong> Hotline{" "}
              <a
                href="tel:0692348560"
                className="font-mono font-semibold underline"
                style={{ color: "var(--r-danger)" }}
              >
                069.234.8560
              </a>
            </li>
            <li>
              • <strong className="text-[var(--r-ink)]">Cổng không gian mạng quốc gia:</strong>{" "}
              <a
                href="https://canhbao.khonggianmang.vn"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
                style={{ color: "var(--r-accent)" }}
              >
                canhbao.khonggianmang.vn
              </a>
            </li>
          </ul>
        </div>

        <div className="ribbon-panel p-5 space-y-3">
          <div className="font-semibold text-sm flex items-center gap-2" style={{ color: "var(--r-safe)" }}>
            <ShieldCheck className="w-4 h-4" />
            4 nguyên tắc vàng dành cho người dân
          </div>
          <ol className="space-y-1.5 text-xs sm:text-sm text-[var(--r-ink-2)] list-decimal list-inside">
            <li>
              <strong className="text-[var(--r-ink)]">Không có công an nào làm việc qua điện thoại hay Zalo</strong> hoặc yêu cầu chuyển tiền xác minh.
            </li>
            <li>
              <strong className="text-[var(--r-ink)]">Không nhân viên ngân hàng nào được hỏi mã OTP</strong> của khách hàng.
            </li>
            <li>
              <strong className="text-[var(--r-ink)]">Không chuyển tiền khi người thân nhắn gấp</strong> nếu chưa gọi điện nghe trực tiếp giọng nói.
            </li>
            <li>
              <strong className="text-[var(--r-ink)]">Không tin việc nhẹ lương cao</strong> hay làm nhiệm vụ nạp tiền nhận hoa hồng.
            </li>
          </ol>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        <div className="ribbon-recessed inline-flex items-center gap-1 p-1">
          <button
            type="button"
            onClick={() => setSourceType("official")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition ${
              sourceType === "official"
                ? "ribbon-part text-[var(--r-ink)]"
                : "text-[var(--r-muted)] hover:text-[var(--r-ink)]"
            }`}
          >
            Bài báo chính thống ({data?.official_count ?? "..."})
          </button>
          <button
            type="button"
            onClick={() => setSourceType("learned")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition ${
              sourceType === "learned"
                ? "ribbon-part text-[var(--r-ink)]"
                : "text-[var(--r-muted)] hover:text-[var(--r-ink)]"
            }`}
          >
            AI tự học ({data?.learned_count ?? "..."})
          </button>
          <button
            type="button"
            onClick={() => setSourceType("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition ${
              sourceType === "all"
                ? "ribbon-part text-[var(--r-ink)]"
                : "text-[var(--r-muted)] hover:text-[var(--r-ink)]"
            }`}
          >
            Tất cả ({data?.total ?? "..."})
          </button>
        </div>

        <span className="text-xs font-mono text-[var(--r-muted)]">
          Đang hiển thị <strong className="text-[var(--r-ink)]">{data?.filtered_count ?? 0}</strong> cảnh báo
        </span>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-[var(--r-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            id="library-search-input"
            name="q"
            aria-label="Tìm kiếm cảnh báo theo từ khóa"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm theo từ khóa (VD: công an, shopee, vneid, bill...)"
            className="ribbon-recessed w-full pl-10 pr-4 py-2.5 text-sm text-[var(--r-ink)] placeholder-[var(--r-muted)] focus:outline-none focus:border-[var(--r-accent)]"
          />
        </div>
        <select
          id="library-category-select"
          name="category"
          aria-label="Lọc theo nhóm thủ đoạn"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="ribbon-recessed px-3.5 py-2.5 text-sm text-[var(--r-ink)] focus:outline-none focus:border-[var(--r-accent)]"
        >
          <option value="Tất cả">Tất cả nhóm thủ đoạn</option>
          {(data?.categories || []).map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-10 text-sm text-[var(--r-muted)]">
          Đang tải dữ liệu cảnh báo...
        </div>
      ) : data && data.items.length === 0 ? (
        <div className="ribbon-panel p-8 text-center text-sm text-[var(--r-muted)]">
          Không tìm thấy bài cảnh báo nào khớp với bộ lọc hiện tại.
        </div>
      ) : (
        <div className="divide-y divide-[var(--r-rule)] border-t border-b border-[var(--r-rule)]">
          {(data?.items || []).map((item) => {
            const isOpen = expandedId === item.id;
            return (
              <div key={item.id}>
                <button
                  type="button"
                  onClick={() => setExpandedId(isOpen ? null : item.id)}
                  className="w-full py-4 px-2 flex items-center justify-between gap-3 text-left cursor-pointer hover:bg-[var(--r-paper-2)]/60 transition"
                >
                  <div className="min-w-0 flex-1 space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className="text-[11px] font-medium px-2 py-0.5 rounded-md"
                        style={{
                          backgroundColor: "var(--r-accent-soft)",
                          color: "var(--r-accent)",
                        }}
                      >
                        {item.category_name}
                      </span>
                      <span className="text-[11px] text-[var(--r-muted)]">{item.source}</span>
                    </div>
                    <div className="font-medium text-sm sm:text-[15px] text-[var(--r-ink)]">
                      {item.title}
                    </div>
                  </div>
                  {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-[var(--r-muted)] flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-[var(--r-muted)] flex-shrink-0" />
                  )}
                </button>

                {isOpen && (
                  <div className="px-4 pb-4 pt-3 mb-2 ribbon-recessed space-y-3">
                    <p className="text-xs sm:text-sm text-[var(--r-ink-2)] leading-relaxed">
                      {item.summary}
                    </p>
                    {item.keywords && item.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {item.keywords.map((kw, i) => (
                          <span
                            key={i}
                            className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-[var(--r-paper-2)] border border-[var(--r-rule)] text-[var(--r-ink-2)]"
                          >
                            #{kw}
                          </span>
                        ))}
                      </div>
                    )}
                    {item.url && item.url.startsWith("http") && item.source_type === "official" && (
                      <div>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ribbon-btn inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-medium"
                        >
                          Mở bài báo gốc chính thống
                          <ExternalLink className="w-3.5 h-3.5" style={{ color: "var(--r-accent)" }} />
                        </a>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
