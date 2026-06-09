from __future__ import annotations

import sys
import types

import pytest


class _FakePersistentClient:
    def __init__(self, *args, **kwargs):
        del args, kwargs


class _FakeSentenceTransformer:
    def __init__(self, *args, **kwargs):
        del args, kwargs


_fake_chromadb = types.ModuleType("chromadb")
_fake_chromadb.PersistentClient = _FakePersistentClient
sys.modules.setdefault("chromadb", _fake_chromadb)

_fake_sentence_transformers = types.ModuleType("sentence_transformers")
_fake_sentence_transformers.SentenceTransformer = _FakeSentenceTransformer
sys.modules.setdefault("sentence_transformers", _fake_sentence_transformers)

_fake_mcp = types.ModuleType("mcp")
_fake_mcp.ClientSession = type("ClientSession", (), {})
_fake_mcp.types = types.SimpleNamespace()
sys.modules.setdefault("mcp", _fake_mcp)
sys.modules.setdefault("mcp.client", types.ModuleType("mcp.client"))

_fake_streamable_http = types.ModuleType("mcp.client.streamable_http")
_fake_streamable_http.streamablehttp_client = lambda *args, **kwargs: None
sys.modules.setdefault("mcp.client.streamable_http", _fake_streamable_http)

_fake_sse = types.ModuleType("mcp.client.sse")
_fake_sse.sse_client = lambda *args, **kwargs: None
sys.modules.setdefault("mcp.client.sse", _fake_sse)

from app.api.chapters import _should_apply_batch_remix_style_augmentation
from app.api.outlines import _should_apply_remix_style_augmentation


@pytest.mark.parametrize(
    ("has_durable_remix_lineage", "expected"),
    [(False, False), (True, True)],
)
def test_outline_remix_style_augmentation_gate(
    has_durable_remix_lineage: bool,
    expected: bool,
):
    assert (
        _should_apply_remix_style_augmentation(
            has_durable_remix_lineage=has_durable_remix_lineage
        )
        is expected
    )


@pytest.mark.parametrize(
    ("has_durable_remix_lineage", "expected"),
    [(False, False), (True, True)],
)
def test_batch_remix_style_augmentation_gate(
    has_durable_remix_lineage: bool,
    expected: bool,
):
    assert (
        _should_apply_batch_remix_style_augmentation(
            has_durable_remix_lineage=has_durable_remix_lineage
        )
        is expected
    )
