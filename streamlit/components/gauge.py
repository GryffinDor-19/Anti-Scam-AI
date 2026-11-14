"""
Component: gauge.py
Vẽ đồng hồ đo rủi ro bán nguyệt phong cách Neon Cyber Dark HUD bằng Matplotlib.
Hỗ trợ dải màu phát sáng và góc quay động mượt mà.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge, Circle

# Cấu hình font chữ cho matplotlib
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def render_gauge_chart(score: int):
    """Vẽ đồng hồ đo rủi ro bán nguyệt phong cách Neon Cyber Dark HUD bằng Matplotlib"""
    fig, ax = plt.subplots(figsize=(5.5, 3.1), dpi=150)

    # Nền tối chuẩn Cyber Dark (#0d1527)
    dark_bg = '#0d1527'
    fig.patch.set_facecolor(dark_bg)
    ax.set_facecolor(dark_bg)

    # 1. Cung tròn nền viền xám mờ phía sau
    ax.add_patch(Wedge((0, 0), 1.04, 0, 180, color='#1e293b', width=0.36, zorder=1))

    # 2. Ba cung tròn dải màu phát sáng: Xanh (0-30), Vàng (30-70), Đỏ (70-100)
    ax.add_patch(Wedge((0, 0), 1.0, 126, 180, color='#10b981', width=0.30, zorder=2))  # Xanh An Toàn
    ax.add_patch(Wedge((0, 0), 1.0, 54, 126, color='#f59e0b', width=0.30, zorder=2))   # Vàng Hổ Phách
    ax.add_patch(Wedge((0, 0), 1.0, 0, 54, color='#ef4444', width=0.30, zorder=2))     # Đỏ Cảnh Báo

    # 3. Tính toán góc kim chỉ (0 điểm = 180 độ; 100 điểm = 0 độ)
    angle = 180.0 - (float(score) / 100.0) * 180.0
    angle = max(0.0, min(180.0, angle))
    rad = np.radians(angle)

    # 4. Kim chỉ màu trắng viền Cyan phát sáng
    needle_color = '#ef4444' if score >= 70 else ('#f59e0b' if score >= 40 else '#10b981')
    ax.annotate(
        '', xy=(0.80 * np.cos(rad), 0.80 * np.sin(rad)), xytext=(0, 0),
        arrowprops=dict(arrowstyle="wedge,tail_width=0.42", color=needle_color, lw=1.2),
        zorder=4
    )

    # Trục kim tròn tâm đồng hồ (Hiệu ứng vòng sáng)
    ax.add_patch(Circle((0, 0), 0.12, color='#1e293b', zorder=5))
    ax.add_patch(Circle((0, 0), 0.08, color=needle_color, zorder=6))
    ax.add_patch(Circle((0, 0), 0.03, color='#ffffff', zorder=7))

    # 5. Hiển thị điểm số to ở giữa phong cách Neon HUD
    ax.text(0, -0.15, f"{score}/100", ha='center', va='center', fontsize=23, fontweight='black', color=needle_color)

    # 6. Nhãn cấp độ rủi ro động dưới điểm số
    status_text = "NGUY CƠ CAO" if score >= 70 else ("ĐÁNG NGỜ" if score >= 40 else "AN TOÀN")
    ax.text(0, -0.32, f"● {status_text} ●", ha='center', va='center', fontsize=9.5, fontweight='bold', color=needle_color)

    # 7. Nhãn các mốc đo lường trên cung tròn
    ax.text(-0.85, -0.06, "0\nAn toàn", ha='center', va='top', fontsize=8.5, color='#34d399', fontweight='bold')
    ax.text(0, 1.10, "50\nĐáng ngờ", ha='center', va='bottom', fontsize=8.5, color='#fbbf24', fontweight='bold')
    ax.text(0.85, -0.06, "100\nNguy hiểm", ha='center', va='top', fontsize=8.5, color='#f87171', fontweight='bold')

    ax.set_xlim(-1.18, 1.18)
    ax.set_ylim(-0.42, 1.25)
    ax.axis('off')
    return fig
