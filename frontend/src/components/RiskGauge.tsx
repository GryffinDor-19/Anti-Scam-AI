"use client";

import React from "react";

interface RiskGaugeProps {
  score: number;
  threatLevel: string;
}

export function RiskGauge({ score, threatLevel }: RiskGaugeProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const radius = 44;
  const circumference = Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;

  const isHigh = clamped >= 65 || threatLevel === "Nguy cơ cao";
  const isMedium = !isHigh && (clamped >= 35 || threatLevel === "Đáng ngờ");

  const strokeColor = isHigh
    ? "var(--r-danger)"
    : isMedium
    ? "var(--r-warn)"
    : "var(--r-safe)";
  const badgeBg = isHigh
    ? "var(--r-danger-soft)"
    : isMedium
    ? "var(--r-warn-soft)"
    : "var(--r-safe-soft)";

  return (
    <div className="ribbon-recessed flex flex-col items-center justify-center p-3.5 min-w-[144px]">
      <div className="relative w-28 h-16 flex items-end justify-center">
        <svg viewBox="0 0 100 56" className="w-full h-full overflow-visible">
          <path
            d="M 6 50 A 44 44 0 0 1 94 50"
            fill="none"
            stroke="var(--r-gauge-track)"
            strokeWidth="8"
            strokeLinecap="round"
          />
          <path
            d="M 6 50 A 44 44 0 0 1 94 50"
            fill="none"
            stroke={strokeColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute bottom-0 text-center">
          <div className="text-xl font-semibold text-[var(--r-ink)] leading-none tabular-nums">
            {clamped}
            <span className="text-xs text-[var(--r-muted)] font-normal">/100</span>
          </div>
        </div>
      </div>
      <span
        className="mt-2 px-2.5 py-0.5 rounded text-[11px] font-semibold"
        style={{ backgroundColor: badgeBg, color: strokeColor }}
      >
        {threatLevel}
      </span>
    </div>
  );
}
