"""
Verify correct metrics for GRU, ICEEMDAN-GRU, VMD-GRU using scaler-based denormalization.
This mimics exactly what the notebooks do in cell 18/19.
"""
import os, sys
import numpy as np
import pandas as pd
import joblib
import glob

BASE = "c:/Users/TOSHIBA/Documents/SIstem Informasi/Skripsi/Draft Skripsi/FORECASTING/Strimlit"

def safe_mape(y_true, y_pred, eps=1e-8):
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    denom = np.maximum(np.abs(y_true), eps)
    return float(np.mean(np.abs((y_true - y_pred) / denom)))

def check_method(method_folder, dest_subfolder):
    folder = os.path.join(BASE, method_folder, dest_subfolder)
    preds_dir = os.path.join(folder, "retrain-preds")
    scaler_dir = os.path.join(folder, "scaler")
    inter_p = os.path.join(folder, "hasil-interpolasi", "data_cleaned_after_imputation.xlsx")
    
    df_clean = pd.read_excel(inter_p, sheet_name="cleaned_data")
    orig_min = float(df_clean["visitors"].min())
    orig_max = float(df_clean["visitors"].max())
    
    pred_files = glob.glob(os.path.join(preds_dir, "preds_*.csv"))
    test_len = len(pd.read_csv(pred_files[0]))
    
    y_pred_den_dict = {}
    for pf in pred_files:
        comp = os.path.splitext(os.path.basename(pf))[0].replace("preds_", "")
        dfp = pd.read_csv(pf)
        y_pred_norm = dfp['y_pred'].values.astype(float)
        y_true_norm = dfp['y_true'].values.astype(float)
        
        scaler_file = os.path.join(scaler_dir, f"scaler_{comp}.pkl")
        if os.path.exists(scaler_file):
            scaler = joblib.load(scaler_file)
            y_pred_den_dict[comp] = scaler.inverse_transform(y_pred_norm.reshape(-1,1)).ravel()
        else:
            print(f"  WARNING: No scaler for {comp}")
            y_pred_den_dict[comp] = y_pred_norm
    
    x_pred_den_final = np.sum([y_pred_den_dict[c] for c in y_pred_den_dict], axis=0)
    
    # Actual test signal
    visitors = df_clean['visitors'].values.astype(float)
    split_idx = len(visitors) - test_len
    actual_test_signal = visitors[split_idx:]
    
    final_mae = float(np.mean(np.abs(actual_test_signal - x_pred_den_final)))
    final_mape = safe_mape(actual_test_signal, x_pred_den_final) * 100
    
    return {
        "test_len": test_len,
        "mae": final_mae,
        "mape": final_mape,
        "pred_sample": x_pred_den_final[:3].tolist(),
        "actual_sample": actual_test_signal[:3].tolist()
    }

print("=== GRU - Gunung geger ===")
r = check_method("GRU", "Gunung geger")
print(f"  test_len={r['test_len']}, MAE={r['mae']:.4f}, MAPE={r['mape']:.4f}%")
print(f"  pred_sample={r['pred_sample']}")
print(f"  actual_sample={r['actual_sample']}")

print("\n=== ICEEMDAN-GRU - Gunung Geger ===")
r = check_method("ICEEMDAN-GRU", "Gunung Geger")
print(f"  test_len={r['test_len']}, MAE={r['mae']:.4f}, MAPE={r['mape']:.4f}%")
print(f"  pred_sample={r['pred_sample']}")
print(f"  actual_sample={r['actual_sample']}")

print("\n=== VMD-GRU - Gunung geger ===")
r = check_method("VMD-GRU", "Gunung geger")
print(f"  test_len={r['test_len']}, MAE={r['mae']:.4f}, MAPE={r['mape']:.4f}%")
print(f"  pred_sample={r['pred_sample']}")
print(f"  actual_sample={r['actual_sample']}")
