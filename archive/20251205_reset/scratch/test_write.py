
import os

file_path = "test_large_file.txt"
content = "a" * 5000  # 5KB of data

with open(file_path, "w") as f:
    f.write(content)

print(f"Wrote {len(content)} bytes to {file_path}")
