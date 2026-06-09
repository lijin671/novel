from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app.services.bandao_batch_queue_plan import (
    BANDAO_TARGET_TOTAL_CHAPTERS,
    BANDAO_TARGET_WORD_COUNT,
    build_bandao_chapter_expansion_plan,
)


def _compact_word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def _chapter_title(chapter_number: int, plan: dict[str, Any]) -> str:
    if chapter_number == 201:
        return "第201章 沉默的清晨"
    expansion = build_bandao_chapter_expansion_plan(chapter_number, plan["artifact_dir"])
    return f"第{chapter_number}章 {expansion['stage_title']}"


def _load_json(artifact_dir: Path, filename: str) -> dict[str, Any]:
    return json.loads((artifact_dir / filename).read_text(encoding="utf-8"))


def _repeat_until_target(paragraphs: list[str], *, target_word_count: int) -> str:
    text_parts = list(paragraphs)
    seed = list(paragraphs[1:]) or list(paragraphs)
    index = 0
    while _compact_word_count("\n\n".join(text_parts)) < target_word_count:
        base = seed[index % len(seed)]
        index += 1
        text_parts.append(
            base.replace("这一章", "这一段")
            + f"\n\n第{index}次回到同一个约束：情绪可以推进，现实时间线不能被改写。"
        )
    return "\n\n".join(text_parts)


def build_bandao_sample_chapter_text(
    chapter_number: int,
    *,
    artifact_dir: Path,
    target_word_count: int = 1200,
) -> str:
    """生成受限烟测章节正文。

    该函数只用于验证拆书续写链路能把章节规划、现实约束和人物焦点落到正文样本里。
    它不声称生成 800 章完整商业正文。
    """
    expansion = build_bandao_chapter_expansion_plan(chapter_number, artifact_dir)
    title = "第201章 沉默的清晨" if chapter_number == 201 else f"第{chapter_number}章 {expansion['stage_title']}"
    focus = "、".join(expansion.get("character_focus") or [])
    goals = "；".join(expansion.get("stage_goals") or expansion.get("key_events") or [])
    constraints = str(expansion.get("reality_timeline_constraints") or "").strip()
    guardrails = "；".join(str(item) for item in expansion.get("guardrails") or [])

    if chapter_number == 201:
        paragraphs = [
            title,
            "承接第200章，宿舍没有真正睡着。杨翠把楼梯间那一下呼吸压回胸口，像把一枚还发烫的奖牌藏进掌心。张元英在下铺尽量放轻动作，崔叡娜背过身，却把沉默留得比玩笑更响。",
            "清晨洗漱时，金珉周看见杨翠避开镜子里的视线，也看见张元英比平常更早把笑容挂回脸上。没有人提楼梯间，没有人提奖励。她们都知道，IZ*ONE 的日程不会因为谁心跳乱了就停下来。",
            f"这一章的人物焦点是{focus}。权恩菲把成员往车上赶，崔叡娜用一句轻飘飘的玩笑试探杨翠，杨翠只笑了一下，没有接。张元英坐在后排，手指按着手机边缘，像还记得昨晚那句一起等。",
            "车窗外的首尔还没完全亮，车内已经有化妆包、早餐袋和经纪人的提醒声。杨翠明白，所谓不公开恋情不是一句安全提示，而是她们还能继续站在舞台上的现实条件。",
            "本章规划锚点：" + expansion["plot_summary"] + " 场景推进：" + expansion["scene_plan"] + "。必须守住的近端边界包括：不公开恋情、不让崔叡娜立刻摊牌、不跳到解散后。",
            "到练习室后，音乐一响，所有私人情绪都被拍子切开。杨翠站在队形里，余光扫到张元英，又被崔叡娜捕捉到。叡娜没有说破，只在换队形时撞了撞她的肩，像平常那样笑，笑意却没有落到眼底。",
            "夜里短暂独处时，杨翠只说不能急。张元英点头，说她记得。门外有脚步声停了一下，很快离开。杨翠没有追出去，因为她知道，有些关系不能靠解释立刻修好，只能在之后的每一天里慢慢偿还。",
        ]
    else:
        late_line = ""
        if chapter_number >= 761:
            late_line = (
                "后 IZ*ONE 阶段，杨翠 / Rene 继续走 solo、制作合作和跨国资源线，"
                "不加入 IVE 或 LE SSERAFIM 固定阵容；张元英与安宥真按现实归入 IVE，"
                "宫胁咲良与金采源按现实归入 LE SSERAFIM。"
            )
        paragraphs = [
            title,
            f"这一章处在“{expansion['stage_title']}”阶段。章节目标不是重启一本新书，而是在原世界观里继续推进杨翠 / Rene 的事业、队内牵连和情感克制。",
            f"人物焦点：{focus}。阶段目标：{goals}。杨翠仍然习惯先照顾别人，再把自己的选择往后放；张元英、崔叡娜、金珉周留下的关系压力不会因为时间推进而消失。",
            f"现实时间线约束：{constraints or '沿用已确认的 IZ*ONE 活动期与后续成员归属。'}",
            f"硬边界：{guardrails}。{late_line}",
            "这一章的写法保持宿舍、练习室、后台、车内和公司会议之间的切换。事业节点只推进一个，情感节点也只推进一个，避免用突兀公开、退团或换团制造廉价冲突。",
            "杨翠听完行程安排，没有立刻回答。她先确认成员们接下来的舞台、采访和个人资源，再把自己的名字放到最后。这个习惯让她显得稳定，也让身边的人更容易看出她什么时候在硬撑。",
            "当现实节点压下来，承诺就不再是楼梯间里一句轻声的话，而会变成日程表、合同、粉丝视线和公司会议里的每一次取舍。她能做的不是改写现实，而是在现实留下的缝隙里，把关系和作品都守住。",
        ]

    return _repeat_until_target(paragraphs, target_word_count=target_word_count)


def build_bandao_sample_continuation_pack(
    *,
    artifact_dir: Path,
    output_dir: Path,
    chapter_numbers: Iterable[int],
    target_word_count: int = 1200,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    samples = []
    for chapter_number in chapter_numbers:
        text = build_bandao_sample_chapter_text(
            int(chapter_number),
            artifact_dir=artifact_dir,
            target_word_count=target_word_count,
        )
        path = output_dir / f"chapter_{int(chapter_number):04d}_sample.txt"
        path.write_text(text, encoding="utf-8")
        samples.append(
            {
                "chapter_number": int(chapter_number),
                "path": str(path),
                "word_count": _compact_word_count(text),
            }
        )

    manifest = {
        "type": "bandao_sample_continuation_pack",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "target_total_chapters": BANDAO_TARGET_TOTAL_CHAPTERS,
        "full_target_word_count_per_chapter": BANDAO_TARGET_WORD_COUNT,
        "sample_target_word_count": target_word_count,
        "chapter_count": len(samples),
        "sample_chapters": [item["chapter_number"] for item in samples],
        "samples": samples,
        "contains_full_800_chapter_text": False,
        "note": "受限烟测样本文包：验证拆书续写约束能进入正文，不代表已完成 800 章万字正文。",
    }
    manifest_path = output_dir / "sample_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**manifest, "manifest_path": manifest_path}


def validate_bandao_sample_continuation_pack(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required_by_chapter = {
        201: ["杨翠", "张元英", "崔叡娜", "金珉周", "不公开恋情", "第200章"],
        231: ["HEART*IZ", "杨翠"],
        381: ["2019-11", "Produce 系列投票造假争议"],
        761: ["2021-12-01", "IVE", "不加入 IVE 或 LE SSERAFIM 固定阵容"],
        1000: ["2021-04-29", "IVE", "LE SSERAFIM", "不加入 IVE 或 LE SSERAFIM 固定阵容"],
    }
    chapters: dict[str, Any] = {}
    passed = True
    min_word_count = None
    for item in manifest.get("samples") or []:
        chapter_number = int(item["chapter_number"])
        path = Path(item["path"])
        text = path.read_text(encoding="utf-8")
        word_count = _compact_word_count(text)
        min_word_count = word_count if min_word_count is None else min(min_word_count, word_count)
        required_terms = required_by_chapter.get(chapter_number, ["杨翠"])
        missing_terms = [term for term in required_terms if term not in text]
        chapter_passed = word_count >= int(manifest.get("sample_target_word_count") or 0) and not missing_terms
        passed = passed and chapter_passed
        chapters[str(chapter_number)] = {
            "path": str(path),
            "word_count": word_count,
            "missing_terms": missing_terms,
            "required_terms_present": not missing_terms,
            "passed": chapter_passed,
        }

    report = {
        "passed": passed,
        "manifest_path": str(manifest_path),
        "target_total_chapters": manifest.get("target_total_chapters"),
        "sample_chapter_count": len(manifest.get("samples") or []),
        "min_word_count": min_word_count or 0,
        "contains_full_800_chapter_text": bool(manifest.get("contains_full_800_chapter_text")),
        "chapters": chapters,
    }
    report_path = manifest_path.parent / "sample_validation_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**report, "report_path": report_path}
