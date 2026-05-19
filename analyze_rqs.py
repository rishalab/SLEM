import pandas as pd
import glob
import os

print("=== ESEM 2026: RQ1, RQ2, RQ4, RQ5 ANALYSIS ===\n")

csv_files = glob.glob("evaluation/evaluation_results/*.csv")
data_store = {}

for f in csv_files:
    if "groupby" in f: continue  
    
    try:
        df = pd.read_csv(f)
        df.columns = df.columns.str.strip()
        
        if df.empty or 'Domain' not in df.columns:
            continue
            
        means = df.groupby('Domain')['Energy (micro joules)'].mean()
        
        pkg = means.get('package-0', 0) + means.get('package-1', 0)
        dram = means.get('dram-0', 0) + means.get('dram-1', 0)

        total_energy = (pkg + dram) / 1_000_000 
        
        filename = os.path.basename(f).replace('.csv', '')
        data_store[filename] = total_energy
        
    except Exception as e:
        print(f"Skipped {f} due to error: {e}")
        continue

print("--- RQ1: Intra-Domain Baselines (Average Joules per run) ---")
print(f"Data: Pandas DropNA: {data_store.get('measure_data_pandas_dropna', 0):.4f} J vs Polars DropNA: {data_store.get('measure_data_polars_dropna', 0):.4f} J")
print(f"Image (2048): OpenCV: {data_store.get('measure_image_cv2_resize_2048', 0):.4f} J vs Pillow: {data_store.get('measure_image_pil_resize_2048', 0):.4f} J")
print(f"Serialization (10MB): JSON: {data_store.get('measure_serialization_json_10MB', 0):.4f} J | ORJSON: {data_store.get('measure_serialization_orjson_10MB', 0):.4f} J | UJSON: {data_store.get('measure_serialization_ujson_10MB', 0):.4f} J\n")

print("--- RQ2: Workload Modulation (Small vs Large Payloads) ---")
cv2_scale = data_store.get('measure_image_cv2_resize_2048', 1) / data_store.get('measure_image_cv2_resize_512', 1)
pil_scale = data_store.get('measure_image_pil_resize_2048', 1) / data_store.get('measure_image_pil_resize_512', 1)
print(f"Image scaling (512px -> 2048px): OpenCV energy increased {cv2_scale:.1f}x, Pillow increased {pil_scale:.1f}x.")

json_scale = data_store.get('measure_serialization_json_10MB', 1) / data_store.get('measure_serialization_json_100KB', 1)
orjson_scale = data_store.get('measure_serialization_orjson_10MB', 1) / data_store.get('measure_serialization_orjson_100KB', 1)
print(f"JSON scaling (100KB -> 10MB): Standard JSON increased {json_scale:.1f}x, ORJSON increased {orjson_scale:.1f}x.\n")

print("--- RQ4: Backend Architecture Efficiency ---")
polars_savings = (1 - (data_store.get('measure_data_polars_dropna', 0) / data_store.get('measure_data_pandas_dropna', 1))) * 100
orjson_savings = (1 - (data_store.get('measure_serialization_orjson_10MB', 0) / data_store.get('measure_serialization_json_10MB', 1))) * 100
print(f"Rust Backend vs Standard: Polars uses {polars_savings:.1f}% less energy than Pandas.")
print(f"Rust Backend vs Standard: ORJSON uses {orjson_savings:.1f}% less energy than standard JSON.\n")

print("--- RQ5: Cross-Domain Synthesis ---")
print("Check above metrics: Do Rust-backed/C-backed libraries universally win across Data (Polars), Image (OpenCV), and Serialization (ORJSON/UJSON)? If yes, the architectural rule holds true across all software domains.")