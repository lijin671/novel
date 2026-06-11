import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "reports", "stylometric_quantitative.json")

with open(json_path, "r", encoding="utf-8") as f:
    d = json.load(f)

total_chars = d["total_chars"]

print("=" * 60)
print("  10 QUANTITATIVE STYLOMETRIC DIMENSIONS")
print(f"  Novel: Total {total_chars:,} chars, {d['chapter_count']} chapters")
print("=" * 60)

print("\n1. Chapter Length CV (Control)")
cl = d["chapter_length"]
print(f"   Mean: {cl['mean']:.0f}")
print(f"   Std:  {cl['std']:.0f}")
print(f"   CV:   {cl['cv']:.4f}")
if cl['cv'] < 0.15:
    print("   -> EXTREMELY STABLE chapter length")
else:
    print("   -> Moderate variation")

print("\n2. Sentence Length Distribution")
sl = d['sentence_length']
print(f"   Mean:   {sl['mean']:.1f} chars")
print(f"   Median: {sl['median']:.1f}")
print(f"   Std:    {sl['std']:.1f}")
dist = sl['distribution']
total_sent = sum(dist.values())
print(f"   Short (1-10):   {dist['1-5']+dist['6-10']:5d}  ({(dist['1-5']+dist['6-10'])/total_sent*100:.1f}%)")
print(f"   Mid   (11-30):  {dist['11-15']+dist['16-20']+dist['21-30']:5d}  ({(dist['11-15']+dist['16-20']+dist['21-30'])/total_sent*100:.1f}%)")
print(f"   Long  (31+):    {dist['31-50']+dist['51-100']+dist['101-999']:5d}  ({(dist['31-50']+dist['51-100']+dist['101-999'])/total_sent*100:.1f}%)")

print("\n3. Dialogue vs Narrative")
dp = d['dialogue_percent']
print(f"   Dialogue:  {dp:.1f}%")
print(f"   Narrative: {100-dp:.1f}%")
if dp > 30:
    print("   -> DIALOGUE-DRIVEN (typical for web novels)")

print("\n4. Lexical Richness (TTR)")
print(f"   Type-Token Ratio: {d['ttr']:.4f}")
print(f"   Hapax Legomena:   {d['hapax_ratio']:.4f}")

print("\n5. Word Length")
wl = d['word_length']
print(f"   Mean:   {wl['mean']:.2f} chars")
print(f"   Median: {wl['median']:.1f}")

print("\n6. Function Word Frequency (top 10 per 1K chars)")
fws = list(d["function_words_top20"].items())
for fw, cnt in fws[:10]:
    per_1k = cnt / total_chars * 1000
    print(f"   \\u{ord(fw):04X}: {per_1k:.2f}/1K chars")

print("\n7. POS Distribution (top 8)")
pos_map = {"v":"Verb","n":"Noun","r":"Pronoun","d":"Adverb","a":"Adj","c":"Conj","p":"Prep","nr":"Person"}
pos_total = sum(d.get("pos_top20", {}).values())
pos_items = list(d["pos_top20"].items())
for tag, cnt in pos_items[:8]:
    name = pos_map.get(tag, tag)
    print(f"   {tag:4s} ({name:8s}): {cnt/pos_total*100:.1f}%" if pos_total else f"   {tag:4s} ({name:8s}): {cnt}")

print("\n8. Sentiment Polarity")
sr = d["sentiment_ratio"]
print(f"   Positive/Negative ratio: {sr:.2f}")
if sr > 2:
    print("   -> STRONG POSITIVE BIAS")
elif sr > 1:
    print("   -> Mild positive bias")
else:
    print("   -> Neutral")

print("\n9-10. N-gram data available in JSON")

print("\n" + "=" * 60)
print("  Full JSON: reports/stylometric_quantitative.json")
print("=" * 60)
