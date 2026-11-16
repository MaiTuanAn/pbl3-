# 🛸 Quantum-Secured UAV Communication Network (FANET)

Dự án nghiên cứu: **Bảo mật mạng UAV (FANET) ứng dụng Mật mã Lượng tử (Quantum Cryptography) và Phân phối Khóa Lượng tử (QKD)**.

Dự án này tập trung vào việc mô phỏng và đánh giá hiệu năng của giao thức Phân phối khóa lượng tử (BB84) qua kênh truyền quang học không gian tự do (FSO) dựa trên quỹ đạo di chuyển thực tế của UAV.

---

## 1. Giới thiệu & Mục tiêu (Introduction & Objectives)

### Giới thiệu
Mạng bay không người lái (FANET) đang đóng vai trò quan trọng trong các ứng dụng quân sự, cứu hộ và dân sự. Tuy nhiên, liên kết không dây của UAV rất dễ bị nghe lén. Sự ra đời của máy tính lượng tử trong tương lai gần với thuật toán Shor sẽ phá vỡ hoàn toàn các chuẩn mật mã khóa công khai hiện tại (RSA, ECC). Để giải quyết vấn đề này, Phân phối khóa lượng tử (QKD) cung cấp mức độ bảo mật tuyệt đối dựa trên các định luật vật lý lượng tử (Định lý không sao chép).

### Mục tiêu
*   Đề xuất cơ chế thiết lập khóa bí mật an toàn tuyệt đối cho UAV sử dụng giao thức BB84.
*   Xây dựng mô hình toán học tính toán suy hao kênh truyền quang học (FSO) khi UAV di chuyển liên tục.
*   Phát triển hệ thống mô phỏng bằng Python để đánh giá Tỷ lệ lỗi bit lượng tử (QBER) và Tốc độ sinh khóa bí mật (Secret Key Rate - SKR) theo thời gian thực.
*   Đánh giá tính khả thi khi triển khai hệ thống lượng tử trên môi trường UAV bị giới hạn tài nguyên và bị ảnh hưởng bởi nhiễu môi trường.

---

## 2. Related Work (Các nghiên cứu liên quan)

Dự án được xây dựng dựa trên sự kế thừa và cải tiến từ các hướng nghiên cứu sau:
*   **Mật mã cổ điển trên UAV:** Các giải pháp sử dụng AES, RSA, ECC truyền thống có chi phí tính toán thấp nhưng bộc lộ rủi ro bảo mật lớn trước các cuộc tấn công "Lưu trữ trước, Giải mã sau" (Store-now, Decrypt-later) của máy tính lượng tử.
*   **QKD qua cáp quang (Fiber-based QKD):** Đã được thương mại hóa nhưng không thể áp dụng cho mạng di động như UAV.
*   **QKD qua không gian tự do (FSO-QKD):** Đã có các nghiên cứu thử nghiệm truyền QKD từ vệ tinh Micius xuống mặt đất. Tuy nhiên, môi trường FANET với quỹ đạo bay phức tạp, khoảng cách thay đổi liên tục, nhiễu loạn khí quyển và rung lắc cơ học vẫn là một bài toán mở cần được mô phỏng chi tiết.

---

## 3. Phương pháp & Thuật toán Đề xuất

Dự án sử dụng phương pháp mô phỏng số (Numerical Simulation) kết hợp với mô hình dữ liệu bay thực tế.

*   **Thuật toán sinh khóa:** Giao thức **BB84** (Bennett and Brassard, 1984). Sử dụng cơ sở phân cực quang học (Rectilinear và Diagonal) để mã hóa bit.
*   **Mô hình suy hao FSO:** Áp dụng định luật Beer-Lambert kết hợp suy hao hình học:
    $$P_{survival} = \eta \cdot e^{-\sigma \cdot d} \cdot \left( \frac{D_R}{D_T + \theta \cdot d} \right)^2$$
*   **Xử lý hậu kỳ (Post-Processing):**
    *   *Sửa lỗi (Information Reconciliation):* Sử dụng hàm Shannon Binary Entropy $H(e)$ để tính toán hao hụt lý thuyết thay cho thuật toán Cascade nhằm tối ưu tài nguyên mô phỏng.
    *   *Khuếch đại bảo mật (Privacy Amplification):* Sử dụng thuật toán băm (Hash Function - SHA-256) để nén Sifted Key thành khóa AES-256 an toàn tuyệt đối, loại bỏ hoàn toàn thông tin bị rò rỉ.

---

## 4. Mô hình Mô phỏng & Thực nghiệm

Mô hình được xây dựng theo kiến trúc **Clean Architecture** sử dụng ngôn ngữ Python.

### Cấu trúc hệ thống (Repository Structure)
*   `trajectory.py`: Đọc dữ liệu tọa độ thực tế (Lat, Lng, Alt, Time) trích xuất từ file log CSV của **Mission Planner / ArduPilot (SITL)** và tính toán khoảng cách 3D.
*   `channel.py`: Tính toán xác suất tồn tại của photon (Survival Probability) trong môi trường khí quyển.
*   `bb84.py`: Lõi mô phỏng lượng tử sử dụng cơ chế Vector hóa của Numpy để xử lý hàng triệu photon/giây. Giả lập nhiễu tối (Dark Count) và nhiễu quang học (Optical Error).
*   `post_processing.py`: Xử lý Sifting, kiểm tra ngưỡng QBER và chiết xuất Secret Key.
*   `plotter.py`: Giao diện trực quan hóa dữ liệu bằng Matplotlib.
*   `main.py`: Trình điều phối (Orchestrator) liên kết các module.

---

## 5. Đánh giá Kết quả (Expected Results)

Các số liệu đầu ra chính của bộ mô phỏng bao gồm:
1.  **Sự biến thiên của QBER:** Tỷ lệ lỗi bit lượng tử (QBER) sẽ duy trì ở mức thấp (do nhiễu nền) khi UAV ở gần, và tăng vọt theo hàm mũ khi UAV bay xa do tín hiệu suy hao bị nhiễu tối (Dark Count) lấn át.
2.  **Ngưỡng bảo mật (Security Threshold):** Biểu diễn chính xác thời điểm QBER vượt quá **11%** (Ngưỡng Shor-Preskill), khiến hệ thống lập tức ngừng cung cấp khóa để đảm bảo an toàn.
3.  **Secret Key Rate (SKR):** Đồ thị biểu diễn số lượng bit khóa sinh ra mỗi giây giảm dần theo khoảng cách và chạm mức 0 khi QBER vượt ngưỡng an toàn.

---

## 6. Kết luận & Hướng cải tiến

### Kết luận
Mô hình chứng minh được tính khả thi của việc thiết lập khóa lượng tử trong mạng UAV dựa trên các tham số vật lý quang học. Nó cung cấp một cái nhìn định lượng về khoảng cách an toàn tối đa mà UAV có thể hoạt động mà vẫn đảm bảo tính bí mật tuyệt đối.

### Hướng cải tiến (Future Work)
*   Tích hợp thuật toán Mật mã hậu lượng tử (PQC - ví dụ: CRYSTALS-Kyber) cho bước xác thực ban đầu nhằm ngăn chặn tấn công Man-in-the-Middle (MitM).
*   Đưa mô hình kênh truyền quang học này vào phần mềm mô phỏng mạng **ns-3** để kiểm tra ảnh hưởng của Delay và Jitter lên giao thức định tuyến mạng FANET.
*   Thực nghiệm trên vi điều khiển (ESP32/Raspberry Pi) sử dụng tín hiệu Wi-Fi giả lập cho liên kết quang học.

---

## 7. Kế hoạch Dự kiến (Project Plan)

*   **Tuần 1-2:** Nghiên cứu tổng quan (Related Work) về QKD, thiết lập môi trường Python và lấy log bay từ phần mềm Mission Planner SITL.
*   **Tuần 3-4:** Lập trình lõi thuật toán: Kênh truyền quang học (`channel.py`) và logic BB84 (`bb84.py`).
*   **Tuần 5:** Lập trình module xử lý hậu kỳ (Sửa lỗi, Hash) và tích hợp các module lại thông qua `main.py`.
*   **Tuần 6:** Chạy mô phỏng, thu thập kết quả, tinh chỉnh thông số nhiễu và thiết kế biểu đồ (Matplotlib).
*   **Tuần 7-8:** Viết báo cáo tổng kết, đánh giá kết quả so với lý thuyết và chuẩn bị tài liệu thuyết trình/bảo vệ đồ án.