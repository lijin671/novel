from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.bandao_batch_queue_plan import (
    BANDAO_START_CHAPTER,
    BANDAO_TARGET_TOTAL_CHAPTERS,
    BANDAO_TARGET_WORD_COUNT,
    build_bandao_chapter_expansion_plan,
)

REQUIRED_TERM_ALIASES = {
    "杨翠": ["杨翠", "Rene"],
    "张元英": ["张元英", "张员瑛", "元英", "员瑛", "Wonyoung"],
    "2019-04-01": ["2019-04-01", "2019年4月1日", "4月1日", "四月一日"],
    "2019-11": ["2019-11", "2019年11月", "2019 年 11 月", "11月", "十一月"],
    "2020-02-17": ["2020-02-17", "2020年2月17日", "2020 年 2 月 17 日", "2月17日", "二月十七日"],
    "2020-06-15": ["2020-06-15", "2020年6月15日", "2020 年 6 月 15 日", "6月15日", "六月十五日"],
    "2020-12-07": ["2020-12-07", "2020年12月7日", "2020 年 12 月 7 日", "12月7日", "十二月七日"],
    "2021-04-29": ["2021-04-29", "2021年4月29日", "2021 年 4 月 29 日", "4月29日", "四月二十九日"],
    "2021-12-01": ["2021-12-01", "2021年12月1日", "2021 年 12 月 1 日", "12月1日", "十二月一日"],
    "2022-05-02": ["2022-05-02", "2022年5月2日", "2022 年 5 月 2 日", "5月2日", "五月二日"],
    "风波": ["风波", "造假", "争议", "停摆"],
}

STAGE_GROUP_REQUIRED_TERMS = {
    "651-760": ["IVE"],
    "761-860": ["IVE"],
    "861-940": ["IVE", "LE SSERAFIM"],
    "941-1000": ["IVE", "LE SSERAFIM"],
}


def compact_word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def chapter_path(output_dir: Path, chapter_number: int) -> Path:
    return output_dir / f"chapter_{chapter_number:04d}.txt"


def required_terms_for_chapter(chapter_number: int, plan: dict[str, Any]) -> list[str]:
    terms = ["杨翠"]
    stage_title = str(plan.get("stage_title") or "")
    reality = str(plan.get("reality_timeline_constraints") or "")
    stage_range = str(plan.get("stage_range") or "")
    stage_start = int(str(plan.get("stage_range") or "0-0").split("-", 1)[0] or 0)
    stage_opening_chapter = chapter_number == stage_start
    near_stage_anchor = chapter_number in {231, 381, 461, 561, 651, 761, 861, 941}
    for name in plan.get("character_focus") or []:
        value = str(name).split("/")[0].strip()
        if (
            stage_opening_chapter
            and value
            and value not in terms
            and value not in {"IVE", "LE SSERAFIM", "IZ*ONE"}
        ):
            terms.append(value)
    if chapter_number == 201:
        terms.extend(["楼梯间", "张元英", "崔叡娜"])
    if stage_opening_chapter and near_stage_anchor:
        for marker in ["2019-04-01", "2019-11", "2020-02-17", "2020-06-15", "2020-12-07", "2021-04-29", "2021-12-01", "2022-05-02"]:
            if marker in reality:
                terms.append(marker)
        if "HEART*IZ" in reality or "HEART*IZ" in stage_title:
            terms.extend(["HEART*IZ", "Violeta"])
        if "造假" in reality or "风波" in stage_title:
            terms.extend(["Produce", "风波"])
        for term in STAGE_GROUP_REQUIRED_TERMS.get(stage_range, []):
            if term not in terms:
                terms.append(term)
    return list(dict.fromkeys(terms))


def forbidden_terms_for_chapter() -> list[str]:
    return [
        "杨翠加入IVE",
        "Rene加入IVE",
        "杨翠成为IVE成员",
        "Rene成为IVE成员",
        "杨翠加入LE SSERAFIM",
        "Rene加入LE SSERAFIM",
        "杨翠成为LE SSERAFIM成员",
        "Rene成为LE SSERAFIM成员",
        "公开恋情",
        "官宣恋情",
    ]


def required_term_present(term: str, text: str) -> bool:
    aliases = REQUIRED_TERM_ALIASES.get(term, [term])
    return any(alias in text for alias in aliases)


def audit_chapter(*, artifact_dir: Path, output_dir: Path, chapter_number: int, required_word_count: int) -> dict[str, Any]:
    path = chapter_path(output_dir, chapter_number)
    if not path.exists():
        return {
            "chapter_number": chapter_number,
            "path": str(path),
            "passed": False,
            "reason": "missing_file",
            "word_count": 0,
            "missing_terms": [],
            "forbidden_hits": [],
        }
    text = path.read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", text)
    word_count = compact_word_count(text)
    plan = build_bandao_chapter_expansion_plan(chapter_number, artifact_dir)
    required_terms = required_terms_for_chapter(chapter_number, plan)
    missing_terms = [term for term in required_terms if not required_term_present(term, text)]
    forbidden_hits = [term for term in forbidden_terms_for_chapter() if term in compact]
    reasons = []
    if word_count < required_word_count:
        reasons.append("short_chapter")
    if missing_terms:
        reasons.append("missing_required_terms")
    if forbidden_hits:
        reasons.append("forbidden_terms")
    return {
        "chapter_number": chapter_number,
        "path": str(path),
        "passed": not reasons,
        "reasons": reasons,
        "word_count": word_count,
        "required_word_count": required_word_count,
        "required_terms": required_terms,
        "missing_terms": missing_terms,
        "forbidden_hits": forbidden_hits,
        "stage_title": plan.get("stage_title"),
        "stage_range": plan.get("stage_range"),
    }


def audit_pack(
    *,
    artifact_dir: Path,
    output_dir: Path,
    start_chapter: int = BANDAO_START_CHAPTER,
    end_chapter: int = BANDAO_TARGET_TOTAL_CHAPTERS,
    required_word_count: int = BANDAO_TARGET_WORD_COUNT,
) -> dict[str, Any]:
    chapters = [
        audit_chapter(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            chapter_number=chapter_number,
            required_word_count=required_word_count,
        )
        for chapter_number in range(start_chapter, end_chapter + 1)
    ]
    failed = [item for item in chapters if not item["passed"]]
    report = {
        "type": "bandao_real_ai_regression_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        "required_word_count": required_word_count,
        "chapter_count": len(chapters),
        "passed": not failed,
        "passed_chapter_count": len(chapters) - len(failed),
        "failed_chapter_count": len(failed),
        "failed_chapters_preview": failed[:20],
        "chapters": chapters,
        "note": "逐章回归审查：字数、关键人物、阶段现实时间线、组织边界、禁止改写真实阵容。该审查用于机器门禁，不替代人工文学精读。",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "real_ai_regression_audit_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report
