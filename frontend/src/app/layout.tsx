import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/context/AppContext";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "Lá Chắn Số — Hỗ trợ phòng chống lừa đảo trực tuyến",
  description:
    "Công cụ kiểm tra tin nhắn lừa đảo, đường link giả mạo, soi biên lai chuyển khoản và hướng dẫn cấp cứu giờ vàng.",
};

// Script khởi tạo sớm trước khi paint để tránh nháy sáng/tối (FOUC)
const THEME_INIT_SCRIPT = `(function(){try{var s=localStorage.getItem('lachanso_theme');var t=(s==='light'||s==='dark')?s:(window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.setAttribute('data-theme',t);}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>
        <AppProvider>
          <AppShell>{children}</AppShell>
        </AppProvider>
      </body>
    </html>
  );
}
