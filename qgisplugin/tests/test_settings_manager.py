"""Unit tests for ANNCSUSettingsManager and related dataclasses."""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import geopandas
import pandas
import pytest
from shapely.geometry import Point

# conftest.py patches all QGIS / heavy deps and provides shared fixtures.
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager

# Module path prefix for patching names inside the module under test.
_SM = "anncsu_manager.utils.settings_manager"


# ===========================================================================
# MunicipalityData tests
# ===========================================================================

class TestMunicipalityData:
    def test_to_dict(self, sample_municipality):
        d = sample_municipality.to_dict()
        assert d == {
            "id": 1,
            "nome": "Roma",
            "provincia": "RM",
            "regione": "Lazio",
            "anncsu_id": "H501",
        }

    def test_toJson_roundtrip(self, sample_municipality):
        j = sample_municipality.toJson()
        parsed = json.loads(j)
        assert parsed["nome"] == "Roma"
        assert parsed["anncsu_id"] == "H501"

    def test_fields_accessible(self, sample_municipality):
        assert sample_municipality.id == 1
        assert sample_municipality.nome == "Roma"
        assert sample_municipality.provincia == "RM"
        assert sample_municipality.regione == "Lazio"
        assert sample_municipality.anncsu_id == "H501"


# ===========================================================================
# ScopeData tests
# ===========================================================================

class TestScopeData:
    def test_to_dict(self, sample_scope):
        d = sample_scope.to_dict()
        assert d["syncked"] is False
        assert d["description"] == "Test scope"
        assert d["municipality_data"]["nome"] == "Roma"
        assert d["creation_date"] == "2025-06-15T10:30:00"
        assert d["update_date"] is None

    def test_toJson(self, sample_scope):
        j = sample_scope.toJson()
        parsed = json.loads(j)
        assert parsed["remote_git_repo"] == "https://github.com/example/repo.git"

    def test_to_dict_with_update_date(self, sample_scope):
        sample_scope.update_date = datetime(2025, 7, 1, 12, 0, 0)
        d = sample_scope.to_dict()
        assert d["update_date"] == "2025-07-01T12:00:00"

    def test_get_local_repo_path_no_remote(self, sample_scope):
        sample_scope.remote_git_repo = None
        assert sample_scope.get_local_repo_path() is None

    def test_get_local_repo_path_no_git_dir(self, sample_scope, tmp_path):
        sample_scope.duckdb_path = tmp_path / "no_git" / "test.duckdb"
        sample_scope.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        assert sample_scope.get_local_repo_path() is None

    def test_get_local_repo_path_with_git_dir(self, sample_scope, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        sample_scope.duckdb_path = tmp_path / "test.duckdb"
        result = sample_scope.get_local_repo_path()
        assert result == tmp_path.resolve()

    def test_sync_raises_without_remote(self, sample_scope):
        sample_scope.remote_git_repo = None
        with pytest.raises(Exception, match="Cannot sync scope without remote git repo"):
            sample_scope.sync()

    def test_sync_skips_if_already_syncked(self, sample_scope):
        sample_scope.syncked = True
        # Should return without error (just logs)
        sample_scope.sync()


# ===========================================================================
# ANNCSUSettingsManager – default values
# ===========================================================================

class TestSettingsManagerDefaults:
    def test_default_coordinate_distance_threshold(self):
        result = ANNCSUSettingsManager.get_default_coordinate_distance_threshold()
        assert result == pytest.approx(0.00001)

    def test_default_session_repo_url(self):
        result = ANNCSUSettingsManager.get_default_session_repo_url()
        assert "{nome}" in result
        assert "{anncsu_id}" in result

    def test_default_geofence_polygons_source(self):
        result = ANNCSUSettingsManager.get_geofence_polygons_source()
        assert "parquet" in result

    def test_default_anncsu_repo(self):
        result = ANNCSUSettingsManager.get_anncsu_repo()
        assert "duckdb" in result or "anncsu" in result.lower()

    def test_default_municipality_code(self):
        assert ANNCSUSettingsManager.get_municipality_code() == "0000000"

    def test_default_current_scope_id(self):
        assert ANNCSUSettingsManager.get_current_scope_id() == ""


# ===========================================================================
# ANNCSUSettingsManager – getters / setters
# ===========================================================================

class TestSettingsManagerGettersSetters:
    def test_set_and_get_coordinate_distance_threshold(self):
        ANNCSUSettingsManager.set_default_coordinate_distance_threshold(0.001)
        assert ANNCSUSettingsManager.get_default_coordinate_distance_threshold() == pytest.approx(0.001)

    def test_set_and_get_session_repo_url(self):
        url = "https://github.com/test/{nome}.git"
        ANNCSUSettingsManager.set_default_session_repo_url(url)
        assert ANNCSUSettingsManager.get_default_session_repo_url() == url

    def test_set_and_get_geofence_polygons_source(self):
        src = "https://example.com/geofence.parquet"
        ANNCSUSettingsManager.set_geofence_polygons_source(src)
        assert ANNCSUSettingsManager.get_geofence_polygons_source() == src

    def test_set_and_get_anncsu_repo(self):
        repo = "https://example.com/anncsu.duckdb"
        ANNCSUSettingsManager.set_anncsu_repo(repo)
        assert ANNCSUSettingsManager.get_anncsu_repo() == repo

    def test_set_and_get_municipality_code(self):
        ANNCSUSettingsManager.set_municipality_code("1234567")
        assert ANNCSUSettingsManager.get_municipality_code() == "1234567"

    def test_set_and_get_current_scope_id(self):
        ANNCSUSettingsManager.set_current_scope_id("H501_20250615_103000")
        assert ANNCSUSettingsManager.get_current_scope_id() == "H501_20250615_103000"


# ===========================================================================
# ANNCSUSettingsManager – reset methods
# ===========================================================================

class TestSettingsManagerResets:
    def test_reset_default_session_repo_url(self):
        ANNCSUSettingsManager.set_default_session_repo_url("custom_url")
        ANNCSUSettingsManager.reset_default_session_repo_url()
        assert ANNCSUSettingsManager.get_default_session_repo_url() == ANNCSUSettingsManager.DEFAULT_SESSION_REPO_URL

    def test_reset_geofence_polygons_source(self):
        ANNCSUSettingsManager.set_geofence_polygons_source("custom")
        ANNCSUSettingsManager.reset_geofence_polygons_source()
        assert ANNCSUSettingsManager.get_geofence_polygons_source() == ANNCSUSettingsManager.DEFAULT_GEOFENCE_POLYGONS_SOURCE

    def test_reset_anncsu_repo(self):
        ANNCSUSettingsManager.set_anncsu_repo("custom")
        ANNCSUSettingsManager.reset_anncsu_repo()
        assert ANNCSUSettingsManager.get_anncsu_repo() == ANNCSUSettingsManager.DEFAULT_ANNCSU_REPO_URL

    def test_reset_municipality_code(self):
        ANNCSUSettingsManager.set_municipality_code("9999999")
        ANNCSUSettingsManager.reset_municipality_code()
        assert ANNCSUSettingsManager.get_municipality_code() == "0000000"

    def test_reset_all_restores_defaults(self):
        ANNCSUSettingsManager.set_municipality_code("1111111")
        ANNCSUSettingsManager.set_anncsu_repo("custom_repo")
        ANNCSUSettingsManager.reset_all()
        assert ANNCSUSettingsManager.get_municipality_code() == "0000000"
        assert ANNCSUSettingsManager.get_anncsu_repo() == ANNCSUSettingsManager.DEFAULT_ANNCSU_REPO_URL


# ===========================================================================
# ANNCSUSettingsManager – environment-based git credential methods
# ===========================================================================

class TestGitCredentialsEnv:
    # --- token ---
    def test_get_git_token_env_empty_by_default(self):
        assert ANNCSUSettingsManager.get_git_token_env() == ""

    def test_set_and_get_git_token_env(self):
        ANNCSUSettingsManager.set_git_token_env("my-token")
        assert ANNCSUSettingsManager.get_git_token_env() == "my-token"
        assert os.environ["ANNCSU_GIT_TOKEN"] == "my-token"

    def test_set_git_token_env_empty_unsets(self):
        os.environ["ANNCSU_GIT_TOKEN"] = "temp"
        ANNCSUSettingsManager.set_git_token_env("")
        assert "ANNCSU_GIT_TOKEN" not in os.environ

    # --- user ---
    def test_get_git_user_env_empty_by_default(self):
        assert ANNCSUSettingsManager.get_git_user_env() == ""

    def test_set_and_get_git_user_env(self):
        ANNCSUSettingsManager.set_git_user_env("myuser")
        assert ANNCSUSettingsManager.get_git_user_env() == "myuser"

    def test_set_git_user_env_empty_unsets(self):
        os.environ["ANNCSU_GIT_USER"] = "temp"
        ANNCSUSettingsManager.set_git_user_env("")
        assert "ANNCSU_GIT_USER" not in os.environ

    # --- password ---
    def test_get_git_password_env_empty_by_default(self):
        assert ANNCSUSettingsManager.get_git_password_env() == ""

    def test_set_and_get_git_password_env(self):
        ANNCSUSettingsManager.set_git_password_env("secret")
        assert ANNCSUSettingsManager.get_git_password_env() == "secret"

    def test_set_git_password_env_empty_unsets(self):
        os.environ["ANNCSU_GIT_PASSWORD"] = "temp"
        ANNCSUSettingsManager.set_git_password_env("")
        assert "ANNCSU_GIT_PASSWORD" not in os.environ

    # --- ssh key ---
    def test_get_git_ssh_key_env_empty_by_default(self):
        assert ANNCSUSettingsManager.get_git_ssh_key_env() == ""

    def test_set_and_get_git_ssh_key_env(self):
        ANNCSUSettingsManager.set_git_ssh_key_env("/home/user/.ssh/id_rsa")
        assert ANNCSUSettingsManager.get_git_ssh_key_env() == "/home/user/.ssh/id_rsa"

    def test_set_git_ssh_key_env_empty_unsets(self):
        os.environ["ANNCSU_SSH_KEY"] = "temp"
        ANNCSUSettingsManager.set_git_ssh_key_env("")
        assert "ANNCSU_SSH_KEY" not in os.environ


# ===========================================================================
# ANNCSUSettingsManager – combined credential getters (env + QgsSettings)
# ===========================================================================

class TestGitCredentialsCombined:
    def test_get_git_token_prefers_env(self, qgs_settings_store):
        os.environ["ANNCSU_GIT_TOKEN"] = "env-token"
        qgs_settings_store[ANNCSUSettingsManager.GIT_TOKEN_KEY] = "qgs-token"
        assert ANNCSUSettingsManager.get_git_token() == "env-token"

    def test_get_git_token_falls_back_to_qgs(self, qgs_settings_store):
        qgs_settings_store[ANNCSUSettingsManager.GIT_TOKEN_KEY] = "qgs-token"
        assert ANNCSUSettingsManager.get_git_token() == "qgs-token"

    def test_get_git_token_returns_empty_default(self):
        assert ANNCSUSettingsManager.get_git_token() == ""

    def test_set_git_token_sets_both(self, qgs_settings_store):
        ANNCSUSettingsManager.set_git_token("dual-token")
        assert os.environ.get("ANNCSU_GIT_TOKEN") == "dual-token"
        assert qgs_settings_store[ANNCSUSettingsManager.GIT_TOKEN_KEY] == "dual-token"

    def test_get_git_user_prefers_env(self, qgs_settings_store):
        os.environ["ANNCSU_GIT_USER"] = "env-user"
        qgs_settings_store[ANNCSUSettingsManager.GIT_USER_KEY] = "qgs-user"
        assert ANNCSUSettingsManager.get_git_user() == "env-user"

    def test_get_git_user_falls_back_to_qgs(self, qgs_settings_store):
        qgs_settings_store[ANNCSUSettingsManager.GIT_USER_KEY] = "qgs-user"
        assert ANNCSUSettingsManager.get_git_user() == "qgs-user"

    def test_set_git_user_sets_both(self, qgs_settings_store):
        ANNCSUSettingsManager.set_git_user("dual-user")
        assert os.environ.get("ANNCSU_GIT_USER") == "dual-user"
        assert qgs_settings_store[ANNCSUSettingsManager.GIT_USER_KEY] == "dual-user"

    def test_get_git_password_prefers_env(self, qgs_settings_store):
        os.environ["ANNCSU_GIT_PASSWORD"] = "env-pass"
        qgs_settings_store[ANNCSUSettingsManager.GIT_PASSWORD_KEY] = "qgs-pass"
        assert ANNCSUSettingsManager.get_git_password() == "env-pass"

    def test_get_git_password_falls_back_to_qgs(self, qgs_settings_store):
        qgs_settings_store[ANNCSUSettingsManager.GIT_PASSWORD_KEY] = "qgs-pass"
        assert ANNCSUSettingsManager.get_git_password() == "qgs-pass"

    def test_set_git_password_sets_both(self, qgs_settings_store):
        ANNCSUSettingsManager.set_git_password("dual-pass")
        assert os.environ.get("ANNCSU_GIT_PASSWORD") == "dual-pass"
        assert qgs_settings_store[ANNCSUSettingsManager.GIT_PASSWORD_KEY] == "dual-pass"

    def test_get_git_ssh_key_prefers_env(self, qgs_settings_store):
        os.environ["ANNCSU_SSH_KEY"] = "/env/key"
        qgs_settings_store[ANNCSUSettingsManager.GIT_SSH_KEY_KEY] = "/qgs/key"
        assert ANNCSUSettingsManager.get_git_ssh_key() == "/env/key"

    def test_get_git_ssh_key_falls_back_to_qgs(self, qgs_settings_store):
        qgs_settings_store[ANNCSUSettingsManager.GIT_SSH_KEY_KEY] = "/qgs/key"
        assert ANNCSUSettingsManager.get_git_ssh_key() == "/qgs/key"

    def test_set_git_ssh_key_sets_both(self, qgs_settings_store):
        ANNCSUSettingsManager.set_git_ssh_key("/dual/key")
        assert os.environ.get("ANNCSU_SSH_KEY") == "/dual/key"
        assert qgs_settings_store[ANNCSUSettingsManager.GIT_SSH_KEY_KEY] == "/dual/key"


# ===========================================================================
# ANNCSUSettingsManager – geocoders config (JSON file-based)
# ===========================================================================

class TestGeocodersConfigs:
    def test_set_and_get_geocoders_configs(self, tmp_path, qgs_settings_store):
        json_path = tmp_path / "geocoders.json"
        qgs_settings_store[ANNCSUSettingsManager.GEOCODERS_JSON_PATH_KEY] = str(json_path)

        config = {"Nominatim": {"active": "True", "url": "https://nom.example.com"}}
        ANNCSUSettingsManager.set_geocoders_configs(config)

        result = ANNCSUSettingsManager.get_geocoders_configs()
        assert result["Nominatim"]["active"] == "True"
        assert result["Nominatim"]["url"] == "https://nom.example.com"

    def test_get_geocoders_configs_returns_default_keys(self):
        defaults = ANNCSUSettingsManager.DEFAULT_GEOCODERS_CONFIGS
        assert "Nominatim" in defaults
        assert "Pelias" in defaults
        assert "Photon" in defaults
        assert "WhereAbouts" in defaults


# ===========================================================================
# ANNCSUSettingsManager – scopes
# ===========================================================================

class TestScopes:
    def _make_scope_dict(self, **overrides):
        base = {
            "duckdb_path": "/tmp/test.duckdb",
            "remote_git_repo": "https://github.com/example/repo.git",
            "syncked": False,
            "municipality_data": {
                "id": 1,
                "nome": "Roma",
                "provincia": "RM",
                "regione": "Lazio",
                "anncsu_id": "H501",
            },
            "source_db": "https://example.com/source.duckdb",
            "creation_date": "2025-06-15T10:30:00",
            "update_date": None,
            "description": "Test scope",
        }
        base.update(overrides)
        return base

    def test_get_scopes_empty_by_default(self):
        scopes = ANNCSUSettingsManager.get_scopes()
        assert scopes == {}

    def test_get_scopes_deserialises_from_qgs_settings(self, qgs_settings_store):
        scope_dict = {"H501_20250615": self._make_scope_dict()}
        qgs_settings_store[ANNCSUSettingsManager.SCOPES_KEY] = json.dumps(scope_dict)

        scopes = ANNCSUSettingsManager.get_scopes()
        assert "H501_20250615" in scopes
        scope = scopes["H501_20250615"]
        assert scope.municipality_data.nome == "Roma"
        assert scope.syncked is False
        assert scope.creation_date == datetime(2025, 6, 15, 10, 30, 0)

    def test_get_scopes_skips_invalid_entries(self, qgs_settings_store):
        scope_dict = {
            "valid": self._make_scope_dict(),
            "invalid": {"duckdb_path": "/tmp/x.duckdb"},
        }
        qgs_settings_store[ANNCSUSettingsManager.SCOPES_KEY] = json.dumps(scope_dict)

        scopes = ANNCSUSettingsManager.get_scopes()
        assert "valid" in scopes
        assert "invalid" not in scopes

    def test_set_scopes(self, sample_scope, qgs_settings_store):
        scopes = {"test_scope": sample_scope}
        ANNCSUSettingsManager.set_scopes(scopes)
        assert ANNCSUSettingsManager.SCOPES == scopes
        assert ANNCSUSettingsManager.SCOPES_KEY in qgs_settings_store

    def test_reset_scopes(self, qgs_settings_store):
        qgs_settings_store[ANNCSUSettingsManager.SCOPES_KEY] = '{"old": "data"}'
        ANNCSUSettingsManager.reset_scopes()
        assert qgs_settings_store[ANNCSUSettingsManager.SCOPES_KEY] == ANNCSUSettingsManager.DEFAULT_SCOPES

    def test_get_scopes_with_update_date(self, qgs_settings_store):
        scope_dict = {
            "scope1": self._make_scope_dict(update_date="2025-07-01T12:00:00"),
        }
        qgs_settings_store[ANNCSUSettingsManager.SCOPES_KEY] = json.dumps(scope_dict)

        scopes = ANNCSUSettingsManager.get_scopes()
        assert scopes["scope1"].update_date == datetime(2025, 7, 1, 12, 0, 0)


# ===========================================================================
# ANNCSUSettingsManager – session management
# ===========================================================================

class TestSessionManagement:
    def test_get_session_repo_local_path_no_scope(self):
        assert ANNCSUSettingsManager.get_session_repo_local_path() is None

    def test_get_session_repo_local_path_scope_not_found(self):
        ANNCSUSettingsManager.set_current_scope_id("nonexistent")
        assert ANNCSUSettingsManager.get_session_repo_local_path() is None

    def test_get_session_repo_local_path_returns_parent(self, sample_scope):
        ANNCSUSettingsManager.SCOPES = {"test_scope": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("test_scope")
        result = ANNCSUSettingsManager.get_session_repo_local_path()
        assert result == sample_scope.duckdb_path.parent

    def test_delete_session_removes_scope(self, sample_scope, tmp_path):
        session_dir = tmp_path / "session"
        session_dir.mkdir()
        duckdb_file = session_dir / "test.duckdb"
        duckdb_file.touch()
        sample_scope.duckdb_path = duckdb_file

        ANNCSUSettingsManager.SCOPES = {"test_scope": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("test_scope")

        ANNCSUSettingsManager.delete_session("test_scope")

        assert "test_scope" not in ANNCSUSettingsManager.SCOPES
        assert ANNCSUSettingsManager.get_current_scope_id() == ""
        assert not session_dir.exists()

    def test_delete_session_nonexistent_is_noop(self):
        ANNCSUSettingsManager.SCOPES = {}
        ANNCSUSettingsManager.delete_session("nonexistent")

    def test_delete_session_does_not_reset_scope_id_if_different(self, sample_scope, tmp_path):
        session_dir = tmp_path / "session"
        session_dir.mkdir()
        duckdb_file = session_dir / "test.duckdb"
        duckdb_file.touch()
        sample_scope.duckdb_path = duckdb_file

        ANNCSUSettingsManager.SCOPES = {"scope_a": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("scope_b")

        ANNCSUSettingsManager.delete_session("scope_a")

        assert ANNCSUSettingsManager.get_current_scope_id() == "scope_b"


# ===========================================================================
# ANNCSUSettingsManager – class-level constants
# ===========================================================================

class TestConstants:
    def test_plugin_path_is_path(self):
        assert isinstance(ANNCSUSettingsManager.PLUGIN_PATH, Path)

    def test_defaults_dict_has_expected_keys(self):
        defaults = ANNCSUSettingsManager.DEFAULTS
        assert ANNCSUSettingsManager.MUNICIPALITY_CODE_KEY in defaults
        assert ANNCSUSettingsManager.ANNCSU_REPO_URL_KEY in defaults
        assert ANNCSUSettingsManager.SCOPES_KEY in defaults
        assert ANNCSUSettingsManager.SCOPE_ID_KEY in defaults
        assert ANNCSUSettingsManager.GIT_TOKEN_KEY in defaults
        assert ANNCSUSettingsManager.GIT_USER_KEY in defaults
        assert ANNCSUSettingsManager.GIT_PASSWORD_KEY in defaults
        assert ANNCSUSettingsManager.GIT_SSH_KEY_KEY in defaults

    def test_default_geocoders_json_path_ends_with_json(self):
        assert str(ANNCSUSettingsManager.DEFAULT_GEOCODERS_JSON_PATH).endswith("geocoders.json")


# ===========================================================================
# ANNCSUSettingsManager – get_anncsu_table_dataframe
# ===========================================================================

class TestGetAnncsuTableDataframe:
    """Tests for get_anncsu_table_dataframe which reads a DuckDB and
    returns a typed pandas DataFrame."""

    def _make_raw_df(self):
        """Build a minimal DataFrame mimicking raw DuckDB output."""
        return pandas.DataFrame({
            "PROGRESSIVO_ACCESSO": ["100", "200", "nan"],
            "PROGRESSIVO_NAZIONALE": ["10", "20", "30"],
            "CIVICO": ["1", "2", "nan"],
            "COORD_X_COMUNE": ["12.49", "nan", "11.25"],
            "COORD_Y_COMUNE": ["41.89", "42.01", "nan"],
            "QUOTA": ["50.5", "nan", "30.0"],
            "ODONIMO": ["Via Roma", "Via Milano", "Via Napoli"],
        })

    # ── early-return paths ────────────────────────────────────────────

    def test_returns_none_when_no_scope_id(self):
        """No current scope → None."""
        assert ANNCSUSettingsManager.get_anncsu_table_dataframe() is None

    def test_returns_none_when_scope_id_not_in_scopes(self):
        ANNCSUSettingsManager.set_current_scope_id("missing")
        assert ANNCSUSettingsManager.get_anncsu_table_dataframe() is None

    def test_returns_none_when_duckdb_path_is_none(self, sample_scope):
        sample_scope.duckdb_path = None
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")
        assert ANNCSUSettingsManager.get_anncsu_table_dataframe() is None

    # ── happy path ────────────────────────────────────────────────────

    def test_returns_typed_dataframe(self, sample_scope):
        raw_df = self._make_raw_df()

        mock_conn = MagicMock()
        mock_conn.execute.return_value.df.return_value = raw_df
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_conn

        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.pandas", pandas):
            result = ANNCSUSettingsManager.get_anncsu_table_dataframe()

        assert result is not None
        assert len(result) == 3

        # dtype checks
        assert result["PROGRESSIVO_ACCESSO"].dtype.name == "Int64"
        assert result["PROGRESSIVO_NAZIONALE"].dtype.name == "Int64"
        assert result["CIVICO"].dtype.name == "Int64"
        assert result["COORD_X_COMUNE"].dtype.name == "Float64"
        assert result["COORD_Y_COMUNE"].dtype.name == "Float64"
        assert result["QUOTA"].dtype.name == "Float64"

    def test_nan_strings_replaced_with_none(self, sample_scope):
        raw_df = self._make_raw_df()

        mock_conn = MagicMock()
        mock_conn.execute.return_value.df.return_value = raw_df
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_conn

        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.pandas", pandas):
            result = ANNCSUSettingsManager.get_anncsu_table_dataframe()

        # Row 2 had "nan" for PROGRESSIVO_ACCESSO → should be pandas NA
        assert pandas.isna(result["PROGRESSIVO_ACCESSO"].iloc[2])

    def test_installs_and_loads_spatial_extension(self, sample_scope):
        raw_df = self._make_raw_df()

        mock_conn = MagicMock()
        mock_conn.execute.return_value.df.return_value = raw_df
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_conn

        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.pandas", pandas):
            ANNCSUSettingsManager.get_anncsu_table_dataframe()

        sql_calls = [str(c) for c in mock_conn.execute.call_args_list]
        assert any("INSTALL spatial" in c for c in sql_calls)
        assert any("LOAD spatial" in c for c in sql_calls)

    # ── error path ────────────────────────────────────────────────────

    def test_returns_none_on_duckdb_error(self, sample_scope):
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = RuntimeError("table not found")
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_conn

        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.pandas", pandas):
            result = ANNCSUSettingsManager.get_anncsu_table_dataframe()

        assert result is None


# ===========================================================================
# ANNCSUSettingsManager – merge_geocoded_with_anncsu_dataframe
# ===========================================================================

class TestMergeGeocodedWithAnncsuDataframe:
    """Tests for merge_geocoded_with_anncsu_dataframe which left-joins a
    geocoded GeoDataFrame onto the ANNCSU dataframe."""

    def test_merge_returns_geodataframe(self, geocoded_gdf, anncsu_df):
        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded_gdf, anncsu_df,
            )

        assert isinstance(result, geopandas.GeoDataFrame)
        assert result.crs.to_epsg() == 4326

    def test_merge_has_anncsu_columns(self, geocoded_gdf, anncsu_df):
        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded_gdf, anncsu_df,
            )

        assert "ODONIMO" in result.columns
        assert "CIVICO" in result.columns
        assert "PROGRESSIVO_ACCESSO" in result.columns
        assert "PROGRESSIVO_NAZIONALE" in result.columns

    def test_merge_drops_geocoded_columns_except_geometry(self, geocoded_gdf, anncsu_df):
        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded_gdf, anncsu_df,
            )

        # Geocoded-only columns should be dropped
        assert "address_id" not in result.columns
        assert "road_id" not in result.columns
        assert "longitude" not in result.columns
        assert "latitude" not in result.columns
        # Geometry must be kept
        assert "geometry" in result.columns

    def test_merge_copies_coords_from_lonlat(self, geocoded_gdf, anncsu_df):
        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded_gdf, anncsu_df,
            )

        assert result["COORD_X_COMUNE"].iloc[0] == pytest.approx(12.49)
        assert result["COORD_Y_COMUNE"].iloc[0] == pytest.approx(41.89)

    def test_merge_preserves_row_count(self, geocoded_gdf, anncsu_df):
        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded_gdf, anncsu_df,
            )

        assert len(result) == len(geocoded_gdf)

    def test_merge_unmatched_rows_have_null_anncsu_fields(self):
        """Geocoded rows with no ANNCSU match should still appear (left join)."""
        geocoded = geopandas.GeoDataFrame({
            "address_id": pandas.array([100, 999], dtype="Int64"),
            "road_id": pandas.array([10, 99], dtype="Int64"),
            "longitude": [12.49, 0.0],
            "latitude": [41.89, 0.0],
            "geometry": [Point(12.49, 41.89), Point(0, 0)],
        }, crs="EPSG:4326")

        anncsu = pandas.DataFrame({
            "PROGRESSIVO_ACCESSO": pandas.array([100], dtype="Int64"),
            "PROGRESSIVO_NAZIONALE": pandas.array([10], dtype="Int64"),
            "ODONIMO": ["Via Roma"],
            "CIVICO": pandas.array([1], dtype="Int64"),
        })

        with patch(f"{_SM}.pandas", pandas), \
             patch(f"{_SM}.geopandas", geopandas):
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                geocoded, anncsu,
            )

        assert len(result) == 2
        assert pandas.isna(result["ODONIMO"].iloc[1])

    def test_merge_returns_none_on_error(self):
        with patch(f"{_SM}.pandas") as mock_pd, \
             patch(f"{_SM}.geopandas", geopandas):
            mock_pd.merge.side_effect = ValueError("bad merge")
            result = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                MagicMock(), MagicMock(),
            )

        assert result is None


# ===========================================================================
# ANNCSUSettingsManager – _populate_table_from_source
# ===========================================================================

class TestPopulateTableFromSource:
    """Tests for _populate_table_from_source which creates a DuckDB table
    from either an agenziaentrate.gov.it ZIP or a remote .duckdb file."""

    # ── DuckDB source path (.duckdb URL) ─────────────────────────────

    def test_duckdb_source_attaches_and_creates_table(self, sample_municipality):
        mock_conn = MagicMock()
        source = "https://example.com/data/indirizzarioItalia.duckdb"

        ANNCSUSettingsManager._populate_table_from_source(
            duckdb_conn=mock_conn,
            source_db=source,
            table_name="anncsu",
            municipality_data=sample_municipality,
            scope_name="H501_20250615",
        )

        sql_calls = [str(c) for c in mock_conn.execute.call_args_list]

        # Must ATTACH, CREATE TABLE … FROM indirizzarioItalia.anncsu_global, then DETACH
        assert any("ATTACH DATABASE" in c and source in c for c in sql_calls)
        assert any("CREATE TABLE anncsu" in c for c in sql_calls)
        assert any("indirizzarioItalia.anncsu_global" in c for c in sql_calls)
        assert any("DETACH DATABASE indirizzarioItalia" in c for c in sql_calls)

    def test_duckdb_source_filters_by_municipality_code(self, sample_municipality):
        mock_conn = MagicMock()

        ANNCSUSettingsManager._populate_table_from_source(
            duckdb_conn=mock_conn,
            source_db="https://example.com/data.duckdb",
            table_name="anncsu",
            municipality_data=sample_municipality,
            scope_name="scope1",
        )

        create_call = [
            str(c) for c in mock_conn.execute.call_args_list
            if "CREATE TABLE" in str(c)
        ]
        assert len(create_call) == 1
        assert sample_municipality.anncsu_id in create_call[0]

    def test_duckdb_source_injects_plugin_columns(self, sample_municipality):
        mock_conn = MagicMock()

        ANNCSUSettingsManager._populate_table_from_source(
            duckdb_conn=mock_conn,
            source_db="https://example.com/data.duckdb",
            table_name="anncsu",
            municipality_data=sample_municipality,
            scope_name="scope1",
        )

        create_call = [
            str(c) for c in mock_conn.execute.call_args_list
            if "CREATE TABLE" in str(c)
        ][0]
        assert "PLUGIN_COMUNE" in create_call
        assert "PLUGIN_PROVINCIA" in create_call
        assert "PLUGIN_REGIONE" in create_call
        assert sample_municipality.nome in create_call
        assert sample_municipality.provincia in create_call
        assert sample_municipality.regione in create_call

    def test_duckdb_source_raises_on_invalid_extension(self, sample_municipality):
        mock_conn = MagicMock()

        with pytest.raises(Exception, match="not a valid duckdb file"):
            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://example.com/data.parquet",
                table_name="anncsu",
                municipality_data=sample_municipality,
                scope_name="scope1",
            )

    # ── agenziaentrate.gov.it ZIP source path ────────────────────────

    def test_zip_source_installs_zipfs_extension(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Disposition": 'attachment; filename="INDIR_ITA.zip"'}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = True

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task), \
             patch(f"{_SM}.os.remove"):
            mock_requests.head.return_value = mock_response

            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                table_name="anncsu",
                municipality_data=sample_municipality,
                scope_name="scope1",
            )

        sql_calls = [str(c) for c in mock_conn.execute.call_args_list]
        assert any("INSTALL zipfs" in c for c in sql_calls)
        assert any("LOAD zipfs" in c for c in sql_calls)

    def test_zip_source_uses_content_disposition_filename(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Disposition": 'attachment; filename="INDIR_ITA.zip"'}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = True

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task) as mock_dl, \
             patch(f"{_SM}.os.remove"):
            mock_requests.head.return_value = mock_response

            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                table_name="anncsu",
                municipality_data=sample_municipality,
                scope_name="scope1",
            )

        # download_file_async should receive a path ending with the extracted filename
        dl_path = mock_dl.call_args[0][1]
        assert str(dl_path).endswith("INDIR_ITA.zip")

    def test_zip_source_falls_back_to_temp_filename(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = True

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task) as mock_dl, \
             patch(f"{_SM}.os.remove"):
            mock_requests.head.return_value = mock_response

            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                table_name="anncsu",
                municipality_data=sample_municipality,
                scope_name="myscope",
            )

        dl_path = mock_dl.call_args[0][1]
        assert str(dl_path).endswith("temp_myscope.zip")

    def test_zip_source_creates_table_from_csv(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Disposition": 'attachment; filename="data.zip"'}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = True

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task), \
             patch(f"{_SM}.os.remove"):
            mock_requests.head.return_value = mock_response

            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                table_name="my_table",
                municipality_data=sample_municipality,
                scope_name="scope1",
            )

        sql_calls = [str(c) for c in mock_conn.execute.call_args_list]
        create_call = [c for c in sql_calls if "CREATE TABLE" in c]
        assert len(create_call) == 1
        assert "my_table" in create_call[0]
        assert "READ_CSV_AUTO" in create_call[0]
        assert sample_municipality.anncsu_id in create_call[0]

    def test_zip_source_removes_temp_file(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Disposition": 'attachment; filename="data.zip"'}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = True

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task), \
             patch(f"{_SM}.os.remove") as mock_remove:
            mock_requests.head.return_value = mock_response

            ANNCSUSettingsManager._populate_table_from_source(
                duckdb_conn=mock_conn,
                source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                table_name="anncsu",
                municipality_data=sample_municipality,
                scope_name="scope1",
            )

        mock_remove.assert_called_once()
        removed_path = mock_remove.call_args[0][0]
        assert str(removed_path).endswith("data.zip")

    def test_zip_source_raises_on_download_failure(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = False
        mock_task.exception = RuntimeError("network error")

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task):
            mock_requests.head.return_value = mock_response

            with pytest.raises(Exception, match="Failed to download source database"):
                ANNCSUSettingsManager._populate_table_from_source(
                    duckdb_conn=mock_conn,
                    source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                    table_name="anncsu",
                    municipality_data=sample_municipality,
                    scope_name="scope1",
                )

    def test_zip_source_raises_on_cancelled_download(self, sample_municipality):
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}

        mock_task = MagicMock()
        mock_task.waitForFinished.return_value = False
        mock_task.exception = None  # cancelled, no exception

        with patch(f"{_SM}.requests") as mock_requests, \
             patch(f"{_SM}.download_file_async", return_value=mock_task):
            mock_requests.head.return_value = mock_response

            with pytest.raises(Exception, match="cancelled or timed out"):
                ANNCSUSettingsManager._populate_table_from_source(
                    duckdb_conn=mock_conn,
                    source_db="https://anncsu.open.agenziaentrate.gov.it/getds.php?INDIR_ITA",
                    table_name="anncsu",
                    municipality_data=sample_municipality,
                    scope_name="scope1",
                )


# ===========================================================================
# ANNCSUSettingsManager – create_new_session
# ===========================================================================

class TestCreateNewSession:
    """Tests for create_new_session which orchestrates cloning a git repo,
    populating a DuckDB, creating a geofence table, and registering a scope."""

    SOURCE_DB = "https://example.com/indirizzarioItalia.duckdb"

    # ── happy path ────────────────────────────────────────────────────

    def test_returns_scope_name_and_scope(
        self, sample_municipality, patch_externals,
    ):
        scope_name, scope = ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        assert scope_name is not None
        assert scope is not None
        assert sample_municipality.anncsu_id in scope_name

    def test_scope_data_fields(
        self, sample_municipality, patch_externals,
    ):
        scope_name, scope = ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        assert scope.municipality_data.nome == "Roma"
        assert scope.source_db == self.SOURCE_DB
        assert scope.syncked is True
        assert scope.update_date is None
        assert scope.creation_date is not None
        assert str(scope.duckdb_path).endswith(".duckdb")

    def test_scope_registered_and_set_as_current(
        self, sample_municipality, patch_externals,
    ):
        scope_name, _ = ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        assert scope_name in ANNCSUSettingsManager.SCOPES
        assert ANNCSUSettingsManager.get_current_scope_id() == scope_name

    def test_remote_repo_url_formatted_from_municipality(
        self, sample_municipality, patch_externals,
    ):
        _, scope = ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        # Default template contains {nome} and {anncsu_id}
        assert sample_municipality.nome.lower() in scope.remote_git_repo
        assert sample_municipality.anncsu_id.lower() in scope.remote_git_repo

    def test_clone_called_with_credentials(
        self, sample_municipality, patch_externals, qgs_settings_store,
    ):
        os.environ["ANNCSU_GIT_TOKEN"] = "tok123"
        os.environ["ANNCSU_GIT_USER"] = "usr"
        os.environ["ANNCSU_GIT_PASSWORD"] = "pwd"
        os.environ["ANNCSU_SSH_KEY"] = "/key"

        ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        clone_call = patch_externals["clone"]
        clone_call.assert_called_once()
        kwargs = clone_call.call_args[1]
        assert kwargs["git_token"] == "tok123"
        assert kwargs["git_user"] == "usr"
        assert kwargs["git_password"] == "pwd"
        assert kwargs["ssh_key"] == "/key"

    def test_duckdb_installs_spatial_and_creates_geofence(
        self, sample_municipality, patch_externals,
    ):
        ANNCSUSettingsManager.create_new_session(
            task=MagicMock(),
            source_db=self.SOURCE_DB,
            municipality_data=sample_municipality,
            feedback=MagicMock(),
        )

        conn = patch_externals["conn"]
        sql_calls = [str(c) for c in conn.execute.call_args_list]
        assert any("INSTALL spatial" in c for c in sql_calls)
        assert any("LOAD spatial" in c for c in sql_calls)
        assert any("geofence_polygon" in c for c in sql_calls)
        assert any(sample_municipality.nome in c for c in sql_calls)

    def test_populate_table_from_source_called(
        self, sample_municipality, patch_externals,
    ):
        with patch.object(
            ANNCSUSettingsManager, "_populate_table_from_source"
        ) as mock_pop:
            ANNCSUSettingsManager.create_new_session(
                task=MagicMock(),
                source_db=self.SOURCE_DB,
                municipality_data=sample_municipality,
                feedback=MagicMock(),
            )

        mock_pop.assert_called_once()
        kwargs = mock_pop.call_args[1]
        assert kwargs["source_db"] == self.SOURCE_DB
        assert kwargs["table_name"] == "anncsu"
        assert kwargs["municipality_data"] is sample_municipality

    # ── failure paths ─────────────────────────────────────────────────

    def test_returns_none_when_clone_fails(
        self, sample_municipality, mock_duckdb_conn,
    ):
        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn

        with patch(f"{_SM}.clone_or_pull_git_repo", return_value=None), \
             patch(f"{_SM}.duckdb", mock_duckdb):
            scope_name, scope = ANNCSUSettingsManager.create_new_session(
                task=MagicMock(),
                source_db=self.SOURCE_DB,
                municipality_data=sample_municipality,
                feedback=MagicMock(),
            )

        assert scope_name is None
        assert scope is None

    def test_returns_none_when_repo_url_is_invalid(self, sample_municipality):
        """A non-URL, non-SSH repo template should cause (None, None)."""
        bad_template = "not-a-valid-url-{nome}-{anncsu_id}"
        ANNCSUSettingsManager.set_default_session_repo_url(bad_template)

        # AnyUrl is mocked as str (never raises) – override it so the
        # validation branch is actually exercised.
        def strict_any_url(value):
            if not value.startswith(("http://", "https://")):
                raise ValueError(f"invalid URL: {value}")
            return value

        with patch(f"{_SM}.AnyUrl", side_effect=strict_any_url):
            scope_name, scope = ANNCSUSettingsManager.create_new_session(
                task=MagicMock(),
                source_db=self.SOURCE_DB,
                municipality_data=sample_municipality,
                feedback=MagicMock(),
            )

        assert scope_name is None
        assert scope is None

    def test_ssh_url_is_accepted(
        self, sample_municipality, mock_duckdb_conn,
    ):
        """git@... SSH URLs should not be rejected."""
        ssh_template = "git@github.com:org/anncsu-{nome}-{anncsu_id}.git"
        ANNCSUSettingsManager.set_default_session_repo_url(ssh_template)

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn

        with patch(f"{_SM}.clone_or_pull_git_repo", return_value=MagicMock()), \
             patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            scope_name, scope = ANNCSUSettingsManager.create_new_session(
                task=MagicMock(),
                source_db=self.SOURCE_DB,
                municipality_data=sample_municipality,
                feedback=MagicMock(),
            )

        assert scope_name is not None
        assert "git@github.com" in scope.remote_git_repo


# ===========================================================================
# ANNCSUSettingsManager – update_current_session
# ===========================================================================

class TestUpdateCurrentSession:
    """Tests for update_current_session which merges updated ANNCSU data
    into the current session's DuckDB, handling sync checks, coordinate
    threshold warnings, and user confirmation dialogs."""

    # ── early-exit paths ─────────────────────────────────────────────

    def test_raises_when_no_scope_id(self):
        with pytest.raises(Exception, match="No current session to update"):
            ANNCSUSettingsManager.update_current_session()

    def test_raises_when_scope_id_not_in_scopes(self):
        ANNCSUSettingsManager.set_current_scope_id("missing")
        with pytest.raises(Exception, match="No current session to update"):
            ANNCSUSettingsManager.update_current_session()

    def test_returns_early_when_not_synced_and_user_declines(self, sample_scope):
        """User says No to the 'not synced' warning → no DB operations."""
        sample_scope.syncked = False
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_qmb = MagicMock()
        mock_qmb.No = 0x00010000
        mock_qmb.Yes = 0x00004000
        mock_qmb.question.return_value = mock_qmb.No

        with patch(f"{_SM}.QMessageBox", mock_qmb), \
             patch(f"{_SM}.duckdb") as mock_duckdb:
            ANNCSUSettingsManager.update_current_session()

        mock_duckdb.connect.assert_not_called()

    def test_not_synced_user_accepts_continues_to_db(self, sample_scope, mock_duckdb_conn):
        """User says Yes to the 'not synced' warning → proceeds with DB work."""
        sample_scope.syncked = False
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_qmb = MagicMock()
        mock_qmb.No = 0x00010000
        mock_qmb.Yes = 0x00004000
        mock_qmb.question.return_value = mock_qmb.Yes

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        with patch(f"{_SM}.QMessageBox", mock_qmb), \
             patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        mock_duckdb.connect.assert_called_once()

    # ── happy path (synced, no coordinate diffs) ─────────────────────

    def test_installs_spatial_and_begins_transaction(self, sample_scope, mock_duckdb_conn):
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("BEGIN" in c for c in sql_calls)
        assert any("INSTALL spatial" in c for c in sql_calls)
        assert any("LOAD spatial" in c for c in sql_calls)

    def test_populate_table_called_with_to_delete(self, sample_scope, mock_duckdb_conn):
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source") as mock_pop:
            ANNCSUSettingsManager.update_current_session()

        mock_pop.assert_called_once()
        kwargs = mock_pop.call_args[1]
        assert kwargs["table_name"] == "to_delete"
        assert kwargs["source_db"] == sample_scope.source_db
        assert kwargs["municipality_data"] is sample_scope.municipality_data
        assert kwargs["scope_name"] == "s1"

    def test_creates_updated_anncsu_via_full_outer_join(self, sample_scope, mock_duckdb_conn):
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("updated_anncsu" in c and "FULL OUTER JOIN" in c for c in sql_calls)

    def test_drops_temp_table_and_commits_in_finally(self, sample_scope, mock_duckdb_conn):
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("DROP TABLE IF EXISTS to_delete" in c for c in sql_calls)
        assert any("COMMIT" in c for c in sql_calls)

    # ── coordinate threshold warnings ────────────────────────────────

    def test_no_coordinate_diffs_skips_dialog(self, sample_scope, mock_duckdb_conn):
        """When fetchall returns empty, no QMessageBox is shown for coords."""
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = []

        mock_qmb = MagicMock()

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.QMessageBox", mock_qmb), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        mock_qmb.question.assert_not_called()

    def test_coordinate_diffs_user_views_details_and_proceeds(
        self, sample_scope, mock_duckdb_conn,
    ):
        """Out-of-threshold records → user views details → proceeds with update."""
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        out_of_threshold = [
            {
                "CODICE_COMUNALE_ACCESSO": "001",
                "PROGRESSIVO_NAZIONALE": 10,
                "ANNCSU_COORD_X": 12.50,
                "ANNCSU_COORD_Y": 41.90,
                "LOCAL_COORD_X_COMUNE": 12.49,
                "LOCAL_COORD_Y_COMUNE": 41.89,
            }
        ]

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = out_of_threshold

        mock_qmb = MagicMock()
        mock_qmb.No = 0x00010000
        mock_qmb.Yes = 0x00004000
        # First question: "view details?" → Yes, Second: "proceed?" → Yes
        mock_qmb.question.return_value = mock_qmb.Yes

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.QMessageBox", mock_qmb), \
             patch(f"{_SM}.iface", MagicMock()), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        # Details dialog shown
        mock_qmb.information.assert_called_once()
        # Proceeds: drops local coord columns and renames table
        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("DROP COLUMN LOCAL_COORD_X_COMUNE" in c for c in sql_calls)
        assert any("ALTER TABLE updated_anncsu RENAME TO anncsu" in c for c in sql_calls)

    def test_coordinate_diffs_user_declines_update_rollback(
        self, sample_scope, mock_duckdb_conn,
    ):
        """Out-of-threshold records → user declines proceed → ROLLBACK."""
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        out_of_threshold = [
            {
                "CODICE_COMUNALE_ACCESSO": "001",
                "PROGRESSIVO_NAZIONALE": 10,
                "ANNCSU_COORD_X": 12.50,
                "ANNCSU_COORD_Y": 41.90,
                "LOCAL_COORD_X_COMUNE": 12.49,
                "LOCAL_COORD_Y_COMUNE": 41.89,
            }
        ]

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn
        mock_duckdb_conn.execute.return_value.fetchall.return_value = out_of_threshold

        mock_qmb = MagicMock()
        mock_qmb.No = 0x00010000
        mock_qmb.Yes = 0x00004000
        # First question: "view details?" → No, Second: "proceed?" → No
        mock_qmb.question.return_value = mock_qmb.No

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch(f"{_SM}.QMessageBox", mock_qmb), \
             patch(f"{_SM}.iface", MagicMock()), \
             patch.object(ANNCSUSettingsManager, "_populate_table_from_source"):
            ANNCSUSettingsManager.update_current_session()

        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("ROLLBACK" in c for c in sql_calls)
        # Should NOT rename table
        assert not any("RENAME TO anncsu" in c for c in sql_calls)

    # ── error path ───────────────────────────────────────────────────

    def test_exception_during_db_work_rollbacks_and_raises(
        self, sample_scope, mock_duckdb_conn,
    ):
        sample_scope.syncked = True
        ANNCSUSettingsManager.SCOPES = {"s1": sample_scope}
        ANNCSUSettingsManager.set_current_scope_id("s1")

        mock_duckdb = MagicMock()
        mock_duckdb.connect.return_value = mock_duckdb_conn

        with patch(f"{_SM}.duckdb", mock_duckdb), \
             patch.object(
                 ANNCSUSettingsManager, "_populate_table_from_source",
                 side_effect=RuntimeError("source unavailable"),
             ):
            with pytest.raises(Exception, match="Error updating session"):
                ANNCSUSettingsManager.update_current_session()

        sql_calls = [str(c) for c in mock_duckdb_conn.execute.call_args_list]
        assert any("ROLLBACK" in c for c in sql_calls)
        assert any("DROP TABLE IF EXISTS to_delete" in c for c in sql_calls)
