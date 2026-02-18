# Unit Tests for ANNCSU Manager QGIS Plugin

Unit tests for the `anncsu_manager` plugin that run **without** a real QGIS
installation. QGIS and other heavy dependencies are replaced with lightweight
fakes and mocks configured in `conftest.py`.

## Prerequisites

| Package      | Minimum version | Purpose                          |
|--------------|-----------------|----------------------------------|
| Python       | 3.10+           | Runtime                          |
| pytest       | 7.x             | Test runner                      |
| pandas       | 2.x             | DataFrame operations             |
| geopandas    | 0.14+           | GeoDataFrame operations          |
| shapely      | 2.x             | Geometry objects for test data   |

### Install dependencies

If you already have a working Python environment, install the test
dependencies with:

```bash
pip install pytest pandas geopandas shapely
```

> **Note:** `duckdb`, `pydantic`, `qgis`, and other heavy runtime dependencies
> are **not** needed. They are mocked automatically by `conftest.py`.

## Project layout

```
qgisplugin/
├── anncsu_manager/          # Plugin source code
│   └── utils/
│       └── settings_manager.py   # Module under test
└── tests/
    ├── conftest.py           # QGIS mocks, shared fixtures
    ├── test_settings_manager.py  # Test suite (120 tests)
    └── README.md             # This file
```

## How the test environment works

The test suite needs to import `anncsu_manager.utils.settings_manager`, which
normally depends on QGIS, DuckDB, pydantic, and several other packages.
`conftest.py` solves this by injecting fakes into `sys.modules` **before** any
plugin code is imported:

- **QGIS modules** (`qgis.core`, `qgis.gui`, `qgis.PyQt.*`, etc.) are
  replaced with `MagicMock` objects. `QgsSettings` is backed by a plain Python
  dict so get/set operations work realistically.
- **Heavy third-party deps** (`duckdb`, `pydantic`, `requests`, `git`, etc.)
  are mocked at the module level.
- **pandas and geopandas** are kept real (not mocked) because several tests
  exercise actual DataFrame logic.
- **Plugin-internal modules** that cascade into UI/wizard imports
  (`anncsu_manager.plugin`, `anncsu_manager.anncsu_wizard`, etc.) are stubbed
  to prevent Qt initialisation errors.

Individual tests then use `unittest.mock.patch` to swap specific module-level
references (e.g. `duckdb`, `QMessageBox`) with controlled mocks as needed.

## Running the tests

From the `qgisplugin/` directory:

```bash
# Run the full suite
python -m pytest tests/test_settings_manager.py -v

# Run a single test class
python -m pytest tests/test_settings_manager.py::TestUpdateCurrentSession -v

# Run a single test
python -m pytest tests/test_settings_manager.py::TestCreateNewSession::test_scope_data_fields -v

# Run with short summary on failures
python -m pytest tests/test_settings_manager.py --tb=short
```

You can also run from the repository root by specifying the full path:

```bash
python -m pytest qgisplugin/tests/test_settings_manager.py -v
```

## Test classes overview

| Class | Tests | What it covers |
|-------|------:|----------------|
| `TestMunicipalityData` | 3 | `MunicipalityData` dataclass serialisation |
| `TestScopeData` | 8 | `ScopeData` dataclass, `to_dict`, `sync`, repo paths |
| `TestSettingsManagerDefaults` | 7 | Default values for all settings |
| `TestSettingsManagerGettersSetters` | 7 | Set/get round-trips |
| `TestSettingsManagerResets` | 6 | Reset methods restore defaults |
| `TestGitCredentialsEnv` | 12 | Environment-variable-based git credentials |
| `TestGitCredentialsCombined` | 15 | Env + QgsSettings fallback for credentials |
| `TestGeocodersConfigs` | 2 | JSON-based geocoder configuration |
| `TestScopes` | 6 | Scope serialisation/deserialisation from QgsSettings |
| `TestSessionManagement` | 6 | `get_session_repo_local_path`, `delete_session` |
| `TestConstants` | 3 | Class-level constants and defaults |
| `TestGetAnncsuTableDataframe` | 7 | DuckDB read + DataFrame type conversion |
| `TestMergeGeocodedWithAnncsuDataframe` | 7 | Left-join geocoded GeoDataFrame with ANNCSU |
| `TestPopulateTableFromSource` | 11 | DuckDB and ZIP source ingestion |
| `TestCreateNewSession` | 10 | Full session creation orchestration |
| `TestUpdateCurrentSession` | 12 | Session update with coordinate threshold checks |

## Shared fixtures (conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `qgs_settings_store` | function | Direct access to the fake `QgsSettings` backing dict |
| `_clean_state` | function (autouse) | Resets QgsSettings store and `SCOPES` before/after each test |
| `_clean_env_vars` | function (autouse) | Removes credential env-vars before/after each test |
| `sample_municipality` | function | A `MunicipalityData` instance (Roma, H501) |
| `sample_scope` | function | A `ScopeData` instance with a temp DuckDB file |
| `geocoded_gdf` | function | A small `GeoDataFrame` for merge tests |
| `anncsu_df` | function | A small ANNCSU `DataFrame` for merge tests |
| `mock_duckdb_conn` | function | A `MagicMock` DuckDB connection (context-manager-compatible) |
| `patch_externals` | function | Patches `clone_or_pull_git_repo`, `duckdb`, `_populate_table_from_source` |

## Troubleshooting

**`ModuleNotFoundError: No module named 'qgis'`**
Make sure you are running pytest from the `qgisplugin/` directory (or using
`python -m pytest` with the correct path). The `conftest.py` must load before
any test collection happens.

**`ImportError` from `anncsu_manager.__init__`**
The conftest stubs `anncsu_manager.plugin` via `sys.modules` to prevent the
`__init__.py` → `plugin.py` import cascade. If new modules are added to the
plugin that trigger QGIS imports at module level, add corresponding
`sys.modules.setdefault(...)` entries in `conftest.py`.

**Tests pass locally but fail in CI**
Ensure `pandas`, `geopandas`, and `shapely` are installed in the CI
environment. These are the only real (non-mocked) third-party dependencies
required by the test suite.
