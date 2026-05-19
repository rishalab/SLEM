import json, orjson, ujson, msgpack, os

# Global Fallbacks
with open('payload_10MB.json', 'r') as f: payload_10MB = json.load(f)
with open('payload_100KB.json', 'r') as f: payload_100KB = json.load(f)

# --- 10MB Workloads ---
def json_10MB(data=None): return json.dumps(payload_10MB)
def orjson_10MB(data=None): return orjson.dumps(payload_10MB) # Rust backend (RQ4)
def ujson_10MB(data=None): return ujson.dumps(payload_10MB)   # C backend (RQ4)

# --- 100KB Workloads ---
def json_100KB(data=None): return json.dumps(payload_100KB)
def orjson_100KB(data=None): return orjson.dumps(payload_100KB)
def ujson_100KB(data=None): return ujson.dumps(payload_100KB)