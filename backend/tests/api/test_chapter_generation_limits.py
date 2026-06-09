from pydantic import ValidationError

from app.api.chapters import _calculate_generation_max_tokens
from app.schemas.chapter import BatchGenerateRequest, ChapterGenerateRequest, ExpansionPlanUpdate


def test_chapter_generation_accepts_ten_thousand_word_target():
    request = ChapterGenerateRequest(target_word_count=10000)

    assert request.target_word_count == 10000
    assert _calculate_generation_max_tokens(10000) == 30000


def test_batch_generation_accepts_eight_hundred_chapters_for_full_remix_continuation():
    request = BatchGenerateRequest(start_chapter_number=201, count=800, target_word_count=10000)

    assert request.count == 800
    assert request.target_word_count == 10000


def test_expansion_plan_accepts_ten_thousand_estimated_words():
    plan = ExpansionPlanUpdate(estimated_words=10000)

    assert plan.estimated_words == 10000


def test_chapter_generation_rejects_above_ten_thousand_word_target():
    try:
        ChapterGenerateRequest(target_word_count=10001)
    except ValidationError:
        return

    raise AssertionError("target_word_count above 10000 should stay invalid")
