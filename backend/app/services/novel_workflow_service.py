"""小说自动化全流程编排服务"""
from __future__ import annotations

from datetime import datetime
import inspect
import json
import re
from statistics import mean
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import get_logger
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.memory import PlotAnalysis
from app.models.novel_workflow import ChapterWorkflowResult
from app.models.outline import Outline
from app.models.project import Project
from app.models.project_default_style import ProjectDefaultStyle
from app.models.regeneration_task import RegenerationTask
from app.models.writing_style import WritingStyle
from app.schemas.regeneration import ChapterRegenerateRequest, PreserveElementsConfig
from app.services.ai_service import AIService
from app.services.chapter_regenerator import ChapterRegenerator
from app.services.book_remix_continuation_state_service import book_remix_continuation_state_service
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest

logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
READER_PULL_FIELDS = (
    "pov_character",
    "current_want",
    "obstacle",
    "stakes",
    "changed_state",
    "pull_forward",
)
LIVE_DIAGNOSTIC_FIELDS = (
    "event_line",
    "open_plot_lines",
    "connection_web",
    "story_pulse",
    "inline_suggestions",
)
LIVE_DIAGNOSTIC_ANCHOR_FIELDS = (
    "event_line",
    "open_plot_lines",
    "story_pulse",
)
HOOK_PAYOFF_FIELDS = (
    "opening_hook_type",
    "reader_promise",
    "ending_hook_job",
    "micro_payoff",
    "required_payoff",
)
STORY_PULSE_FIELDS = (
    "pacing",
    "tension",
    "atmosphere",
    "depth",
)


class NovelWorkflowService:
    """章节级自动化工作流服务"""

    REVIEWER_ROLES = (
        "剧情总编",
        "人物一致性审校",
        "市场节奏编辑",
    )

    READER_PERSONAS = (
        "番茄爽感读者",
        "长线剧情读者",
        "情感代入读者",
    )

    MAX_SAFE_REVIEW_ROUNDS = 12
    MIN_ACCEPTANCE_SCORE = 5.0
    MAX_ACCEPTANCE_SCORE = 9.5

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def resolve_review_round_policy(
        self,
        *,
        requested_max_rounds: int,
        min_score: float,
    ) -> Dict[str, Any]:
        """Resolve requested review rounds into a bounded stop-condition policy."""
        try:
            requested = int(requested_max_rounds)
        except (TypeError, ValueError):
            requested = 0

        try:
            requested_score = float(min_score)
        except (TypeError, ValueError):
            requested_score = 7.8

        clamped_score = round(
            max(self.MIN_ACCEPTANCE_SCORE, min(self.MAX_ACCEPTANCE_SCORE, requested_score)),
            2,
        )
        unlimited_requested = requested <= 0
        if unlimited_requested:
            effective_max_rounds = self.MAX_SAFE_REVIEW_ROUNDS
        else:
            effective_max_rounds = max(1, min(self.MAX_SAFE_REVIEW_ROUNDS, requested))

        reader_floor = round(max(6.8, clamped_score - 0.4), 2)
        return {
            "requested_max_rounds": requested,
            "effective_max_rounds": effective_max_rounds,
            "unlimited_requested": unlimited_requested,
            "min_score": clamped_score,
            "stop_conditions": [
                f"overall_score >= {clamped_score:g}",
                "no high/critical issues",
                f"style_fidelity_score >= {reader_floor:g}",
                "no high/critical style drift",
                f"reader_score >= {reader_floor:g}",
                f"round_index >= {effective_max_rounds}",
            ],
        }

    async def run_chapter_workflow(
        self,
        db: AsyncSession,
        chapter: Chapter,
        user_id: str,
        analysis: Optional[PlotAnalysis] = None,
        workflow_task_id: Optional[str] = None,
        source: str = "manual",
        auto_regenerate: bool = True,
        max_rounds: int = 2,
        min_score: float = 7.8,
        style_id: Optional[int] = None,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """运行单章自动化工作流"""
        if not chapter.content or not chapter.content.strip():
            raise ValueError("章节内容为空，无法执行自动化工作流")

        latest_analysis = analysis
        final_result: Optional[Dict[str, Any]] = None
        applied_regeneration_meta: Optional[Dict[str, Any]] = None
        applied_remix_sync_meta: Optional[Dict[str, Any]] = None
        applied_analysis_stale_meta: Optional[Dict[str, Any]] = None
        round_policy = self.resolve_review_round_policy(
            requested_max_rounds=max_rounds,
            min_score=min_score,
        )
        effective_max_rounds = int(round_policy["effective_max_rounds"])
        effective_min_score = float(round_policy["min_score"])
        resolved_source_pattern_pack = source_pattern_pack
        if resolved_source_pattern_pack is None:
            resolved_source_pattern_pack = await source_discovery_service.resolve_fresh_pattern_pack(
                repo_root=PROJECT_ROOT,
                force=False,
            )

        for round_index in range(1, effective_max_rounds + 1):
            reviewers = await self._run_review_panel(
                chapter,
                latest_analysis,
                source_pattern_pack=resolved_source_pattern_pack,
            )
            readers = await self._call_reader_panel(
                chapter,
                latest_analysis,
                source_pattern_pack=resolved_source_pattern_pack,
            )
            aggregate = self._aggregate_feedback(
                analysis=latest_analysis,
                reviewers=reviewers,
                readers=readers,
                min_score=effective_min_score,
                source_pattern_pack=resolved_source_pattern_pack,
            )
            revision_brief = self._build_revision_brief(
                chapter=chapter,
                analysis=latest_analysis,
                aggregate=aggregate,
            )

            record = ChapterWorkflowResult(
                workflow_task_id=workflow_task_id,
                project_id=chapter.project_id,
                chapter_id=chapter.id,
                user_id=user_id,
                source=source,
                round_index=round_index,
                status="completed",
                decision=aggregate["decision"],
                overall_score=aggregate["overall_score"],
                analysis_score=aggregate["analysis_score"],
                review_score=aggregate["review_score"],
                reader_score=aggregate["reader_score"],
                reviewers=reviewers,
                reader_feedback=readers,
                aggregate=aggregate,
                revision_brief=revision_brief,
                applied_regeneration=False,
                completed_at=datetime.now(),
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)

            final_result = {
                "workflow_result_id": record.id,
                "round_index": round_index,
                "decision": aggregate["decision"],
                "overall_score": aggregate["overall_score"],
                "analysis_score": aggregate["analysis_score"],
                "review_score": aggregate["review_score"],
                "reader_score": aggregate["reader_score"],
                "aggregate": aggregate,
                "applied_regeneration": bool(applied_regeneration_meta),
                "regeneration_task_id": applied_regeneration_meta.get("task_id") if applied_regeneration_meta else None,
                "chapter_updated": bool(applied_regeneration_meta),
                "round_policy": round_policy,
            }
            if applied_remix_sync_meta:
                final_result["remix_continuation_sync"] = applied_remix_sync_meta
                final_result["aggregate"] = {
                    **final_result["aggregate"],
                    "remix_continuation_sync": applied_remix_sync_meta,
                }
            if applied_analysis_stale_meta:
                final_result["analysis_stale"] = applied_analysis_stale_meta
                final_result["aggregate"] = {
                    **final_result["aggregate"],
                    "analysis_stale": applied_analysis_stale_meta,
                }

            if aggregate["decision"] == "pass":
                return final_result

            if not auto_regenerate:
                final_result["decision"] = "revise"
                return final_result

            if round_index >= effective_max_rounds:
                record.decision = "max_rounds_reached"
                record.aggregate = {
                    **aggregate,
                    "decision_reason": "已达到最大返工轮次，停止自动返工",
                }
                await db.commit()
                final_result["decision"] = "max_rounds_reached"
                final_result["aggregate"] = record.aggregate
                return final_result

            regeneration_meta = await self._auto_regenerate_chapter(
                db=db,
                chapter=chapter,
                analysis=latest_analysis,
                user_id=user_id,
                revision_brief=revision_brief,
                round_index=round_index,
                style_id=style_id,
            )

            record.applied_regeneration = regeneration_meta["applied"]
            record.regeneration_task_id = regeneration_meta.get("task_id")
            record.aggregate = {
                **aggregate,
                "regeneration": regeneration_meta,
            }
            stale_analysis_meta = await self._mark_analysis_stale_after_auto_regeneration(
                chapter=chapter,
                analysis=latest_analysis,
                workflow_record=record,
                regeneration_meta=regeneration_meta,
            )
            await db.commit()

            remix_sync_meta = await self._commit_auto_regeneration_to_remix_state(
                db=db,
                chapter=chapter,
                regeneration_meta=regeneration_meta,
            )
            if remix_sync_meta:
                record.aggregate = {
                    **record.aggregate,
                    "remix_continuation_sync": remix_sync_meta,
                }
                await db.commit()

            applied_regeneration_meta = regeneration_meta if regeneration_meta.get("applied") else None
            applied_remix_sync_meta = remix_sync_meta
            final_result.update(
                {
                    "applied_regeneration": bool(applied_regeneration_meta),
                    "regeneration_task_id": regeneration_meta.get("task_id"),
                    "chapter_updated": bool(applied_regeneration_meta),
                    "aggregate": record.aggregate,
                }
            )
            if applied_remix_sync_meta:
                final_result["remix_continuation_sync"] = applied_remix_sync_meta
            if stale_analysis_meta:
                applied_analysis_stale_meta = stale_analysis_meta
                final_result["analysis_stale"] = stale_analysis_meta
            latest_analysis = None

        if not final_result:
            raise ValueError("自动化工作流未产出结果")
        return final_result

    async def _run_review_panel(
        self,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """运行多评审面板"""
        source_pattern_digest = render_source_pattern_pack_digest(
            source_pattern_pack,
            empty_message="(no public source pattern pack; review only local project canon and chapter content.)",
        )
        prompt = f"""
你要模拟小说内审委员会，对同一章内容做多角色评审。
请严格返回 JSON 对象，不要输出 Markdown，不要解释。

返回结构：
{{
  "reviewers": [
    {{
      "role": "剧情总编",
      "overall_score": 8.4,
      "pacing_score": 8.1,
      "engagement_score": 8.7,
      "coherence_score": 8.3,
      "style_fidelity_score": 8.2,
      "verdict": "pass 或 revise",
      "strengths": ["最多3条"],
      "issues": [
        {{
          "severity": "low/medium/high/critical",
          "title": "问题标题",
          "detail": "问题详情",
          "advice": "修改建议"
        }}
      ],
      "style_drift_issues": [
        {{
          "severity": "low/medium/high/critical",
          "title": "style drift title",
          "detail": "where the continuation diverges from the original voice",
          "advice": "how to restore cadence, POV, and narrative temperature"
        }}
      ],
      "must_fix": ["最多3条必须修的问题"]
    }}
  ],
  "consensus": {{
    "headline": "一句话总评",
    "top_strengths": ["最多3条"],
    "top_issues": ["最多5条"]
  }}
}}

评审角色固定为：
1. 剧情总编
2. 人物一致性审校
3. 市场节奏编辑

要求：
1. 分数必须是 0 到 10 的数字，可带一位小数。
2. issue 必须具体，可执行，不能空泛。
3. 如果内容存在明显拖沓、人物跑偏、吸引力不足、承接生硬，请明确指出。
4. 如果整体可过，也要保留少量可优化点。

Style fidelity gate:
1. Always return style_fidelity_score from 0 to 10.
2. Check original voice, cadence, POV behavior, sentence rhythm, scene density, emotional pressure, and narrative temperature.
3. Report every style drift in style_drift_issues; high or critical style drift must set verdict to revise.
4. If style_fidelity_hints or style_signature_hints appear below, treat them as hard review criteria.

章节信息：
- 章节序号：{chapter.chapter_number}
- 章节标题：{chapter.title}
- 章节摘要：{(chapter.summary or "暂无摘要")[:500]}

现有分析快照：
{self._build_analysis_snapshot(analysis)}

Public source pattern constraints:
{source_pattern_digest}

章节正文：
{self._truncate_text(chapter.content)}
""".strip()

        result = await self.ai_service.call_with_json_retry(
            prompt=prompt,
            expected_type="object",
            temperature=0.3,
            auto_mcp=False,
        )
        reviewers = result.get("reviewers") if isinstance(result, dict) else None
        return self._normalize_reviewers(reviewers)

    async def _run_reader_panel(
        self,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """运行读者模拟面板。"""
        source_pattern_digest = render_source_pattern_pack_digest(
            source_pattern_pack,
            empty_message="(no public source pattern pack; reader review only local project canon and chapter content.)",
        )
        prompt = f"""
你要模拟 3 位不同取向的网文读者，阅读同一章并给出反馈。
请严格返回 JSON 对象，不要输出 Markdown，不要解释。

返回结构：
{{
  "personas": [
    {{
      "persona": "番茄爽感读者",
      "immersion_score": 8.6,
      "continue_score": 9.1,
      "favorite_points": ["最多3条"],
      "drop_risks": ["最多3条可能弃读点"],
      "expectations": ["最多3条后续期待"],
      "reader_pull_answers": {{
        "pov_character": "本章可读出的视角人物",
        "current_want": "视角人物当前想要什么",
        "obstacle": "阻碍是什么",
        "stakes": "为什么这件事重要",
        "changed_state": "本章结尾发生了什么状态变化",
        "pull_forward": "什么问题或欲望会拉动读者继续看"
      }},
      "live_diagnostics": {{
        "event_line": "本章可见事件线：起点 -> 转折 -> 结尾状态",
        "open_plot_lines": ["仍未解决、但被本章推进或加压的情节线"],
        "connection_web": [
          {{"source": "人物/线索/地点", "target": "人物/线索/地点", "relation": "本章可见关系变化"}}
        ],
        "story_pulse": {{
          "pacing": "节奏诊断",
          "tension": "张力诊断",
          "atmosphere": "氛围诊断",
          "depth": "人物/主题深度诊断"
        }},
        "inline_suggestions": [
          {{"scope": "chapter/scene/paragraph", "finding": "diagnostic finding", "suggestion": "repair suggestion", "status": "advisory"}}
        ]
      }},
      "hook_payoff_answers": {{
        "opening_hook_type": "visible opening hook type from the page",
        "reader_promise": "reader promise or genre expectation served by this chapter",
        "ending_hook_job": "what the ending hook does: danger, reframing, decision, cost, or payoff",
        "micro_payoff": "chapter-level payoff or pressure turn delivered on page",
        "required_payoff": "carried hook, promise, or debt this chapter handles"
      }}
    }}
  ],
  "summary": {{
    "overall_impression": "一句话总结",
    "core_hook": "最能吸引读者继续追读的点",
    "largest_risk": "最可能导致流失的点"
  }}
}}

读者画像固定为：
1. 番茄爽感读者
2. 长线剧情读者
3. 情感代入读者

要求：
1. 分数必须是 0 到 10 的数字，可带一位小数。
2. 反馈要站在真实读者视角，不要像编辑报告。
3. drop_risks 必须具体，能直接反映读者流失风险。
4. expectations 要体现他们下一章最想看到什么。

Reader-pull fresh-reader gate:
1. 每个 persona 都必须返回 reader_pull_answers。
2. 新读者必须能回答：pov_character, current_want, obstacle, stakes, changed_state, pull_forward。
3. 只根据正文可见内容判断，不要依赖隐藏大纲、作者注或假设设定。
4. 如果某个字段不清楚，对该字段返回空字符串，不要猜测。

Live manuscript diagnostics gate:
1. When novelwriter_live_manuscript_analytics_gate appears in Public source pattern constraints, every persona must return live_diagnostics.
2. live_diagnostics must keep Event Line, open plot lines, Connection Web, Story Pulse, and inline suggestions as advisory diagnostics, not accepted canon.
3. At minimum, make event_line, open_plot_lines, or story_pulse visible from chapter text. If a layer is unclear, return an empty string/object/list rather than guessing.
4. inline_suggestions status must stay advisory unless the author explicitly accepts it later.

Hook/payoff integrity gate:
1. When premise_structure_hook_payoff_gate, opening_ending_hook_integrity_gate, or reader_promise_micro_payoff_gate appears in Public source pattern constraints, every persona must return hook_payoff_answers.
2. hook_payoff_answers must identify opening_hook_type, reader_promise, ending_hook_job, micro_payoff, and required_payoff from the visible chapter text.
3. If a hook/payoff field is not visible on the page, return an empty string rather than guessing from outline or author intent.
4. A fake cliffhanger that has no cost, decision, reveal, or payoff should leave ending_hook_job or micro_payoff empty.

章节信息：
- 章节序号：{chapter.chapter_number}
- 章节标题：{chapter.title}
- 章节摘要：{(chapter.summary or "暂无摘要")[:500]}

现有分析快照：
{self._build_analysis_snapshot(analysis)}

Public source pattern constraints:
{source_pattern_digest}

章节正文：
{self._truncate_text(chapter.content)}
""".strip()

        result = await self.ai_service.call_with_json_retry(
            prompt=prompt,
            expected_type="object",
            temperature=0.5,
            auto_mcp=False,
        )
        personas = result.get("personas") if isinstance(result, dict) else None
        return self._normalize_readers(personas)

    async def _call_reader_panel(
        self,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        *,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """调用读者面板，同时兼容旧的两参数测试替身。"""
        panel = self._run_reader_panel
        try:
            parameters = inspect.signature(panel).parameters
        except (TypeError, ValueError):
            parameters = {}
        if "source_pattern_pack" in parameters:
            return await panel(
                chapter,
                analysis,
                source_pattern_pack=source_pattern_pack,
            )
        return await panel(chapter, analysis)

    def _aggregate_feedback(
        self,
        analysis: Optional[PlotAnalysis],
        reviewers: Sequence[Dict[str, Any]],
        readers: Sequence[Dict[str, Any]],
        min_score: float,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """聚合分析、多评审和读者模拟结果"""
        analysis_scores = []
        if analysis:
            for value in (
                analysis.overall_quality_score,
                analysis.pacing_score,
                analysis.engagement_score,
                analysis.coherence_score,
            ):
                if value is not None and value > 0:
                    analysis_scores.append(float(value))

        analysis_score = round(mean(analysis_scores), 2) if analysis_scores else 0.0
        review_score = round(
            mean([self._clamp_score(item.get("overall_score")) for item in reviewers]),
            2,
        ) if reviewers else 0.0
        reader_score = round(
            mean([
                mean([
                    self._clamp_score(item.get("immersion_score")),
                    self._clamp_score(item.get("continue_score")),
                ])
                for item in readers
            ]),
            2,
        ) if readers else 0.0

        if analysis_score > 0:
            overall_score = round((analysis_score * 0.35) + (review_score * 0.4) + (reader_score * 0.25), 2)
        else:
            overall_score = round((review_score * 0.65) + (reader_score * 0.35), 2)

        high_risk_issues = self._collect_high_risk_issues(reviewers)
        style_drift_issues = self._collect_style_drift_issues(reviewers)
        style_fidelity_scores = [
            self._clamp_score(item.get("style_fidelity_score"))
            for item in reviewers
            if item.get("style_fidelity_score") is not None
        ]
        style_fidelity_score = round(mean(style_fidelity_scores), 2) if style_fidelity_scores else 0.0
        min_style_fidelity_score = round(min(style_fidelity_scores), 2) if style_fidelity_scores else 0.0
        style_fidelity_floor = max(6.8, min_score - 0.4)
        has_low_style_fidelity = bool(style_fidelity_scores) and min_style_fidelity_score < style_fidelity_floor
        blocking_style_drift = any(
            issue.get("severity") in {"high", "critical"}
            for issue in style_drift_issues
        )
        reader_risks = self._collect_reader_risks(readers)
        reader_pull = self._reader_pull_gate_audit(
            readers,
            source_pattern_pack=source_pattern_pack,
        )
        live_diagnostics = self._live_diagnostics_gate_audit(
            readers,
            source_pattern_pack=source_pattern_pack,
        )
        hook_payoff = self._hook_payoff_gate_audit(
            readers,
            source_pattern_pack=source_pattern_pack,
        )
        revise_votes = sum(1 for item in reviewers if str(item.get("verdict", "")).strip().lower() == "revise")

        should_revise = (
            overall_score < min_score
            or revise_votes >= 2
            or len(high_risk_issues) >= 2
            or blocking_style_drift
            or has_low_style_fidelity
            or reader_score < max(6.8, min_score - 0.4)
            or reader_pull["blocking"]
            or live_diagnostics["blocking"]
            or hook_payoff["blocking"]
        )

        decision = "revise" if should_revise else "pass"
        highlights = self._unique_texts(
            [
                *[text for item in reviewers for text in item.get("strengths", [])],
                *[text for item in readers for text in item.get("favorite_points", [])],
            ],
            limit=6,
        )
        top_issues = self._unique_texts(
            [
                *[issue["title"] for issue in high_risk_issues],
                *[issue["title"] for issue in style_drift_issues],
                *(["reader_pull_missing"] if reader_pull["blocking"] else []),
                *(["live_diagnostics_missing"] if live_diagnostics["blocking"] else []),
                *(["hook_payoff_missing"] if hook_payoff["blocking"] else []),
                *reader_risks,
            ],
            limit=8,
        )

        return {
            "decision": decision,
            "decision_reason": "综合评分不足或存在明显流失风险" if should_revise else "评分达标且主要风险可控",
            "overall_score": overall_score,
            "analysis_score": analysis_score,
            "review_score": review_score,
            "reader_score": reader_score,
            "min_score": min_score,
            "revise_votes": revise_votes,
            "high_risk_issues": high_risk_issues[:6],
            "style_fidelity": {
                "score": style_fidelity_score,
                "min_score": min_style_fidelity_score,
                "floor": round(style_fidelity_floor, 2),
                "has_low_score": has_low_style_fidelity,
                "has_blocking_drift": blocking_style_drift,
            },
            "style_drift_issues": style_drift_issues[:6],
            "reader_risks": reader_risks[:6],
            "reader_pull": reader_pull,
            "live_diagnostics": live_diagnostics,
            "hook_payoff": hook_payoff,
            "highlights": highlights,
            "top_issues": top_issues,
        }

    def _build_revision_brief(
        self,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        aggregate: Dict[str, Any],
    ) -> str:
        """生成返工说明"""
        lines = [
            f"请在保留第{chapter.chapter_number}章核心事件顺序和人物定位的前提下，重写并优化本章。",
            "",
            "本轮优先修复：",
        ]
        issues = aggregate.get("high_risk_issues", [])
        if issues:
            for index, issue in enumerate(issues[:5], 1):
                advice = issue.get("advice") or issue.get("detail") or issue.get("title")
                lines.append(f"{index}. {issue.get('title', '重点问题')}：{advice}")
        else:
            for index, issue in enumerate(aggregate.get("top_issues", [])[:5], 1):
                lines.append(f"{index}. {issue}")

        reader_risks = aggregate.get("reader_risks", [])
        if reader_risks:
            lines.extend([
                "",
                "读者流失风险：",
            ])
            for risk in reader_risks[:4]:
                lines.append(f"- {risk}")

        style_drift_issues = aggregate.get("style_drift_issues", [])
        if style_drift_issues:
            lines.extend([
                "",
                "Style fidelity repair:",
            ])
            for issue in style_drift_issues[:5]:
                advice = issue.get("advice") or issue.get("detail") or issue.get("title")
                lines.append(f"- {issue.get('title', 'style drift')}: {advice}")

        reader_pull = aggregate.get("reader_pull") or {}
        if reader_pull.get("blocking"):
            lines.extend([
                "",
                "Reader-pull repair:",
                "- Make POV, current want, obstacle, stakes, changed exit state, and pull-forward question/desire visible in the chapter text.",
            ])
            missing_fields = [
                str(item.get("field", "")).strip()
                for item in reader_pull.get("missing", []) or []
                if isinstance(item, dict) and str(item.get("field", "")).strip()
            ]
            if missing_fields:
                lines.append(
                    "- Missing reader-pull fields: "
                    + ", ".join(self._unique_texts(missing_fields, limit=8))
                )

        live_diagnostics = aggregate.get("live_diagnostics") or {}
        if live_diagnostics.get("blocking"):
            lines.extend([
                "",
                "Live-diagnostics repair:",
                "- Make the chapter's Event Line, open plot lines, and Story Pulse readable from the text.",
                "- Keep Connection Web and inline suggestions as advisory diagnostics; do not turn them into accepted canon without author acceptance.",
            ])
            missing_layers = [
                str(item.get("field", "")).strip()
                for item in live_diagnostics.get("missing", []) or []
                if isinstance(item, dict) and str(item.get("field", "")).strip()
            ]
            if missing_layers:
                lines.append(
                    "- Missing live-diagnostics layers: "
                    + ", ".join(self._unique_texts(missing_layers, limit=8))
                )

        hook_payoff = aggregate.get("hook_payoff") or {}
        if hook_payoff.get("blocking"):
            lines.extend([
                "",
                "Hook/payoff repair:",
                "- Make opening hook, reader promise, ending hook job, micro payoff, and required payoff visible from the chapter text.",
                "- Pay off, complicate, or explicitly defer carried hooks with a visible cost, decision, reveal, or changed board state.",
                "- Do not rely on a fake cliffhanger; the ending hook must do one clear job and the chapter must deliver at least one earned payoff or pressure turn.",
            ])
            missing_hook_fields = [
                str(item.get("field", "")).strip()
                for item in hook_payoff.get("missing", []) or []
                if isinstance(item, dict) and str(item.get("field", "")).strip()
            ]
            if missing_hook_fields:
                lines.append(
                    "- Missing hook/payoff fields: "
                    + ", ".join(self._unique_texts(missing_hook_fields, limit=8))
                )

        if analysis and analysis.suggestions:
            lines.extend([
                "",
                "可结合原分析建议继续强化：",
            ])
            for suggestion in self._unique_texts(analysis.suggestions, limit=3):
                lines.append(f"- {suggestion}")

        lines.extend([
            "",
            "写作要求：",
            "- 保持人物性格、关系与既有设定一致。",
            "- 保留本章关键剧情节点，不要改成完全不同的故事走向。",
            "- 优先优化节奏、冲突推进、读者期待和情绪起伏。",
            "- 结尾要保留足够的追读钩子。",
            "- Preserve original voice, cadence, POV behavior, and narrative temperature.",
        ])
        return "\n".join(lines)

    async def _auto_regenerate_chapter(
        self,
        db: AsyncSession,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        user_id: str,
        revision_brief: str,
        round_index: int,
        style_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """自动返工章节"""
        project_context, resolved_style_id, style_content = await self._load_regeneration_context(
            db=db,
            chapter=chapter,
            user_id=user_id,
            style_id=style_id,
        )

        preserve_plot_points = []
        if analysis and analysis.plot_points:
            preserve_plot_points = [
                str(item.get("content", "")).strip()
                for item in analysis.plot_points[:3]
                if str(item.get("content", "")).strip()
            ]

        regenerate_request = ChapterRegenerateRequest(
            modification_source="custom",
            custom_instructions=revision_brief,
            preserve_elements=PreserveElementsConfig(
                preserve_structure=True,
                preserve_plot_points=preserve_plot_points,
                preserve_character_traits=True,
            ),
            style_id=resolved_style_id,
            target_word_count=max(chapter.word_count or len(chapter.content or ""), 800),
            focus_areas=self._infer_focus_areas(revision_brief),
            save_as_version=True,
            version_note=f"自动化全流程第{round_index}轮返工",
            auto_apply=True,
        )

        regen_task = RegenerationTask(
            chapter_id=chapter.id,
            analysis_id=analysis.id if analysis else None,
            user_id=user_id,
            project_id=chapter.project_id,
            modification_instructions=revision_brief,
            original_suggestions=analysis.suggestions if analysis else None,
            selected_suggestion_indices=None,
            custom_instructions=revision_brief,
            style_id=resolved_style_id,
            target_word_count=regenerate_request.target_word_count,
            focus_areas=regenerate_request.focus_areas,
            preserve_elements=regenerate_request.preserve_elements.model_dump() if regenerate_request.preserve_elements else None,
            status="running",
            progress=15,
            original_content=chapter.content,
            original_word_count=chapter.word_count or len(chapter.content or ""),
            version_note=regenerate_request.version_note,
            started_at=datetime.now(),
        )
        db.add(regen_task)
        await db.commit()
        await db.refresh(regen_task)

        regenerator = ChapterRegenerator(self.ai_service)
        full_content = ""

        try:
            async for event in regenerator.regenerate_with_feedback(
                chapter=chapter,
                analysis=analysis,
                regenerate_request=regenerate_request,
                project_context=project_context,
                style_content=style_content,
                user_id=user_id,
                db=db,
            ):
                if event.get("type") == "chunk":
                    full_content += event.get("content", "")

            content = full_content.strip()
            if not content:
                raise ValueError("自动返工未生成有效内容")

            chapter.content = content
            chapter.word_count = len(content)
            chapter.summary = self._build_summary(content, chapter.summary)

            regen_task.status = "completed"
            regen_task.progress = 100
            regen_task.regenerated_content = content
            regen_task.regenerated_word_count = len(content)
            regen_task.completed_at = datetime.now()
            await db.commit()

            return {
                "applied": True,
                "task_id": regen_task.id,
                "word_count": len(content),
                "style_id": resolved_style_id,
            }
        except Exception as exc:
            regen_task.status = "failed"
            regen_task.error_message = str(exc)[:1000]
            regen_task.completed_at = datetime.now()
            await db.commit()
            logger.error(f"自动返工失败: chapter_id={chapter.id}, error={exc}")
            raise

    async def _commit_auto_regeneration_to_remix_state(
        self,
        *,
        db: AsyncSession,
        chapter: Chapter,
        regeneration_meta: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Persist workflow-applied regenerated content as the latest remix checkpoint."""
        if not regeneration_meta.get("applied"):
            return None
        content = (chapter.content or "").strip()
        if not content:
            return None

        result = await book_remix_continuation_state_service.commit_generated_chapter(
            db=db,
            project_id=chapter.project_id,
            chapter_id=chapter.id,
            chapter_number=chapter.chapter_number,
            chapter_title=chapter.title or "",
            chapter_content=content,
            chapter_outline=chapter.summary or "",
            previous_chapter_summary="",
            continuation_point="workflow_auto_regeneration",
        )
        return {
            "changed": bool(result.get("changed")) if isinstance(result, dict) else False,
            "reason": result.get("reason") if isinstance(result, dict) else "unknown",
            "changed_sections": result.get("changed_sections", []) if isinstance(result, dict) else [],
        }

    async def _mark_analysis_stale_after_auto_regeneration(
        self,
        *,
        chapter: Chapter,
        analysis: Optional[PlotAnalysis],
        workflow_record: ChapterWorkflowResult,
        regeneration_meta: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Mark the previous analysis as stale when workflow rewrites the chapter."""
        del chapter
        if not regeneration_meta.get("applied") or analysis is None:
            return None

        stale_meta = {
            "stale": True,
            "analysis_id": analysis.id,
            "reason": "workflow_auto_regeneration_updated_chapter_content",
            "reanalysis_required": True,
        }
        analysis.analysis_report = (
            "Stale after workflow auto regeneration; reanalysis required for updated chapter content."
        )
        analysis.suggestions = [
            "Chapter content was auto-regenerated after this analysis. Re-run chapter analysis before using this PlotAnalysis as final continuity evidence."
        ]
        analysis.overall_quality_score = 0
        analysis.pacing_score = 0
        analysis.engagement_score = 0
        analysis.coherence_score = 0
        analysis.plot_points = []
        analysis.plot_points_count = 0
        analysis.foreshadows = []
        analysis.foreshadows_planted = 0
        analysis.foreshadows_resolved = 0
        analysis.character_states = []
        analysis.hooks = []
        analysis.hooks_count = 0
        analysis.scenes = []
        analysis.emotional_tone = ""
        analysis.emotional_intensity = 0
        analysis.emotional_curve = {}
        workflow_record.aggregate = {
            **(workflow_record.aggregate or {}),
            "analysis_stale": stale_meta,
        }
        return stale_meta

    async def _load_regeneration_context(
        self,
        db: AsyncSession,
        chapter: Chapter,
        user_id: str,
        style_id: Optional[int],
    ) -> tuple[Dict[str, Any], Optional[int], str]:
        """构建返工所需上下文"""
        project_result = await db.execute(
            select(Project).where(Project.id == chapter.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError("项目不存在，无法执行自动返工")

        characters_result = await db.execute(
            select(Character).where(Character.project_id == chapter.project_id)
        )
        all_characters = characters_result.scalars().all()

        focus_names = self._extract_focus_names(chapter)
        if focus_names:
            character_pool = [item for item in all_characters if item.name in focus_names]
            if not character_pool:
                character_pool = all_characters
        else:
            character_pool = all_characters

        outline = None
        if chapter.outline_id:
            outline_result = await db.execute(
                select(Outline).where(Outline.id == chapter.outline_id)
            )
            outline = outline_result.scalar_one_or_none()

        resolved_style_id = style_id
        if not resolved_style_id:
            default_style_result = await db.execute(
                select(ProjectDefaultStyle.style_id)
                .where(ProjectDefaultStyle.project_id == chapter.project_id)
            )
            resolved_style_id = default_style_result.scalar_one_or_none()

        style_content = ""
        if resolved_style_id:
            style_result = await db.execute(
                select(WritingStyle).where(WritingStyle.id == resolved_style_id)
            )
            style = style_result.scalar_one_or_none()
            if style and (style.user_id is None or style.user_id == user_id):
                style_content = style.prompt_content or ""

        project_context = {
            "project_title": project.title,
            "genre": project.genre or "未设定",
            "theme": project.theme or "未设定",
            "narrative_perspective": project.narrative_perspective or "第三人称",
            "time_period": project.world_time_period or "未设定",
            "location": project.world_location or "未设定",
            "atmosphere": project.world_atmosphere or "未设定",
            "characters_info": self._build_characters_brief(character_pool),
            "chapter_outline": outline.content if outline else chapter.summary or "暂无章节规划",
            "previous_context": "",
        }
        return project_context, resolved_style_id, style_content

    def _build_characters_brief(self, characters: Sequence[Character]) -> str:
        """构建简化角色上下文"""
        if not characters:
            return "暂无角色信息"

        lines = []
        for character in characters[:12]:
            parts = [f"姓名：{character.name}"]
            if character.role_type:
                parts.append(f"定位：{character.role_type}")
            if character.personality:
                parts.append(f"性格：{self._shorten(character.personality, 80)}")
            if character.background:
                parts.append(f"背景：{self._shorten(character.background, 80)}")
            if character.current_state:
                parts.append(f"当前状态：{self._shorten(character.current_state, 60)}")
            lines.append("；".join(parts))
        return "\n".join(lines)

    def _extract_focus_names(self, chapter: Chapter) -> List[str]:
        """从章节规划中提取焦点角色"""
        if not chapter.expansion_plan:
            return []
        try:
            plan = json.loads(chapter.expansion_plan)
            raw_names = plan.get("character_focus", [])
            return [str(name).strip() for name in raw_names if str(name).strip()]
        except Exception:
            return []

    def _build_analysis_snapshot(self, analysis: Optional[PlotAnalysis]) -> str:
        """构建分析快照文本"""
        if not analysis:
            return "暂无章节分析结果"

        payload = {
            "plot_stage": analysis.plot_stage,
            "overall_quality_score": analysis.overall_quality_score,
            "pacing_score": analysis.pacing_score,
            "engagement_score": analysis.engagement_score,
            "coherence_score": analysis.coherence_score,
            "suggestions": (analysis.suggestions or [])[:5],
            "plot_points": (analysis.plot_points or [])[:3],
            "foreshadows": (analysis.foreshadows or [])[:3],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _normalize_reviewers(self, reviewers: Any) -> List[Dict[str, Any]]:
        """标准化评审结果"""
        normalized: List[Dict[str, Any]] = []
        if not isinstance(reviewers, list):
            reviewers = []

        for role_name, item in zip(self.REVIEWER_ROLES, reviewers[:len(self.REVIEWER_ROLES)]):
            if not isinstance(item, dict):
                item = {}
            issues = []
            for issue in item.get("issues", []) or []:
                if not isinstance(issue, dict):
                    continue
                title = str(issue.get("title", "")).strip()
                detail = str(issue.get("detail", "")).strip()
                advice = str(issue.get("advice", "")).strip()
                if not (title or detail or advice):
                    continue
                severity = str(issue.get("severity", "medium")).strip().lower()
                if severity not in {"low", "medium", "high", "critical"}:
                    severity = "medium"
                issues.append(
                    {
                        "severity": severity,
                        "title": title or "待优化项",
                        "detail": detail,
                        "advice": advice,
                    }
                )

            style_drift_issues = self._normalize_issue_list(
                item.get("style_drift_issues") or [],
                limit=5,
            )
            normalized.append(
                {
                    "role": str(item.get("role") or role_name),
                    "overall_score": self._clamp_score(item.get("overall_score")),
                    "pacing_score": self._clamp_score(item.get("pacing_score")),
                    "engagement_score": self._clamp_score(item.get("engagement_score")),
                    "coherence_score": self._clamp_score(item.get("coherence_score")),
                    "style_fidelity_score": (
                        self._clamp_score(item.get("style_fidelity_score"))
                        if item.get("style_fidelity_score") is not None
                        else None
                    ),
                    "verdict": "revise" if str(item.get("verdict", "")).strip().lower() == "revise" else "pass",
                    "strengths": self._unique_texts(item.get("strengths") or [], limit=3),
                    "issues": issues[:5],
                    "style_drift_issues": style_drift_issues,
                    "must_fix": self._unique_texts(item.get("must_fix") or [], limit=3),
                }
            )

        while len(normalized) < len(self.REVIEWER_ROLES):
            role_name = self.REVIEWER_ROLES[len(normalized)]
            normalized.append(
                {
                    "role": role_name,
                    "overall_score": 7.0,
                    "pacing_score": 7.0,
                    "engagement_score": 7.0,
                    "coherence_score": 7.0,
                    "style_fidelity_score": None,
                    "verdict": "pass",
                    "strengths": [],
                    "issues": [],
                    "style_drift_issues": [],
                    "must_fix": [],
                }
            )
        return normalized

    def _normalize_readers(self, readers: Any) -> List[Dict[str, Any]]:
        """标准化读者模拟结果"""
        normalized: List[Dict[str, Any]] = []
        if not isinstance(readers, list):
            readers = []

        for persona_name, item in zip(self.READER_PERSONAS, readers[:len(self.READER_PERSONAS)]):
            if not isinstance(item, dict):
                item = {}
            normalized.append(
                {
                    "persona": str(item.get("persona") or persona_name),
                    "immersion_score": self._clamp_score(item.get("immersion_score")),
                    "continue_score": self._clamp_score(item.get("continue_score")),
                    "favorite_points": self._unique_texts(item.get("favorite_points") or [], limit=3),
                    "drop_risks": self._unique_texts(item.get("drop_risks") or [], limit=3),
                    "expectations": self._unique_texts(item.get("expectations") or [], limit=3),
                    "reader_pull_answers": self._normalize_reader_pull_answers(
                        item.get("reader_pull_answers") or item.get("reader_pull") or {}
                    ),
                    "live_diagnostics": self._normalize_live_diagnostics(
                        item.get("live_diagnostics") or item.get("live_manuscript_diagnostics") or {}
                    ),
                    "hook_payoff_answers": self._normalize_hook_payoff_answers(
                        item.get("hook_payoff_answers") or item.get("hook_payoff") or {}
                    ),
                }
            )

        while len(normalized) < len(self.READER_PERSONAS):
            persona_name = self.READER_PERSONAS[len(normalized)]
            normalized.append(
                {
                    "persona": persona_name,
                    "immersion_score": 7.0,
                    "continue_score": 7.0,
                    "favorite_points": [],
                    "drop_risks": [],
                    "expectations": [],
                    "reader_pull_answers": {},
                    "live_diagnostics": {},
                    "hook_payoff_answers": {},
                }
            )
        return normalized

    def _collect_high_risk_issues(self, reviewers: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取高风险问题"""
        issues: List[Dict[str, Any]] = []
        for reviewer in reviewers:
            for issue in reviewer.get("issues", []) or []:
                if issue.get("severity") in {"high", "critical"}:
                    issues.append(issue)
            for must_fix in reviewer.get("must_fix", []) or []:
                issues.append(
                    {
                        "severity": "high",
                        "title": str(must_fix).strip(),
                        "detail": "",
                        "advice": str(must_fix).strip(),
                    }
                )
        deduped = []
        seen = set()
        for item in issues:
            key = (item.get("title"), item.get("advice"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    def _normalize_issue_list(self, value: Any, *, limit: int) -> List[Dict[str, Any]]:
        """Normalize model-provided issue dictionaries."""
        if not isinstance(value, list):
            return []
        issues: List[Dict[str, Any]] = []
        for issue in value:
            if not isinstance(issue, dict):
                continue
            title = str(issue.get("title", "")).strip()
            detail = str(issue.get("detail", "")).strip()
            advice = str(issue.get("advice", "")).strip()
            if not (title or detail or advice):
                continue
            severity = str(issue.get("severity", "medium")).strip().lower()
            if severity not in {"low", "medium", "high", "critical"}:
                severity = "medium"
            issues.append(
                {
                    "severity": severity,
                    "title": title or "style drift",
                    "detail": detail,
                    "advice": advice,
                }
            )
            if len(issues) >= limit:
                break
        return issues

    def _collect_style_drift_issues(self, reviewers: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Collect style drift issues from all reviewers."""
        issues: List[Dict[str, Any]] = []
        for reviewer in reviewers:
            issues.extend(
                self._normalize_issue_list(
                    reviewer.get("style_drift_issues") or [],
                    limit=5,
                )
            )
        deduped = []
        seen = set()
        for item in issues:
            key = (item.get("title"), item.get("advice"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    def _collect_reader_risks(self, readers: Sequence[Dict[str, Any]]) -> List[str]:
        """提取读者流失风险"""
        return self._unique_texts(
            [risk for reader in readers for risk in reader.get("drop_risks", []) or []],
            limit=8,
        )

    def _reader_pull_gate_audit(
        self,
        readers: Sequence[Dict[str, Any]],
        *,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """检查新读者是否能回答追读力六问。"""
        required = self._source_pattern_pack_has(
            source_pattern_pack,
            "reader_pull_fresh_reader_gate",
        )
        missing: List[Dict[str, str]] = []
        if not required:
            return {
                "required": False,
                "blocking": False,
                "missing_count": 0,
                "missing": [],
                "fields": list(READER_PULL_FIELDS),
            }

        if not readers:
            readers = [{"persona": "fresh reader", "reader_pull_answers": {}}]

        for reader in readers:
            answers = reader.get("reader_pull_answers") or {}
            if not isinstance(answers, dict):
                answers = {}
            persona = str(reader.get("persona") or "fresh reader").strip() or "fresh reader"
            for field in READER_PULL_FIELDS:
                if not str(answers.get(field) or "").strip():
                    missing.append({"persona": persona, "field": field})

        return {
            "required": True,
            "blocking": bool(missing),
            "missing_count": len(missing),
            "missing": missing[:24],
            "fields": list(READER_PULL_FIELDS),
        }

    def _live_diagnostics_gate_audit(
        self,
        readers: Sequence[Dict[str, Any]],
        *,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """检查 NovelWriter 式现场诊断层是否可从正文读出。"""
        required = self._source_pattern_pack_has(
            source_pattern_pack,
            "novelwriter_live_manuscript_analytics_gate",
        )
        missing: List[Dict[str, str]] = []
        if not required:
            return {
                "required": False,
                "blocking": False,
                "missing_count": 0,
                "missing": [],
                "fields": list(LIVE_DIAGNOSTIC_FIELDS),
                "anchor_fields": list(LIVE_DIAGNOSTIC_ANCHOR_FIELDS),
                "advisory_only": True,
            }

        if not readers:
            readers = [{"persona": "fresh reader", "live_diagnostics": {}}]

        for reader in readers:
            diagnostics = reader.get("live_diagnostics") or {}
            if not isinstance(diagnostics, dict):
                diagnostics = {}
            persona = str(reader.get("persona") or "fresh reader").strip() or "fresh reader"
            has_anchor = any(
                self._has_live_diagnostic_value(diagnostics.get(field))
                for field in LIVE_DIAGNOSTIC_ANCHOR_FIELDS
            )
            if not has_anchor:
                missing.append(
                    {
                        "persona": persona,
                        "field": "event_line|open_plot_lines|story_pulse",
                    }
                )

            inline_suggestions = diagnostics.get("inline_suggestions") or []
            if isinstance(inline_suggestions, list):
                for suggestion in inline_suggestions:
                    if not isinstance(suggestion, dict):
                        continue
                    status = str(suggestion.get("status") or "advisory").strip().lower()
                    if status and status != "advisory":
                        missing.append(
                            {
                                "persona": persona,
                                "field": "inline_suggestions.status",
                            }
                        )
                        break

        return {
            "required": True,
            "blocking": bool(missing),
            "missing_count": len(missing),
            "missing": missing[:24],
            "fields": list(LIVE_DIAGNOSTIC_FIELDS),
            "anchor_fields": list(LIVE_DIAGNOSTIC_ANCHOR_FIELDS),
            "advisory_only": True,
        }

    def _hook_payoff_gate_audit(
        self,
        readers: Sequence[Dict[str, Any]],
        *,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """检查钩子、承诺、回报字段是否能从正文读出。"""
        required = any(
            self._source_pattern_pack_has(source_pattern_pack, pattern_name)
            for pattern_name in (
                "premise_structure_hook_payoff_gate",
                "opening_ending_hook_integrity_gate",
                "reader_promise_micro_payoff_gate",
            )
        )
        missing: List[Dict[str, str]] = []
        if not required:
            return {
                "required": False,
                "blocking": False,
                "missing_count": 0,
                "missing": [],
                "fields": list(HOOK_PAYOFF_FIELDS),
            }

        if not readers:
            readers = [{"persona": "fresh reader", "hook_payoff_answers": {}}]

        for reader in readers:
            answers = reader.get("hook_payoff_answers") or {}
            if not isinstance(answers, dict):
                answers = {}
            persona = str(reader.get("persona") or "fresh reader").strip() or "fresh reader"
            for field in HOOK_PAYOFF_FIELDS:
                if not str(answers.get(field) or "").strip():
                    missing.append({"persona": persona, "field": field})

        return {
            "required": True,
            "blocking": bool(missing),
            "missing_count": len(missing),
            "missing": missing[:24],
            "fields": list(HOOK_PAYOFF_FIELDS),
        }

    def _normalize_reader_pull_answers(self, value: Any) -> Dict[str, str]:
        """规范化模型返回的追读力答案。"""
        if not isinstance(value, dict):
            return {}
        normalized: Dict[str, str] = {}
        for field in READER_PULL_FIELDS:
            text = str(value.get(field) or "").strip()
            if text:
                normalized[field] = self._shorten(text, 160)
            else:
                normalized[field] = ""
        return normalized

    def _normalize_hook_payoff_answers(self, value: Any) -> Dict[str, str]:
        """规范化读者侧钩子 / 回报可见性答案。"""
        if not isinstance(value, dict):
            return {}
        normalized: Dict[str, str] = {}
        for field in HOOK_PAYOFF_FIELDS:
            text = str(value.get(field) or "").strip()
            normalized[field] = self._shorten(text, 180) if text else ""
        return normalized

    def _normalize_live_diagnostics(self, value: Any) -> Dict[str, Any]:
        """规范化模型返回的现场诊断层，保留建议态边界。"""
        if not isinstance(value, dict):
            return {}

        story_pulse = value.get("story_pulse") or {}
        normalized_story_pulse: Dict[str, str] = {}
        if isinstance(story_pulse, dict):
            for field in STORY_PULSE_FIELDS:
                text = str(story_pulse.get(field) or "").strip()
                normalized_story_pulse[field] = self._shorten(text, 160) if text else ""

        return {
            "event_line": self._shorten(str(value.get("event_line") or "").strip(), 240),
            "open_plot_lines": self._unique_texts(
                value.get("open_plot_lines") or value.get("open_plot_line_ids") or [],
                limit=6,
            ),
            "connection_web": self._normalize_connection_web(value.get("connection_web") or []),
            "story_pulse": normalized_story_pulse,
            "inline_suggestions": self._normalize_inline_suggestions(
                value.get("inline_suggestions") or []
            ),
        }

    def _normalize_connection_web(self, value: Any) -> List[Dict[str, str]]:
        """规范化人物、线索、地点之间的可见关系诊断。"""
        if not isinstance(value, list):
            return []
        edges: List[Dict[str, str]] = []
        seen = set()
        for item in value:
            if isinstance(item, dict):
                source = self._shorten(str(item.get("source") or item.get("from") or "").strip(), 80)
                target = self._shorten(str(item.get("target") or item.get("to") or "").strip(), 80)
                relation = self._shorten(str(item.get("relation") or item.get("label") or "").strip(), 120)
            else:
                source = ""
                target = ""
                relation = self._shorten(str(item).strip(), 160)
            if not (source or target or relation):
                continue
            key = (source, target, relation)
            if key in seen:
                continue
            seen.add(key)
            edges.append({"source": source, "target": target, "relation": relation})
            if len(edges) >= 6:
                break
        return edges

    def _normalize_inline_suggestions(self, value: Any) -> List[Dict[str, str]]:
        """规范化段内建议，并强制保持 advisory 状态。"""
        if not isinstance(value, list):
            return []
        suggestions: List[Dict[str, str]] = []
        seen = set()
        for item in value:
            if isinstance(item, dict):
                scope = self._shorten(str(item.get("scope") or "").strip(), 80)
                finding = self._shorten(str(item.get("finding") or item.get("detail") or "").strip(), 160)
                suggestion = self._shorten(str(item.get("suggestion") or item.get("advice") or "").strip(), 160)
            else:
                scope = ""
                finding = self._shorten(str(item).strip(), 160)
                suggestion = ""
            if not (scope or finding or suggestion):
                continue
            key = (scope, finding, suggestion)
            if key in seen:
                continue
            seen.add(key)
            suggestions.append(
                {
                    "scope": scope,
                    "finding": finding,
                    "suggestion": suggestion,
                    "status": "advisory",
                }
            )
            if len(suggestions) >= 6:
                break
        return suggestions

    def _has_live_diagnostic_value(self, value: Any) -> bool:
        """判断诊断层是否包含可用内容。"""
        if isinstance(value, dict):
            return any(self._has_live_diagnostic_value(item) for item in value.values())
        if isinstance(value, list):
            return any(self._has_live_diagnostic_value(item) for item in value)
        return bool(str(value or "").strip())

    def _source_pattern_pack_has(
        self,
        source_pattern_pack: Optional[dict[str, Any]],
        pattern_name: str,
    ) -> bool:
        """判断来源模式包是否启用了指定工作流模式。"""
        if not source_pattern_pack:
            return False

        workflow_patterns = source_pattern_pack.get("workflow_patterns") or []
        if isinstance(workflow_patterns, list):
            for item in workflow_patterns:
                if isinstance(item, dict) and str(item.get("name") or "").strip() == pattern_name:
                    return True
                if str(item).strip() == pattern_name:
                    return True

        for key in ("absorbed_patterns", "patterns", "pattern_names"):
            values = source_pattern_pack.get(key) or []
            if isinstance(values, list) and pattern_name in {str(item).strip() for item in values}:
                return True

        hints_key = f"{pattern_name}_hints"
        hints = source_pattern_pack.get(hints_key)
        return bool(hints)

    def _infer_focus_areas(self, revision_brief: str) -> List[str]:
        """从返工说明中推断重点优化方向"""
        mapping = {
            "pacing": ("节奏", "拖沓", "推进"),
            "emotion": ("情感", "情绪", "代入"),
            "description": ("描写", "场景", "画面"),
            "dialogue": ("对白", "对话"),
            "conflict": ("冲突", "悬念", "钩子"),
        }
        result = []
        for key, keywords in mapping.items():
            if any(word in revision_brief for word in keywords):
                result.append(key)
        return result[:3]

    def _build_summary(self, content: str, fallback: Optional[str]) -> str:
        """构建章节摘要"""
        plain = re.sub(r"\s+", " ", (content or "").strip())
        if plain:
            return plain[:180].rstrip("，。；、 ") + ("..." if len(plain) > 180 else "")
        return fallback or ""

    def _truncate_text(self, text: Optional[str], max_length: int = 7000) -> str:
        """截断长文本，避免提示词过大"""
        value = (text or "").strip()
        if len(value) <= max_length:
            return value
        return value[:max_length] + "\n\n[后文已截断]"

    def _clamp_score(self, value: Any) -> float:
        """规范化分数"""
        try:
            numeric = float(value)
        except Exception:
            numeric = 7.0
        return round(max(0.0, min(10.0, numeric)), 2)

    def _unique_texts(self, values: Sequence[Any], limit: int) -> List[str]:
        """去重并裁剪文本列表"""
        if isinstance(values, (str, bytes)):
            values = [values]
        result = []
        seen = set()
        for value in values:
            text = self._shorten(str(value).strip(), 120)
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(text)
            if len(result) >= limit:
                break
        return result

    def _shorten(self, text: str, limit: int) -> str:
        """截断单条文本"""
        normalized = re.sub(r"\s+", " ", text or "").strip()
        if len(normalized) <= limit:
            return normalized
        return normalized[:limit].rstrip("，。；、 ") + "..."
