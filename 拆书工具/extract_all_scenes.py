import re, os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")
OUTPUT_FILE = os.path.join(BASE_DIR, "reports", "scene_extracts.txt")

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

scene_queries = config.get("scene_keywords", {})

def extract_context(text, keyword, context_lines=20):
    lines = text.split('\n')
    results = []
    for i, line in enumerate(lines):
        if keyword in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            excerpt = "\n".join(lines[start:end])
            results.append((keyword, i+1, excerpt))
    return results

total_queries = len(scene_queries)
print(f"Total scenes to extract: {total_queries}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("=" * 70 + "\n")
    out.write("  全部场景原文提取\n")
    out.write(f"  共 {total_queries} 个场景\n")
    out.write("=" * 70 + "\n\n")

    count = 0
    for scene_name, spec in sorted(scene_queries.items()):
        fname = spec["file"]
        fpath = os.path.join(CHAPTERS_DIR, fname)

        if not os.path.exists(fpath):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        ctx_lines = spec.get("context", 20)
        keywords = spec["keywords"]

        out.write(f"\n{'─' * 70}\n")
        out.write(f"  #{count+1:3d} 【{scene_name}】\n")
        out.write(f"{'─' * 70}\n\n")

        found_any = False
        for kw in keywords:
            extracts = extract_context(text, kw, ctx_lines)
            if extracts:
                found_any = True
                for kw_found, line_num, excerpt in extracts:
                    out.write(f">>> [{kw_found}] at line {line_num}:\n")
                    out.write(excerpt + "\n\n")

        if not found_any:
            out.write(f"[Searching broader...]\n")
            out.write(text[:300] + "\n")

        count += 1
        if count % 20 == 0:
            print(f"  Progress: {count}/{total_queries}")

print(f"\nDone! {count} scenes extracted to {OUTPUT_FILE}")

json_data = []
for scene_name, spec in sorted(scene_queries.items()):
    fpath = os.path.join(CHAPTERS_DIR, spec["file"])
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        excerpts = []
        for kw in spec["keywords"]:
            for kw_found, line_num, excerpt in extract_context(text, kw, spec.get("context", 20)):
                excerpts.append({"keyword": kw_found, "line": line_num, "text": excerpt[:200]})
        json_data.append({"name": scene_name, "file": spec["file"], "excerpts": excerpts})

with open(OUTPUT_FILE.replace(".txt", ".json"), "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)
print(f"JSON index saved to {OUTPUT_FILE.replace('.txt', '.json')}")
