import math

def calculate_survival_probability(distance_m):
    """Tính xác suất 1 photon từ UAV lọt vào mắt đọc của GCS."""
    # Thông số phần cứng & môi trường
    sigma = 0.0001           # Hệ số tán xạ khí quyển (trời quang)
    D_R = 0.2                # Đường kính kính viễn vọng thu (20cm)
    D_T = 0.05               # Đường kính ống phát laser (5cm)
    theta = 0.001            # Góc phân kỳ laser (1 mrad)
    eta = 0.2                # Hiệu suất Quantum (20%)
    
    # Suy hao khí quyển
    h_atm = math.exp(-sigma * distance_m)
    
    # Suy hao hình học (chùm sáng bị loe ra)
    beam_diameter = D_T + theta * distance_m
    h_geo = min((D_R / beam_diameter)**2, 1.0)
    
    # Xác suất sống sót tổng thể
    return eta * h_atm * h_geo