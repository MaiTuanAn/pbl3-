import csv
import math
from datetime import datetime


def generate_flight_path(filename, duration_sec=60, speed_mps=20):
    """Hàm sinh quỹ đạo giả (test code)."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "distance"])
        for t in range(duration_sec + 1):
            dist = math.sqrt((t * speed_mps) ** 2 + 100**2)
            writer.writerow([t, round(dist, 2)])


def _parse_mavlink_kv(row):
    """Trích xuất các cặp key-value từ gói tin MAVLink CSV."""
    kv = {}
    for i in range(10, len(row) - 1, 2):
        key = row[i].strip()
        if key:
            kv[key] = row[i + 1].strip()
    return kv


def read_trajectory(filename, resample_1hz=True):
    """
    Tự động lọc dữ liệu bay từ file CSV xuất ra từ Telemetry Log (.tlog) của Mission Planner:
    1. Tự dò mốc thời gian 'Mission: 1 Takeoff' đến 'Disarming motors'.
    2. Trích xuất tọa độ 3D (lat, lon, relative_alt) và tính khoảng cách tới GCS.
    3. Chuẩn hóa tần số lấy mẫu về 1 Hz (1 điểm/giây) cho mô phỏng QKD.
    """
    start_time = None
    end_time = None

    # Bước 1: Quét tìm mốc cất cánh và hạ cánh
    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 11:
                continue
            try:
                dt = datetime.fromisoformat(row[0].strip())
            except ValueError:
                continue

            if row[9].strip() == "mavlink_statustext_t":
                kv = _parse_mavlink_kv(row)
                text = kv.get("text", "")
                if "Mission: 1 Takeoff" in text and start_time is None:
                    start_time = dt
                elif "Disarming motors" in text and start_time is not None:
                    end_time = dt
                    break

    if start_time is None:
        raise ValueError(
            f"[Trajectory] Không tìm thấy lệnh 'Mission: 1 Takeoff' trong file '{filename}'."
        )

    # Bước 2: Đọc tọa độ GPS 3D và tính khoảng cách tới trạm mặt đất (GCS)
    raw_data = []
    home_lat, home_lon = None, None
    t0 = None

    with open(filename, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 11:
                continue
            try:
                dt = datetime.fromisoformat(row[0].strip())
            except ValueError:
                continue

            if dt < start_time:
                continue
            if end_time is not None and dt > end_time:
                break

            if row[9].strip() == "mavlink_global_position_int_t":
                kv = _parse_mavlink_kv(row)
                lat = float(kv["lat"]) / 1e7
                lon = float(kv["lon"]) / 1e7
                rel_alt = max(0.0, float(kv["relative_alt"]) / 1000.0)

                if t0 is None:
                    t0 = dt
                    home_lat, home_lon = lat, lon

                time_sec = (dt - t0).total_seconds()
                dx = (lat - home_lat) * 111320.0
                dy = (lon - home_lon) * 111320.0 * math.cos(math.radians(home_lat))
                distance_3d = math.sqrt(dx**2 + dy**2 + rel_alt**2)

                raw_data.append({
                    "time": time_sec,
                    "distance": distance_3d,
                    "alt": rel_alt,
                })

    if not raw_data:
        raise ValueError("[Trajectory] Không trích xuất được bản ghi tọa độ nào trong khoảng thời gian bay.")

    # Bước 3: Lọc về chuẩn 1 mẫu/giây (1 Hz) để khớp với đơn vị xung/giây (bps)
    if resample_1hz:
        sampled_data = []
        seen_seconds = set()
        for point in raw_data:
            sec_int = int(point["time"])
            if sec_int not in seen_seconds:
                seen_seconds.add(sec_int)
                sampled_data.append({
                    "time": sec_int,
                    "distance": round(point["distance"], 3),
                    "alt": round(point["alt"], 3),
                })
        result = sampled_data
    else:
        result = raw_data

    max_dist = max(p["distance"] for p in result)
    print(f"[Trajectory] Đã nạp {len(result)} điểm quỹ đạo (1 Hz) từ '{filename}'.")
    print(f"[Trajectory] Thời gian bay: {result[-1]['time']}s | Khoảng cách 3D cực đại: {max_dist:.2f}m")
    return result