import re, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports")

print("=== Dialogue Quote Analysis ===")
total_ascii = 0
total_all = 0
chapter_files = sorted([f for f in os.listdir(CHAPTERS_DIR) if f.endswith('.txt') and f[0].isdigit()],
                       key=lambda x: int(x.replace('.txt', '')))

for fname in chapter_files:
    fpath = os.path.join(CHAPTERS_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    ascii_quote_chars = sum(len(m.group()) for m in re.finditer(r'"[^"]{1,500}"', text))
    total_ascii += ascii_quote_chars
    total_all += len(text)

dialogue_pct = total_ascii / total_all * 100
print(f"Total chars in ASCII quotes: {total_ascii}")
print(f"Total text chars: {total_all}")
print(f"Dialogue ratio (ASCII quotes): {dialogue_pct:.1f}%")

json_path = os.path.join(OUTPUT_DIR, "stylometric_quantitative.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
data["dialogue_percent"] = round(dialogue_pct, 1)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Updated {json_path}")
