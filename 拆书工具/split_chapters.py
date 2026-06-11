import re, os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

input_path = os.path.join(BASE_DIR, config["novel"]["source_file"])
output_dir = os.path.join(BASE_DIR, "chapters")
encoding = config["novel"].get("encoding", "utf-8")

os.makedirs(output_dir, exist_ok=True)

with open(input_path, "r", encoding=encoding, errors="replace") as f:
    text = f.read()

pattern = r'^第[一二三四五六七八九十百千万零\d]+章[^\n]*'
matches = list(re.finditer(pattern, text, re.MULTILINE))

print(f"共找到 {len(matches)} 章\n")

chapters = []
for i, m in enumerate(matches):
    start = m.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    content = text[start:end].strip()
    chapters.append(content)

for i, ch in enumerate(chapters):
    first_line = ch.split('\n')[0].strip()
    safe_name = re.sub(r'[<>:"/\\|?*]', '', first_line)
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    fname = f"{i+1:03d}_{safe_name}.txt"
    fpath = os.path.join(output_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(ch)
    lines = ch.count('\n') + 1
    chars = len(ch)
    print(f"第{i+1:3d}章 | {first_line:30s} | {lines:5d}行 | {chars:6d}字")
    print(f"      -> {fpath}")

print(f"\n已拆解完成，共 {len(chapters)} 章，保存至: {output_dir}")
