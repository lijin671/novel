import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_engine
from app.models.analysis_task import AnalysisTask
from app.models.chapter import Chapter
from app.models.settings import Settings
from app.services.ai_service import create_user_ai_service
from app.api.chapters import _run_batch_analysis_in_sequence


async def main(project_id: str, user_id: str) -> None:
    engine = await get_engine(user_id)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as db:
        settings_result = await db.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        settings = settings_result.scalar_one_or_none()
        if not settings:
            raise RuntimeError(f"未找到用户设置: {user_id}")

        task_rows = await db.execute(
            select(AnalysisTask, Chapter.chapter_number)
            .join(Chapter, Chapter.id == AnalysisTask.chapter_id)
            .where(AnalysisTask.project_id == project_id)
            .order_by(AnalysisTask.chapter_id, AnalysisTask.created_at.desc())
        )

        latest_pending_queue: list[dict[str, int | str]] = []
        seen_chapter_ids: set[str] = set()
        for task, chapter_number in task_rows.all():
            if task.chapter_id in seen_chapter_ids:
                continue
            seen_chapter_ids.add(task.chapter_id)
            if task.status != "pending":
                continue
            latest_pending_queue.append(
                {
                    "chapter_id": task.chapter_id,
                    "chapter_number": int(chapter_number),
                    "task_id": task.id,
                }
            )

        latest_pending_queue.sort(key=lambda item: int(item["chapter_number"]))

        if not latest_pending_queue:
            print("没有需要续跑的 pending 分析任务")
            return

        print(f"准备续跑 {len(latest_pending_queue)} 个 pending 分析任务")
        print(latest_pending_queue)

        ai_service = create_user_ai_service(
            api_provider=settings.api_provider,
            api_key=settings.api_key,
            api_base_url=settings.api_base_url or "",
            model_name=settings.llm_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            system_prompt=settings.system_prompt,
        )

        await _run_batch_analysis_in_sequence(
            tasks_queue=latest_pending_queue,
            user_id=user_id,
            project_id=project_id,
            ai_service=ai_service,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--user-id", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.project_id, args.user_id))
