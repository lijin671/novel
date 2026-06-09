from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

_ORIGINAL_ENV = {
    "DEBUG": os.environ.get("DEBUG"),
    "WORKSHOP_MODE": os.environ.get("WORKSHOP_MODE"),
}

# Keep DEBUG parseable for pydantic bool fields, but avoid blunt overrides.
_VALID_BOOL_VALUES = {"1", "0", "true", "false", "t", "f", "yes", "no", "y", "n", "on", "off"}
_debug_value = os.environ.get("DEBUG")
if _debug_value is None or _debug_value.strip().lower() not in _VALID_BOOL_VALUES:
    os.environ["DEBUG"] = "false"

# Force safe import-time mode so config bootstrap does not create backend/.instance_id.
os.environ["WORKSHOP_MODE"] = "server"


def _install_optional_dependency_stubs() -> None:
    """Stub heavy optional integrations that are not needed by unit tests."""
    from types import ModuleType, SimpleNamespace

    if "chromadb" not in sys.modules:
        chromadb_stub = ModuleType("chromadb")

        class _DummyCollection:
            def add(self, **kwargs):
                return None

            def query(self, **kwargs):
                return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

            def update(self, **kwargs):
                return None

            def delete(self, **kwargs):
                return None

            def get(self, **kwargs):
                return {"ids": [], "documents": [], "metadatas": []}

        class _DummyPersistentClient:
            def __init__(self, *args, **kwargs) -> None:
                self._collection = _DummyCollection()

            def get_or_create_collection(self, *args, **kwargs):
                return self._collection

            def delete_collection(self, *args, **kwargs):
                return None

        chromadb_stub.PersistentClient = _DummyPersistentClient
        sys.modules["chromadb"] = chromadb_stub

    if "sentence_transformers" not in sys.modules:
        sentence_transformers_stub = ModuleType("sentence_transformers")

        class _DummySentenceTransformer:
            def __init__(self, *args, **kwargs) -> None:
                return None

            def encode(self, texts, **kwargs):
                if isinstance(texts, str):
                    return [0.0]
                return [[0.0] for _ in texts]

        sentence_transformers_stub.SentenceTransformer = _DummySentenceTransformer
        sys.modules["sentence_transformers"] = sentence_transformers_stub

    if "mcp" not in sys.modules:
        mcp_stub = ModuleType("mcp")

        class _DummyClientSession:
            async def initialize(self):
                return None

        mcp_stub.ClientSession = _DummyClientSession
        mcp_stub.types = SimpleNamespace()
        sys.modules["mcp"] = mcp_stub
        sys.modules["mcp.client"] = ModuleType("mcp.client")

        streamable_http_stub = ModuleType("mcp.client.streamable_http")

        async def _dummy_streamablehttp_client(*args, **kwargs):
            raise RuntimeError("streamablehttp_client is stubbed in tests")

        streamable_http_stub.streamablehttp_client = _dummy_streamablehttp_client
        sys.modules["mcp.client.streamable_http"] = streamable_http_stub

        sse_stub = ModuleType("mcp.client.sse")

        async def _dummy_sse_client(*args, **kwargs):
            raise RuntimeError("sse_client is stubbed in tests")

        sse_stub.sse_client = _dummy_sse_client
        sys.modules["mcp.client.sse"] = sse_stub


_install_optional_dependency_stubs()



def _patch_starlette_router_lifespan_compat() -> None:
    """Keep tests importable when FastAPI is newer than the installed Starlette."""
    try:
        from starlette.routing import Router
    except Exception:
        return

    if getattr(Router.__init__, "_mumu_accepts_fastapi_lifespan_kwargs", False):
        return

    original_init = Router.__init__

    def compatible_init(
        self,
        routes=None,
        redirect_slashes=True,
        default=None,
        lifespan=None,
        *,
        middleware=None,
        on_startup=None,
        on_shutdown=None,
    ):
        original_init(
            self,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            lifespan=lifespan,
            middleware=middleware,
        )
        self.on_startup = list(on_startup or [])
        self.on_shutdown = list(on_shutdown or [])

    compatible_init._mumu_accepts_fastapi_lifespan_kwargs = True
    Router.__init__ = compatible_init


_patch_starlette_router_lifespan_compat()

from app.database import Base


def pytest_sessionfinish(session, exitstatus):
    del session, exitstatus
    for key, value in _ORIGINAL_ENV.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest_asyncio.fixture
async def async_engine(tmp_path):
    db_path = tmp_path / "test_book_remix_bible.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}", future=True)

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def create_schema(async_engine):
    async def _create_schema(*tables):
        async with async_engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(sync_conn, tables=list(tables))
            )

    return _create_schema


@pytest_asyncio.fixture
async def db_session(async_engine):
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
