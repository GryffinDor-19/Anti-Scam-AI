"""
Component: gauge.py
Vẽ đồng hồ đo rủi ro bán nguyệt phong cách Neon Cyber Dark bằng Matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

# Cấu hình font chữ cho matplotlib
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def render_gauge_chart(score: int):
    """Vẽ đồng hồ đo rủi ro bán nguyệt phong cách Neon Cyber Dark bằng Matplotlib"""
    fig, ax = plt.subplots(figsize=(5.5, 2.9), dpi=150)

    # Nền tối chuẩn Cyber Space (#0d1527)
    dark_bg = '#0d1527'
    fig.patch.set_facecolor(dark_bg)
    ax.set_facecolor(dark_bg)

    # 1. Cung tròn nền xám mờ phía sau
    ax.add_patch(Wedge((0, 0), 1.02, 0, 180, color='#1e293b', width=0.34, zorder=1))

    # 2. Ba cung tròn dải màu phát sáng Neon: Xanh (0-30), Vàng (30-70), Đỏ (70-100)
    ax.add_patch(Wedge((0, 0), 1.0, 126, 180, color='#10b981', width=0.30, zorder=2))  # Xanh Neon
    ax.add_patch(Wedge((0, 0), 1.0, 54, 126, color='#f59e0b', width=0.30, zorder=2))   # Vàng Hổ Phách
    ax.add_patch(Wedge((0, 0), 1.0, 0, 54, color='#ef4444', width=0.30, zorder=2))     # Đỏ Cảnh Báo

    # 3. Tính toán góc kim chỉ (0 điểm = 180 độ; 100 điểm = 0 độ)
    angle = 180 - (float(score) / 100.0) * 180.0
    angle = max(0, min(180, angle))
    rad = np.radians(angle)

    # 4. Kim chỉ màu trắng viền xanh Cyan phát sáng
    ax.annotate(
        '', xy=(0.78 * np.cos(rad), 0.78 * np.sin(rad)), xytext=(0, 0),
        arrowprops=dict(arrowstyle="wedge,tail_width=0.45", color="#38bdf8", lw=0.8),
        zorder=4
    )
    # Trục kim tròn phát sáng
    ax.plot(0, 0, 'o', color='#38bdf8', markersize=14, zorder=5)
    ax.plot(0, 0, 'o', color='#ffffff', markersize=6, zorder=6)

    # 5. Hiển thị điểm số to ở giữa phong cách Neon HUD
    text_color = '#ef4444' if score >= 70 else ('#f59e0b' if score >= 40 else '#10b981')
    ax.text(0, -0.16, f"{score}/100", ha='center', va='center', fontsize=22, fontweight='bold', color=text_color)

    # 6. Nhãn các mức đo lường
    ax.text(-0.85, -0.06, "0\nAn toàn", ha='center', va='top', fontsize=8.5, color='#34d399', fontweight='bold')
    ax.text(0, 1.10, "50\nĐáng ngờ", ha='center', va='bottom', fontsize=8.5, color='#fbbf24', fontweight='bold')
    ax.text(0.85, -0.06, "100\nNguy hiểm", ha='center', va='top', fontsize=8.5, color='#f87171', fontweight='bold')

    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.28, 1.25)
    ax.axis('off')
    return fig
