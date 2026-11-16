import matplotlib.pyplot as plt

def plot_performance_metrics(distances, qbers, skrs, sifted_rates):
    """
    Vẽ đồ thị biểu diễn Sifted Key, Secret Key Rate (SKR) và QBER theo khoảng cách.
    """
    # Thiết lập giao diện biểu đồ nền tối
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.patch.set_facecolor('#1e1e1e') # Dark gray background
    
    # ---------------------------------------------------------
    # Đồ thị 1: Tốc độ sinh khóa (Key Rate)
    # ---------------------------------------------------------
    ax1.set_facecolor('#1e1e1e')
    ax1.plot(distances, sifted_rates, label='Sifted Key Rate', color='white', linestyle='--', alpha=0.7)
    ax1.plot(distances, skrs, label='Secret Key Rate (SKR)', color='#00ffff', linewidth=2) # Cyan
    ax1.set_ylabel('Key Rate (bits/s)', color='#00ffff', fontsize=12)
    ax1.set_title('Hiệu năng Phân phối Khóa Lượng tử (QKD BB84) trên UAV', color='white', fontsize=14)
    ax1.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='none')
    ax1.grid(color='#444444', linestyle=':', linewidth=1)

    # ---------------------------------------------------------
    # Đồ thị 2: Tỷ lệ lỗi bit lượng tử (QBER)
    # ---------------------------------------------------------
    qber_percentages = [q * 100 for q in qbers]
    
    ax2.set_facecolor('#1e1e1e')
    ax2.plot(distances, qber_percentages, label='QBER Thực tế', color='#ff5555', linewidth=2)
    ax2.axhline(y=11.0, color='#ffff00', linestyle='-.', linewidth=1.5, label='Ngưỡng rò rỉ (11%)')
    
    ax2.set_xlabel('Khoảng cách UAV tới GCS (mét)', color='white', fontsize=12)
    ax2.set_ylabel('QBER (%)', color='#ff5555', fontsize=12)
    ax2.set_ylim(0, max(15, max(qber_percentages) + 2)) # Giữ khung dọc hợp lý
    ax2.legend(loc='upper left', facecolor='#2d2d2d', edgecolor='none')
    ax2.grid(color='#444444', linestyle=':', linewidth=1)

    # Căn chỉnh và xuất file
    plt.tight_layout()
    plt.savefig('qkd_performance_chart.png', dpi=300, facecolor=fig.get_facecolor())
    print("[Plotter] Đã xuất biểu đồ ra file: qkd_performance_chart.png")
    
    # Hiển thị trực tiếp (Nếu có X-Server trên WSL)
    plt.show()