from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch_generation_task import BatchGenerationTask
from app.models.chapter import Chapter
from app.models.outline import Outline
from app.models.project import Project

BANDAO_EXPECTED_SOURCE_SHA256 = "3ab0897d497a1804b4b1052f927d34fa2bcf9a5f8212e4711e9f33b70ca5b823"
BANDAO_SOURCE_CHAPTERS = 200
BANDAO_TARGET_TOTAL_CHAPTERS = 1000
BANDAO_START_CHAPTER = 201
BANDAO_CONTINUATION_COUNT = 800
BANDAO_TARGET_WORD_COUNT = 10000


def _load_artifact_json(artifact_dir: Path, filename: str) -> dict[str, Any]:
    path = artifact_dir / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_stage_range(range_text: str) -> tuple[int, int] | None:
    if "-" not in range_text:
        return None
    start_text, end_text = range_text.split("-", 1)
    try:
        return int(start_text), int(end_text)
    except ValueError:
        return None


def _find_stage_for_chapter(chapter_number: int, plan: dict[str, Any]) -> dict[str, Any]:
    for stage in plan.get("stage_plan") or []:
        parsed_range = _parse_stage_range(str(stage.get("range") or ""))
        if not parsed_range:
            continue
        start, end = parsed_range
        if start <= chapter_number <= end:
            return stage
    return {"range": f"{chapter_number}-{chapter_number}", "title": "续写", "goals": []}


def _guardrail_rules(bible: dict[str, Any], chapter_outline: dict[str, Any]) -> list[str]:
    rules: list[str] = []
    for item in bible.get("hard_constraints") or []:
        if isinstance(item, dict):
            rule = str(item.get("rule") or "").strip()
        else:
            rule = str(item or "").strip()
        if rule:
            rules.append(rule)
    for rule in chapter_outline.get("must_not_do") or []:
        rule_text = str(rule or "").strip()
        if rule_text:
            rules.append(rule_text)

    # 批量续写时每章都需要携带的现实边界，避免生成器为了戏剧冲突改写真实团体阵容。
    fixed_rules = [
        "不公开恋情",
        "不加入 IVE 或 LE SSERAFIM 固定阵容",
        "不改写 IZ*ONE 于 2021-04-29 活动结束的现实节点",
    ]
    for rule in fixed_rules:
        if rule not in rules:
            rules.append(rule)
    return rules


def _reality_events_for_stage(stage_title: str, stage_range: str, timeline: dict[str, Any]) -> list[str]:
    events = timeline.get("events") or []
    constraints_by_stage = {
        "201-230": ["2019-02-06", "2019-04-01"],
        "231-300": ["2019-02-06", "2019-04-01"],
        "301-380": ["2019-06-26", "2019-09-25"],
        "381-460": ["2019-11"],
        "461-560": ["2020-02-17", "2020-06-15"],
        "561-650": ["2020-12-07", "2021-03-13/2021-03-14", "2021-04-29"],
        "651-760": ["2021-04-29", "2021-12-01"],
        "761-860": ["2021-04-29", "2021-12-01"],
        "861-940": ["2021-04-29", "2021-12-01", "2022-05-02"],
        "941-1000": ["2021-04-29", "2021-12-01", "2022-05-02"],
    }
    wanted_dates = set(constraints_by_stage.get(stage_range, []))

    if "HEART*IZ" in stage_title:
        wanted_dates.add("2019-04-01")
    if "风波" in stage_title or "停摆" in stage_title:
        wanted_dates.add("2019-11")
    if "IVE" in stage_title:
        wanted_dates.update(["2021-04-29", "2021-12-01"])
    if "LE SSERAFIM" in stage_title:
        wanted_dates.update(["2021-04-29", "2022-05-02"])

    selected: list[str] = []
    for event in events:
        date = str(event.get("date") or "")
        text = str(event.get("event") or "")
        if date in wanted_dates:
            selected.append(f"{date}：{text}")

    decision = str(timeline.get("continuation_decision") or "").strip()
    if decision and any(marker in stage_title for marker in ["IVE", "LE SSERAFIM", "公开边界", "solo"]):
        selected.append(decision)
    return selected


def _chapter_201_plan(
    *,
    chapter_outline: dict[str, Any],
    bible: dict[str, Any],
    timeline: dict[str, Any],
    stage: dict[str, Any],
    guardrails: list[str],
) -> dict[str, Any]:
    scenes = chapter_outline.get("scenes") or []
    scene_plan = "；".join(
        f"{scene.get('scene')}：{scene.get('purpose')}"
        for scene in scenes
        if isinstance(scene, dict) and scene.get("scene")
    )
    stage_range = str(stage.get("range") or "201-230")
    stage_title = str(stage.get("title") or "楼梯间余波与日常修罗场")
    reality_constraints = _reality_events_for_stage(stage_title, stage_range, timeline)
    return {
        "plot_summary": (
            "承接第200章，进入第201章《沉默的清晨》："
            "杨翠 / Rene、张元英与崔叡娜都要把楼梯间秘密亲吻后的余波压回宿舍和行程里，"
            "金珉周作为安静观察者察觉细节，权恩菲负责把队伍带回 IZ*ONE 的日常秩序。"
        ),
        "key_events": [
            str(chapter_outline.get("continuity_anchor") or ""),
            "崔叡娜先以沉默和玩笑试探，不立刻摊牌。",
            "张元英维持忙内状态，与杨翠继续遵守等待承诺。",
            "用节目补拍、练习室和车内日程压住私人情绪。",
        ],
        "character_focus": ["杨翠 / Rene", "张元英", "崔叡娜", "金珉周", "权恩菲"],
        "emotional_tone": "克制、心虚、暗流涌动，表面仍是 IZ*ONE 群像日常。",
        "narrative_goal": "把第200章的秘密后果落到次日生活，并为张元英、崔叡娜、金珉周三线情感张力定调。",
        "conflict_type": "队内秘密、偶像职业约束、成员观察与回避。",
        "scene_plan": scene_plan,
        "target_word_count": int(chapter_outline.get("target_word_count") or BANDAO_TARGET_WORD_COUNT),
        "estimated_words": int(chapter_outline.get("target_word_count") or BANDAO_TARGET_WORD_COUNT),
        "stage_range": stage_range,
        "stage_title": stage_title,
        "stage_goals": stage.get("goals") or [],
        "reality_timeline_constraints": "\n".join(reality_constraints),
        "guardrails": guardrails,
        "source_bible_anchor": bible.get("world_rules", {}).get("hard_reality_rule", ""),
    }


def build_bandao_chapter_expansion_plan(chapter_number: int, artifact_dir: Path) -> dict[str, Any]:
    """构建《混在半岛的日子》201-1000 章的章节级展开规划。

    这里不生成正文，只把阶段计划、现实时间线和人物关系边界写入每章占位记录，
    供后续批量生成时作为可审计的章节约束。
    """
    if chapter_number < BANDAO_START_CHAPTER or chapter_number > BANDAO_TARGET_TOTAL_CHAPTERS:
        raise ValueError(f"章节号必须在 {BANDAO_START_CHAPTER}-{BANDAO_TARGET_TOTAL_CHAPTERS} 之间")

    plan = _load_artifact_json(artifact_dir, "continuation_plan_to_1000.json")
    chapter_outline = _load_artifact_json(artifact_dir, "chapter_201_outline.json")
    bible = _load_artifact_json(artifact_dir, "continuation_bible_draft.json")
    timeline = _load_artifact_json(artifact_dir, "reality_timeline.json")

    stage = _find_stage_for_chapter(chapter_number, plan)
    stage_range = str(stage.get("range") or "")
    stage_title = str(stage.get("title") or "续写")
    stage_goals = [str(goal) for goal in stage.get("goals") or []]
    guardrails = _guardrail_rules(bible, chapter_outline)

    if chapter_number == BANDAO_START_CHAPTER:
        return _chapter_201_plan(
            chapter_outline=chapter_outline,
            bible=bible,
            timeline=timeline,
            stage=stage,
            guardrails=guardrails,
        )

    reality_constraints = _reality_events_for_stage(stage_title, stage_range, timeline)
    stage_goal_text = "；".join(stage_goals) if stage_goals else "延续前章关系与事业线"
    plot_summary = (
        f"第{chapter_number}章处于“{stage_title}”阶段，围绕{stage_goal_text}推进；"
        "保持杨翠 / Rene 在 IZ*ONE 或后 IZ*ONE 时间线中的事业选择、成员牵连和情感克制。"
    )

    character_focus = ["杨翠 / Rene", "张元英", "崔叡娜", "金珉周"]
    if "IVE" in stage_title or "IVE" in stage_goal_text:
        character_focus.extend(["安宥真", "IVE"])
    if "LE SSERAFIM" in stage_title or "LE SSERAFIM" in stage_goal_text:
        character_focus.extend(["宫胁咲良", "金采源", "LE SSERAFIM"])
    if "风波" in stage_title or "停摆" in stage_title:
        character_focus.extend(["权恩菲", "IZ*ONE"])
    if "solo" in stage_goal_text or "解散" in stage_title:
        character_focus.extend(["权恩菲", "IZ*ONE"])

    # 去重但保留顺序，便于后续上下文服务筛选角色。
    deduped_focus = list(dict.fromkeys(character_focus))

    return {
        "plot_summary": plot_summary,
        "key_events": stage_goals,
        "character_focus": deduped_focus,
        "emotional_tone": "现实压力下的克制、牵挂与群像陪伴。",
        "narrative_goal": f"完成“{stage_title}”阶段内的事业节点，同时维持原书的队内日常和暗线情感张力。",
        "conflict_type": "事业时间线、公司约束、成员关系与私人承诺的冲突。",
        "scene_plan": "宿舍、练习室、后台、车内、节目现场与公司会议交替推进；每章只推进一个主要现实节点或关系节点。",
        "target_word_count": BANDAO_TARGET_WORD_COUNT,
        "estimated_words": BANDAO_TARGET_WORD_COUNT,
        "stage_range": stage_range,
        "stage_title": stage_title,
        "stage_goals": stage_goals,
        "reality_timeline_constraints": "\n".join(reality_constraints),
        "guardrails": guardrails,
    }


def _build_title_by_chapter(artifact_dir: Path) -> dict[int, str]:
    outline = _load_artifact_json(artifact_dir, "chapter_201_outline.json")
    titles: dict[int, str] = {
        BANDAO_START_CHAPTER: str(outline.get("title") or "第201章 沉默的清晨")
    }
    plan = _load_artifact_json(artifact_dir, "continuation_plan_to_1000.json")
    for stage in plan.get("stage_plan") or []:
        range_text = str(stage.get("range") or "")
        if "-" not in range_text:
            continue
        start_text, end_text = range_text.split("-", 1)
        try:
            start = int(start_text)
            end = int(end_text)
        except ValueError:
            continue
        title = str(stage.get("title") or "续写阶段")
        for chapter_number in range(max(BANDAO_START_CHAPTER, start), min(BANDAO_TARGET_TOTAL_CHAPTERS, end) + 1):
            titles.setdefault(chapter_number, f"第{chapter_number}章 {title}")
    for chapter_number in range(BANDAO_START_CHAPTER, BANDAO_TARGET_TOTAL_CHAPTERS + 1):
        titles.setdefault(chapter_number, f"第{chapter_number}章 续写")
    return titles


def _build_expansion_plan_json(chapter_number: int, artifact_dir: Path) -> str:
    return json.dumps(
        build_bandao_chapter_expansion_plan(chapter_number, artifact_dir),
        ensure_ascii=False,
    )


async def _ensure_bandao_continuation_outlines(
    *,
    db_session: AsyncSession,
    project_id: str,
    artifact_dir: Path,
) -> dict[str, int]:
    plan = _load_artifact_json(artifact_dir, "continuation_plan_to_1000.json")
    created = 0
    reused = 0

    for stage in plan.get("stage_plan") or []:
        parsed_range = _parse_stage_range(str(stage.get("range") or ""))
        if not parsed_range:
            continue
        start, _end = parsed_range
        stage_title = str(stage.get("title") or "续写阶段")
        title = f"第{stage.get('range')}章 {stage_title}"

        existing_result = await db_session.execute(
            select(Outline)
            .where(Outline.project_id == project_id)
            .where(Outline.order_index == start)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            reused += 1
            continue

        goals = [str(goal) for goal in stage.get("goals") or []]
        structure = {
            "type": "bandao_continuation_stage",
            "range": stage.get("range"),
            "title": stage_title,
            "goals": goals,
            "target_word_count_per_chapter": BANDAO_TARGET_WORD_COUNT,
            "chapter_count_target": (
                parsed_range[1] - parsed_range[0] + 1
                if parsed_range
                else None
            ),
        }
        db_session.add(
            Outline(
                project_id=project_id,
                title=title,
                content="\n".join(goals),
                structure=json.dumps(structure, ensure_ascii=False),
                order_index=start,
            )
        )
        created += 1

    if created:
        await db_session.flush()
    return {"created_continuation_outlines": created, "reused_continuation_outlines": reused}


async def create_bandao_continuation_queue_plan(
    *,
    db_session: AsyncSession,
    project_id: str,
    user_id: str,
    artifact_dir: Path,
    dry_run: bool = True,
) -> dict[str, Any]:
    """为《混在半岛的日子》续写到 1000 章创建可执行批量任务。

    dry_run=True 时只做预检和缺章计算，不写库。
    dry_run=False 时会补齐第 201-1000 章 draft 占位，并创建 pending 批量任务。
    """
    source = _load_artifact_json(artifact_dir, "source_file_report.json")
    split = _load_artifact_json(artifact_dir, "chapter_split_report.json")
    plan = _load_artifact_json(artifact_dir, "continuation_plan_to_1000.json")

    source_sha256 = str(source.get("sha256") or "")
    if source_sha256 != BANDAO_EXPECTED_SOURCE_SHA256:
        raise ValueError(f"源文件 SHA256 不匹配: {source_sha256}")
    source_chapters = int(split.get("chapter_count") or 0)
    if source_chapters != BANDAO_SOURCE_CHAPTERS:
        raise ValueError(f"源书切章数量应为 200，实际为 {source_chapters}")
    target_total = int(plan.get("target_total_chapters") or 0)
    continuation_count = int(plan.get("continuation_chapters_needed") or 0)
    target_word_count = int(plan.get("target_words_per_chapter") or 0)
    if target_total != BANDAO_TARGET_TOTAL_CHAPTERS or continuation_count != BANDAO_CONTINUATION_COUNT:
        raise ValueError("续写规划不是 201-1000 共 800 章")
    if target_word_count != BANDAO_TARGET_WORD_COUNT:
        raise ValueError("续写规划目标字数不是每章 10000 字")

    project = await db_session.get(Project, project_id)
    if project is None:
        raise ValueError(f"项目不存在: {project_id}")
    if project.user_id != user_id:
        raise ValueError("项目不属于当前用户")

    existing_result = await db_session.execute(
        select(Chapter).where(Chapter.project_id == project_id).order_by(Chapter.chapter_number)
    )
    existing_chapters = list(existing_result.scalars().all())
    existing_by_number = {int(ch.chapter_number): ch for ch in existing_chapters}
    missing_source_numbers = [
        number for number in range(1, BANDAO_SOURCE_CHAPTERS + 1) if number not in existing_by_number
    ]
    if missing_source_numbers:
        raise ValueError(f"项目缺少原书章节: {missing_source_numbers[:10]}")
    incomplete_source_numbers = [
        number
        for number in range(1, BANDAO_SOURCE_CHAPTERS + 1)
        if not (existing_by_number[number].content or "").strip()
    ]
    if incomplete_source_numbers:
        raise ValueError(f"原书章节内容未导入完整: {incomplete_source_numbers[:10]}")

    continuation_numbers = range(BANDAO_START_CHAPTER, BANDAO_TARGET_TOTAL_CHAPTERS + 1)
    missing_continuation_numbers = [number for number in continuation_numbers if number not in existing_by_number]
    existing_continuation_numbers = [number for number in continuation_numbers if number in existing_by_number]
    titles = _build_title_by_chapter(artifact_dir)
    outline_stats = {"created_continuation_outlines": 0, "reused_continuation_outlines": 0}

    if dry_run:
        return {
            "dry_run": True,
            "project_id": project_id,
            "source_sha256": source_sha256,
            "source_chapters": source_chapters,
            "target_total_chapters": target_total,
            "continuation_chapters_needed": continuation_count,
            "target_words_per_chapter": target_word_count,
            "created_missing_chapters": len(missing_continuation_numbers),
            "existing_continuation_chapters": len(existing_continuation_numbers),
            **outline_stats,
            "batch_task_id": None,
            "start_chapter_number": BANDAO_START_CHAPTER,
            "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
        }

    outline_stats = await _ensure_bandao_continuation_outlines(
        db_session=db_session,
        project_id=project_id,
        artifact_dir=artifact_dir,
    )

    for chapter_number in missing_continuation_numbers:
        db_session.add(
            Chapter(
                project_id=project_id,
                chapter_number=chapter_number,
                title=titles[chapter_number],
                content=None,
                summary=None,
                expansion_plan=_build_expansion_plan_json(chapter_number, artifact_dir),
                word_count=0,
                status="draft",
            )
        )
    if missing_continuation_numbers:
        await db_session.flush()

    refreshed_result = await db_session.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .where(Chapter.chapter_number >= BANDAO_START_CHAPTER)
        .where(Chapter.chapter_number <= BANDAO_TARGET_TOTAL_CHAPTERS)
        .order_by(Chapter.chapter_number)
    )
    continuation_chapters = list(refreshed_result.scalars().all())
    if len(continuation_chapters) != BANDAO_CONTINUATION_COUNT:
        raise ValueError(f"续写章节数量异常: {len(continuation_chapters)}")

    backfilled_expansion_plans = 0
    for chapter in continuation_chapters:
        if chapter.expansion_plan:
            continue
        chapter.expansion_plan = _build_expansion_plan_json(int(chapter.chapter_number), artifact_dir)
        backfilled_expansion_plans += 1
    if backfilled_expansion_plans:
        await db_session.flush()

    continuation_chapter_ids = [chapter.id for chapter in continuation_chapters]
    active_task_result = await db_session.execute(
        select(BatchGenerationTask)
        .where(BatchGenerationTask.project_id == project_id)
        .where(BatchGenerationTask.user_id == user_id)
        .where(BatchGenerationTask.start_chapter_number == BANDAO_START_CHAPTER)
        .where(BatchGenerationTask.chapter_count == BANDAO_CONTINUATION_COUNT)
        .where(BatchGenerationTask.target_word_count == BANDAO_TARGET_WORD_COUNT)
        .where(BatchGenerationTask.status.in_(["pending", "running"]))
        .order_by(BatchGenerationTask.created_at.desc())
    )
    for active_task in active_task_result.scalars().all():
        if list(active_task.chapter_ids or []) == continuation_chapter_ids:
            project.chapter_count = BANDAO_TARGET_TOTAL_CHAPTERS
            await db_session.commit()
            return {
                "dry_run": False,
                "project_id": project_id,
                "source_sha256": source_sha256,
                "source_chapters": source_chapters,
                "target_total_chapters": target_total,
                "continuation_chapters_needed": continuation_count,
                "target_words_per_chapter": target_word_count,
                "created_missing_chapters": len(missing_continuation_numbers),
                "existing_continuation_chapters": len(existing_continuation_numbers),
                "backfilled_expansion_plans": backfilled_expansion_plans,
                **outline_stats,
                "batch_task_id": active_task.id,
                "reused_batch_task": True,
                "start_chapter_number": BANDAO_START_CHAPTER,
                "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
            }

    batch_task = BatchGenerationTask(
        project_id=project_id,
        user_id=user_id,
        start_chapter_number=BANDAO_START_CHAPTER,
        chapter_count=BANDAO_CONTINUATION_COUNT,
        chapter_ids=continuation_chapter_ids,
        style_id=None,
        target_word_count=BANDAO_TARGET_WORD_COUNT,
        enable_analysis=False,
        enable_workflow=False,
        workflow_auto_regenerate=True,
        workflow_max_rounds=2,
        workflow_min_score=7.8,
        max_retries=3,
        status="pending",
        total_chapters=BANDAO_CONTINUATION_COUNT,
        completed_chapters=0,
        failed_chapters=[],
        current_stage="queued",
        stage_message="已创建《混在半岛的日子》201-1000 续写批量任务",
        current_stage_progress=0,
        current_retry_count=0,
    )
    db_session.add(batch_task)
    project.chapter_count = BANDAO_TARGET_TOTAL_CHAPTERS
    await db_session.commit()
    await db_session.refresh(batch_task)

    return {
        "dry_run": False,
        "project_id": project_id,
        "source_sha256": source_sha256,
        "source_chapters": source_chapters,
        "target_total_chapters": target_total,
        "continuation_chapters_needed": continuation_count,
        "target_words_per_chapter": target_word_count,
        "created_missing_chapters": len(missing_continuation_numbers),
        "existing_continuation_chapters": len(existing_continuation_numbers),
        "backfilled_expansion_plans": backfilled_expansion_plans,
        **outline_stats,
        "batch_task_id": batch_task.id,
        "reused_batch_task": False,
        "start_chapter_number": BANDAO_START_CHAPTER,
        "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
    }
