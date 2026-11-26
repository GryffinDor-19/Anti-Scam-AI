"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  UploadCloud,
  ShieldAlert,
  ShieldCheck,
  ScanEye,
  Cpu,
  AlertTriangle,
  Loader2,
  FileImage,
  Maximize2,
  X,
} from "lucide-react";
import { useAppContext } from "@/context/AppContext";
import { API_BASE, analyzeFakeBillApi, FakeBillResult } from "@/lib/api";

type BillMode = "fake" | "real" | "custom";

export default function FakeBillPage() {
  const { geminiApiKey } = useAppContext();
  const [mode, setMode] = useState<BillMode>("fake");
  const [previewUrl, setPreviewUrl] = useState<string>(`${API_BASE}/api/fake-bill/sample/fake`);
  const [result, setResult] = useState<FakeBillResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [zoomOpen, setZoomOpen] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const runSample = async (sample: "fake" | "real") => {
    setMode(sample);
    setPreviewUrl(`${API_BASE}/api/fake-bill/sample/${sample}`);
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeFakeBillApi({ sampleType: sample, apiKey: geminiApiKey });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể giám định mẫu biên lai.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    setMode("custom");
    setPreviewUrl(URL.createObjectURL(file));
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeFakeBillApi({ image: file, apiKey: geminiApiKey });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi khi phân tích ảnh tải lên.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSample("fake");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-5">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-[var(--r-rule)]">
        <div>
          <h1 className="text-2xl sm:text-[1.75rem] font-semibold tracking-tight text-[var(--r-ink)] leading-tight">
            Kiểm tra biên lai chuyển khoản
          </h1>
          <p className="text-sm text-[var(--r-ink-2)] mt-1">
            Kiểm tra 2 lớp: phông chữ, bố cục ngân hàng và cấu trúc pixel, metadata, chữ ký AI (C2PA)
          </p>
        </div>

        <div className="ribbon-recessed inline-flex items-center gap-1 p-1 self-start md:self-auto flex-shrink-0">
          <button
            type="button"
            onClick={() => runSample("fake")}
            className={`px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap cursor-pointer transition-colors ${
              mode === "fake"
                ? "ribbon-part text-[var(--r-accent)] font-semibold"
                : "text-[var(--r-ink-2)] hover:text-[var(--r-ink)]"
            }`}
          >
            Mẫu bill giả
          </button>
          <button
            type="button"
            onClick={() => runSample("real")}
            className={`px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap cursor-pointer transition-colors ${
              mode === "real"
                ? "ribbon-part text-[var(--r-accent)] font-semibold"
                : "text-[var(--r-ink-2)] hover:text-[var(--r-ink)]"
            }`}
          >
            Mẫu bill thật
          </button>
        </div>
      </div>

      {/* Khu vực kéo thả ảnh */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const file = e.dataTransfer.files?.[0];
          if (file) handleUpload(file);
        }}
        className="ribbon-recessed p-5 transition cursor-pointer flex flex-col sm:flex-row items-center justify-between gap-4 border-dashed hover:border-[var(--r-accent)]"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleUpload(f);
          }}
          className="hidden"
        />
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl ribbon-part flex items-center justify-center flex-shrink-0">
            <UploadCloud className="w-5 h-5" style={{ color: "var(--r-accent)" }} />
          </div>
          <div>
            <div className="font-medium text-sm text-[var(--r-ink)]">
              Tải ảnh biên lai của riêng bạn để AI giám định
            </div>
            <div className="text-xs text-[var(--r-muted)] mt-0.5">
              Kéo thả hoặc chọn tệp PNG, JPG — ảnh được xử lý tức thì và xóa ngay sau khi phân tích
            </div>
          </div>
        </div>
        <span className="ribbon-btn-accent px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap">
          Chọn ảnh từ máy
        </span>
      </div>

      {error && (
        <div
          className="ribbon-panel p-4 text-sm flex items-center gap-2.5"
          style={{ borderColor: "var(--r-danger)", color: "var(--r-danger)" }}
        >
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        <div className="lg:col-span-5 ribbon-panel p-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-medium text-[var(--r-ink-2)]">
            <span className="flex items-center gap-1.5">
              <FileImage className="w-4 h-4" style={{ color: "var(--r-accent)" }} />
              Ảnh biên lai đang giám định
            </span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[11px] text-[var(--r-muted)]">
                {mode === "fake" ? "Demo giả" : mode === "real" ? "Demo thật" : "Ảnh tải lên"}
              </span>
              <button
                type="button"
                onClick={() => setZoomOpen(true)}
                className="ribbon-btn inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium cursor-pointer"
                title="Phóng to ảnh biên lai"
              >
                <Maximize2 className="w-3 h-3" />
                <span>Phóng to</span>
              </button>
            </div>
          </div>
          <div
            onClick={() => setZoomOpen(true)}
            className="ribbon-recessed overflow-hidden flex items-center justify-center min-h-[340px] p-2 cursor-zoom-in"
            title="Bấm để phóng to ảnh"
          >
            <img
              src={previewUrl}
              alt="Ảnh biên lai chuyển khoản"
              className="max-h-[480px] w-full object-contain rounded-lg"
            />
          </div>
        </div>

        <div className="lg:col-span-7 space-y-4">
          {loading ? (
            <div className="ribbon-panel p-10 flex flex-col items-center justify-center gap-3 text-[var(--r-ink-2)]">
              <Loader2 className="w-7 h-7 animate-spin" style={{ color: "var(--r-accent)" }} />
              <div className="text-sm font-medium">Đang chạy giám định pháp y số 2 lớp...</div>
            </div>
          ) : result ? (
            <>
              <div
                className="ribbon-panel p-5 space-y-3 border-2"
                style={{
                  borderColor: result.is_fake ? "var(--r-danger)" : "var(--r-safe)",
                }}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    {result.is_fake ? (
                      <ShieldAlert className="w-5 h-5" style={{ color: "var(--r-danger)" }} />
                    ) : (
                      <ShieldCheck className="w-5 h-5" style={{ color: "var(--r-safe)" }} />
                    )}
                    <h2
                      className="text-base font-semibold"
                      style={{ color: result.is_fake ? "var(--r-danger)" : "var(--r-safe)" }}
                    >
                      {result.is_fake
                        ? "Biên lai có dấu hiệu làm giả"
                        : "Biên lai có vẻ hợp lệ"}
                    </h2>
                  </div>
                  <span
                    className="px-2.5 py-1 rounded-md text-xs font-mono font-semibold"
                    style={{
                      backgroundColor: result.is_fake
                        ? "var(--r-danger-soft)"
                        : "var(--r-safe-soft)",
                      color: result.is_fake ? "var(--r-danger)" : "var(--r-safe)",
                    }}
                  >
                    Độ tin cậy: {result.confidence_score ?? 85}%
                  </span>
                </div>

                <p className="text-sm text-[var(--r-ink)] leading-relaxed">{result.conclusion}</p>

                {result.suspicious_points && result.suspicious_points.length > 0 && (
                  <div className="pt-2.5 border-t border-[var(--r-rule)] space-y-1.5">
                    <div
                      className="text-xs font-semibold"
                      style={{ color: "var(--r-danger)" }}
                    >
                      Điểm bất thường phát hiện:
                    </div>
                    <ul className="space-y-1 text-xs sm:text-sm text-[var(--r-ink-2)]">
                      {result.suspicious_points.map((pt, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span style={{ color: "var(--r-danger)" }}>•</span>
                          <span>{pt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="ribbon-panel p-4 space-y-2">
                  <div
                    className="text-xs font-semibold flex items-center gap-1.5"
                    style={{ color: "var(--r-accent)" }}
                  >
                    <ScanEye className="w-4 h-4" />
                    Lớp 1: Thị giác và phông chữ
                  </div>
                  <ul className="space-y-1.5 text-xs sm:text-sm text-[var(--r-ink-2)]">
                    {(result.layer_1_typography || ["Đã kiểm tra bố cục, phông chữ và logo ngân hàng."]).map(
                      (item, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-[var(--r-muted)]">▸</span>
                          <span>{item}</span>
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div className="ribbon-panel p-4 space-y-2">
                  <div
                    className="text-xs font-semibold flex items-center gap-1.5"
                    style={{ color: "var(--r-accent)" }}
                  >
                    <Cpu className="w-4 h-4" />
                    Lớp 2: Pixel, ELA và metadata
                  </div>
                  <ul className="space-y-1.5 text-xs sm:text-sm text-[var(--r-ink-2)]">
                    {(result.layer_2_pixel_forensics || ["Đã quét chữ ký tệp và chỉ số nhiễu cạnh."]).map(
                      (item, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-[var(--r-muted)]">▸</span>
                          <span>{item}</span>
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </div>

              {result.technical_metadata && (
                <div className="ribbon-recessed p-4 space-y-2.5">
                  <div className="text-xs font-medium text-[var(--r-muted)]">
                    Thông số kỹ thuật tệp ảnh
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div className="p-2.5 rounded-lg bg-[var(--r-paper-2)] border border-[var(--r-rule)]">
                      <div className="text-[var(--r-muted)]">Định dạng</div>
                      <div className="font-mono font-medium text-[var(--r-ink)] mt-0.5">
                        {result.technical_metadata.format || "N/A"}
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[var(--r-paper-2)] border border-[var(--r-rule)]">
                      <div className="text-[var(--r-muted)]">Độ phân giải</div>
                      <div className="font-mono font-medium text-[var(--r-ink)] mt-0.5">
                        {result.technical_metadata.resolution || "N/A"}
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[var(--r-paper-2)] border border-[var(--r-rule)]">
                      <div className="text-[var(--r-muted)]">Dung lượng</div>
                      <div className="font-mono font-medium text-[var(--r-ink)] mt-0.5">
                        {result.technical_metadata.file_size_kb ?? 0} KB
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[var(--r-paper-2)] border border-[var(--r-rule)]">
                      <div className="text-[var(--r-muted)]">Chữ ký phần mềm</div>
                      <div className="font-mono font-medium text-[var(--r-ink)] mt-0.5 truncate">
                        {result.technical_metadata.software_signatures?.length
                          ? result.technical_metadata.software_signatures[0]
                          : "Không phát hiện"}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>

      {/* Modal phóng to ảnh biên lai (Lightbox) */}
      {zoomOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
          onClick={() => setZoomOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Xem ảnh biên lai phóng to"
        >
          <div
            className="relative max-w-4xl max-h-[92vh] w-full flex flex-col items-center"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setZoomOpen(false)}
              className="self-end mb-2 px-3 py-1.5 rounded-md bg-white/15 hover:bg-white/25 text-white text-xs font-medium inline-flex items-center gap-1.5 cursor-pointer"
            >
              <X className="w-4 h-4" />
              Đóng
            </button>
            <img
              src={previewUrl}
              alt="Ảnh biên lai phóng to"
              className="max-h-[84vh] max-w-full object-contain rounded-lg border border-white/20"
            />
          </div>
        </div>
      )}
    </div>
  );
}
