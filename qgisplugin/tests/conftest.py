"""
conftest.py – Patch QGIS and heavy dependencies *before* any project code
is imported by pytest, so tests can run without a real QGIS installation.
"""

import dataclasses as _dc
import os
import sys
import typing
from datetime import datetime
from unittest.mock import MagicMock, patch

import geopandas
import pandas
import pytest
from shapely.geometry import Point

# ── Fake QgsSettings backed by a plain dict ──────────────────────────────
_qgs_settings_store: dict = {}


class FakeQgsSettings:
    NoSection = 0
    Plugins = 1

    def value(self, key, default=None):
        return _qgs_settings_store.get(key, default)

    def setValue(self, key, value):
        _qgs_settings_store[key] = value


class FakeQgis:
    Info = 0
    Warning = 1
    Critical = 2


class FakeQgsMessageLog:
    messages: list = []

    @classmethod
    def logMessage(cls, msg, *args, **kwargs):
        cls.messages.append(msg)


# ── Install fakes into sys.modules ───────────────────────────────────────

_qgis_core = MagicMock()
_qgis_core.QgsSettings = FakeQgsSettings
_qgis_core.QgsMessageLog = FakeQgsMessageLog
_qgis_core.Qgis = FakeQgis

# All qgis.* sub-modules that are transitively imported
sys.modules["qgis"] = MagicMock()
sys.modules["qgis.core"] = _qgis_core
sys.modules["qgis.gui"] = MagicMock()
sys.modules["qgis.utils"] = MagicMock()
sys.modules["qgis.PyQt"] = MagicMock()
sys.modules["qgis.PyQt.QtCore"] = MagicMock()
sys.modules["qgis.PyQt.QtGui"] = MagicMock()
sys.modules["qgis.PyQt.QtWidgets"] = MagicMock()
sys.modules["qgis.PyQt.QtNetwork"] = MagicMock()
sys.modules["qgis.PyQt.QtXml"] = MagicMock()
sys.modules["qgis.PyQt.Qsci"] = MagicMock()
sys.modules["qgis.PyQt.uic"] = MagicMock()

# Heavy third-party deps imported at module level.
# pandas / geopandas are available on this system – keep them real.
for _mod in (
    "duckdb", "dotenv", "requests",
    "osgeo", "processing", "git",
):
    sys.modules.setdefault(_mod, MagicMock())

# pydantic – keep the real dataclass decorator from stdlib
sys.modules["pydantic"] = MagicMock(AnyUrl=str)
sys.modules["pydantic.dataclasses"] = MagicMock(dataclass=_dc.dataclass)

_te = MagicMock()
_te.Annotated = typing.Annotated
sys.modules["typing_extensions"] = _te

# ── Mock the plugin's own heavy modules to prevent cascading imports ─────
# anncsu_manager.plugin triggers UI / wizard imports that need real Qt.
# We replace it *before* anncsu_manager.__init__ can import it.
sys.modules["anncsu_manager.plugin"] = MagicMock()

# Also stub internal utility modules that pull in more QGIS deps
sys.modules.setdefault("anncsu_manager.utils.message_manager", MagicMock())
sys.modules.setdefault("anncsu_manager.utils.processing_feedback", MagicMock())
sys.modules.setdefault("anncsu_manager.utils.misc_utils", MagicMock())

# Stub the wizard / UI sub-packages that cascade heavily
sys.modules.setdefault("anncsu_manager.anncsu_wizard", MagicMock())
sys.modules.setdefault("anncsu_manager.qgis_plugin_tools", MagicMock())


# ── Fixtures ─────────────────────────────────────────────────────────────
# Lazy-import settings_manager helpers only inside fixtures (after mocks are
# installed above) to avoid circular-import issues at collection time.


@pytest.fixture
def qgs_settings_store():
    """Provide direct access to the fake QgsSettings backing dict."""
    return _qgs_settings_store


@pytest.fixture(autouse=True)
def _clean_state(qgs_settings_store):
    """Reset QgsSettings store and in-memory SCOPES before every test."""
    from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager

    qgs_settings_store.clear()
    ANNCSUSettingsManager.SCOPES = {}
    yield
    qgs_settings_store.clear()
    ANNCSUSettingsManager.SCOPES = {}


@pytest.fixture(autouse=True)
def _clean_env_vars():
    """Remove credential env-vars before/after each test."""
    env_keys = [
        "ANNCSU_GIT_TOKEN",
        "ANNCSU_GIT_USER",
        "ANNCSU_GIT_PASSWORD",
        "ANNCSU_SSH_KEY",
    ]
    for k in env_keys:
        os.environ.pop(k, None)
    yield
    for k in env_keys:
        os.environ.pop(k, None)


@pytest.fixture
def sample_municipality():
    from anncsu_manager.utils.settings_manager import MunicipalityData

    return MunicipalityData(
        id=1,
        nome="Roma",
        provincia="RM",
        regione="Lazio",
        anncsu_id="H501",
    )


@pytest.fixture
def sample_scope(sample_municipality, tmp_path):
    from anncsu_manager.utils.settings_manager import ScopeData

    duckdb_file = tmp_path / "test.duckdb"
    duckdb_file.touch()
    return ScopeData(
        duckdb_path=duckdb_file,
        remote_git_repo="https://github.com/example/repo.git",
        syncked=False,
        municipality_data=sample_municipality,
        source_db="https://example.com/source.duckdb",
        creation_date=datetime(2025, 6, 15, 10, 30, 0),
        update_date=None,
        description="Test scope",
    )


# ── Dataframe fixtures ───────────────────────────────────────────────────

# Module path prefix for patching names inside the module under test.
_SM = "anncsu_manager.utils.settings_manager"


@pytest.fixture
def geocoded_gdf():
    """A small geocoded GeoDataFrame for merge tests."""
    return geopandas.GeoDataFrame({
        "address_id": pandas.array([100, 200], dtype="Int64"),
        "road_id": pandas.array([10, 20], dtype="Int64"),
        "longitude": [12.49, 11.88],
        "latitude": [41.89, 43.77],
        "geometry": [Point(12.49, 41.89), Point(11.88, 43.77)],
    }, crs="EPSG:4326")


@pytest.fixture
def anncsu_df():
    """A small ANNCSU DataFrame for merge tests."""
    return pandas.DataFrame({
        "PROGRESSIVO_ACCESSO": pandas.array([100, 200], dtype="Int64"),
        "PROGRESSIVO_NAZIONALE": pandas.array([10, 20], dtype="Int64"),
        "ODONIMO": ["Via Roma", "Via Milano"],
        "CIVICO": pandas.array([1, 2], dtype="Int64"),
    })


# ── DuckDB / create_new_session fixtures ─────────────────────────────────


@pytest.fixture
def mock_duckdb_conn():
    """A mock DuckDB connection usable as a context manager."""
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


@pytest.fixture
def patch_externals(mock_duckdb_conn):
    """Patch clone_or_pull_git_repo, duckdb.connect, and
    _populate_table_from_source so tests run without side effects."""
    from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager

    mock_duckdb = MagicMock()
    mock_duckdb.connect.return_value = mock_duckdb_conn

    with patch(f"{_SM}.clone_or_pull_git_repo") as mock_clone, \
         patch(f"{_SM}.duckdb", mock_duckdb), \
         patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
        mock_clone.return_value = MagicMock()  # non-None ⇒ success
        yield {
            "clone": mock_clone,
            "duckdb": mock_duckdb,
            "conn": mock_duckdb_conn,
        }
