import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import admin_methods as am
    print("admin_methods imported successfully!")
    folder = am.cari_folder("Hybrid ICEEMDAN-VMD-GRU", "Makam Syaikhona Kholil")
    h = am.muat_hasil_folder(folder, "Makam Syaikhona Kholil", "Hybrid ICEEMDAN-VMD-GRU")
    print(f"MAE: {h['mae']:.2f}, MAPE: {h['mape']:.2f}%")
    print(f"MAE Norm: {h['mae_norm']:.4f}, MAPE Norm: {h['mape_norm']:.2f}%")
    print(f"actual_test_signal_norm len: {len(h['actual_test_signal_norm'])}")
    print(f"x_pred_norm_final len: {len(h['x_pred_norm_final'])}")
    print("muat_hasil_folder executed without any issue!")
except Exception as e:
    import traceback
    traceback.print_exc()
