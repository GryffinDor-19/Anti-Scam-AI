"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { AnalyzeResult, fetchHealth } from "@/lib/api";

export type FontScaleLevel = "115" | "130" | "145";
export type ColorTheme = "dark" | "light";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  imagePreview?: string;
  result?: AnalyzeResult;
  error?: string;
  timestamp: string;
}

interface AppContextValue {
  theme: ColorTheme;
  setTheme: (val: ColorTheme) => void;
  toggleTheme: () => void;
  elderlyMode: boolean;
  setElderlyMode: (val: boolean) => void;
  fontScale: FontScaleLevel;
  setFontScale: (val: FontScaleLevel) => void;
  geminiApiKey: string;
  setGeminiApiKey: (val: string) => void;
  emergencyOpen: boolean;
  setEmergencyOpen: (val: boolean) => void;
  apiModalOpen: boolean;
  setApiModalOpen: (val: boolean) => void;
  backendOnline: boolean;
  hasEnvKey: boolean;
  chatMessages: ChatMessage[];
  setChatMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  clearChatMessages: () => void;
}

const AppContext = createContext<AppContextValue | null>(null);
const THEME_STORAGE_KEY = "lachanso_theme";
const CHAT_STORAGE_KEY = "lachanso_chat_history";

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ColorTheme>("dark");
  const [elderlyMode, setElderlyModeState] = useState(false);
  const [fontScale, setFontScaleState] = useState<FontScaleLevel>("130");
  const [geminiApiKey, setGeminiApiKeyState] = useState("");
  const [emergencyOpen, setEmergencyOpen] = useState(false);
  const [apiModalOpen, setApiModalOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);
  const [hasEnvKey, setHasEnvKey] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme === "dark" || savedTheme === "light") {
        setThemeState(savedTheme);
        document.documentElement.setAttribute("data-theme", savedTheme);
      } else {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        const sysTheme: ColorTheme = prefersDark ? "dark" : "light";
        setThemeState(sysTheme);
        document.documentElement.setAttribute("data-theme", sysTheme);
      }

      const savedElderly = localStorage.getItem("antiscam_elderly_mode");
      const savedScale = localStorage.getItem("antiscam_font_scale") as FontScaleLevel | null;
      const savedKey = localStorage.getItem("antiscam_gemini_key");
      if (savedElderly === "true") setElderlyModeState(true);
      if (savedScale && ["115", "130", "145"].includes(savedScale)) {
        setFontScaleState(savedScale);
      }
      if (savedKey) setGeminiApiKeyState(savedKey);

      const savedChat = sessionStorage.getItem(CHAT_STORAGE_KEY);
      if (savedChat) {
        const parsed = JSON.parse(savedChat);
        if (Array.isArray(parsed)) setChatMessages(parsed);
      }
    } catch {
      // ignore
    }

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handleSystemChange = (e: MediaQueryListEvent) => {
      try {
        if (!localStorage.getItem(THEME_STORAGE_KEY)) {
          const next: ColorTheme = e.matches ? "dark" : "light";
          setThemeState(next);
          document.documentElement.setAttribute("data-theme", next);
        }
      } catch {
        // ignore
      }
    };
    mq.addEventListener("change", handleSystemChange);

    fetchHealth()
      .then((res) => {
        setBackendOnline(res.status === "ok");
        setHasEnvKey(Boolean(res.has_env_gemini_key));
      })
      .catch(() => {
        setBackendOnline(false);
      });

    return () => mq.removeEventListener("change", handleSystemChange);
  }, []);

  // Lưu lịch sử chat phiên làm việc vào sessionStorage (không mất khi chuyển trang / F5)
  useEffect(() => {
    try {
      const serializable = chatMessages.map(({ imagePreview: _img, ...rest }) => rest);
      if (serializable.length > 0) {
        sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(serializable));
      } else {
        sessionStorage.removeItem(CHAT_STORAGE_KEY);
      }
    } catch {
      // ignore
    }
  }, [chatMessages]);

  useEffect(() => {
    const html = document.documentElement;
    if (elderlyMode) {
      html.style.fontSize = `${fontScale}%`;
      html.setAttribute("data-elderly", "true");
    } else {
      html.style.fontSize = "100%";
      html.removeAttribute("data-elderly");
    }
  }, [elderlyMode, fontScale]);

  const setTheme = (val: ColorTheme) => {
    setThemeState(val);
    document.documentElement.setAttribute("data-theme", val);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, val);
    } catch {
      // ignore
    }
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const setElderlyMode = (val: boolean) => {
    setElderlyModeState(val);
    try {
      localStorage.setItem("antiscam_elderly_mode", String(val));
    } catch {
      // ignore
    }
  };

  const setFontScale = (val: FontScaleLevel) => {
    setFontScaleState(val);
    try {
      localStorage.setItem("antiscam_font_scale", val);
    } catch {
      // ignore
    }
  };

  const setGeminiApiKey = (val: string) => {
    const trimmed = val.trim();
    setGeminiApiKeyState(trimmed);
    try {
      if (trimmed) localStorage.setItem("antiscam_gemini_key", trimmed);
      else localStorage.removeItem("antiscam_gemini_key");
    } catch {
      // ignore
    }
  };

  const clearChatMessages = () => {
    setChatMessages([]);
    try {
      sessionStorage.removeItem(CHAT_STORAGE_KEY);
    } catch {
      // ignore
    }
  };

  return (
    <AppContext.Provider
      value={{
        theme,
        setTheme,
        toggleTheme,
        elderlyMode,
        setElderlyMode,
        fontScale,
        setFontScale,
        geminiApiKey,
        setGeminiApiKey,
        emergencyOpen,
        setEmergencyOpen,
        apiModalOpen,
        setApiModalOpen,
        backendOnline,
        hasEnvKey,
        chatMessages,
        setChatMessages,
        clearChatMessages,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used inside AppProvider");
  return ctx;
}
