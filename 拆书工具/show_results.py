import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "reports", "stylometric_quantitative.json")

with open(json_path, "r", encoding="utf-8") as f:
    d = json.load(f)

total_chars = d["total_chars"]

print("=" * 55)
print("   10项量化文风指纹 - 完整结果")
print("=" * 55)

print("\nA. 章节长度变异系数")
cl = d["chapter_length"]
print(f"   均值: {cl['mean']:.0f}  标准差: {cl['std']:.0f}")
print(f"   CV系数: {cl['cv']:.4f}  → {'极其稳定' if cl['cv']<0.15 else '中等稳定'}")
print(f"   范围: {cl['min']} ~ {cl['max']}")

print("\nB. 句长分布与方差")
sl = d["sentence_length"]
print(f"   均值: {sl['mean']:.1f}字符  中位数: {sl['median']:.1f}")
print(f"   标准差: {sl['std']:.1f}  CV: {sl['std']/sl['mean']:.2f}")
dist = sl["distribution"]
print(f"   分布: 短句(1-10): {dist['1-5']+dist['6-10']}")
print(f"         中句(11-30): {dist['11-15']+dist['16-20']+dist['21-30']}")
print(f"         长句(31+): {dist['31-50']+dist['51-100']+dist['101-999']}")

print("\nC. 对话/叙述比例")
print(f"   对话: {d['dialogue_percent']}%")
print(f"   叙述: {100-d['dialogue_percent']}%")
print(f"   特征: {'对话驱动型' if d['dialogue_percent']>30 else '叙述驱动型'}")

print("\nD. 词汇丰富度TTR")
print(f"   TTR: {d['ttr']:.4f}  (类符/形符比)")
print(f"   Hapax Ratio: {d['hapax_ratio']:.4f}  (仅出现一次词比例)")

print("\nE. 词长分布")
wl = d["word_length"]
print(f"   均值: {wl['mean']:.2f}字符")

print("\nF. 高频虚词频率 (Top 8)")
fws = list(d["function_words_top20"].items())
for fw, cnt in fws[:8]:
    per_1k = cnt / total_chars * 1000
    print(f"   {fw}: {cnt:6d}次 ({per_1k:.2f}/1K字符)")

print("\nG. 词性分布 (Top 8)")
pos_names = {"v":"动词","n":"名词","r":"代词","d":"副词","a":"形容词","c":"连词","p":"介词","nr":"人名","uj":"助词的","m":"数词","ul":"助词了"}
pos_total = sum(d.get("pos_top20", {}).values())
for tag, cnt in list(d.get("pos_top20", {}).items())[:8]:
    name = pos_names.get(tag, tag)
    print(f"   {tag} ({name}): {cnt:6d} ({cnt/pos_total*100:.1f}%)" if pos_total else f"   {tag} ({name}): {cnt}")

print("\nH. 情感极性比")
print(f"   Pos/Neg: {d['sentiment_ratio']:.2f}")

print("\nI. 高频Bigram (Top 10)")
for bg in d.get("bigram_top20", [])[:10]:
    parts = bg.split("|")
    print(f"   {' '.join(parts)}")

print("\nJ. 高频Trigram (Top 5)")
for tg in d.get("trigram_top20", [])[:5]:
    parts = tg.split("|")
    print(f"   {' '.join(parts)}")

print("\n" + "=" * 55)
print("   完整JSON已保存: stylometric_quantitative.json")
print("=" * 55)
