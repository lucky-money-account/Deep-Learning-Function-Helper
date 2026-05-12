"""将各库的 JSON 数据文件合并为 functions.json"""
import json
import os

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJ_ROOT, "data")

files = ["torch.json", "numpy.json", "matplotlib.json", "opencv.json", "sklearn.json", "pandas.json"]

all_funcs = []
for fname in files:
    fpath = os.path.join(DATA_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_funcs.extend(data)
            print(f"  {fname}: {len(data)} functions")

output_path = os.path.join(DATA_DIR, "functions.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_funcs, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(all_funcs)} functions -> {output_path}")
