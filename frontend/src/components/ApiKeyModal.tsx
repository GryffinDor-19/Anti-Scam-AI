"use client";

import React, { useState, useEffect } from "react";
import { X, KeyRound, Eye, EyeOff, CheckCircle2, Trash2 } from "lucide-react";
import { useAppContext } from "@/context/AppContext";

export function ApiKeyModal() {
  const { apiModalOpen, setApiModalOpen, geminiApiKey, setGeminiApiKey, hasEnvKey } =
    useAppContext();
  const [inputVal, setInputVal] = useState(geminiApiKey);
  const [showKey, setShowKey] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  useEffect(() => {
    setInputVal(geminiApiKey);
    setSavedNotice(false);
  }, [apiModalOpen, geminiApiKey]);

  if (!apiModalOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setGeminiApiKey(inputVal);
    setSavedNotice(true);
    setTimeout(() => setApiModalOpen(false), 600);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Cài đặt nâng cao API Key"
    >
      <div className="ribbon-panel w-full max-w-md overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--r-rule)] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl ribbon-part flex items-center justify-center">
              <KeyRound className="w-4 h-4" style={{ color: "var(--r-accent)" }} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[var(--r-ink)]">
                Cài đặt nâng cao (API key)
              </h3>
              <p className="text-xs text-[var(--r-muted)]">
                Kết nối trực tiếp mô hình Google Gemini AI
              </p>
            </div>
          </div>
          <button
            onClick={() => setApiModalOpen(false)}
            className="p-1.5 rounded-lg text-[var(--r-muted)] hover:text-[var(--r-ink)] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="p-5 space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[var(--r-ink-2)]">
              Khóa Google Gemini API (tùy chọn)
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="AIzaSy..."
                className="ribbon-recessed w-full pl-3.5 pr-10 py-2.5 text-sm text-[var(--r-ink)] placeholder-[var(--r-muted)] focus:outline-none focus:border-[var(--r-accent)]"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-[var(--r-muted)] hover:text-[var(--r-ink)] cursor-pointer"
                aria-label="Hiện hoặc ẩn API Key"
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-[var(--r-muted)]">
              {hasEnvKey
                ? "Máy chủ đã có sẵn GEMINI_API_KEY trong tệp .env. Bạn có thể để trống ô này."
                : "Nếu để trống, hệ thống tự động dùng bộ lọc phòng thủ đa tiêu chí & RAG cục bộ."}
            </p>
          </div>

          {savedNotice && (
            <div
              className="flex items-center gap-2 text-xs font-medium rounded-xl px-3 py-2"
              style={{ backgroundColor: "var(--r-safe-soft)", color: "var(--r-safe)" }}
            >
              <CheckCircle2 className="w-4 h-4" />
              Đã lưu cài đặt API Key thành công
            </div>
          )}

          <div className="flex items-center justify-between gap-2 pt-1">
            {geminiApiKey ? (
              <button
                type="button"
                onClick={() => {
                  setInputVal("");
                  setGeminiApiKey("");
                }}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium cursor-pointer"
                style={{ color: "var(--r-danger)" }}
              >
                <Trash2 className="w-3.5 h-3.5" />
                Xóa khóa
              </button>
            ) : (
              <div />
            )}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setApiModalOpen(false)}
                className="ribbon-btn px-3.5 py-2 rounded-xl text-xs font-medium cursor-pointer"
              >
                Đóng
              </button>
              <button
                type="submit"
                className="ribbon-btn-accent px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer"
              >
                Lưu cài đặt
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
