import re, os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")
OUTPUT_FILE = os.path.join(BASE_DIR, "reports", "scene_extracts.txt")

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

scene_queries = config.get("scene_keywords", {})

def extract_context(text, keyword, context_lines=15):
    lines = text.split('\n')
    result_parts = []
    for i, line in enumerate(lines):
        if keyword in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            prefix = f">>> [{keyword}] found at line {i+1}"
            excerpt = "\n".join(lines[start:end])
            result_parts.append(f"{prefix}\n{excerpt}\n")
    return result_parts

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("=" * 70 + "\n")
    out.write("  全部经典场景原文提取\n")
    out.write(f"  共 {len(scene_queries)} 个场景\n")
    out.write("=" * 70 + "\n\n")

    for scene_name, spec in scene_queries.items():
        fname = spec["file"]
        fpath = os.path.join(CHAPTERS_DIR, fname)

        if not os.path.exists(fpath):
            out.write(f"\n--- {scene_name} ---\n[FILE NOT FOUND]\n\n")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        out.write(f"\n\n{'─' * 70}\n")
        out.write(f"  【{scene_name}】\n")
        out.write(f"{'─' * 70}\n\n")

        found_any = False
        for kw in spec["keywords"]:
            extracts = extract_context(text, kw, spec.get("context", 15))
            if extracts:
                found_any = True
                for ext in extracts:
                    out.write(ext + "\n")

        if not found_any:
            out.write("[No exact match found, showing first 200 chars]\n")
            out.write(text[:200] + "\n")

        out.write("\n")

print(f"Done! Output saved to {OUTPUT_FILE}")
