import os, re, json
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

CHARACTERS = config["characters"]
THEMES = config["themes"]

def analyze_chapter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.strip().split('\n')
    title = lines[0].strip() if lines else "Unknown"
    char_count = {}
    for name, keywords in CHARACTERS.items():
        count = sum(text.count(kw) for kw in keywords)
        if count > 0:
            char_count[name] = count
    theme_count = {}
    for theme, keywords in THEMES.items():
        count = sum(text.count(kw) for kw in keywords)
        if count > 0:
            theme_count[theme] = count
    return {
        "title": title,
        "lines": len(lines),
        "chars": len(text),
        "characters": char_count,
        "themes": theme_count,
    }

def batch_analysis(start, end):
    result = {
        "batch": f"ch{start:03d}-{end:03d}",
        "chapters": [],
        "total_chars": {},
        "total_themes": Counter(),
        "total_lines": 0,
        "total_size": 0,
    }
    for i in range(start, end + 1):
        fname = f"{i:03d}.txt"
        fpath = os.path.join(CHAPTERS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        try:
            ch_data = analyze_chapter(fpath)
            result["chapters"].append(ch_data)
            result["total_lines"] += ch_data["lines"]
            result["total_size"] += ch_data["chars"]
            for char, count in ch_data["characters"].items():
                result["total_chars"][char] = result["total_chars"].get(char, 0) + count
            for theme, count in ch_data["themes"].items():
                result["total_themes"][theme] += count
        except Exception as e:
            print(f"  Error: {fname}: {e}")
    return result

def save_report(report_data):
    batch = report_data["batch"]
    filepath = os.path.join(REPORTS_DIR, f"data_{batch}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    return filepath

print("=" * 60)
print("Auto Analysis: Batch Extract Character/Theme Frequencies")
print("=" * 60)

total_files = len([f for f in os.listdir(CHAPTERS_DIR) if f.endswith('.txt') and f[0].isdigit()])
print(f"Total files: {total_files}")

batch_size = 20
start_chapter = 1

for batch_start in range(start_chapter, total_files + 1, batch_size):
    batch_end = min(batch_start + batch_size - 1, total_files)
    print(f"\nBatch: {batch_start:03d}-{batch_end:03d}")
    result = batch_analysis(batch_start, batch_end)
    saved = save_report(result)
    ch_count = len(result["chapters"])
    print(f"  Chapters: {ch_count}, Lines: {result['total_lines']}, Size: {result['total_size']}")
    if result["total_chars"]:
        top_chars = sorted(result["total_chars"].items(), key=lambda x: -x[1])[:5]
        print(f"  Top chars: {', '.join(f'{k}({v})' for k, v in top_chars)}")
    if result["total_themes"]:
        top_themes = result["total_themes"].most_common(3)
        print(f"  Top themes: {', '.join(f'{k}({v})' for k, v in top_themes)}")
    print(f"  Saved: {saved}")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)
