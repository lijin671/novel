import os, re, json
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

files = sorted(os.listdir(CHAPTERS_DIR))
files = [f for f in files if f.endswith('.txt') and f != 'index.txt']

total_chars = 0
total_lines = 0
chapter_titles = []
chapter_stats = []

characters = {}
for name, aliases in config["characters"].items():
    characters[name] = 0

keywords = Counter()

for fname in files:
    fpath = os.path.join(CHAPTERS_DIR, fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = text.split('\n')
    first_line = lines[0].strip() if lines else ''

    chapter_titles.append(first_line)
    total_lines += len(lines)
    total_chars += len(text)

    num = int(fname.replace('.txt', ''))

    char_counts = {}
    for name in characters:
        cnt = text.count(name)
        characters[name] += cnt
        if cnt > 0:
            char_counts[name] = cnt

    chapter_stats.append({
        'num': num,
        'title': first_line,
        'lines': len(lines),
        'chars': len(text),
        'chars_count': char_counts,
    })

sorted_chars = sorted(characters.items(), key=lambda x: -x[1])
print("=== 角色名出场频次 TOP30 ===")
for name, cnt in sorted_chars[:30]:
    if cnt > 0:
        print(f"  {name}: {cnt}次")

print(f"\n=== 全书概览 ===")
print(f"  总章节数: {len(files)}")
print(f"  总行数: {total_lines}")
print(f"  总字符数: {total_chars}")

print(f"\n=== 章节标题列表（前30章 + 后20章）===")
for s in chapter_stats[:30]:
    print(f"  第{s['num']}章: {s['title'][:40]} ({s['chars']}字)")
print(f"  ...（中间省略）...")
for s in chapter_stats[-20:]:
    print(f"  第{s['num']}章: {s['title'][:40]} ({s['chars']}字)")

total = len(chapter_stats)
if total > 100:
    step = total // 7
    print(f"\n=== 每{step}章的角色出场变化 ===")
    for chunk_start in range(0, total, step):
        chunk_end = min(chunk_start + step, total)
        sub = chapter_stats[chunk_start:chunk_end]
        char_chunk = {name: 0 for name in list(characters.keys())[:8]}
        for s in sub:
            for name in char_chunk:
                char_chunk[name] += s['chars_count'].get(name, 0)
        active = [f"{k}({v})" for k,v in sorted(char_chunk.items(), key=lambda x:-x[1]) if v > 0]
        print(f"  第{chunk_start+1}~{chunk_end}章: {' | '.join(active[:6])}")
