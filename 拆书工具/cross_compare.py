"""跨作品对比表生成器
扫描 deconstruction/ 目录下的所有拆解报告，
为每个维度生成一份跨作品横向对比表（Markdown格式），
结果存入 reports/cross_compare/。
"""
import os, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DECON_DIR = os.path.join(BASE_DIR, "deconstruction")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "cross_compare")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DIMENSION_NAMES = {
    "D1": "剧情结构", "D2": "节奏控制", "D3": "人物体系",
    "D4": "爽点类型", "D5": "金句体系", "D6": "战斗/冲突",
    "D7": "世界构建", "D8": "力量体系", "D9": "对话技法",
    "D10": "环境描写", "D11": "伏笔/悬念", "D12": "情感线",
}

def extract_dimension_section(report_text, dim_id):
    """从拆解报告中提取某个维度的分析内容"""
    pattern = rf"## {re.escape(dim_id)} .*?\n(.*?)(?=\n## (?:D\d|综合评分卡|首次阅读笔记|---|$))"
    match = re.search(pattern, report_text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content[:300]
    return "（未填写）"

def generate_comparison_table():
    if not os.path.exists(DECON_DIR):
        print("错误：deconstruction/ 目录不存在。请先运行 deconstruction_report.py 生成报告。")
        return

    report_files = sorted([f for f in os.listdir(DECON_DIR) if f.endswith(".md")])
    if not report_files:
        print("错误：deconstruction/ 目录下没有拆解报告。")
        return

    work_names = []
    reports_text = []
    for fname in report_files:
        fpath = os.path.join(DECON_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        reports_text.append(text)
        title_match = re.search(r"^# (.+?)(?:\n|$)", text)
        work_names.append(title_match.group(1) if title_match else fname.replace("_拆解报告.md", ""))

    for dim_id in [f"D{i}" for i in range(1, 13)]:
        dim_name = DIMENSION_NAMES[dim_id]
        lines = [
            f"# 跨作品对比：{dim_id} {dim_name}",
            f"",
            f"> 由 cross_compare.py 自动生成 | 共 {len(work_names)} 部作品",
            f"",
            f"| 作品 | {dim_name}核心特征 | 可复用模板 |",
            f"|------|------------------|------------|",
        ]
        for i, text in enumerate(reports_text):
            content = extract_dimension_section(text, dim_id)
            short_content = content[:100].replace("\n", " ").replace("|", "/")
            lines.append(f"| {work_names[i]} | {short_content} | （提取关键模式） |")

        lines += [
            f"",
            f"## 总结",
            f"",
            f"### 共同规律",
            f"",
            f"（填写多部作品共有的模式）",
            f"",
            f"### 差异化创新点",
            f"",
            f"（填写某部作品独有的技巧）",
            f"",
            f"### 当前作品可迁移项",
            f"",
            f"| 来源作品 | 可迁移模板 | 当前作品的用法 |",
            f"|----------|------------|----------------|",
            f"|（作品名）|（提取的模式）|（如何改造使用）|",
            f"",
            f"---",
            f"",
            f"*由 cross_compare.py 自动生成，需手动填充内容*",
        ]

        safe_name = dim_id
        filepath = os.path.join(OUTPUT_DIR, f"compare_{safe_name}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"已生成：{filepath}")

    print(f"\n完成！共 {len(work_names)} 部作品，12 个维度对照表已保存至 {OUTPUT_DIR}")

def generate_all_in_one():
    """生成一份总览表，包含所有维度的简略对比"""
    if not os.path.exists(DECON_DIR):
        print("错误：deconstruction/ 目录不存在。")
        return

    report_files = sorted([f for f in os.listdir(DECON_DIR) if f.endswith(".md")])
    if not report_files:
        print("错误：deconstruction/ 目录下没有拆解报告。")
        return

    work_names = []
    reports_text = []
    for fname in report_files:
        fpath = os.path.join(DECON_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        reports_text.append(text)
        title_match = re.search(r"^# (.+?)(?:\n|$)", text)
        work_names.append(title_match.group(1) if title_match else fname.replace("_拆解报告.md", ""))

    lines = [
        f"# 跨作品总览对照表",
        f"",
        f"> 由 cross_compare.py 自动生成 | 共 {len(work_names)} 部作品",
        f"",
    ]

    for dim_id in [f"D{i}" for i in range(1, 13)]:
        dim_name = DIMENSION_NAMES[dim_id]
        lines += [
            f"## {dim_id} {dim_name}",
            f"",
            f"| 作品 | 关键特征 |",
            f"|------|----------|",
        ]
        for i, text in enumerate(reports_text):
            content = extract_dimension_section(text, dim_id)
            short = content[:80].replace("\n", " ")
            lines.append(f"| {work_names[i]} | {short} |")
        lines.append("")

    filepath = os.path.join(OUTPUT_DIR, "compare_ALL.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"总览表已生成：{filepath}")

if __name__ == "__main__":
    print("=" * 50)
    print("跨作品对比表生成器")
    print("=" * 50)
    print("1. 逐个维度生成对照表")
    print("2. 生成总览表（推荐）")
    choice = input("请选择 (1/2，默认2)：").strip() or "2"

    if choice == "1":
        generate_comparison_table()
    else:
        generate_all_in_one()

    print("\n提示：生成的 markdown 文件需要手动填充分析内容。")
