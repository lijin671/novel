import os, re, json, math
from collections import Counter
import jieba
import jieba.posseg as pseg
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters_renamed")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

POSITIVE_WORDS = config.get("emotion_positive", [])
NEGATIVE_WORDS = config.get("emotion_negative", [])

print("Reading chapters...")
all_text = ""
chapter_lengths = []
chapter_files = sorted([f for f in os.listdir(CHAPTERS_DIR) if f.endswith('.txt') and f[0].isdigit()],
                       key=lambda x: int(x.replace('.txt', '')))

for fname in chapter_files:
    fpath = os.path.join(CHAPTERS_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    all_text += text + "\n"
    chapter_lengths.append(len(text))

print(f"Total text length: {len(all_text)} chars")
print(f"Total chapters: {len(chapter_lengths)}")

cv = np.std(chapter_lengths) / np.mean(chapter_lengths)
print(f"\n=== Chapter Length CV: {cv:.4f} ===")
print(f"  Mean: {np.mean(chapter_lengths):.0f}, Std: {np.std(chapter_lengths):.0f}")
print(f"  Min: {min(chapter_lengths)}, Max: {max(chapter_lengths)}")

print("\n=== Sentence Length Distribution ===")
sentences = re.split(r'[。！？\n]+', all_text)
sentences = [s.strip() for s in sentences if len(s.strip()) > 2]
sent_lens = [len(s) for s in sentences]
print(f"  Total sentences: {len(sentences)}")
print(f"  Mean sentence length: {np.mean(sent_lens):.1f} chars")
print(f"  Std: {np.std(sent_lens):.1f}")
print(f"  Median: {np.median(sent_lens):.1f}")
print(f"  Min: {min(sent_lens)}, Max: {max(sent_lens)}")

bins = [(1,5),(6,10),(11,15),(16,20),(21,30),(31,50),(51,100),(101,999)]
print("  Distribution:")
for lo, hi in bins:
    cnt = sum(1 for l in sent_lens if lo <= l <= hi)
    pct = cnt / len(sent_lens) * 100
    print(f"    {lo:3d}-{hi:3d} chars: {cnt:6d} ({pct:5.1f}%)")

print("\n=== Dialogue / Narrative Ratio ===")
dialogue_chars = len(re.findall(r'「[^」]*」|"[^"]*"|『[^』]*』|\u201c[^\u201d]*\u201d', all_text))
total_chars = len(all_text.replace('\n','').replace(' ',''))
dialogue_pct = dialogue_chars / total_chars * 100
print(f"  Dialogue chars: {dialogue_chars} ({dialogue_pct:.1f}%)")
print(f"  Narrative chars: {total_chars - dialogue_chars} ({100-dialogue_pct:.1f}%)")

print("\n=== Word Segmentation (jieba) ===")
sample = all_text[:500000]
print("  Segmenting sample text (500K chars)...")
words = list(jieba.cut(sample))
total_words = len(words)
unique_words = len(set(words))

ttr = unique_words / total_words
print(f"  Total words (tokens): {total_words}")
print(f"  Unique words (types): {unique_words}")
print(f"  ** TTR (Type-Token Ratio): {ttr:.4f} **")

word_freq = Counter(words)
hapax = sum(1 for v in word_freq.values() if v == 1)
hapax_ratio = hapax / total_words
print(f"  Hapax Legomena (once-only): {hapax}")
print(f"  ** Hapax Ratio: {hapax_ratio:.4f} **")

word_lens = [len(w) for w in words]
wl_mean = np.mean(word_lens)
wl_median = np.median(word_lens)
print(f"  Mean word length: {wl_mean:.2f} chars")
print(f"  Median word length: {wl_median:.1f}")
print("  Word length distribution:")
wl_bins = [(1,1),(2,2),(3,3),(4,4),(5,6),(7,99)]
for lo, hi in wl_bins:
    cnt = sum(1 for l in word_lens if lo <= l <= hi)
    pct = cnt / total_words * 100
    print(f"    {lo:2d}-{hi:2d} chars: {cnt:6d} ({pct:5.1f}%)")

print("\n=== Function Word Frequency ===")
function_words = [
    '\u7684', '\u4e86', '\u5728', '\u662f', '\u548c', '\u4e5f', '\u5c31',
    '\u90fd', '\u800c', '\u4e0e', '\u6216', '\u53c8', '\u628a', '\u88ab',
    '\u7740', '\u8fc7', '\u5427', '\u5417', '\u5617', '\u5440',
    '\u5462', '\u554a', '\u561e', '\u5422', '\u4ece', '\u5bf9',
    '\u7531', '\u7528', '\u4ee5', '\u56e0', '\u4e3a', '\u6240\u4ee5',
    '\u4f46\u662f', '\u7136\u800c', '\u867d\u7136', '\u5982\u679c',
    '\u90a3\u4e48', '\u5e76\u4e14', '\u800c\u4e14', '\u6216\u8005',
]
fw_freq = {}
for fw in function_words:
    fw_freq[fw] = all_text.count(fw)
total_fw = sum(fw_freq.values())
print(f"  Total function word occurrences: {total_fw}")
print(f"  Frequency per 1000 chars:")
for fw in sorted(function_words, key=lambda x: -fw_freq.get(x,0))[:20]:
    freq_per_1k = fw_freq[fw] / len(all_text) * 1000
    print(f"    '{fw}': {fw_freq[fw]:6d} ({freq_per_1k:.2f}/1K chars)")

print("\n=== POS Tag Distribution ===")
print("  POS tagging sample (100K chars)...")
pos_words = list(pseg.cut(all_text[:100000]))
pos_counter = Counter()
for word, flag in pos_words:
    pos_counter[flag] += 1
total_pos = sum(pos_counter.values())
print(f"  Total POS-tagged words: {total_pos}")
print("  POS distribution (top 20):")
pos_map = {
    'n': 'noun', 'v': 'verb', 'a': 'adj', 'd': 'adv', 'p': 'prep',
    'c': 'conj', 'u': 'aux', 'm': 'numeral', 'q': 'quantifier',
    'r': 'pronoun', 'f': 'direction', 't': 'time', 'ns': 'place',
    'nr': 'person', 'x': 'unknown', 'w': 'punctuation',
    'vn': 'verb-noun', 'vd': 'verb-adv', 'an': 'adj-noun',
    'l': 'idiom', 'i': 'idiom', 'e': 'interj', 'o': 'onomat',
    'y': 'modal', 'k': 'suffix',
}
for (tag, cnt) in pos_counter.most_common(20):
    pct = cnt / total_pos * 100
    name = pos_map.get(tag, tag)
    print(f"    {tag:4s} ({name:10s}): {cnt:6d} ({pct:5.1f}%)")

print("\n=== N-gram (Bigram/Trigram) Top 30 ===")
text_sample = all_text[:300000]
words2 = list(jieba.cut(text_sample))
bigrams = Counter()
trigrams = Counter()
for i in range(len(words2)-1):
    bigrams[words2[i] + '|' + words2[i+1]] += 1
for i in range(len(words2)-2):
    trigrams[words2[i] + '|' + words2[i+1] + '|' + words2[i+2]] += 1

print("  Top 20 Bigrams:")
for bg, cnt in bigrams.most_common(20):
    parts = bg.split('|')
    print(f"    {' '.join(parts)}: {cnt}")

print("\n  Top 20 Trigrams:")
for tg, cnt in trigrams.most_common(20):
    parts = tg.split('|')
    print(f"    {' '.join(parts)}: {cnt}")

print("\n=== Rough Sentiment Analysis ===")
pos_count = sum(all_text.count(w) for w in POSITIVE_WORDS)
neg_count = sum(all_text.count(w) for w in NEGATIVE_WORDS)
print(f"  Positive word mentions: {pos_count}")
print(f"  Negative word mentions: {neg_count}")
print(f"  Pos/Neg ratio: {pos_count/max(neg_count,1):.2f}")

results = {
    "chapter_count": len(chapter_lengths),
    "total_chars": len(all_text),
    "chapter_length": {
        "mean": float(np.mean(chapter_lengths)),
        "std": float(np.std(chapter_lengths)),
        "cv": float(cv),
        "min": int(min(chapter_lengths)),
        "max": int(max(chapter_lengths)),
    },
    "sentence_length": {
        "mean": float(np.mean(sent_lens)),
        "std": float(np.std(sent_lens)),
        "median": float(np.median(sent_lens)),
        "distribution": {
            f"{lo}-{hi}": int(sum(1 for l in sent_lens if lo <= l <= hi))
            for lo, hi in bins
        }
    },
    "dialogue_percent": dialogue_pct,
    "ttr": ttr,
    "hapax_ratio": hapax_ratio,
    "word_length": {
        "mean": float(wl_mean),
        "median": float(wl_median),
    },
    "function_words_top20": {
        fw: fw_freq[fw] for fw in sorted(function_words, key=lambda x: -fw_freq.get(x,0))[:20]
    },
    "pos_top20": {tag: cnt for tag, cnt in pos_counter.most_common(20)},
    "bigram_top20": [bg for bg, cnt in bigrams.most_common(20)],
    "trigram_top20": [tg for tg, cnt in trigrams.most_common(20)],
    "sentiment_ratio": float(pos_count / max(neg_count,1)),
}

with open(os.path.join(OUTPUT_DIR, "stylometric_quantitative.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== Saved to stylometric_quantitative.json ===")
