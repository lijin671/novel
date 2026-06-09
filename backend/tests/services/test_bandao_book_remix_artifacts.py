from __future__ import annotations

import json
from pathlib import Path

ARTIFACT_DIR = Path("tmp/book-remix-test-ban-dao-20260530")


def _load_json(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _assert_no_encoding_damage(name: str) -> None:
    text = (ARTIFACT_DIR / name).read_text(encoding="utf-8")
    assert "????" not in text
    assert "\ufffd" not in text


def test_bandao_artifacts_verify_source_split_and_generation_route():
    for name in [
        "source_file_report.json",
        "chapter_split_report.json",
        "continuation_bible_draft.json",
        "reality_timeline.json",
        "continuation_plan_to_1000.json",
        "chapter_201_outline.json",
        "chapter_201_short_smoke_sample.txt",
        "run_summary.json",
    ]:
        assert (ARTIFACT_DIR / name).exists(), name
        _assert_no_encoding_damage(name)

    source = _load_json("source_file_report.json")
    split = _load_json("chapter_split_report.json")
    plan = _load_json("continuation_plan_to_1000.json")
    summary = _load_json("run_summary.json")

    assert source["source_file"].endswith("混在半岛的日子_7576088966319852606.txt")
    assert source["sha256"] == "3ab0897d497a1804b4b1052f927d34fa2bcf9a5f8212e4711e9f33b70ca5b823"
    assert source["detected_declared_total_header"] == "总章节: 200"

    assert split["chapter_count"] == 200
    assert split["first_chapter"]["title"] == "第 1 章  第1章 逃离"
    assert split["last_chapter"]["title"] == "第 200 章  第200章 奖励"
    assert split["warnings"] == []

    assert plan["target_total_chapters"] == 1000
    assert plan["continuation_chapters_needed"] == 800
    assert plan["target_words_per_chapter"] == 10000
    assert plan["estimated_new_words"] == 8000000
    assert plan["generation_route"]["batch_request"] == {
        "start_chapter_number": 201,
        "count": 800,
        "target_word_count": 10000,
        "enable_analysis": True,
        "enable_workflow": False,
    }
    assert plan["generation_route"]["max_tokens_for_10000_words"] == 30000
    assert summary["contains_full_800_chapter_text"] is False


def test_bandao_artifacts_lock_reality_timeline_and_continuation_decision():
    timeline = _load_json("reality_timeline.json")
    bible = _load_json("continuation_bible_draft.json")
    outline = _load_json("chapter_201_outline.json")

    source_urls = {source["url"] for source in timeline["sources"]}
    assert "https://www.le-sserafim.jp/discography" in source_urls
    assert "https://ive-official.jp/mob/news/diarKiji.php?cd=DISCOGRAPHY&ima=2521&site=DIVE" in source_urls
    assert "https://ive-official.jp/mob/news/diarKijiShw.php?site=DIVE&ima=5746&id=303477" in source_urls

    events_by_date = {event["date"]: event["event"] for event in timeline["events"]}
    assert "IZ*ONE" in events_by_date["2018-10-29"]
    assert "2021-04-29" in {event["date"] for event in timeline["events"]}
    assert "IVE" in events_by_date["2021-12-01"]
    assert "LE SSERAFIM" in events_by_date["2022-05-02"]
    assert "IVE EMPATHY" in events_by_date["2025-02-03"]
    assert "IVE SECRET" in events_by_date["2025-08-25"]
    assert "LE SSERAFIM" in events_by_date["2025-03-14"]
    assert "SPAGHETTI" in events_by_date["2025-10-24"]
    assert "REVIVE+" in events_by_date["2026-02-23"]
    assert "PUREFLOW" in events_by_date["2026-05-22"]
    assert "不加入 IVE 或 LE SSERAFIM 固定阵容" in timeline["continuation_decision"]

    rules = [item["rule"] for item in bible["hard_constraints"]]
    assert any("第201章必须紧接第200章" in rule for rule in rules)
    assert any("IVE 与 LE SSERAFIM 固定阵容按现实保持" in rule for rule in rules)
    assert any("每章 10000 字" in rule for rule in rules)

    assert outline["chapter_number"] == 201
    assert outline["target_word_count"] == 10000
    assert "第200章" in outline["continuity_anchor"]
    assert "不公开恋情" in outline["must_not_do"]
