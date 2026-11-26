import React from "react";

interface BrandMarkProps {
  className?: string;
}

/**
 * Logo mới cho "Lá Chắn Số" (tông Furrow):
 * Nền đen than ấm (#221F1C) nổi bật trên nền giấy ngà,
 * bên trong là chiếc khiên 2 mảng (trắng ngà + cam đất #E56B24)
 * kèm dấu tích xác minh rõ nét, tinh gọn và bắt mắt.
 */
export function BrandMark({ className = "w-9 h-9" }: BrandMarkProps) {
  return (
    <svg
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <rect
        x="0.75"
        y="0.75"
        width="34.5"
        height="34.5"
        rx="7.5"
        fill="#24211E"
        stroke="#4A443D"
        strokeWidth="1.5"
      />
      {/* Nửa trái lá chắn: trắng ngà */}
      <path
        d="M18 6.5L8.5 10.2V17.4C8.5 23.1 12.6 27.6 18 29.4V6.5Z"
        fill="#FDFCF9"
      />
      {/* Nửa phải lá chắn: cam đất Furrow */}
      <path
        d="M18 6.5L27.5 10.2V17.4C27.5 23.1 23.4 27.6 18 29.4V6.5Z"
        fill="#E56B24"
      />
      {/* Dấu tích xác minh cắt ngang trung tâm */}
      <path
        d="M13.6 18.2L16.6 21.2L22.6 14.8"
        stroke="#221F1C"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
