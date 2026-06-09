from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.scripts import generate_bandao_full_pack as script


def test_parse_chapter_numbers_uses_inclusive_range():
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            "tmp/out",
            "--start-chapter",
            "201",
            "--end-chapter",
            "203",
        ]
    )

    assert script.chapter_numbers_from_args(args) == [201, 202, 203]


def test_dry_run_summary_reports_scope_without_touching_ai(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "203",
            "--dry-run",
        ]
    )

    summary = script.build_dry_run_summary(args)

    assert summary["dry_run"] is True
    assert summary["chapter_count"] == 3
    assert summary["start_chapter"] == 201
    assert summary["end_chapter"] == 203
    assert summary["target_word_count"] == 10000
    assert summary["estimated_total_words"] == 30000
    assert summary["output_dir"] == str(tmp_path)


def test_merge_txt_args_are_accepted(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--merge-txt",
            "--merged-path",
            str(tmp_path / "merged.txt"),
        ]
    )

    assert args.merge_txt is True
    assert args.merged_path == str(tmp_path / "merged.txt")


def test_audit_only_args_are_accepted(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--audit-only",
        ]
    )

    assert args.audit_only is True


def test_retry_args_are_accepted_and_included_in_plan_commands(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "202",
            "--max-attempts-per-segment",
            "3",
            "--retry-delay-seconds",
            "0.5",
            "--chunk-size",
            "1",
            "--plan-only",
        ]
    )

    commands = script.build_chunked_run_commands(args)

    assert args.max_attempts_per_segment == 3
    assert args.retry_delay_seconds == 0.5
    assert "--max-attempts-per-segment 3" in commands[0]
    assert "--retry-delay-seconds 0.5" in commands[0]

def test_max_segments_per_chapter_arg_is_accepted(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--max-segments-per-chapter",
            "6",
        ]
    )

    assert args.max_segments_per_chapter == 6


def test_build_chunked_run_commands_documents_resumable_full_generation(tmp_path):
    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "205",
            "--target-word-count",
            "10000",
            "--max-segments-per-chapter",
            "8",
            "--chunk-size",
            "2",
            "--plan-only",
        ]
    )

    commands = script.build_chunked_run_commands(args)

    assert len(commands) == 3
    assert "--start-chapter 201" in commands[0]
    assert "--end-chapter 202" in commands[0]
    assert "--start-chapter 205" in commands[2]
    assert "--end-chapter 205" in commands[2]
    assert "--max-segments-per-chapter 8" in commands[0]
    assert "--chunk-size" not in commands[0]
    assert "--plan-only" not in commands[0]


def test_merge_chapters_to_single_txt_requires_complete_range(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("第201章\n\n正文", encoding="utf-8")

    with pytest.raises(ValueError, match="缺少章节"):
        script.merge_chapters_to_single_txt(
            output_dir=output_dir,
            merged_path=tmp_path / "merged.txt",
            start_chapter=201,
            end_chapter=202,
        )


def test_merge_chapters_to_single_txt_writes_ordered_content(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("第201章\n\n正文201", encoding="utf-8")
    (output_dir / "chapter_0202.txt").write_text("# 第202章\n\n正文202", encoding="utf-8")
    merged_path = tmp_path / "merged.txt"

    result = script.merge_chapters_to_single_txt(
        output_dir=output_dir,
        merged_path=merged_path,
        start_chapter=201,
        end_chapter=202,
    )

    text = merged_path.read_text(encoding="utf-8")
    assert result["chapter_count"] == 2
    assert result["path"] == str(merged_path)
    assert text.index("第201章") < text.index("# 第202章")
    assert "正文201" in text
    assert "正文202" in text



def test_merge_chapters_to_single_txt_normalizes_missing_ai_headings(tmp_path):
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    (artifact_dir / "chapter_201_outline.json").write_text(
        '{"title":"第201章 沉默的清晨"}',
        encoding="utf-8",
    )
    (artifact_dir / "continuation_plan_to_1000.json").write_text(
        '{"stage_plan":[{"range":"201-230","title":"楼梯间余波与日常修罗场"}]}',
        encoding="utf-8",
    )
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("杨翠醒来。", encoding="utf-8")
    (output_dir / "chapter_0202.txt").write_text("# 第202章\n\n杨翠继续。", encoding="utf-8")
    merged_path = tmp_path / "merged.txt"

    script.merge_chapters_to_single_txt(
        output_dir=output_dir,
        merged_path=merged_path,
        start_chapter=201,
        end_chapter=202,
        artifact_dir=artifact_dir,
        normalize_headings=True,
    )

    text = merged_path.read_text(encoding="utf-8")
    assert text.startswith("第201章 沉默的清晨\n\n杨翠醒来。")
    assert "# 第202章" not in text
    assert "第202章 楼梯间余波与日常修罗场\n\n杨翠继续。" in text


def test_merge_chapters_to_single_txt_filters_inner_ai_chapter_noise(tmp_path):
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    (artifact_dir / "chapter_201_outline.json").write_text(
        '{"title":"第201章 沉默的清晨"}',
        encoding="utf-8",
    )
    (artifact_dir / "continuation_plan_to_1000.json").write_text(
        '{"stage_plan":[{"range":"201-230","title":"楼梯间余波与日常修罗场"}]}',
        encoding="utf-8",
    )
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text(
        "# 第201章 沉默的界线\n\n正文一\n\n第201章 完。\n\n正文二\n\n# 第201章\n\n正文三",
        encoding="utf-8",
    )
    (output_dir / "chapter_0202.txt").write_text(
        "# 第202章\n\n正文三\n\n第203章 楼梯间余波与日常修罗场\n\n误生成下一章",
        encoding="utf-8",
    )
    merged_path = tmp_path / "merged.txt"

    script.merge_chapters_to_single_txt(
        output_dir=output_dir,
        merged_path=merged_path,
        start_chapter=201,
        end_chapter=202,
        artifact_dir=artifact_dir,
        normalize_headings=True,
    )

    text = merged_path.read_text(encoding="utf-8")
    assert "第201章 完。" not in text
    assert "\n# 第201章" not in text
    assert "第203章 楼梯间余波与日常修罗场" not in text
    assert "误生成下一章" not in text
    assert "正文二" in text
    assert "正文三" in text
    assert "第201章 沉默的界线" in text
    assert "第202章 楼梯间余波与日常修罗场" in text

def test_script_help_runs_from_repo_root_without_pythonpath():
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "-m", "backend.scripts.generate_bandao_full_pack", "--help"],
        cwd=Path(__file__).resolve().parents[3],
        env=env,
        capture_output=True,
        timeout=10,
        check=False,
    )

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 0, stderr
    assert "--user-id" in stdout


@pytest.mark.asyncio
async def test_build_ai_service_requires_user_settings(monkeypatch):
    class EmptyResult:
        def scalar_one_or_none(self):
            return None

    class FakeDB:
        async def execute(self, statement):
            del statement
            return EmptyResult()

    with pytest.raises(RuntimeError, match="AI"):
        await script.build_ai_service(FakeDB(), "missing-user")


@pytest.mark.asyncio
async def test_main_prints_manifest_summary(monkeypatch, capsys, tmp_path):
    class FakeDB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSessionFactory:
        def __call__(self):
            return FakeDB()

    async def fake_get_engine(user_id):
        assert user_id == "tester"
        return object()

    async def fake_build_ai_service(db, user_id):
        assert isinstance(db, FakeDB)
        assert user_id == "tester"
        return object()

    async def fake_generate(**kwargs):
        assert kwargs["chapter_numbers"] == [201]
        assert kwargs["target_word_count"] == 10000
        assert kwargs["max_segments_per_chapter"] == 4
        return {
            "generated_chapter_count": 1,
            "skipped_existing_chapter_count": 0,
            "failed_chapter_count": 0,
            "manifest_path": tmp_path / "full_pack_manifest.json",
            "audit": {"completed": False, "missing_chapter_count": 799},
            "regression_audit": {"passed": True, "failed_chapter_count": 0},
        }

    def fake_regression_audit(**kwargs):
        raise AssertionError("generate should return its own regression audit")

    monkeypatch.setattr(script, "get_engine", fake_get_engine)
    monkeypatch.setattr(script, "async_sessionmaker", lambda *args, **kwargs: FakeSessionFactory())
    monkeypatch.setattr(script, "build_ai_service", fake_build_ai_service)
    monkeypatch.setattr(script, "generate_bandao_full_pack_with_ai", fake_generate)
    monkeypatch.setattr(script, "audit_bandao_regression_pack", fake_regression_audit)

    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "201",
        ]
    )
    result = await script.main(args)

    assert result["generated_chapter_count"] == 1
    output = capsys.readouterr().out
    assert "generated=1" in output
    assert "audit_completed=False" in output
    assert "regression_passed=True" in output


@pytest.mark.asyncio
async def test_main_merge_txt_only_does_not_build_ai_service(monkeypatch, tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("第201章\n\n正文201", encoding="utf-8")
    merged_path = tmp_path / "merged.txt"

    async def should_not_get_engine(user_id):
        raise AssertionError(f"merge-txt should not open database for {user_id}")

    monkeypatch.setattr(script, "get_engine", should_not_get_engine)

    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(output_dir),
            "--start-chapter",
            "201",
            "--end-chapter",
            "201",
            "--merge-txt",
            "--merged-path",
            str(merged_path),
        ]
    )
    result = await script.main(args)

    assert result["merged_txt"]["path"] == str(merged_path)
    assert merged_path.exists()


@pytest.mark.asyncio
async def test_main_raises_when_generation_regression_audit_fails(monkeypatch, tmp_path):
    class FakeDB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSessionFactory:
        def __call__(self):
            return FakeDB()

    async def fake_get_engine(user_id):
        assert user_id == "tester"
        return object()

    async def fake_build_ai_service(db, user_id):
        assert isinstance(db, FakeDB)
        assert user_id == "tester"
        return object()

    async def fake_generate(**kwargs):
        return {
            "generated_chapter_count": 1,
            "skipped_existing_chapter_count": 0,
            "failed_chapter_count": 0,
            "manifest_path": tmp_path / "full_pack_manifest.json",
            "audit": {"completed": False},
            "regression_audit": {"passed": False, "failed_chapter_count": 1},
        }

    monkeypatch.setattr(script, "get_engine", fake_get_engine)
    monkeypatch.setattr(script, "async_sessionmaker", lambda *args, **kwargs: FakeSessionFactory())
    monkeypatch.setattr(script, "build_ai_service", fake_build_ai_service)
    monkeypatch.setattr(script, "generate_bandao_full_pack_with_ai", fake_generate)

    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "201",
        ]
    )

    with pytest.raises(RuntimeError, match="regression audit failed"):
        await script.main(args)


@pytest.mark.asyncio
async def test_main_dry_run_does_not_build_ai_service(monkeypatch, tmp_path):
    async def should_not_get_engine(user_id):
        raise AssertionError(f"dry-run should not open database for {user_id}")

    monkeypatch.setattr(script, "get_engine", should_not_get_engine)

    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--start-chapter",
            "201",
            "--end-chapter",
            "201",
            "--dry-run",
        ]
    )
    result = await script.main(args)

    assert result["dry_run"] is True
    assert result["chapter_count"] == 1


@pytest.mark.asyncio
async def test_main_audit_only_does_not_build_ai_service(monkeypatch, tmp_path):
    async def should_not_get_engine(user_id):
        raise AssertionError(f"audit-only should not open database for {user_id}")

    def fake_audit(**kwargs):
        assert kwargs["continuation_dir"] == tmp_path
        return {
            "completed": False,
            "chapter_files_found": 0,
            "missing_chapter_count": 800,
            "short_chapter_count": 0,
        }

    monkeypatch.setattr(script, "get_engine", should_not_get_engine)
    monkeypatch.setattr(script, "audit_bandao_full_completion", fake_audit)

    args = script.parse_args(
        [
            "--user-id",
            "tester",
            "--output-dir",
            str(tmp_path),
            "--audit-only",
        ]
    )
    result = await script.main(args)

    assert result["completed"] is False
    assert result["missing_chapter_count"] == 800
