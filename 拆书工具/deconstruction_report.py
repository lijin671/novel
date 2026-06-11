"""12维度拆解报告生成器
按统一模板生成单部作品的拆解报告（Markdown格式），
结果存入 deconstruction/ 目录，供 cross_compare.py 跨作品对比。
"""
import os, json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_DIR = os.path.join(BASE_DIR, "deconstruction")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DIMENSION_NAMES = {
    "D1": "剧情结构", "D2": "节奏控制", "D3": "人物体系",
    "D4": "爽点类型", "D5": "金句体系", "D6": "战斗/冲突",
    "D7": "世界构建", "D8": "力量体系", "D9": "对话技法",
    "D10": "环境描写", "D11": "伏笔/悬念", "D12": "情感线",
}

DIMENSION_PROMPTS = {
    "D1": "三幕/起承转合划分、开篇钩子方式、高潮设计、收尾方式",
    "D2": "爽点间隔（小/中/大高潮）、黄金三章节奏、情绪曲线",
    "D3": "主角公式（能力+道德+性格+反差）、女主原型、配角功能表",
    "D4": "身份反差/权谋反转/情感突破/地位升级/战斗碾压等类型",
    "D5": "章末金句、对话名句、哲理句，至少提取20条",
    "D6": "单挑/小规模冲突/大军团作战的分镜技巧",
    "D7": "地理/历史/政治体制/经济系统/文化宗教",
    "D8": "等级体系/能力分类/晋升代价/突破模式",
    "D9": "对话如何推进剧情、塑造性格、埋设伏笔",
    "D10": "山水场景/城市风貌/建筑室内/服饰器物",
    "D11": "长线伏笔铺设与回收、中线悬念、短线钩子",
    "D12": "CP模式、感情节奏推进、虐点甜点分布",
}

def generate_report(work_name, author, word_count=None, genre=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', work_name)
    filename = f"{safe_name}_拆解报告.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    lines = [
        f"# {work_name} 拆解报告",
        f"",
        f"> 生成时间：{timestamp}",
        f"> 作者：{author or '（待填）'}",
        f"> 字数：{word_count or '（待填）'}",
        f"> 类型：{genre or '（待填）'}",
        f"",
        f"---",
        f"",
    ]

    for dim_id in [f"D{i}" for i in range(1, 13)]:
        name = DIMENSION_NAMES[dim_id]
        prompt = DIMENSION_PROMPTS[dim_id]
        lines += [
            f"## {dim_id} {name}",
            f"",
            f"**分析要点**：{prompt}",
            f"",
            f"### 关键发现",
            f"",
            f"（填写分析结果）",
            f"",
            f"### 可复用模板/公式",
            f"",
            f"（提取可直接迁移的模式）",
            f"",
            f"### 与当前作品的差异",
            f"",
            f"（对比已有的作品，记录异同）",
            f"",
            f"---",
            f"",
        ]

    lines += [
        f"## 综合评分卡",
        f"",
        f"| 维度 | 评分(1-10) | 备注 |",
        f"|------|-----------|------|",
    ]
    for dim_id in [f"D{i}" for i in range(1, 13)]:
        lines.append(f"| {dim_id} {DIMENSION_NAMES[dim_id]} | （填） |（填） |")

    lines += [
        f"",
        f"## 首次阅读笔记",
        f"",
        f"- 黄金开篇章节：",
        f"- 爽点高潮章节：",
        f"- 权谋转折章节：",
        f"- 战斗名场面：",
        f"- 情感高光章节：",
        f"- 章末金句摘录：",
        f"",
        f"---",
        f"",
        f"*报告由 deconstruction_report.py 自动生成*",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已生成：{filepath}")
    return filepath

def batch_generate():
    print("=" * 50)
    print("12维度拆解报告生成器")
    print("=" * 50)
    work_name = input("作品名称：").strip() or "未命名作品"
    author = input("作者：").strip()
    word_count = input("字数：").strip()
    genre = input("类型：").strip()
    filepath = generate_report(work_name, author, word_count, genre)
    print(f"\n完成！请在 {filepath} 中填写分析内容。")
    print("填写完毕后，运行 cross_compare.py 进行跨作品对比。")

if __name__ == "__main__":
    import re
    batch_generate()
