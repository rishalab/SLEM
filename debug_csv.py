import pandas as pd
import glob

test_file = glob.glob("evaluation/evaluation_results/measure_serialization_json_10MB.csv")[0]

print(f"Reading: {test_file}")
df = pd.read_csv(test_file)

print("\nExact Column Names:")
print(df.columns.tolist())

print("\nData Preview:")
print(df.head())