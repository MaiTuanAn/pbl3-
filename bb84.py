import numpy as np

def run_bb84_simulation(pulse_rate, p_survival):
    """
    Chạy giao thức BB84 trong 1 giây.
    Trả về mảng bit khóa thô (Sifted bits) và QBER.
    """
    p_dark_count = 5e-5     # Nhiễu tối của cảm biến (Dark count)
    p_optical_error = 0.015 # Nhiễu phân cực nền (Optical error 1.5%)

    # 1. Alice (UAV) sinh bit và cơ sở
    alice_bits = np.random.randint(2, size=pulse_rate, dtype=np.int8)
    alice_bases = np.random.randint(2, size=pulse_rate, dtype=np.int8)
    
    # 2. Kênh truyền & Nhiễu
    true_photon_mask = np.random.random(pulse_rate) < p_survival
    dark_count_mask = np.random.random(pulse_rate) < p_dark_count
    
    bob_received_mask = true_photon_mask | dark_count_mask
    num_received = np.count_nonzero(bob_received_mask)
    
    if num_received == 0:
        return np.array([]), 0.0, "Mất tín hiệu"
        
    # Lọc ra các bit đến được Bob
    received_alice_bits = alice_bits[bob_received_mask]
    received_alice_bases = alice_bases[bob_received_mask]
    is_true_photon = true_photon_mask[bob_received_mask]
    
    # 3. Bob (GCS) đo đạc
    bob_bases = np.random.randint(2, size=num_received, dtype=np.int8)
    bob_bits = np.zeros(num_received, dtype=np.int8)
    
    # Giả lập lỗi quang học (Dù đo đúng cơ sở vẫn có 1.5% sai)
    optical_errors = np.random.random(num_received) < p_optical_error
    true_bits_measured = np.where(optical_errors, 1 - received_alice_bits, received_alice_bits)
    
    # Xử lý logic đo:
    correct_basis_mask = (received_alice_bases == bob_bases)
    
    # - Đo đúng & Photon thật
    good_mask = is_true_photon & correct_basis_mask
    bob_bits[good_mask] = true_bits_measured[good_mask]
    
    # - Đo sai HOẶC đo trúng nhiễu (kết quả 50/50)
    random_mask = (~is_true_photon) | (~correct_basis_mask)
    bob_bits[random_mask] = np.random.randint(2, size=np.count_nonzero(random_mask))
    
    # 4. Sifting (Lọc khóa công khai)
    sifted_mask = (received_alice_bases == bob_bases)
    sifted_alice_bits = received_alice_bits[sifted_mask]
    sifted_bob_bits = bob_bits[sifted_mask]
    
    if len(sifted_alice_bits) == 0:
        return np.array([]), 0.0, "Không đủ khóa"
        
    # Tính QBER
    error_count = np.count_nonzero(sifted_alice_bits != sifted_bob_bits)
    qber = error_count / len(sifted_alice_bits)
    
    status = "An Toàn" if qber < 0.11 else "Nguy Hiểm"
    return sifted_alice_bits, qber, status