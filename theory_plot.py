"""
Vẽ mô hình GIẢI TÍCH (kỳ vọng, không ngẫu nhiên) của kênh FSO + QBER + SKR
theo khoảng cách, kể cả ngoài dải bay thực tế. Dùng để đối chiếu với kết quả
mô phỏng (Hình 5 trong báo cáo).

Chạy:  python theory_plot.py
"""
import math
import numpy as np
import matplotlib.pyplot as plt

import channel
from post_processing import binary_entropy

# --- Phải khớp với bb84.py / channel.py / post_processing.py ---
PULSE_RATE = 1_000_000
P_DARK = 5e-5
E_OPT = 0.015
F_EC = 1.2
QBER_LIMIT = 0.11
MIN_KEY_BITS = 256
SIGMA, D_R, D_T, THETA, ETA = 0.0001, 0.2, 0.05, 0.001, 0.2   # = channel.py
MAX_FLIGHT_DIST = 2885  # m, khoảng cách lớn nhất trong 3 chuyến bay


def expected_metrics(d):
    """Giá trị kỳ vọng tại khoảng cách d: P_survival, N_sift, QBER, L (SKR)."""
    p = channel.calculate_survival_probability(d)
    p_det = p + P_DARK - p * P_DARK              # Công thức (4)
    phi = p / p_det                              # Công thức (5)
    qber = (1 - phi) * 0.5 + phi * E_OPT         # Công thức (6)
    n_sift = PULSE_RATE * p_det * 0.5            # Công thức (7)
    h = binary_entropy(qber)
    L = n_sift * (1 - (1 + F_EC) * h)            # Công thức (9)
    skr = L if (L > MIN_KEY_BITS and qber < QBER_LIMIT) else 0.0   # (10)
    return p, n_sift, qber, skr


def main():
    d = np.arange(5, 6001, 1.0)
    h_atm = np.exp(-SIGMA * d)
    h_geo = np.minimum((D_R / (D_T + THETA * d)) ** 2, 1.0)
    p_surv = np.array([channel.calculate_survival_probability(x) for x in d])
    m = np.array([expected_metrics(x) for x in d])
    qber, skr = m[:, 2] * 100, m[:, 3]

    d_skr0 = d[np.argmax((skr == 0) & (d > 150))]
    d_q11 = d[np.argmax(qber >= 11)] if (qber >= 11).any() else None

    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.4))

    # (a) các thành phần suy hao
    a.semilogy(d, np.full_like(d, ETA), '--', color='#7f7f7f', label=r'$\eta$ (hiệu suất lượng tử)')
    a.semilogy(d, h_atm, color='#2ca02c', label=r'$h_{atm}$ (khí quyển)')
    a.semilogy(d, h_geo, color='#ff7f0e', label=r'$h_{geo}$ (hình học)')
    a.semilogy(d, p_surv, color='#1f3864', lw=2.2, label=r'$P_{survival}$ (tổng)')
    a.axhline(P_DARK, color='#d62728', ls=':', lw=1.4, label=r'Dark count $p_{dc}$')
    knee = (D_R - D_T) / THETA
    a.axvline(knee, color='k', ls=':', lw=1)
    a.text(knee + 40, 1.25, f'd = {knee:.0f} m', fontsize=8)
    a.set_xlabel('Khoảng cách d (m)'); a.set_ylabel('Xác suất'); a.set_ylim(1e-5, 3)
    a.grid(alpha=.3, which='both'); a.legend(fontsize=8, loc='lower left')
    a.set_title('(a) Các thành phần suy hao kênh FSO')

    # (b) QBER và SKR kỳ vọng
    b.plot(d, qber, color='#d62728', lw=2, label='QBER lý thuyết')
    b.axhline(QBER_LIMIT * 100, color='#b8860b', ls='-.', label='Ngưỡng 11%')
    b.axvspan(0, MAX_FLIGHT_DIST, color='#cfe2f3', alpha=.5, label=f'Dải bay thực tế (≤ {MAX_FLIGHT_DIST} m)')
    b.axvline(d_skr0, color='#1f3864', ls='--', lw=1)
    b.text(d_skr0 + 40, 1, f'SKR = 0\n(d ≈ {d_skr0:.0f} m)', fontsize=8, color='#1f3864')
    if d_q11:
        b.axvline(d_q11, color='#b8860b', ls='--', lw=1)
        b.text(d_q11 + 80, 7, f'QBER = 11%\n(d ≈ {d_q11:.0f} m)', fontsize=8, color='#8a6d00')
    b.set_xlabel('Khoảng cách d (m)'); b.set_ylabel('QBER (%)', color='#d62728'); b.set_ylim(0, 16)
    b.grid(alpha=.3)
    b2 = b.twinx()
    b2.plot(d, skr, color='#1f3864', lw=2, label='SKR lý thuyết')
    b2.set_ylabel('SKR (bit/s)', color='#1f3864'); b2.set_ylim(0, 80000)
    h1, l1 = b.get_legend_handles_labels(); h2, l2 = b2.get_legend_handles_labels()
    b.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, 0.99))
    b.set_title('(b) QBER và SKR theo mô hình giải tích')

    plt.tight_layout()
    plt.savefig('qkd_theory_chart.png', dpi=200)
    print(f"[Theory] SKR kỳ vọng = 0 từ d ≈ {d_skr0:.0f} m; QBER kỳ vọng chạm 11% ở d ≈ {d_q11} m")
    print("[Theory] Đã xuất: qkd_theory_chart.png")
    plt.show()


if __name__ == "__main__":
    main()
