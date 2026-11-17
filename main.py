import numpy as np
import trajectory
import channel
import bb84
import post_processing
import plotter


def main():
    # 1. Nạp dữ liệu quỹ đạo bay thực tế từ Mission Planner (chuẩn hóa 1 Hz)
    csv_file = "2026-11-17 18-42-52.csv"
    path_data = trajectory.read_trajectory(csv_file, resample_1hz=True)

    # 2. Cấu hình tần số phát xung laser (1 MHz = 1.000.000 xung/giây)
    LASER_PULSE_RATE = 1_000_000

    distances = []
    qbers = []
    skrs = []
    sifted_rates = []

    # 3. Chạy mô phỏng từng giây dọc theo quỹ đạo chuyến bay
    for point in path_data:
        d = point["distance"]

        # Tính xác suất sống sót của photon qua kênh truyền FSO
        p_survival = channel.calculate_survival_probability(d)

        # Mô phỏng giao thức BB84
        sifted_bits, qber, status = bb84.run_bb84_simulation(LASER_PULSE_RATE, p_survival)

        # Hậu xử lý: lấy giá trị số nguyên/thực của SKR
        res = post_processing.extract_secret_key(sifted_bits, qber)
        if isinstance(res, tuple):
            skr = float(res[0]) if isinstance(res[0], (int, float, np.number)) else float(res[1])
        elif isinstance(res, np.ndarray):
            skr = len(res)
        else:
            skr = float(res)

        distances.append(d)
        qbers.append(qber)
        skrs.append(skr)
        sifted_rates.append(len(sifted_bits))

    # 4. Vẽ đồ thị đánh giá hiệu năng
    plotter.plot_performance_metrics(distances, qbers, skrs, sifted_rates)


if __name__ == "__main__":
    main()