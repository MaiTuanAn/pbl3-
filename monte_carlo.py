"""
Monte Carlo: lặp lại mô phỏng QKD BB84 nhiều lần trên quỹ đạo bay thật để đánh
giá độ tin cậy thống kê (một lần chạy main.py chỉ là MỘT mẫu ngẫu nhiên).

Hai chế độ cho cùng một phân phối thống kê:
  * EXACT : gọi trực tiếp bb84.run_bb84_simulation + post_processing
            (mô phỏng từng bit, chậm ~10 s / chuyến / lần chạy).
  * FAST  : lấy mẫu trực tiếp từ phân phối nhị thức (số xung tới Bob, số bit
            sau sifting, số bit lỗi) -> chạy hàng nghìn lần trong vài giây.
Chế độ FAST được đối chiếu với EXACT để chứng minh hai cách tương đương.

Chạy:
  python monte_carlo.py                          # 3 file mặc định
  python monte_carlo.py --csv a.csv b.csv --exact-runs 10 --fast-runs 1000
"""
import argparse
import contextlib
import io
import json
import time

import numpy as np
import matplotlib.pyplot as plt

import trajectory
import channel
import bb84
import post_processing

# --- Phải khớp với bb84.py / post_processing.py ---
PULSE_RATE = 1_000_000
P_DARK = 5e-5
E_OPT = 0.015
QBER_LIMIT = 0.11

DEFAULT_CSVS = ["2026-11-16 16-07-29.csv", "2026-11-17 16-24-29.csv", "2026-11-17 18-42-52.csv"]
COLORS = ["#00ffff", "#ffb86c", "#ff79c6"]


def load_distances(csv_file):
    with contextlib.redirect_stdout(io.StringIO()):          # tắt log của trajectory
        path = trajectory.read_trajectory(csv_file, resample_1hz=True)
    return np.array([p["distance"] for p in path])


def run_exact(distances, runs, seed):
    """Gọi trực tiếp bb84.py + post_processing.py. Trả về qber[runs,T], skr[runs,T]."""
    np.random.seed(seed)
    qber = np.zeros((runs, len(distances)))
    skr = np.zeros((runs, len(distances)))
    for r in range(runs):
        for t, d in enumerate(distances):
            p = channel.calculate_survival_probability(d)
            sifted, q, _ = bb84.run_bb84_simulation(PULSE_RATE, p)
            res = post_processing.extract_secret_key(sifted, q)
            qber[r, t] = q
            skr[r, t] = float(res[0])
    return qber, skr


def run_fast(distances, runs, seed):
    """Lấy mẫu nhị thức, tương đương thống kê với run_exact."""
    rng = np.random.default_rng(seed)
    p = np.array([channel.calculate_survival_probability(d) for d in distances])
    p_det = p + P_DARK - p * P_DARK
    phi = p / p_det                                    # tỷ lệ sự kiện là photon thật
    q_th = (1 - phi) * 0.5 + phi * E_OPT               # xác suất lỗi mỗi bit sau sifting
    n_rec = rng.binomial(PULSE_RATE, p_det, size=(runs, len(distances)))
    n_sift = rng.binomial(n_rec, 0.5)
    n_err = rng.binomial(n_sift, q_th)
    with np.errstate(divide="ignore", invalid="ignore"):
        qber = np.where(n_sift > 0, n_err / n_sift, 0.0)
    h = np.vectorize(post_processing.binary_entropy)(qber)
    L = np.floor(n_sift - n_sift * 1.2 * h - n_sift * h)
    skr = np.where((qber < QBER_LIMIT) & (L > 256) & (n_sift > 0), L, 0.0)
    return qber, skr, q_th


def summarize(qber, skr):
    peak = qber.max(axis=1) * 100
    total = skr.sum(axis=1)
    return dict(
        runs=int(qber.shape[0]),
        total_mbit_mean=float(total.mean() / 1e6), total_mbit_sd=float(total.std() / 1e6),
        keys_mean=float((skr // 256).sum(axis=1).mean()),
        peak_qber_mean=float(peak.mean()), peak_qber_p5=float(np.percentile(peak, 5)),
        peak_qber_p95=float(np.percentile(peak, 95)), peak_qber_max=float(peak.max()),
        runs_with_qber_ge_11=int((qber >= QBER_LIMIT).any(axis=1).sum()),
        zero_seconds_mean=float((skr == 0).sum(axis=1).mean()),
    )


def plot(results, out="qkd_monte_carlo.png"):
    plt.style.use("dark_background")
    n = len(results)
    fig, axes = plt.subplots(n, 2, figsize=(12, 3.1 * n), gridspec_kw={"width_ratios": [1.6, 1]})
    fig.patch.set_facecolor("#1e1e1e")
    axes = np.atleast_2d(axes)
    for i, R in enumerate(results):
        c = COLORS[i % len(COLORS)]
        ax, bx = axes[i]
        for a in (ax, bx):
            a.set_facecolor("#1e1e1e"); a.grid(color="#444444", linestyle=":")
        t = np.arange(len(R["d"]))
        q = R["fast_q"] * 100
        ax.fill_between(t, np.percentile(q, 5, axis=0), np.percentile(q, 95, axis=0),
                        color=c, alpha=0.30, label="Dải 5–95% (Monte Carlo nhanh)")
        ax.plot(t, R["q_th"] * 100, color=c, lw=1.6, label="QBER kỳ vọng")
        if R["exact_q"] is not None:
            ax.plot(t, R["exact_q"][0] * 100, color="white", lw=0.7, alpha=0.6, label="1 lần chạy bb84.py")
        ax.axhline(11, color="#ffff00", ls="-.", lw=1.2, label="Ngưỡng 11%")
        ax.set_ylim(0, 13); ax.set_ylabel("QBER (%)")
        ax.set_title(f"{R['name']} (d_max = {R['d'].max():.0f} m)", fontsize=11)
        if i == n - 1:
            ax.set_xlabel("Thời gian bay (s)")
        if i == 0:
            ax.legend(fontsize=7, loc="upper left", facecolor="#2d2d2d", edgecolor="none")

        peak = q.max(axis=1)
        bx.hist(peak, bins=30, color=c, alpha=0.8)
        if R["exact_q"] is not None:
            for pk in R["exact_q"].max(axis=1) * 100:
                bx.axvline(pk, color="white", lw=0.8, alpha=0.7)
        bx.axvline(11, color="#ffff00", ls="-.", lw=1.2)
        bx.set_xlim(0, 12); bx.set_ylabel("Số lần chạy")
        bx.set_title("Phân bố đỉnh QBER", fontsize=11)
        if i == n - 1:
            bx.set_xlabel("Đỉnh QBER trong chuyến bay (%)")
    plt.tight_layout()
    plt.savefig(out, dpi=200, facecolor=fig.get_facecolor())
    print(f"[MonteCarlo] Đã xuất biểu đồ: {out}")
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", nargs="+", default=DEFAULT_CSVS)
    ap.add_argument("--fast-runs", type=int, default=1000)
    ap.add_argument("--exact-runs", type=int, default=20, help="0 = bỏ qua chế độ exact")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    results, summary = [], {}
    for i, f in enumerate(args.csv, 1):
        d = load_distances(f)
        t0 = time.time()
        fq, fs, q_th = run_fast(d, args.fast_runs, args.seed + i)
        R = dict(name=f"Chuyến {i}", file=f, d=d, fast_q=fq, q_th=q_th, exact_q=None)
        S = {"fast": summarize(fq, fs)}
        if args.exact_runs > 0:
            eq, es = run_exact(d, args.exact_runs, args.seed + i)
            R["exact_q"] = eq
            S["exact"] = summarize(eq, es)
        results.append(R); summary[f] = S
        print(f"\n[{R['name']}] {f}  ({time.time() - t0:.0f}s)")
        for mode, s in S.items():
            print(f"  {mode:5s} ({s['runs']:4d} lần): tổng khóa {s['total_mbit_mean']:.3f} ± {s['total_mbit_sd']:.3f} Mbit | "
                  f"đỉnh QBER {s['peak_qber_mean']:.2f}% [{s['peak_qber_p5']:.2f}–{s['peak_qber_p95']:.2f}] | "
                  f"lần có QBER≥11%: {s['runs_with_qber_ge_11']} | giây SKR=0: {s['zero_seconds_mean']:.1f}")
    with open("monte_carlo_results.json", "w", encoding="utf-8") as fp:
        json.dump(summary, fp, ensure_ascii=False, indent=2)
    plot(results)


if __name__ == "__main__":
    main()
