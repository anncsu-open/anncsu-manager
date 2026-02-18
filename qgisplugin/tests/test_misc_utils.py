"""Unit tests for anncsu_manager.utils.misc_utils module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from anncsu_manager.utils.misc_utils import (
    PLUGIN_PATH,
    TEMPORARY_OUTPUT,
    EventSource,
    add_output_layer_to_group,
    check_duplicate_names,
    clone_or_pull_git_repo,
    download_file_with_progress,
    find_index_for_text_combobox,
    get_output_layer_name,
    get_output_path,
    get_user_data_directory,
)

# Module path prefix for patching names inside the module under test.
_MU = "anncsu_manager.utils.misc_utils"


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_temporary_output_value(self):
        assert TEMPORARY_OUTPUT == "TEMPORARY_OUTPUT"

    def test_plugin_path_is_string(self):
        assert isinstance(PLUGIN_PATH, str)


# ===========================================================================
# EventSource tests
# ===========================================================================

class TestEventSource:
    def test_connect_adds_listener(self):
        es = EventSource()
        listener = MagicMock()
        es.connect(listener)
        assert listener in es.listeners

    def test_connect_returns_self(self):
        es = EventSource()
        result = es.connect(MagicMock())
        assert result is es

    def test_disconnect_removes_listener(self):
        es = EventSource()
        listener = MagicMock()
        es.connect(listener)
        es.disconnect(listener)
        assert listener not in es.listeners

    def test_disconnect_nonexistent_listener_no_error(self):
        es = EventSource()
        es.disconnect(MagicMock())  # should not raise

    def test_disconnect_returns_self(self):
        es = EventSource()
        result = es.disconnect(MagicMock())
        assert result is es

    def test_emit_calls_all_listeners(self):
        es = EventSource()
        l1 = MagicMock()
        l2 = MagicMock()
        es.connect(l1)
        es.connect(l2)
        es.emit()
        l1.assert_called_once()
        l2.assert_called_once()

    def test_emit_passes_args_and_kwargs(self):
        es = EventSource()
        listener = MagicMock()
        es.connect(listener)
        es.emit("arg1", key="value")
        listener.assert_called_once_with("arg1", key="value")

    def test_emit_continues_after_listener_error(self):
        es = EventSource()
        bad_listener = MagicMock(side_effect=ValueError("boom"))
        good_listener = MagicMock()
        es.connect(bad_listener)
        es.connect(good_listener)
        es.emit()  # should not raise
        good_listener.assert_called_once()

    def test_multiple_connect_adds_duplicate(self):
        es = EventSource()
        listener = MagicMock()
        es.connect(listener)
        es.connect(listener)
        es.emit()
        assert listener.call_count == 2

    def test_emit_no_listeners_does_nothing(self):
        es = EventSource()
        es.emit("ignored")  # should not raise

    def test_chained_connect(self):
        es = EventSource()
        l1 = MagicMock()
        l2 = MagicMock()
        es.connect(l1).connect(l2)
        es.emit()
        l1.assert_called_once()
        l2.assert_called_once()


# ===========================================================================
# check_duplicate_names tests
# ===========================================================================

class TestCheckDuplicateNames:
    def test_no_duplicates(self):
        assert check_duplicate_names(["a", "b", "c"]) == ["a", "b", "c"]

    def test_empty_list(self):
        assert check_duplicate_names([]) == []

    def test_single_item(self):
        assert check_duplicate_names(["a"]) == ["a"]

    def test_with_duplicates(self):
        assert check_duplicate_names(["a", "b", "a"]) == ["a", "b", "a_2"]

    def test_multiple_duplicates_of_same_name(self):
        assert check_duplicate_names(["x", "x", "x"]) == ["x", "x_2", "x_3"]

    def test_preserves_order(self):
        assert check_duplicate_names(["b", "a", "b", "a"]) == ["b", "a", "b_2", "a_2"]

    def test_first_occurrence_unchanged(self):
        result = check_duplicate_names(["name", "name"])
        assert result[0] == "name"
        assert result[1] == "name_2"


# ===========================================================================
# get_output_path tests
# ===========================================================================

class TestGetOutputPath:
    def test_returns_file_path_when_set(self):
        widget = MagicMock()
        widget.filePath.return_value = "/path/to/output.tif"
        assert get_output_path(widget) == "/path/to/output.tif"

    def test_returns_temporary_output_when_empty(self):
        widget = MagicMock()
        widget.filePath.return_value = ""
        assert get_output_path(widget) == TEMPORARY_OUTPUT


# ===========================================================================
# get_output_layer_name tests
# ===========================================================================

class TestGetOutputLayerName:
    def test_returns_basename_when_path_set(self):
        widget = MagicMock()
        widget.filePath.return_value = "/path/to/my_layer.tif"
        result = get_output_layer_name(widget, "default_name")
        assert result == "my_layer"

    def test_returns_default_name_for_temporary_output(self):
        widget = MagicMock()
        widget.filePath.return_value = ""

        mock_project = MagicMock()
        mock_project.instance.return_value.mapLayers.return_value.values.return_value = []

        with patch(f"{_MU}.QgsProject", mock_project):
            result = get_output_layer_name(widget, "default_name")

        assert result == "default_name"

    def test_returns_unique_name_when_default_exists(self):
        widget = MagicMock()
        widget.filePath.return_value = ""

        mock_layer1 = MagicMock()
        mock_layer1.name.return_value = "default_name"
        mock_layer2 = MagicMock()
        mock_layer2.name.return_value = "default_name_1"

        mock_project = MagicMock()
        mock_project.instance.return_value.mapLayers.return_value.values.return_value = [
            mock_layer1, mock_layer2
        ]

        with patch(f"{_MU}.QgsProject", mock_project):
            result = get_output_layer_name(widget, "default_name")

        assert result == "default_name_2"

    def test_strips_extension_from_basename(self):
        widget = MagicMock()
        widget.filePath.return_value = "/data/output.gpkg"
        result = get_output_layer_name(widget, "fallback")
        assert result == "output"


# ===========================================================================
# add_output_layer_to_group tests
# ===========================================================================

class TestAddOutputLayerToGroup:
    def test_adds_layer_to_existing_group(self):
        layer = MagicMock()
        mock_group = MagicMock()
        mock_root = MagicMock()
        mock_root.findGroup.return_value = mock_group

        mock_project = MagicMock()
        mock_project.instance.return_value.layerTreeRoot.return_value = mock_root

        with patch(f"{_MU}.QgsProject", mock_project):
            add_output_layer_to_group(layer, "MyGroup")

        mock_project.instance.return_value.addMapLayer.assert_called_once_with(layer, False)
        mock_group.addLayer.assert_called_once_with(layer)

    def test_creates_group_if_not_found(self):
        layer = MagicMock()
        new_group = MagicMock()
        mock_root = MagicMock()
        mock_root.findGroup.return_value = None
        mock_root.addGroup.return_value = new_group

        mock_project = MagicMock()
        mock_project.instance.return_value.layerTreeRoot.return_value = mock_root

        with patch(f"{_MU}.QgsProject", mock_project):
            add_output_layer_to_group(layer, "NewGroup")

        mock_root.addGroup.assert_called_once_with("NewGroup")
        new_group.addLayer.assert_called_once_with(layer)

    def test_adds_layer_to_subgroup(self):
        layer = MagicMock()
        mock_subgroup = MagicMock()
        mock_group = MagicMock()
        mock_group.findGroup.return_value = mock_subgroup
        mock_root = MagicMock()
        mock_root.findGroup.return_value = mock_group

        mock_project = MagicMock()
        mock_project.instance.return_value.layerTreeRoot.return_value = mock_root

        with patch(f"{_MU}.QgsProject", mock_project):
            add_output_layer_to_group(layer, "Group", subgroup_name="Sub")

        mock_subgroup.addLayer.assert_called_once_with(layer)

    def test_creates_subgroup_if_not_found(self):
        layer = MagicMock()
        new_subgroup = MagicMock()
        mock_group = MagicMock()
        mock_group.findGroup.return_value = None
        mock_group.addGroup.return_value = new_subgroup
        mock_root = MagicMock()
        mock_root.findGroup.return_value = mock_group

        mock_project = MagicMock()
        mock_project.instance.return_value.layerTreeRoot.return_value = mock_root

        with patch(f"{_MU}.QgsProject", mock_project):
            add_output_layer_to_group(layer, "Group", subgroup_name="NewSub")

        mock_group.addGroup.assert_called_once_with("NewSub")
        new_subgroup.addLayer.assert_called_once_with(layer)


# ===========================================================================
# find_index_for_text_combobox tests
# ===========================================================================

class TestFindIndexForTextCombobox:
    def _make_combo(self, items):
        combo = MagicMock()
        combo.count.return_value = len(items)
        combo.itemText.side_effect = lambda i: items[i]
        return combo

    def test_finds_match_case_insensitive(self):
        combo = self._make_combo(["Alpha", "Beta", "Gamma"])
        assert find_index_for_text_combobox(combo, "beta") == 1

    def test_finds_match_case_sensitive(self):
        combo = self._make_combo(["Alpha", "Beta", "Gamma"])
        assert find_index_for_text_combobox(combo, "Beta", case_sensitive=True) == 1

    def test_case_sensitive_no_match(self):
        combo = self._make_combo(["Alpha", "Beta", "Gamma"])
        assert find_index_for_text_combobox(combo, "beta", case_sensitive=True) is None

    def test_returns_none_when_not_found(self):
        combo = self._make_combo(["Alpha", "Beta"])
        assert find_index_for_text_combobox(combo, "delta") is None

    def test_returns_first_match(self):
        combo = self._make_combo(["a", "b", "a"])
        assert find_index_for_text_combobox(combo, "a") == 0

    def test_empty_combo(self):
        combo = self._make_combo([])
        assert find_index_for_text_combobox(combo, "x") is None

    def test_case_insensitive_is_default(self):
        combo = self._make_combo(["HELLO", "world"])
        assert find_index_for_text_combobox(combo, "hello") == 0
        assert find_index_for_text_combobox(combo, "WORLD") == 1


# ===========================================================================
# get_user_data_directory tests
# ===========================================================================

class TestGetUserDataDirectory:
    def test_returns_path_with_plugin_dir_name(self, tmp_path):
        with patch(f"{_MU}.QgsApplication") as mock_app:
            mock_app.qgisSettingsDirPath.return_value = str(tmp_path)
            result = get_user_data_directory()

        assert result == os.path.join(str(tmp_path), "anncsu_plugin_user_data")

    def test_creates_directory_if_not_exists(self, tmp_path):
        with patch(f"{_MU}.QgsApplication") as mock_app:
            mock_app.qgisSettingsDirPath.return_value = str(tmp_path)
            result = get_user_data_directory()

        assert os.path.isdir(result)

    def test_does_not_fail_if_directory_exists(self, tmp_path):
        target = tmp_path / "anncsu_plugin_user_data"
        target.mkdir()

        with patch(f"{_MU}.QgsApplication") as mock_app:
            mock_app.qgisSettingsDirPath.return_value = str(tmp_path)
            result = get_user_data_directory()

        assert result == str(target)


# ===========================================================================
# clone_or_pull_git_repo tests
# ===========================================================================

class TestCloneOrPullGitRepo:
    """Tests for clone_or_pull_git_repo with various auth methods."""

    # ── pull (repo exists) ────────────────────────────────────────────

    def test_pull_when_repo_exists(self, tmp_path):
        local_path = tmp_path / "repo"
        local_path.mkdir()

        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/example/repo.git"
        mock_repo.remotes.origin = mock_origin

        with patch(f"{_MU}.Repo", return_value=mock_repo):
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
            )

        mock_origin.pull.assert_called_once()
        assert result is mock_repo

    def test_pull_with_token_sets_and_restores_url(self, tmp_path):
        local_path = tmp_path / "repo"
        local_path.mkdir()

        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/example/repo.git"
        mock_repo.remotes.origin = mock_origin

        with patch(f"{_MU}.Repo", return_value=mock_repo):
            clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
                git_token="mytoken",
            )

        calls = mock_origin.set_url.call_args_list
        # First call: sets auth URL with token
        assert "mytoken" in str(calls[0])
        # Last call: restores original URL
        assert calls[-1] == call("https://github.com/example/repo.git")

    def test_pull_with_user_password(self, tmp_path):
        local_path = tmp_path / "repo"
        local_path.mkdir()

        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/example/repo.git"
        mock_repo.remotes.origin = mock_origin

        with patch(f"{_MU}.Repo", return_value=mock_repo):
            clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
                git_user="user",
                git_password="p@ss",
            )

        auth_url = str(mock_origin.set_url.call_args_list[0])
        assert "user" in auth_url
        # Password is URL-encoded
        assert "p%40ss" in auth_url

    def test_pull_with_ssh_key_sets_and_restores_env(self, tmp_path):
        local_path = tmp_path / "repo"
        local_path.mkdir()

        mock_repo = MagicMock()
        mock_origin = MagicMock()
        mock_origin.url = "https://github.com/example/repo.git"
        mock_repo.remotes.origin = mock_origin

        old_ssh = os.environ.get("GIT_SSH_COMMAND")

        with patch(f"{_MU}.Repo", return_value=mock_repo):
            clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
                ssh_key="/path/to/key",
            )

        # GIT_SSH_COMMAND should be restored after pull
        if old_ssh is None:
            assert "GIT_SSH_COMMAND" not in os.environ
        else:
            assert os.environ["GIT_SSH_COMMAND"] == old_ssh

    # ── clone (repo does not exist) ───────────────────────────────────

    def test_clone_when_repo_not_exists(self, tmp_path):
        local_path = tmp_path / "new_repo"

        mock_repo = MagicMock()

        with patch(f"{_MU}.Repo") as MockRepo:
            MockRepo.clone_from.return_value = mock_repo
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
            )

        MockRepo.clone_from.assert_called_once_with(
            "https://github.com/example/repo.git", local_path
        )
        assert result is mock_repo

    def test_clone_with_token_uses_auth_url_and_restores(self, tmp_path):
        local_path = tmp_path / "new_repo"
        mock_repo = MagicMock()

        with patch(f"{_MU}.Repo") as MockRepo:
            MockRepo.clone_from.return_value = mock_repo
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
                git_token="mytoken",
            )

        clone_url = MockRepo.clone_from.call_args[0][0]
        assert "mytoken" in clone_url
        # After clone, URL should be restored to the clean original
        mock_repo.remotes.origin.set_url.assert_called_once_with(
            "https://github.com/example/repo.git"
        )

    def test_clone_with_ssh_key_restores_env(self, tmp_path):
        local_path = tmp_path / "new_repo"
        mock_repo = MagicMock()
        old_ssh = os.environ.get("GIT_SSH_COMMAND")

        with patch(f"{_MU}.Repo") as MockRepo:
            MockRepo.clone_from.return_value = mock_repo
            clone_or_pull_git_repo(
                "git@github.com:example/repo.git",
                local_path,
                ssh_key="/path/to/key",
            )

        if old_ssh is None:
            assert "GIT_SSH_COMMAND" not in os.environ
        else:
            assert os.environ["GIT_SSH_COMMAND"] == old_ssh

    def test_clone_error_returns_none(self, tmp_path):
        local_path = tmp_path / "new_repo"

        with patch(f"{_MU}.Repo") as MockRepo:
            MockRepo.clone_from.side_effect = Exception("clone failed")
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
            )

        assert result is None

    def test_returns_none_on_general_error(self, tmp_path):
        local_path = tmp_path / "repo"
        local_path.mkdir()

        with patch(f"{_MU}.Repo", side_effect=Exception("broken")):
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
            )

        assert result is None

    def test_clone_no_credentials(self, tmp_path):
        """Clone without any auth uses the URL as-is."""
        local_path = tmp_path / "new_repo"
        mock_repo = MagicMock()

        with patch(f"{_MU}.Repo") as MockRepo:
            MockRepo.clone_from.return_value = mock_repo
            result = clone_or_pull_git_repo(
                "https://github.com/example/repo.git",
                local_path,
            )

        clone_url = MockRepo.clone_from.call_args[0][0]
        assert clone_url == "https://github.com/example/repo.git"
        assert result is mock_repo


# ===========================================================================
# download_file_with_progress tests
# ===========================================================================

class TestDownloadFileWithProgress:
    def test_downloads_file_successfully(self, tmp_path):
        dest = tmp_path / "downloaded.zip"
        chunk = b"data" * 256  # 1024 bytes

        mock_response = MagicMock()
        mock_response.status_code = 200
        # content-length=0 triggers the fallback (number_of_chunks=100)
        mock_response.headers = {"content-length": "0"}
        mock_response.iter_content.return_value = [chunk]

        with patch(f"{_MU}.requests") as mock_requests, \
             patch(f"{_MU}.QgsMessageLog"):
            mock_requests.get.return_value = mock_response
            download_file_with_progress("https://example.com/file.zip", dest)

        assert dest.read_bytes() == chunk

    def test_raises_on_non_200_status(self, tmp_path):
        dest = tmp_path / "fail.zip"

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch(f"{_MU}.requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            with pytest.raises(Exception, match="Failed to download"):
                download_file_with_progress("https://example.com/file.zip", dest)

    def test_writes_multiple_chunks(self, tmp_path):
        dest = tmp_path / "multi_chunk.bin"

        mock_response = MagicMock()
        mock_response.status_code = 200
        # Use content-length >= chunk_size to avoid division by zero
        mock_response.headers = {"content-length": "16384"}
        mock_response.iter_content.return_value = [b"A" * 8192, b"B" * 8192]

        with patch(f"{_MU}.requests") as mock_requests, \
             patch(f"{_MU}.QgsMessageLog"):
            mock_requests.get.return_value = mock_response
            download_file_with_progress("https://example.com/file.bin", dest)

        data = dest.read_bytes()
        assert len(data) == 16384
        assert data[:8192] == b"A" * 8192
        assert data[8192:] == b"B" * 8192
