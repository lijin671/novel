import os, json, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

print("=" * 60)
print("SELF-AUDIT: Template Project Integrity Check")
print("=" * 60)

issues = []
warnings = []

print("\n[1/5] File Existence Check...")
expected_items = {
    "config.json": BASE_DIR,
    "split_chapters.py": BASE_DIR,
    "rename_chapters.py": BASE_DIR,
    "auto_analyze.py": BASE_DIR,
    "stylometric_quantitative.py": BASE_DIR,
    "fix_dialogue.py": BASE_DIR,
    "display_results.py": BASE_DIR,
    "show_results.py": BASE_DIR,
    "extract_scenes.py": BASE_DIR,
    "extract_all_scenes.py": BASE_DIR,
    "scan_all.py": BASE_DIR,
    "self_audit.py": BASE_DIR,
    "novel.txt": BASE_DIR,
    "stylometric_quantitative.json": REPORTS_DIR,
    "scene_extracts.json": REPORTS_DIR,
}
for name, dirpath in expected_items.items():
    if not os.path.exists(os.path.join(dirpath, name)):
        warnings.append(f"MISSING: {name}")

if not issues:
    print("  All expected files present!")

print("\n[2/5] Config Integrity...")
config_path = os.path.join(BASE_DIR, "config.json")
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if "characters" in cfg and "themes" in cfg:
        print(f"  Config OK: {len(cfg['characters'])} characters, {len(cfg['themes'])} themes")
    else:
        issues.append("Config missing 'characters' or 'themes'")

print("\n[3/5] Chapter Directory Check...")
ch_dir = os.path.join(BASE_DIR, "chapters_renamed")
if os.path.exists(ch_dir):
    ch_files = [f for f in os.listdir(ch_dir) if f.endswith('.txt')]
    print(f"  Chapter files: {len(ch_files)}")
else:
    warnings.append("chapters_renamed/ not found (run split+rename first)")

print("\n[4/5] Reports Check...")
if os.path.exists(REPORTS_DIR):
    report_files = os.listdir(REPORTS_DIR)
    print(f"  Reports: {len(report_files)} files")
else:
    warnings.append("reports/ not found")

print("\n[5/5] Source Novel Check...")
novel_path = os.path.join(BASE_DIR, "novel.txt")
if os.path.exists(novel_path):
    size = os.path.getsize(novel_path)
    print(f"  novel.txt: {size/1024:.1f}KB")
else:
    warnings.append("novel.txt not found (place your novel text here)")

print("\n" + "=" * 60)
print("AUDIT SUMMARY")
print("=" * 60)
print(f"  Issues:   {len(issues)}")
print(f"  Warnings: {len(warnings)}")
if issues:
    print("\n  ISSUES:")
    for i in issues:
        print(f"    [ERR] {i}")
if warnings:
    print("\n  WARNINGS:")
    for w in warnings:
        print(f"    [WARN] {w}")
if not issues and not warnings:
    print("\n  *** ALL CHECKS PASSED ***")
