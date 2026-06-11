import os, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(BASE_DIR, "chapters")
dst_dir = os.path.join(BASE_DIR, "chapters_renamed")
os.makedirs(dst_dir, exist_ok=True)

files = sorted(os.listdir(src_dir))

for f in files:
    src = os.path.join(src_dir, f)
    num = f.split("_")[0]
    dst = os.path.join(dst_dir, f"{num}.txt")
    with open(src, "r", encoding="utf-8") as fh:
        content = fh.read()
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(content)

with open(os.path.join(dst_dir, "index.txt"), "w", encoding="utf-8") as idx:
    for f in files:
        src = os.path.join(src_dir, f)
        with open(src, "r", encoding="utf-8") as fh:
            first_line = fh.readline().strip()
        idx.write(f"{f}\n")

print(f"完成！共 {len(files)} 章已复制到 {dst_dir}")
