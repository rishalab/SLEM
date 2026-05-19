import time
from src.runner import Runner

slem_runner = Runner()
ITERATIONS = 20
IDLE_GAP = 30 

execution_queue = [
    # Serialization
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "json_10MB"}, 
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "orjson_10MB"},
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "ujson_10MB"}, 
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "json_100KB"},
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "orjson_100KB"}, 
    {"mod": "evaluation.evaluation_scripts.measure_serialization", "fn": "ujson_100KB"},
    
    # Image
    {"mod": "evaluation.evaluation_scripts.measure_image", "fn": "cv2_resize_512"}, 
    {"mod": "evaluation.evaluation_scripts.measure_image", "fn": "pil_resize_512"},
    {"mod": "evaluation.evaluation_scripts.measure_image", "fn": "cv2_resize_2048"}, 
    {"mod": "evaluation.evaluation_scripts.measure_image", "fn": "pil_resize_2048"},
    
    # Data
    {"mod": "evaluation.evaluation_scripts.measure_data", "fn": "pandas_groupby"}, 
    {"mod": "evaluation.evaluation_scripts.measure_data", "fn": "polars_groupby"},
    {"mod": "evaluation.evaluation_scripts.measure_data", "fn": "pandas_dropna"}, 
    {"mod": "evaluation.evaluation_scripts.measure_data", "fn": "polars_dropna"}
]

print("--- Starting Empirical Run Sequence ---")
for task in execution_queue:
    mod, fn = task["mod"], task["fn"]
    print(f"\n[{time.strftime('%H:%M:%S')}] Booting cell: {mod} -> {fn}")

    clean_mod = mod.split('.')[-1]
    csv_out = f"evaluation/evaluation_results/{clean_mod}_{fn}.csv"

    runner_logs = slem_runner.run(mod, fn, {}, ITERATIONS, IDLE_GAP, csv_out, {})
    
    print("--- RUNNER LOGS ---")
    print(runner_logs.strip())
    print("-------------------")
    print(f"[{time.strftime('%H:%M:%S')}] Completed cell.")