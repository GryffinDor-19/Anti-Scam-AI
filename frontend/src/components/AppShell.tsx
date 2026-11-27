"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldAlert,
  MessageSquare,
  FileSearch,
  Gamepad2,
  BookOpen,
  Eye,
  Settings,
  Menu,
  X,
  Moon,
  Sun,
} from "lucide-react";
import { useAppContext, FontScaleLevel } from "@/context/AppContext";
import { BrandMark } from "@/components/BrandMark";
import { EmergencyDrawer } from "@/components/EmergencyDrawer";
import { ApiKeyModal } from "@/components/ApiKeyModal";

const NAV_ITEMS = [
  { href: "/", label: "Kiểm tra tin nhắn", icon: MessageSquare },
  { href: "/fake-bill", label: "Soi bill giả", icon: FileSearch },
  { href: "/game", label: "Đấu trường lừa đảo", icon: Gamepad2 },
  { href: "/library", label: "Thư viện cảnh báo", icon: BookOpen },
];

const SCALE_OPTIONS: { value: FontScaleLevel; label: string }[] = [
  { value: "115", label: "115%" },
  { value: "130", label: "130%" },
  { value: "145", label: "145%" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const {
    theme,
    toggleTheme,
    elderlyMode,
    setElderlyMode,
    fontScale,
    setFontScale,
    setEmergencyOpen,
    setApiModalOpen,
    backendOnline,
    geminiApiKey,
  } = useAppContext();

  const sidebarContent = (
    <div className="flex flex-col h-full justify-between p-4 gap-4 select-none">
      {/* Phần trên: Logo gọn + Nút SOS + Menu 4 mục đơn giản */}
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-2 px-1 pt-0.5">
          <Link
            href="/"
            className="flex items-center gap-2.5"
            onClick={() => setMobileMenuOpen(false)}
          >
            <BrandMark className="w-9 h-9 flex-shrink-0" />
            <div className="min-w-0">
              <div className="font-semibold text-base text-[var(--r-ink)] leading-tight tracking-tight">
                Lá Chắn Số
              </div>
              <div className="text-xs text-[var(--r-muted)]">
                Kiểm tra và phòng chống lừa đảo
              </div>
            </div>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-1.5 rounded-md text-[var(--r-muted)] hover:text-[var(--r-ink)]"
            aria-label="Đóng menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nút cấp cứu khẩn cấp — phẳng, rõ ràng, không gradient */}
        <button
          type="button"
          onClick={() => {
            setEmergencyOpen(true);
            setMobileMenuOpen(false);
          }}
          className="ribbon-btn-sos w-full py-2.5 px-3 font-medium text-sm flex items-center justify-center gap-2 cursor-pointer"
        >
          <ShieldAlert className="w-4 h-4 flex-shrink-0" />
          <span>Tôi lỡ bị lừa</span>
        </button>

        <div className="border-t border-[var(--r-rule)]" />

        {/* 4 Mục điều hướng dọc nổi bật rõ ràng */}
        <nav aria-label="Điều hướng chính" className="space-y-1.5">
          <div className="px-2.5 pb-1 text-xs font-medium text-[var(--r-muted)]">
            Danh mục
          </div>
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-r-md text-[14.5px] leading-snug transition-colors border-l-[3px] ${
                  isActive
                    ? "bg-[var(--r-sb-active-bg)] text-[var(--r-sb-active-ink)] font-semibold border-l-[var(--r-accent)]"
                    : "text-[var(--r-ink-2)] hover:bg-[var(--r-sb-hover)] hover:text-[var(--r-ink)] border-l-transparent font-medium"
                }`}
              >
                <Icon
                  className="w-[18px] h-[18px] flex-shrink-0"
                  style={{ color: isActive ? "var(--r-accent)" : "var(--r-muted)" }}
                  strokeWidth={1.85}
                />
                <span className="break-words">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Phần đáy: Chế độ tối/sáng + Chữ to dễ đọc + Cài đặt API + Trạng thái */}
      <div className="space-y-2.5 pt-3 border-t border-[var(--r-rule)]">
        {/* Công tắc bật/tắt Light / Dark mode */}
        <div className="p-2.5 rounded-md bg-[var(--r-paper)] border border-[var(--r-rule)] flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            {theme === "dark" ? (
              <Moon className="w-4 h-4 text-[var(--r-accent)] flex-shrink-0" />
            ) : (
              <Sun className="w-4 h-4 text-[var(--r-accent)] flex-shrink-0" />
            )}
            <span className="text-xs font-medium text-[var(--r-ink)] leading-snug">
              {theme === "dark" ? "Chế độ tối" : "Chế độ sáng"}
            </span>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={theme === "dark"}
            aria-label="Bật hoặc tắt chế độ tối"
            onClick={toggleTheme}
            className="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer flex-shrink-0"
            style={{
              backgroundColor: theme === "dark" ? "var(--r-accent)" : "var(--r-toggle-off)",
            }}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                theme === "dark" ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>

        <div className="p-2.5 rounded-md bg-[var(--r-paper)] border border-[var(--r-rule)] space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <Eye className="w-4 h-4 text-[var(--r-accent)] flex-shrink-0" />
              <span className="text-xs font-medium text-[var(--r-ink)] leading-snug">
                Chữ to, dễ đọc
              </span>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={elderlyMode}
              onClick={() => setElderlyMode(!elderlyMode)}
              className="relative inline-flex h-5 w-9 items-center rounded-full transition-colors cursor-pointer flex-shrink-0"
              style={{
                backgroundColor: elderlyMode ? "var(--r-accent)" : "var(--r-toggle-off)",
              }}
            >
              <span
                className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                  elderlyMode ? "translate-x-5" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          {elderlyMode && (
            <div className="grid grid-cols-3 gap-1 pt-0.5">
              {SCALE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setFontScale(opt.value)}
                  className={`py-1 rounded text-xs font-medium cursor-pointer border transition-colors ${
                    fontScale === opt.value
                      ? "bg-[var(--r-accent)] text-white border-[var(--r-accent)]"
                      : "bg-[var(--r-paper-2)] text-[var(--r-ink-2)] border-[var(--r-rule)] hover:bg-[var(--r-paper-3)]"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={() => setApiModalOpen(true)}
          className="ribbon-btn w-full flex items-center justify-between px-3 py-2 text-xs font-medium cursor-pointer"
        >
          <span className="flex items-center gap-2">
            <Settings className="w-3.5 h-3.5 text-[var(--r-muted)]" />
            <span>Cài đặt API key</span>
          </span>
          {geminiApiKey && (
            <span className="text-[11px] text-[var(--r-safe)] font-medium">Đã gắn</span>
          )}
        </button>

        <div className="flex items-center gap-1.5 px-1 text-[11px] text-[var(--r-muted)]">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: backendOnline ? "var(--r-safe)" : "var(--r-warn)" }}
          />
          <span>{backendOnline ? "Hệ thống sẵn sàng" : "Đang kết nối máy chủ..."}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-[var(--r-paper)] text-[var(--r-ink)]">
      {/* Sidebar Desktop nền tối sâu tách biệt */}
      <aside className="hidden lg:block w-[16.5rem] flex-shrink-0 bg-[var(--r-sidebar)] border-r border-[var(--r-rule)] sticky top-0 h-screen overflow-y-auto">
        {sidebarContent}
      </aside>

      {/* Sidebar Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/60"
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside className="relative z-10 w-[260px] max-w-[85vw] bg-[var(--r-sidebar)] border-r border-[var(--r-rule)] h-full overflow-y-auto">
            {sidebarContent}
          </aside>
        </div>
      )}

      {/* Nội dung chính bên phải */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <div className="lg:hidden sticky top-0 z-30 flex items-center justify-between gap-2 px-4 py-3 bg-[var(--r-paper-2)] border-b border-[var(--r-rule)]">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(true)}
            className="ribbon-btn inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium"
            aria-label="Mở menu"
          >
            <Menu className="w-4 h-4" />
            <span>Menu</span>
          </button>
          <span className="font-semibold text-sm text-[var(--r-ink)] flex items-center gap-2">
            <BrandMark className="w-6 h-6" />
            Lá Chắn Số
          </span>
          <button
            type="button"
            onClick={() => setEmergencyOpen(true)}
            className="ribbon-btn-sos px-3 py-1.5 text-xs font-medium"
          >
            Cấp cứu
          </button>
        </div>

        <main className="flex-1 w-full max-w-[1360px] mx-auto px-5 sm:px-8 lg:px-10 py-6">
          {children}
        </main>
      </div>

      <EmergencyDrawer />
      <ApiKeyModal />
    </div>
  );
}
