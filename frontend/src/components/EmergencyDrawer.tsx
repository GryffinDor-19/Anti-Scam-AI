"use client";

import React, { useEffect, useState } from "react";
import { X, PhoneCall, ShieldAlert, ExternalLink } from "lucide-react";
import { useAppContext } from "@/context/AppContext";
import { EmergencyPayload, fetchEmergencyApi } from "@/lib/api";

function toSentenceCaseHeading(text: string): string {
  if (!text) return "";
  if (text === text.toUpperCase()) {
    const lower = text.toLowerCase();
    return lower.charAt(0).toUpperCase() + lower.slice(1);
  }
  return text;
}

const FALLBACK_EMERGENCY: EmergencyPayload = {
  title: "Quy trình cấp cứu thời điểm vàng (dưới 15 phút)",
  subtitle: "Hãy bình tĩnh và làm đúng theo 3 bước sau để bảo toàn tài sản:",
  checklist: [
    {
      step: "Bước 1: Cắt đứt kết nối ngay lập tức",
      icon: "1",
      action:
        "Nếu vừa bấm vào link lạ hoặc tải file .apk: Hãy bật ngay chế độ máy bay (Airplane Mode) hoặc tắt nguồn điện thoại để ngắt kết nối mạng. Kẻ gian sẽ không thể can thiệp vào máy để đọc mã OTP ngân hàng.",
      priority: "Khẩn cấp nhất trong 60 giây đầu",
    },
    {
      step: "Bước 2: Gọi tổng đài ngân hàng phong tỏa dòng tiền",
      icon: "2",
      action:
        "Bấm gọi ngay cho hotline ngân hàng của bạn bên dưới. Nói rõ với tổng đài viên: 'Tôi vừa bị lừa đảo chuyển tiền/lộ tài khoản, yêu cầu khóa thẻ và tạm dừng mọi giao dịch khẩn cấp'.",
      priority: "Thời điểm vàng: dưới 15 phút",
    },
    {
      step: "Bước 3: Chụp màn hình lưu giữ 3 bằng chứng",
      icon: "3",
      action:
        "Trước khi kẻ gian kịp thu hồi hoặc xóa đoạn chat, hãy chụp ngay: (1) Số tài khoản và tên người nhận tiền, (2) Mã giao dịch chuyển khoản ngân hàng, (3) Toàn bộ tin nhắn đe dọa hoặc dụ dỗ.",
      priority: "Dùng để nộp đơn tố giác cho cơ quan công an",
    },
  ],
  hotlines: [
    { bank: "Vietcombank", hotline: "1900545413", desc: "Bấm phím 1 để khóa thẻ khẩn cấp" },
    { bank: "Techcombank", hotline: "1800588822", desc: "Tổng đài 24/7 khóa tài khoản tức thì" },
    { bank: "MB Bank", hotline: "1900545426", desc: "Hỗ trợ phong tỏa app và thẻ ngay lập tức" },
    { bank: "VietinBank", hotline: "1900558868", desc: "Khóa dịch vụ ngân hàng điện tử khẩn" },
    { bank: "BIDV", hotline: "19009247", desc: "Hỗ trợ khách hàng và xử lý gian lận 24/7" },
    { bank: "VPBank", hotline: "1900545415", desc: "Tự động khóa thẻ qua tổng đài IVR" },
    { bank: "Agribank", hotline: "1900558818", desc: "Trung tâm chăm sóc khách hàng khẩn cấp" },
  ],
  police: {
    name: "Cục An ninh mạng A05 (Bộ Công an)",
    hotline: "0692348560",
    display: "069.234.8560",
    desc: "Tố giác tội phạm lừa đảo công nghệ cao 24/7",
  },
  spam_portal: {
    name: "Tổng đài 156 / 5656",
    hotline: "156",
    desc: "Phản ánh cuộc gọi rác, tin nhắn rác & lừa đảo (miễn phí)",
    portal_url: "https://canhbao.khonggianmang.vn",
  },
};

function renderHighlightedAction(action: string) {
  const cleaned = action.replace(/`([^`]+)`/g, "$1");
  const phrases = [
    "BẬT NGAY CHẾ ĐỘ MÁY BAY",
    "TẮT NGUỒN ĐIỆN THOẠI",
    "bật ngay chế độ máy bay",
    "tắt nguồn điện thoại",
    "khóa thẻ và tạm dừng mọi giao dịch khẩn cấp",
    "chụp ngay",
  ];
  const regex = new RegExp(`(${phrases.join("|")})`, "g");
  const parts = cleaned.split(regex);
  return parts.map((part, idx) =>
    phrases.includes(part) ? (
      <strong
        key={idx}
        className="px-1.5 py-0.5 rounded font-semibold"
        style={{ backgroundColor: "var(--r-em-hl-bg)", color: "var(--r-em-hl-ink)" }}
      >
        {part}
      </strong>
    ) : (
      <React.Fragment key={idx}>{part}</React.Fragment>
    )
  );
}

export function EmergencyDrawer() {
  const { emergencyOpen, setEmergencyOpen } = useAppContext();
  const [data, setData] = useState<EmergencyPayload>(FALLBACK_EMERGENCY);

  useEffect(() => {
    if (!emergencyOpen) return;
    fetchEmergencyApi()
      .then((res) => setData(res))
      .catch(() => setData(FALLBACK_EMERGENCY));
  }, [emergencyOpen]);

  if (!emergencyOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 sm:p-5 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-label="Quy trình cấp cứu thời điểm vàng"
    >
      <div
        className="w-full max-w-5xl bg-[var(--r-paper)] border rounded-lg overflow-hidden my-auto max-h-[92vh] flex flex-col"
        style={{ borderColor: "var(--r-em-border)" }}
      >
        {/* Header đỏ trầm/nhạt tự động thích ứng Light/Dark */}
        <div
          className="border-b px-5 py-4 flex items-start justify-between gap-4"
          style={{ backgroundColor: "var(--r-em-header-bg)", borderColor: "var(--r-em-border)" }}
        >
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-md bg-[#c92a2a] text-white flex items-center justify-center flex-shrink-0 mt-0.5">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2
                className="text-base sm:text-lg font-semibold"
                style={{ color: "var(--r-em-title)" }}
              >
                {toSentenceCaseHeading(data.title)}
              </h2>
              <p className="text-xs sm:text-sm mt-0.5" style={{ color: "var(--r-em-sub)" }}>
                {data.subtitle}
              </p>
            </div>
          </div>
          <button
            onClick={() => setEmergencyOpen(false)}
            className="p-1.5 rounded-md border cursor-pointer flex-shrink-0"
            style={{
              backgroundColor: "var(--r-em-badge-bg)",
              borderColor: "var(--r-em-badge-border)",
              color: "var(--r-em-title)",
            }}
            aria-label="Đóng bảng cấp cứu"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nội dung 2 cột thích ứng Light/Dark */}
        <div className="p-5 overflow-y-auto grid grid-cols-1 lg:grid-cols-12 gap-5 bg-[var(--r-paper)]">
          <div className="lg:col-span-7 space-y-3">
            <div className="text-sm font-semibold text-[var(--r-ink)]">
              3 việc cần làm ngay lập tức
            </div>

            {data.checklist.map((item, idx) => (
              <div
                key={idx}
                className="rounded-md bg-[var(--r-paper-2)] border border-[var(--r-rule)] p-4 space-y-2"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div
                    className="font-semibold text-[14.5px]"
                    style={{ color: "var(--r-em-step)" }}
                  >
                    {toSentenceCaseHeading(item.step)}
                  </div>
                  <span
                    className="text-xs font-medium px-2 py-0.5 rounded border"
                    style={{
                      backgroundColor: "var(--r-em-badge-bg)",
                      borderColor: "var(--r-em-badge-border)",
                      color: "var(--r-em-badge-ink)",
                    }}
                  >
                    {item.priority}
                  </span>
                </div>
                <p className="text-sm text-[var(--r-ink-2)] leading-relaxed">
                  {renderHighlightedAction(item.action)}
                </p>
              </div>
            ))}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div
                className="rounded-md border p-3.5 flex flex-col justify-between gap-2"
                style={{ backgroundColor: "var(--r-em-police-bg)", borderColor: "var(--r-em-border)" }}
              >
                <div>
                  <div className="text-xs font-medium" style={{ color: "var(--r-em-step)" }}>
                    Cơ quan công an
                  </div>
                  <div className="text-sm font-semibold text-[var(--r-ink)] mt-0.5">
                    {data.police.name}
                  </div>
                  <div className="text-xs text-[var(--r-ink-2)] mt-0.5">{data.police.desc}</div>
                </div>
                <a
                  href={`tel:${data.police.hotline}`}
                  className="ribbon-btn-sos inline-flex items-center justify-center gap-1.5 w-full py-2 px-3 text-xs font-semibold"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  Gọi ngay {data.police.display}
                </a>
              </div>

              <div className="rounded-md bg-[var(--r-paper-2)] border border-[var(--r-rule)] p-3.5 flex flex-col justify-between gap-2">
                <div>
                  <div className="text-xs font-medium text-[var(--r-accent)]">Phản ánh lừa đảo</div>
                  <div className="text-sm font-semibold text-[var(--r-ink)] mt-0.5">
                    {data.spam_portal.name}
                  </div>
                  <div className="text-xs text-[var(--r-ink-2)] mt-0.5">
                    {data.spam_portal.desc}
                  </div>
                </div>
                <a
                  href={data.spam_portal.portal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ribbon-btn inline-flex items-center justify-center gap-1.5 w-full py-2 px-3 text-xs font-medium"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-[var(--r-accent)]" />
                  Cổng không gian mạng quốc gia
                </a>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 space-y-3">
            <div className="text-sm font-semibold text-[var(--r-ink)]">
              Hotline khóa tài khoản ngân hàng
            </div>
            <p className="text-xs text-[var(--r-muted)]">
              Bấm gọi trực tiếp để tổng đài phong tỏa thẻ và tạm dừng giao dịch:
            </p>

            <div className="space-y-2">
              {data.hotlines.map((bank) => (
                <div
                  key={bank.bank}
                  className="rounded-md bg-[var(--r-paper-2)] border border-[var(--r-rule)] p-3 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <div className="font-semibold text-sm text-[var(--r-ink)] flex items-center gap-2">
                      <span>{bank.bank}</span>
                      <span className="font-mono text-xs px-1.5 py-0.5 rounded bg-[var(--r-accent-soft)] text-[var(--r-accent)]">
                        {bank.hotline}
                      </span>
                    </div>
                    <div className="text-xs text-[var(--r-muted)] mt-0.5 truncate">{bank.desc}</div>
                  </div>
                  <a
                    href={`tel:${bank.hotline}`}
                    className="ribbon-btn-accent inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold flex-shrink-0"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    Gọi
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
