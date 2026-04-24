import os
import urllib.parse
import requests
from typing import Optional, Callable
from pathlib import Path
from git import Repo
import pandas as pd

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsMessageLog,
    Qgis,
    QgsTask
)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtCore import QCoreApplication

from anncsu_manager.qgis_plugin_tools.tools.resources import resources_path

TEMPORARY_OUTPUT = 'TEMPORARY_OUTPUT'
PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))

def tuple_to_dict(list_of_tuples: list[tuple], keys: list[str]) -> list[dict]:
    return [dict(zip(keys, t)) for t in list_of_tuples]

def tuple_to_dataframe(list_of_tuples: list[tuple], columns: list[str]):
    return pd.DataFrame(list_of_tuples, columns=columns)

class EventSource:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        self.listeners.append(listener)
        return self

    def disconnect(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)
        return self

    def emit(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener(*args, **kwargs)
            except Exception as e:
                print(f"Error in event listener: {e}")

def get_output_path(file_widget: QgsFileWidget) -> str:
    fp = file_widget.filePath()
    return fp if fp != "" else TEMPORARY_OUTPUT

def get_output_layer_name(output_raster_path: QgsFileWidget, default_output_name: str) -> str:
    if get_output_path(output_raster_path) == 'TEMPORARY_OUTPUT':
        layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        unique_name = default_output_name
        suffix = 1
        while unique_name in layer_names:
            unique_name = f"{default_output_name}_{suffix}"
            suffix += 1
        return unique_name
    else:
        return os.path.splitext(os.path.basename(output_raster_path.filePath()))[0]


def add_output_layer_to_group(layer, group_name: str, subgroup_name: Optional[str] = None):
    QgsProject.instance().addMapLayer(layer, False)
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    if not group:
        group = root.addGroup(group_name)

    if subgroup_name is not None:
        subgroup = group.findGroup(subgroup_name)
        if not subgroup:
            subgroup = group.addGroup(subgroup_name)

        subgroup.addLayer(layer)
    else:
        group.addLayer(layer)


def find_index_for_text_combobox(
    combo_box: QComboBox, text: str, case_sensitive: bool = False
) -> Optional[int]:
    for index in range(combo_box.count()):
        if case_sensitive:
            if combo_box.itemText(index) == text:
                return index
        else:
            if combo_box.itemText(index).lower() == text.lower():
                return index
    return None


def check_duplicate_names(names: list) -> list:
    name_count = {}
    unique_names = []
    for name in names:
        if name in name_count:
            name_count[name] += 1
            new_name = f"{name}_{name_count[name]}"
        else:
            name_count[name] = 1
            new_name = name
        
        unique_names.append(new_name)
    
    return unique_names


def get_user_data_directory() -> str:
    """
    Returns the directory path where user-defined data is stored.
    Ensures the directory exists.
    """
    # Use QGIS settings directory to store persistent data
    user_data_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), "anncsu_plugin_user_data")
    # Ensure the directory exists
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    return user_data_dir


# ============================================================================
# Download and Git Repository Utilities
# ============================================================================

class DownloadFileTask(QgsTask):
    """QgsTask for downloading files with progress tracking."""

    def __init__(self, url: str, destination_path: Path, description: str = "Downloading file"):
        """Initialize download task.

        Args:
            url: URL to download from
            destination_path: Local path where file will be saved
            description: Task description shown in QGIS task manager
        """
        super().__init__(description, QgsTask.CanCancel)
        self.url = url
        self.destination_path = destination_path
        self.exception = None

    def run(self):
        """Execute the download task.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code != 200:
                self.exception = Exception(f"Failed to download from {self.url}. Status code: {response.status_code}")
                return False

            chunk_size = 8192
            total_size = int(response.headers.get('content-length', 0))
            number_of_chunks = total_size // chunk_size if total_size > 0 else 100
            downloaded_size = 0
            chunk_number = 0

            with open(self.destination_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.isCanceled():
                        return False

                    downloaded_size += len(chunk)
                    file.write(chunk)
                    chunk_number += 1

                    # Update progress (0-100)
                    progress = int(100 * (chunk_number / number_of_chunks))
                    self.setProgress(min(progress, 100))

            return True

        except Exception as e:
            self.exception = e
            return False

    def finished(self, result: bool):
        """Called when task completes.

        Args:
            result: True if successful, False otherwise
        """
        if result:
            QgsMessageLog.logMessage(
                self.tr("Successfully downloaded url: {url} to {destination_path}").format(url=self.url, destination_path=self.destination_path),
                level=Qgis.Info
            )
        else:
            error_msg = str(self.exception) if self.exception else "Unknown error"
            QgsMessageLog.logMessage(
                self.tr("Failed to download url: {url}. Error: {error_msg}").format(url=self.url, error_msg=error_msg),
                level=Qgis.Critical
            )

    def waitForFinished(self, timeout_ms: int = 300000):
        """
        NOTE: UNUSED
        TODO: TO BE DELETED

        Wait for the task to finish (blocking).

        Args:
            timeout_ms: Maximum time to wait in milliseconds (default: 5 minutes)

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        from qgis.PyQt.QtCore import QEventLoop, QTimer

        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)

        completed = [False]
        result = [False]

        def on_completed():
            completed[0] = True
            result[0] = True
            loop.quit()

        def on_terminated():
            completed[0] = True
            result[0] = False
            loop.quit()

        def on_timeout():
            if not completed[0]:
                loop.quit()

        self.taskCompleted.connect(on_completed)
        self.taskTerminated.connect(on_terminated)
        timer.timeout.connect(on_timeout)

        timer.start(timeout_ms)
        loop.exec_()

        return result[0]


def download_file_with_progress(
    url: str,
    destination_path: Path,
    chunk_size: int = 8192
) -> None:
    """Download a file from URL with progress logging (synchronous/blocking).

    This method blocks until the download completes. For non-blocking downloads,
    use `download_file_async()` instead.

    Args:
        url: URL to download from
        destination_path: Local path where file will be saved
        chunk_size: Size of chunks to download (default: 8192 bytes)

    Raises:
        Exception: If download fails
    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download from {url}. Status code: {response.status_code}")

    total_size = int(response.headers.get('content-length', 0))
    number_of_chunks = total_size // chunk_size if (total_size > 0 and chunk_size > 0) else 100
    chunk_number = 0

    QgsMessageLog.logMessage(QCoreApplication.translate("DownloadFileTask", "Downloading from {url} to {destination_path}...").format(url=url, destination_path=destination_path), level=Qgis.Info)
    print(f"Downloading from {url} to {destination_path}...")

    with open(destination_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            chunk_number += 1

            # Log progress every 10%
            progress = int(100 * (chunk_number / number_of_chunks))
            if chunk_number % max(1, number_of_chunks // 10) == 0:
                print(f"Download progress: {progress}%")

    QgsMessageLog.logMessage(QCoreApplication.translate("DownloadFileTask", "Download completed: {destination_path}").format(destination_path=destination_path), level=Qgis.Info)


def download_file_async(
    url: str,
    destination_path: Path,
    on_finished: Optional[Callable] = None
) -> DownloadFileTask:
    """
    NOTE: UNUSED BECAUSE USE DIRECTLY DownloadFileTask
    TODO: TO BE DELETED

    Download a file asynchronously using QgsTask (non-blocking).

    This method returns immediately and the download happens in the background.
    Progress is shown in QGIS task manager.

    Args:
        url: URL to download from
        destination_path: Local path where file will be saved
        on_finished: Optional callback function called when download completes.
                    Receives (task, result) as arguments.

    Returns:
        DownloadFileTask: The task object that can be used to monitor progress

    Example:
        ```python
        def on_download_complete(task, result):
            if result:
                print("Download successful!")
            else:
                print("Download failed!")

        task = download_file_async(
            "https://example.com/file.zip",
            Path("/tmp/file.zip"),
            on_finished=on_download_complete
        )
        # Task runs in background, UI remains responsive
        ```
    """
    task = DownloadFileTask(url, destination_path, f"Downloading {destination_path.name}")

    if on_finished:
        task.taskCompleted.connect(lambda: on_finished(task, True))
        task.taskTerminated.connect(lambda: on_finished(task, False))

    QgsApplication.taskManager().addTask(task)
    return task

class clone_or_pull_git_repo_task(QgsTask):
    """Wrapper task to run clone_or_pull_git_repo in a separate thread with progress tracking.

    Args:
        see clone_or_pull_git_repo for details on parameters and return value.
    """

    def __init__(self, 
            remote_git_repo: str,
            local_path: Path,
            git_user: Optional[str] = None,
            git_password: Optional[str] = None,
            git_token: Optional[str] = None,
            ssh_key: Optional[str] = None
        ) -> None:
        super().__init__(f"Cloning repo {remote_git_repo}", QgsTask.CanCancel)
        self.remote_git_repo = remote_git_repo
        self.local_path = local_path
        self.git_user = git_user
        self.git_password = git_password
        self.git_token = git_token
        self.ssh_key = ssh_key

        # task status
        self.exception = None
        self.result = None
        self.repo: Optional[Repo] = None

    def run(self) -> bool:
        try:
            self.repo = clone_or_pull_git_repo(
                remote_git_repo=self.remote_git_repo,
                local_path=self.local_path,
                git_user=self.git_user,
                git_password=self.git_password,
                git_token=self.git_token,
                ssh_key=self.ssh_key
            )
            if self.repo is None:
                self.result = False
            else:
                self.result = True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(self.tr("Error in clone_or_pull_git_repo_task: {e}").format(e=e), level=Qgis.Critical)
            self.result = False
        
        return self.result

    def finished(self, result: bool):
        if result:
            QgsMessageLog.logMessage(self.tr("Repo {remote_git_repo} cloned successfully in {local_path}").format(remote_git_repo=self.remote_git_repo, local_path=self.local_path), level=Qgis.Info)
        else:
            QgsMessageLog.logMessage(self.tr("Error cloning repo {remote_git_repo} in {local_path}").format(remote_git_repo=self.remote_git_repo, local_path=self.local_path), level=Qgis.Critical)
        return super().finished(result)


def clone_or_pull_git_repo(
    remote_git_repo: str,
    local_path: Path,
    git_user: Optional[str] = None,
    git_password: Optional[str] = None,
    git_token: Optional[str] = None,
    ssh_key: Optional[str] = None
) -> Optional[Repo]:
    """Clone or pull a git repository with authentication support.

    This method handles both cloning a new repository and pulling updates
    to an existing one, with support for SSH keys and HTTPS credentials.

    Args:
        remote_git_repo: Remote git repository URL (HTTPS or SSH)
        local_path: Local path where repository should be cloned/pulled
        git_user: Optional git username for HTTPS authentication
        git_password: Optional git password for HTTPS authentication
        git_token: Optional git token for HTTPS authentication
        ssh_key: Optional path to SSH key file

    Returns:
        Optional[Repo]: Git Repo object if successful, None if error occurs

    Raises:
        Exception: If git operations fail
    """
    try:
        if local_path.exists():
            repo = Repo(local_path)
            origin = repo.remotes.origin
            original_url = origin.url
            temp_url_changed = False
            old_git_ssh = os.environ.get("GIT_SSH_COMMAND")
            try:
                if ssh_key:
                    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o IdentitiesOnly=yes"
                elif git_token or (git_user and git_password):
                    creds = git_token if git_token else f"{urllib.parse.quote(git_user)}:{urllib.parse.quote(git_password)}"
                    parsed = urllib.parse.urlsplit(origin.url)
                    if parsed.scheme in ("http", "https"):
                        netloc = f"{creds}@{parsed.netloc}"
                        auth_url = urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
                        origin.set_url(auth_url)
                        temp_url_changed = True

                # NOTE: repo need to have at least 1 file otherwise git pull do not fetch any ref
                QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Pulling latest changes from git repository at {url}...").format(url=origin.url), level=Qgis.Info)
                origin.pull()

            finally:
                if temp_url_changed:
                    try:
                        origin.set_url(original_url)
                    except Exception:
                        pass
                if ssh_key:
                    if old_git_ssh is None:
                        os.environ.pop("GIT_SSH_COMMAND", None)
                    else:
                        os.environ["GIT_SSH_COMMAND"] = old_git_ssh

            QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Repository already exists at {local_path}, pulled latest changes.").format(local_path=local_path), level=Qgis.Info)
            return repo

        else:
            # prepare a temporary URL with credentials or GIT_SSH_COMMAND for cloning
            temp_url = remote_git_repo
            temp_changed = False
            old_git_ssh = os.environ.get("GIT_SSH_COMMAND")
            repo = None
            try:
                if ssh_key:
                    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o IdentitiesOnly=yes"
                elif git_token or (git_user and git_password):
                    creds = git_token if git_token else f"{urllib.parse.quote(git_user)}:{urllib.parse.quote(git_password)}"
                    parsed = urllib.parse.urlsplit(remote_git_repo)
                    if parsed.scheme in ("http", "https"):
                        netloc = f"{creds}@{parsed.netloc}"
                        temp_url = urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
                        temp_changed = True

                QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Cloning latest changes from git repository at {url}...").format(url=temp_url), level=Qgis.Info)
                repo = Repo.clone_from(temp_url, local_path)

            except Exception as e:
                QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Error cloning git repository {remote_git_repo}: {e}").format(remote_git_repo=remote_git_repo, e=e), level=Qgis.Critical)
                return None
            finally:
                if temp_changed and repo is not None:
                    try:
                        origin = repo.remotes.origin
                        origin.set_url(remote_git_repo)
                    except Exception:
                        pass
                if ssh_key:
                    if old_git_ssh is None:
                        os.environ.pop("GIT_SSH_COMMAND", None)
                    else:
                        os.environ["GIT_SSH_COMMAND"] = old_git_ssh
                QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Successfully cloned repo {remote_git_repo} to {local_path}.").format(remote_git_repo=remote_git_repo, local_path=local_path), level=Qgis.Info)

            return repo

    except Exception as e:
        QgsMessageLog.logMessage(QCoreApplication.translate("clone_or_pull_git_repo_task", "Error cloning/pulling git repository {remote_git_repo}: {e}").format(remote_git_repo=remote_git_repo, e=e), level=Qgis.Critical)
        return None

