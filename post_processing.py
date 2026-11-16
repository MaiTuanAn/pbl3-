import math
import hashlib

def binary_entropy(qber):
    if qber <= 0 or qber >= 1:
        return 0.0
    return -qber * math.log2(qber) - (1 - qber) * math.log2(1 - qber)

def extract_secret_key(sifted_bits, qber):
    """
    Thực hiện Information Reconciliation và Privacy Amplification.
    Trả về chiều dài khóa an toàn và chuỗi AES-256 tương ứng.
    """
    N = len(sifted_bits)
    if N == 0 or qber >= 0.11:
        return 0, "Bị hủy do QBER cao"

    # Giới hạn hao hụt lý thuyết
    f_ec = 1.2 # Hiệu suất thuật toán Cascade
    H_e = binary_entropy(qber)
    
    leak_ec = N * f_ec * H_e # Hao hụt do trao đổi parity bit
    leak_eve = N * H_e       # Hao hụt do đánh đổi sự rò rỉ lượng tử
    
    L_final = int(N - leak_ec - leak_eve)
    
    if L_final <= 256: 
        # Cần ít nhất 256 bit an toàn tuyệt đối để sinh khóa AES-256
        return 0, "Không đủ lượng entropy an toàn"

    # Privacy Amplification bằng SHA-256
    bit_string = ''.join(sifted_bits.astype(str))
    byte_data = int(bit_string, 2).to_bytes((len(bit_string) + 7) // 8, byteorder='big')
    
    hash_object = hashlib.sha256(byte_data)
    aes_256_key = hash_object.hexdigest()
    
    return L_final, aes_256_key