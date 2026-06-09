"""Merge all 1000 chapters of 小说第二部 into one TXT file."""
import os
import glob

base = r"C:\ITS\MuMuAINovel\tmp\bandao-izone-nmixx-20260604"
output = os.path.join(base, "半岛_雨季未命名_第二部_完整版.txt")

# Get all pack directories in order
packs = sorted(glob.glob(os.path.join(base, "pack_*")))

total_lines = 0
total_chars = 0

with open(output, "w", encoding="utf-8") as out:
    for pack_dir in packs:
        chapters = sorted(glob.glob(os.path.join(pack_dir, "chapter_*.txt")))
        for ch_path in chapters:
            with open(ch_path, "r", encoding="utf-8") as f:
                content = f.read()
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")
            lines = content.count("\n")
            total_lines += lines
            total_chars += len(content)

print(f"Merge complete!")
print(f"Total packs: {len(packs)}")
print(f"Total lines: {total_lines}")
print(f"Total characters: {total_chars}")
print(f"Output: {output}")
