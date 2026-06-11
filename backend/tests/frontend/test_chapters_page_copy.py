from pathlib import Path

def _u(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


def test_chapters_page_keeps_core_continuation_copy_utf8_clean():
    repo_root = Path(__file__).resolve().parents[3]
    page = repo_root / "frontend" / "src" / "pages" / "Chapters.tsx"
    text = page.read_text(encoding="utf-8")

    expected_fragments = [
        r"\u6ca1\u6709\u627e\u5230\u5339\u914d\u7ae0\u8282",
        r"\u65e0\u5185\u5bb9",
        r"\u6c89\u6d78\u5f0f\u9605\u8bfb",
        r"\u8bf7\u5148\u586b\u5199\u7ae0\u8282\u5185\u5bb9",
        r"\u7eed\u8dd1\u5206\u6790\u4e2d",
        r"\u7b49\u5f85\u5206\u6790",
        r"\u5df2\u540c\u6b65",
        r"\u4e2a\u5df2\u6709\u5206\u6790\u5305",
        r"\u4e2a\u7f3a\u53e3\u5206\u6790\u4efb\u52a1",
        r"\u73b0\u6709\u7ae0\u8282\u5df2\u5168\u90e8\u5b8c\u6210\u62c6\u89e3\u540c\u6b65",
        r"\u8865\u9f50\u62c6\u89e3\u5931\u8d25\uff1a",
        r"\u5168\u77e5\u89c6\u89d2",
        r"\u8bf7\u8f93\u5165\u7ae0\u8282\u6807\u9898",
        r"\u7ae0\u8282\u5e8f\u53f7\u4e0d\u5141\u8bb8\u4fee\u6539\uff0c\u8bf7\u5220\u9664\u5bf9\u5e94\u5927\u7eb2\u540e\u91cd\u65b0\u751f\u6210",
        r"\u7f16\u8f91\u7ae0\u8282\u5185\u5bb9",
        r"AI \u6b63\u5728\u521b\u4f5c\u4e2d\uff0c\u8bf7\u7b49\u5f85\u5b8c\u6210\u540e\u518d\u5173\u95ed",
        r"\u6839\u636e\u5927\u7eb2\u548c\u914d\u7f6e\u521b\u4f5c\u7ae0\u8282\u5185\u5bb9",
        r"\u5220\u9664\u540e\u65e0\u6cd5\u6062\u590d\uff0c\u7ae0\u8282\u5185\u5bb9\u548c\u5206\u6790\u7ed3\u679c\u90fd\u5c06\u88ab\u5220\u9664\u3002",
        r"\u67e5\u770b\u5c55\u5f00\u8be6\u60c5",
        r"\u5148\u8865\u9f50\u7f3a\u53e3",
    ]

    missing = [_u(fragment) for fragment in expected_fragments if _u(fragment) not in text]
    assert missing == []

    forbidden_fragments = [
        "??????????",
        r"\u00e6\u00aa\u00e6\u00be",
        r"\u00e8\u00af\u00b7\u00e5",
        r"\u00e7\u00bb\u00ad\u00e8",
        r"\u00e5\u00a0\u00e9\u00a4",
    ]
    forbidden = [_u(fragment) for fragment in forbidden_fragments if _u(fragment) in text]
    assert forbidden == []

    assert "persistContinuationPlan(forcedPlan);" in text
    assert "forceHighRiskContinuation: parsed.forceHighRiskContinuation === true" in text
    assert "const { forceHighRiskContinuation" not in text
    assert text.count("onCancel: handleStartMissingAnalysisForContinuation") >= 3


def test_guardrail_review_formats_source_copy_signals_for_human_review():
    repo_root = Path(__file__).resolve().parents[3]
    page = repo_root / "frontend" / "src" / "pages" / "Chapters.tsx"
    text = page.read_text(encoding="utf-8")

    assert "formatGuardrailCopySignal" in text
    assert "source_entity_leak:" in text
    assert "source entity leak: " in text
    assert ".split('|')" in text
    assert "entities.join(', ')" in text
    assert "distinctive substring" in text

    raw_signal_inline = (
        "violation.copy_signal ? ` / ${violation.copy_signal}` : ''"
    )
    assert raw_signal_inline not in text
