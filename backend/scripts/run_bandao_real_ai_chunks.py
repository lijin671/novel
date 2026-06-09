from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bandao real-AI full generation in resumable chunks")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--artifact-dir", default="tmp/book-remix-test-ban-dao-20260530")
    parser.add_argument("--start-chapter", type=int, default=201)
    parser.add_argument("--end-chapter", type=int, default=1000)
    parser.add_argument("--chunk-size", type=int, default=10)
    parser.add_argument("--target-word-count", type=int, default=10000)
    parser.add_argument("--max-segments-per-chapter", type=int, default=8)
    parser.add_argument("--max-attempts-per-segment", type=int, default=3)
    parser.add_argument("--retry-delay-seconds", type=float, default=1.0)
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--database-url", default="postgresql+asyncpg://mumuai:123456@localhost:5432/mumuai_novel")
    parser.add_argument("--sleep-between-chunks", type=float, default=0.0)
    return parser.parse_args()


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    state_path = output_dir / "real_ai_chunk_runner_state.json"
    state = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "args": vars(args),
        "chunks": [],
        "status": "running",
    }
    write_state(state_path, state)

    for start in range(args.start_chapter, args.end_chapter + 1, args.chunk_size):
        end = min(args.end_chapter, start + args.chunk_size - 1)
        cmd = [
            sys.executable,
            "-m",
            "backend.scripts.generate_bandao_full_pack",
            "--user-id",
            args.user_id,
            "--artifact-dir",
            args.artifact_dir,
            "--output-dir",
            args.output_dir,
            "--start-chapter",
            str(start),
            "--end-chapter",
            str(end),
            "--target-word-count",
            str(args.target_word_count),
            "--max-segments-per-chapter",
            str(args.max_segments_per_chapter),
            "--max-attempts-per-segment",
            str(args.max_attempts_per_segment),
            "--retry-delay-seconds",
            str(args.retry_delay_seconds),
            "--model",
            args.model,
        ]
        chunk = {
            "start_chapter": start,
            "end_chapter": end,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "command": cmd,
            "status": "running",
        }
        state["chunks"].append(chunk)
        write_state(state_path, state)

        env = dict(**__import__("os").environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONPATH"] = str(Path.cwd() / "backend")
        env["DATABASE_URL"] = args.database_url
        result = subprocess.run(cmd, cwd=Path.cwd(), env=env, text=True, capture_output=True)
        chunk.update(
            {
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-4000:],
                "stderr_tail": result.stderr[-4000:],
                "status": "completed" if result.returncode == 0 else "failed",
            }
        )
        write_state(state_path, state)
        if result.returncode != 0:
            state["status"] = "failed"
            state["failed_chunk"] = {"start_chapter": start, "end_chapter": end}
            write_state(state_path, state)
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return result.returncode
        if args.sleep_between_chunks > 0:
            time.sleep(args.sleep_between_chunks)

    state["status"] = "completed"
    state["finished_at"] = datetime.now(timezone.utc).isoformat()
    write_state(state_path, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
