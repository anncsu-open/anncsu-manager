from time import sleep

import geopandas
import pandas
import numpy
import json
import os
import requests
import shutil
from functools import partial
from git import Repo
from typing import Optional, Dict, Tuple, Union
from pathlib import Path
from pydantic.dataclasses import dataclass
from pydantic import AnyUrl
from typing_extensions import Annotated
from datetime import datetime
import urllib.parse
from dotenv import load_dotenv

import duckdb

from qgis.utils import iface
from qgis.core import (
    QgsApplication,
    QgsSettings,
    QgsMessageLog,
    Qgis,
    QgsTask,
)
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QSpacerItem,
    QSizePolicy
)
from qgis.PyQt.QtCore import QCoreApplication

from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.utils.misc_utils import (
    EventSource,
    DownloadFileTask,
    clone_or_pull_git_repo_task
)


load_dotenv()

update_anncsu_task: Optional[QgsTask] = None

@dataclass
class MunicipalityData:
    id: Annotated[int, "Sequencial ID of the municipality"]
    nome: Annotated[str, "Name of the municipality"]
    provincia: Annotated[str, "Province of the municipality"]
    regione: Annotated[str, "Region of the municipality"]
    anncsu_id: Annotated[str, "ANNCSU code of the municipality"]

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "provincia": self.provincia,
            "regione": self.regione,
            "anncsu_id": self.anncsu_id,
        }

    def toJson(self) -> str:
        return json.dumps(self.to_dict())

@dataclass
class ScopeData:

    sync_changed = EventSource()

    duckdb_path: Annotated[Path, "Path to local duckdb file"]
    remote_git_repo: Annotated[Optional[str], "URL or git ssh string to remote git repo where store session"]
    syncked: Annotated[bool, "Whether the local duckdb is syncked with remote"]
    municipality_data: Annotated[MunicipalityData, "Municipality data associated with this scope"]
    source_db: Annotated[Optional[AnyUrl], "Source URL from where the duckdb has been extracted"]
    creation_date: datetime
    update_date: Optional[datetime]
    description: Optional[str]

    def to_dict(self):
        return {
            "duckdb_path": str(self.duckdb_path),
            "remote_git_repo": str(self.remote_git_repo) if self.remote_git_repo else None,
            "syncked": self.syncked,
            "municipality_data": self.municipality_data.to_dict(),
            "source_db": str(self.source_db) if self.source_db else None,
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat() if self.update_date else None,
            "description": self.description,
        }

    def toJson(self) -> str:
        return json.dumps(self.to_dict())

    def get_local_repo_path(self) -> Optional[Path]:
        """Get local git repo path where the duckdb is stored.

        Returns:
            Optional[Path]: Path to local git repo folder or None if not found.
        """
        if self.remote_git_repo is None:
            return None

        local_path = Path(self.duckdb_path).parent
        if local_path.exists() and (local_path / ".git").exists():
            return local_path.resolve()
        return None

    def sync(self, files_to_sync: Optional[Union[Path, list[Path]]] = None):
        """Sync duckdb (by default) with remote git repo using git library.
        If files_to_sync is provided, sync only those files.
        Inputs:
            files_to_sync (Optional[Union[str, Path, list[Union[str, Path]]]], optional): Files to sync. Defaults to None. If none DuckDB file is synced.
        Raises:
            Exception: If sync fails.
        """
        if self.remote_git_repo is None:
            raise Exception("Cannot sync scope without remote git repo.")

        # do nothing is already syncked and notify
        if self.syncked:
            QgsMessageLog.logMessage(QCoreApplication.translate("ANNCSUSettingsManager", "Scope at {duckdb_path} is already syncked with remote repo {remote_git_repo}.").format(duckdb_path=self.duckdb_path, remote_git_repo=self.remote_git_repo), level=Qgis.Info)
            return

        local_path = self.get_local_repo_path()
        if local_path is None:
            raise Exception(f"Local git repo path for scope at {self.duckdb_path} not found.")

        # manage input files to commit and sync
        if files_to_sync is None:
            files_to_sync = [self.duckdb_path]
        elif isinstance(files_to_sync, (str, Path)):
            files_to_sync = [files_to_sync]

        # do commit and push e.g. sync
        try:
            print(f"Syncing git repository at {local_path}...")
            repo = Repo(local_path)
            origin = repo.remotes.origin

            # make files to sync relative to repo root
            files_to_sync = [f.resolve() if isinstance(f, Path) else Path(f).resolve() for f in files_to_sync]
            files_to_sync = [f.relative_to(local_path) for f in files_to_sync]

            # Credential helpers: read from QGIS settings via ANNCSUSettingsManager
            git_user = ANNCSUSettingsManager.get_git_user()
            git_password = ANNCSUSettingsManager.get_git_password()
            git_token = ANNCSUSettingsManager.get_git_token()
            ssh_key = ANNCSUSettingsManager.get_git_ssh_key()

            original_url = origin.url
            temp_url_changed = False
            old_git_ssh = os.environ.get("GIT_SSH_COMMAND")

            try:
                # If SSH key provided, instruct git to use it for this process.
                if ssh_key:
                    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o IdentitiesOnly=yes"
                # If HTTPS credentials present, inject them into remote URL temporarily.
                elif git_token or (git_user and git_password):
                    creds = git_token if git_token else f"{urllib.parse.quote(git_user)}:{urllib.parse.quote(git_password)}"
                    parsed = urllib.parse.urlsplit(origin.url)
                    if parsed.scheme in ("http", "https"):
                        netloc = f"{creds}@{parsed.netloc}"
                        auth_url = urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
                        origin.set_url(auth_url)
                        temp_url_changed = True

                origin.pull()
                repo.index.add( [str(f) for f in files_to_sync] )
                repo.index.commit(f"Sync at {datetime.now().isoformat()}")
                origin.push()
                self.syncked = True
            finally:
                # restore original remote url and environment
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

            self.sync_changed.emit()

        except Exception as e:
            self.syncked = False
            raise Exception(f"Error syncing git repository at {local_path}: {e}")


class ANNCSUSettingsManager:
    """
    A centralized interface for accessing and modifying settings of ANNCSU QGIS Plugin.
    
    A static class that does not need instantiation, i.e. it should be used like this: \n
    `env_selection = ANNCSUSettingsManager.get_environment_selection()`
    
    Settings are saved to QGIS project. This is the reason to no use pydantinc to manage
    settings because have to saved in QGIS.ini settings.
    """
    PLUGIN_PATH = Path(os.path.dirname(os.path.dirname(__file__)))

    DEFAULT_COORDINATE_DISTANCE_THRESHOLD=0.00001
    DEFAULT_SESSION_REPO_URL = "https://github.com/anncsu-open/anncsu-{nome}-{anncsu_id}.git"  # format with MunicipalityName and Anncsu code
    DEFAULT_GEOFENCE_POLYGONS_SOURCE = 'https://github.com/geobeyond/anncsu-data/raw/refs/heads/main/com01012025_wgs84.parquet'
    DEFAULT_GEOCODERS_JSON_PATH = PLUGIN_PATH / "resources" / "data" / "geocoders.json"
    # DEFAULT_ANNCSU_REPO_URL = "https://anncsu.open.agenziaentrate.gov.it/age-inspire/opendata/anncsu/getds.php?INDIR_ITA"
    DEFAULT_ANNCSU_REPO_URL = "https://github.com/geobeyond/anncsu-data/raw/refs/heads/main/indirizzarioItalia.duckdb"
    DEFAULT_MUNICIPALITY = "NoName"
    DEFAULT_MUNICIPALITY_CODE = "0000000"
    DEFAULT_GEOCODERS_CONFIGS = {
        "Nominatim": {
            "active": "False",
            "addressdetails": "True",
            "bounded": "False",
            "builder": "NominatimGeocoderBuilder",
            "country_codes": "",
            "dedupe": "True",
            "email": "",
            "extratags": "False",
            "language": "en",
            "limit": 1,
            "max_results": 5,
            "min_score": 0,
            "namedetails": "False",
            "polygon_geojson": "False",
            "polygon_kml": "False",
            "rate_limit": 1.0,
            "timeout": 5,
            "url": "https://nominatim.openstreetmap.org/",
            "user_agent": "ANNCSU Geocode QGIS Plugin",
            "viewbox": ""
        },
        "Pelias": {
            "active": "False",
            "api_key": "",
            "boundary.circle.lat": "",
            "boundary.circle.lon": "",
            "boundary.circle.radius": "",
            "boundary.country": "",
            "boundary.rect.max_lat": "",
            "boundary.rect.max_lon": "",
            "boundary.rect.min_lat": "",
            "boundary.rect.min_lon": "",
            "builder": "PeliasGeocoderBuilder",
            "dedupe": "True",
            "focus.point.lat": "",
            "focus.point.lon": "",
            "lang": "en",
            "layers": "",
            "max_results": 5,
            "min_score": 0,
            "size": 10,
            "sources": "",
            "url": "https://search.geocode.earth/v1/"
        },
        "Photon": {
            "active": "False",
            "builder": "PhotonGeocoderBuilder",
            "dedupe": "True",
            "lang": "en",
            "limit": 10,
            "max_results": 5,
            "min_score": 0,
            "url": "https://photon.komoot.io/api/"
        },
        "WhereAbouts": {
            "active": "True",
            "builder": "WhereaboutsGeocoderBuilder",
            "builder_module": "whereabouts_geocoder",
            # Possible values for "standard", "trigram"
            "how": "trigram",
            "matcher_db": "italia_whereabouts",
            "threshold": 0.8
        }
        # "OpenCage",
        # "LocationIQ",
        # "Geoapify",
        # "MapQuest",
        # "Google Maps",
        # "Bing Maps",
        # "Here Maps",
        # "Mapbox",
        # "TomTom",
        # "Yandex",
        # "ArcGIS Online",
        # "US Census",
        # "What3Words",
        # "Geocodio",
        # "Data Science Toolkit",
        # "OpenAddresses",
        # "Geonames",
        # "BigDataCloud",
        # "MapTiler",
        # "Carto",
        # "Mapillary",
        # "Pelias (Italy)",
    }
    # SCOPES available sessions. Each session has the following data e.g.:
    # SCOPES = {
    #     "OOOOOO_20251008": {
    #         "duckdb_path": "https://geodata.civictech.it/anncsu/OOOOOO_20251008.duckdb",
    #         "temporary_duckdb_path": "OOOOOO_20251008.duckdb",
    #         "remote_git_repo": "https://www.github.com/geobeyond/ANNCSU_NomeComune_OOOOOO.git",
    #         "municipality_code": "0000000",
    #         "creation_date": "2025-10-08",
    #         "update_date": "2025-10-08",
    #         "description": "Italy - National (2025-10-08)",
    #     }
    # }
    DEFAULT_SCOPES: Dict[str, ScopeData] = {}
    SCOPES: Dict[str, ScopeData] = {}

    DEFAULT_COORDINATE_DISTANCE_THRESHOLD_KEY = 'anncsu_manager/default_coordinate_distance_threshold'
    DEFAULT_SESSION_REPO_URL_KEY = 'anncsu_manager/default_session_repo_url'
    GEOFENCE_POLYGONS_SOURCE_KEY = 'anncsu_manager/geofence_polygons_source'
    SCOPES_KEY = "anncsu_manager/geocoders_json_path"
    GEOCODERS_JSON_PATH_KEY = "anncsu_manager/geocoders_json_path"
    ANNCSU_REPO_URL_KEY = "anncsu_manager/anncsu_repo_url"
    MUNICIPALITY_KEY = "anncsu_manager/default_municipality"
    MUNICIPALITY_CODE_KEY = "anncsu_manager/default_municipality_code"
    GEOCODERS_CONFIGS_KEY = "anncsu_manager/geocoders_configs" # unused in QGIS.ini because saved in geocoders.json
    SCOPES_KEY = "anncsu_manager/scopes"
    SCOPE_ID_KEY = "anncsu_manager/current_scope_id"

    # Git credential keys to get from environment variables (preferred) or QGIS settings (fallback)
    GIT_TOKEN_KEY = "anncsu_manager/git_token"  # pragma: allowlist secret - no secter at all but obly a key
    GIT_USER_KEY = "anncsu_manager/git_user"  # pragma: allowlist secret - no secter at all but obly a key
    GIT_PASSWORD_KEY = "anncsu_manager/git_password"  # pragma: allowlist secret - no secter at all but obly a key
    GIT_SSH_KEY_KEY = "anncsu_manager/git_ssh_key"  # pragma: allowlist secret - no secter at all but obly a key

    # add defaults for credentials
    DEFAULTS = {
        DEFAULT_COORDINATE_DISTANCE_THRESHOLD_KEY: DEFAULT_COORDINATE_DISTANCE_THRESHOLD,
        DEFAULT_SESSION_REPO_URL_KEY: DEFAULT_SESSION_REPO_URL,
        GEOFENCE_POLYGONS_SOURCE_KEY: DEFAULT_GEOFENCE_POLYGONS_SOURCE,
        GEOCODERS_JSON_PATH_KEY: str(DEFAULT_GEOCODERS_JSON_PATH),
        ANNCSU_REPO_URL_KEY: DEFAULT_ANNCSU_REPO_URL,
        MUNICIPALITY_KEY: DEFAULT_MUNICIPALITY,
        MUNICIPALITY_CODE_KEY: DEFAULT_MUNICIPALITY_CODE,
        GEOCODERS_CONFIGS_KEY: DEFAULT_GEOCODERS_CONFIGS,
        SCOPES_KEY: DEFAULT_SCOPES,
        # A scope id has the following format: "<codice_municipio>_YYYYMMDD_HHMMSS"
        SCOPE_ID_KEY: "",
    }

    # set credential defaults
    DEFAULTS.update({
        GIT_TOKEN_KEY: "",
        GIT_USER_KEY: "",
        GIT_PASSWORD_KEY: "",
        GIT_SSH_KEY_KEY: "",
    })

    @classmethod
    def tr(cls, text: str) -> str:
        return QCoreApplication.translate('ANNCSUSettingsManager', text)

    # GETTERS
    @classmethod
    def get_default_coordinate_distance_threshold(cls) -> float:
        key = cls.DEFAULT_COORDINATE_DISTANCE_THRESHOLD_KEY
        return float(QgsSettings().value(key, cls.DEFAULTS[key]))

    @classmethod
    def get_default_session_repo_url(cls) -> str:
        key = cls.DEFAULT_SESSION_REPO_URL_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_geofence_polygons_source(cls) -> str:
        key = cls.GEOFENCE_POLYGONS_SOURCE_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_geocoders_json_path(cls) -> str:
        key = cls.GEOCODERS_JSON_PATH_KEY
        return QgsSettings().value(key, str(cls.DEFAULTS[key]))

    @classmethod
    def get_anncsu_repo(cls) -> str:
        key = cls.ANNCSU_REPO_URL_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_municipality(cls) -> str:
        key = cls.MUNICIPALITY_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_municipality_code(cls) -> str:
        key = cls.MUNICIPALITY_CODE_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_geocoders_configs(cls) -> dict:
        # Deserialize
        path = cls.get_geocoders_json_path()
        try:
            if Path(path).exists():
                with open(path) as file:
                    geocoders_config = json.load(file)
            else:
                cls.reset_geocoders_configs()
                geocoders_config = cls.get_geocoders_configs()
        
        # If error, reset
        except (TypeError, json.JSONDecodeError) as e:
            ANNCSUMessageManager().show_message(
                cls.tr("Failed to load default geocoder configs. Reset to default values. {e}").format(e=e),
                "error"
            )
            cls.reset_geocoders_configs()
            geocoders_config = cls.get_geocoders_configs()

        return geocoders_config
    
    @classmethod
    def get_current_scope_id(cls) -> str:
        key = cls.SCOPE_ID_KEY
        return QgsSettings().value(key, cls.DEFAULTS[key])

    @classmethod
    def get_scopes(cls) -> Dict[str, ScopeData]:
        """Returns the scopes saved in QGIS settings.
        maintain a static/singleton image of scopes in memory
        to allow modifications and signals.
        In this way events generate by a scope can be listened by all the
        parts of the plugin that have access to settings manager."""

        if cls.SCOPES is None or len(cls.SCOPES) == 0:
            key = cls.SCOPES_KEY
            # Deserialize
            try:
                serialised = str(QgsSettings().value(key, cls.DEFAULTS[key]))
                scopes_dict = json.loads(serialised)
                scopes = {}
                for scope_id, scope_data in scopes_dict.items():
                    # manage if ScopeData has been changed and discard old structures
                    if not all(k in scope_data for k in ("duckdb_path", "remote_git_repo", "syncked", "municipality_data", "source_db", "creation_date", "update_date")):
                        continue

                    # parse dates
                    creation_date = datetime.fromisoformat(scope_data["creation_date"])
                    update_date = datetime.fromisoformat(scope_data["update_date"]) if scope_data["update_date"] else None
                    scopes[scope_id] = ScopeData(
                        duckdb_path=Path(scope_data["duckdb_path"]),
                        remote_git_repo=scope_data["remote_git_repo"],
                        syncked=scope_data["syncked"],
                        municipality_data=MunicipalityData(**scope_data["municipality_data"]),
                        source_db=scope_data["source_db"],
                        creation_date=creation_date,
                        update_date=update_date,
                        description=scope_data.get("description"),
                    )
                cls.SCOPES = scopes
        
            # If error, reset
            except (TypeError, json.JSONDecodeError) as e:
                ANNCSUMessageManager().show_message(
                    cls.tr("Failed to load default scopes. Reset to default values. {e}").format(e=e),
                    "error"
                )
                cls.reset_scopes()
                cls.SCOPES = cls.get_scopes()

        return cls.SCOPES

    # Environment-backed credential getters/setters (preferred)
    @staticmethod
    def get_git_token_env() -> str:
        """Return ANNCSU_GIT_TOKEN from environment if set, else empty string."""
        return os.environ.get("ANNCSU_GIT_TOKEN", "")

    @staticmethod
    def set_git_token_env(token: str):
        """Set ANNCSU_GIT_TOKEN in environment (use None or empty to unset)."""
        if not token:
            os.environ.pop("ANNCSU_GIT_TOKEN", None)
        else:
            os.environ["ANNCSU_GIT_TOKEN"] = token

    @staticmethod
    def get_git_user_env() -> str:
        return os.environ.get("ANNCSU_GIT_USER", "")

    @staticmethod
    def set_git_user_env(user: str):
        if not user:
            os.environ.pop("ANNCSU_GIT_USER", None)
        else:
            os.environ["ANNCSU_GIT_USER"] = user

    @staticmethod
    def get_git_password_env() -> str:
        return os.environ.get("ANNCSU_GIT_PASSWORD", "")

    @staticmethod
    def set_git_password_env(password: str):
        if not password:
            os.environ.pop("ANNCSU_GIT_PASSWORD", None)
        else:
            os.environ["ANNCSU_GIT_PASSWORD"] = password

    @staticmethod
    def get_git_ssh_key_env() -> str:
        return os.environ.get("ANNCSU_SSH_KEY", "")

    @staticmethod
    def set_git_ssh_key_env(ssh_key_path: str):
        if not ssh_key_path:
            os.environ.pop("ANNCSU_SSH_KEY", None)
        else:
            os.environ["ANNCSU_SSH_KEY"] = ssh_key_path

    # Backwards-compatible getters/setters that prefer env vars, fall back to QGIS settings
    @classmethod
    def get_git_token(cls) -> str:
        token = cls.get_git_token_env()
        if token:
            return token
        return QgsSettings().value(cls.GIT_TOKEN_KEY, cls.DEFAULTS.get(cls.GIT_TOKEN_KEY, ""))

    @classmethod
    def set_git_token(cls, token: str):
        # Persist both in env (preferred) and in QgsSettings for persistence if needed
        cls.set_git_token_env(token)
        QgsSettings().setValue(cls.GIT_TOKEN_KEY, token)

    @classmethod
    def get_git_user(cls) -> str:
        user = cls.get_git_user_env()
        if user:
            return user
        return QgsSettings().value(cls.GIT_USER_KEY, cls.DEFAULTS.get(cls.GIT_USER_KEY, ""))

    @classmethod
    def set_git_user(cls, user: str):
        cls.set_git_user_env(user)
        QgsSettings().setValue(cls.GIT_USER_KEY, user)

    @classmethod
    def get_git_password(cls) -> str:
        pwd = cls.get_git_password_env()
        if pwd:
            return pwd
        return QgsSettings().value(cls.GIT_PASSWORD_KEY, cls.DEFAULTS.get(cls.GIT_PASSWORD_KEY, ""))

    @classmethod
    def set_git_password(cls, password: str):
        cls.set_git_password_env(password)
        QgsSettings().setValue(cls.GIT_PASSWORD_KEY, password)

    @classmethod
    def get_git_ssh_key(cls) -> str:
        """get ssh key path file

        Returns:
            str: path of the key file
        """
        key = cls.get_git_ssh_key_env()
        if key:
            return key
        return QgsSettings().value(cls.GIT_SSH_KEY_KEY, cls.DEFAULTS.get(cls.GIT_SSH_KEY_KEY, ""))

    @classmethod
    def set_git_ssh_key(cls, ssh_key_path: str):
        cls.set_git_ssh_key_env(ssh_key_path)
        QgsSettings().setValue(cls.GIT_SSH_KEY_KEY, ssh_key_path)

# SETTERS
    @classmethod
    def set_default_coordinate_distance_threshold(cls, threshold: float):
        QgsSettings().setValue(cls.DEFAULT_COORDINATE_DISTANCE_THRESHOLD_KEY, threshold)

    @classmethod
    def set_default_session_repo_url(cls, url: str):
        QgsSettings().setValue(cls.DEFAULT_SESSION_REPO_URL_KEY, url)

    @classmethod
    def set_geofence_polygons_source(cls, source: str):
        QgsSettings().setValue(cls.GEOFENCE_POLYGONS_SOURCE_KEY, source)

    @classmethod
    def set_geocoders_json_path(cls, path: str):
        if not Path(path).exists():
            ANNCSUMessageManager().show_message(
                cls.tr("Could not find geocoders.json at {path}. Reverting to default path.").format(path=path),
                "warning"
            )
            geocoders_json_path = cls.get_geocoders_json_path()
            ANNCSUSettingsManager.set_geocoders_json_path(str(geocoders_json_path))
        QgsSettings().setValue(cls.GEOCODERS_JSON_PATH_KEY, path)

    @classmethod
    def set_anncsu_repo(cls, anncsu_repo: str):
        QgsSettings().setValue(cls.ANNCSU_REPO_URL_KEY, anncsu_repo)

    @classmethod
    def set_municipality(cls, municipality: str):
        print(f"Setting municipality code to {municipality}")
        QgsSettings().setValue(cls.MUNICIPALITY_KEY, municipality)

    @classmethod
    def set_municipality_code(cls, municipality_code: str):
        print(f"Setting municipality code to {municipality_code}")
        QgsSettings().setValue(cls.MUNICIPALITY_CODE_KEY, municipality_code)

    @classmethod
    def set_geocoders_configs(cls, geocoders_configs: dict):
        encoded_value = json.dumps(geocoders_configs)
        with open(cls.get_geocoders_json_path(), "w") as file:
            file.write(encoded_value)
        # QgsSettings().setValue(cls.GEOCODERS_CONFIGS_KEY, encoded_value)

    @classmethod
    def set_current_scope_id(cls, scope_id: str):
        QgsSettings().setValue(cls.SCOPE_ID_KEY, scope_id)

    @classmethod
    def set_scopes(cls, scopes: dict[str, ScopeData]):
        class jsonEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, ScopeData):
                    return obj.to_dict()
                return super().default(obj)

        encoded_value = json.dumps(scopes, cls=jsonEncoder)
        QgsSettings().setValue(cls.SCOPES_KEY, encoded_value)
        cls.SCOPES = scopes

    # RESETS
    @classmethod
    def reset_default_session_repo_url(cls):
        QgsSettings().setValue(cls.DEFAULT_SESSION_REPO_URL_KEY, cls.DEFAULTS[cls.DEFAULT_SESSION_REPO_URL_KEY])

    @classmethod
    def reset_geofence_polygons_source(cls):
        QgsSettings().setValue(cls.GEOFENCE_POLYGONS_SOURCE_KEY, cls.DEFAULTS[cls.GEOFENCE_POLYGONS_SOURCE_KEY])

    @classmethod
    def reset_anncsu_repo(cls):
        QgsSettings().setValue(cls.ANNCSU_REPO_URL_KEY, cls.DEFAULTS[cls.ANNCSU_REPO_URL_KEY])

    @classmethod
    def reset_municipality(cls):
        QgsSettings().setValue(cls.MUNICIPALITY_KEY, cls.DEFAULTS[cls.MUNICIPALITY_KEY])

    @classmethod
    def reset_municipality_code(cls):
        QgsSettings().setValue(cls.MUNICIPALITY_CODE_KEY, cls.DEFAULTS[cls.MUNICIPALITY_CODE_KEY])

    @classmethod
    def reset_geocoders_configs(cls):
        cls.set_geocoders_configs(cls.DEFAULTS[cls.GEOCODERS_CONFIGS_KEY])
        # QgsSettings().setValue(cls.GEOCODERS_CONFIGS_KEY, cls.DEFAULTS[cls.GEOCODERS_CONFIGS_KEY])

    @classmethod
    def reset_scopes(cls):
        QgsSettings().setValue(cls.SCOPES_KEY, cls.DEFAULTS[cls.SCOPES_KEY])

    @classmethod
    def reset_all(cls):
        cls.reset_default_session_repo_url()
        cls.reset_geofence_polygons_source()
        cls.reset_anncsu_repo()
        cls.reset_municipality()
        cls.reset_municipality_code()
        cls.reset_geocoders_configs()
        cls.reset_scopes()

    @staticmethod
    def delete_session(scope_id: str):
        scopes = ANNCSUSettingsManager.get_scopes()
        if scope_id in scopes:
            scope = scopes[scope_id]
            # remove local duckdb file
            if scope.duckdb_path.exists():
                session_folder = scope.duckdb_path.parent
                if session_folder.exists() and session_folder.is_dir():
                    shutil.rmtree(session_folder, ignore_errors=True)

            # remove from settings
            del scopes[scope_id]
            ANNCSUSettingsManager.set_scopes(scopes)
            # if deleted scope is current scope, reset current scope id
            current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
            if current_scope_id == scope_id:
                ANNCSUSettingsManager.set_current_scope_id("")

    @classmethod
    def get_session_repo_local_path(cls) -> Optional[Path]:
        scope_id = cls.get_current_scope_id()
        scopes = cls.get_scopes()

        if not scope_id or (scope_id not in scopes):
            return None

        scope = scopes[scope_id]
        if scope.duckdb_path is None:
            return None

        local_path = Path(scope.duckdb_path).parent
        return local_path

    @classmethod
    def get_table(cls, table_name: str) -> Tuple[Optional[list[tuple]], Optional[list[str]]]:
        """Get duckdb connection to current scope duckdb and check if table with name "table_name" exists.
        
        NOTE: all columns stating with: PLUGIN_* are introduced by the plugin
        NOTE: the geom column is returned as WKB to avoid issues with duckdb spatial extension that is not compatible with all the libraries that manage geometries, so it's necessary to convert it to geometry in the rest of the code using shapely.wkb.loads or similar functions.
        Returns:
            Tuple[Optional[list[tuple]], Optional[list[str]]]: DuckDB tuple and list of column names 
                                                               if table exists, else None, None.
        """
        scope_id = cls.get_current_scope_id()
        scopes = cls.get_scopes()

        if not scope_id or (scope_id not in scopes):
            return None, None

        scope = scopes[scope_id]
        if scope.duckdb_path is None:
            return None, None

        # connect to duckdb and read anncsu table
        with duckdb.connect(database=str(scope.duckdb_path)) as scopedb:
            try:
                scopedb.execute("INSTALL spatial;")
                scopedb.execute("LOAD spatial;")

                # check if table exists
                exists = scopedb.execute(f"SELECT * FROM information_schema.tables WHERE table_name = '{table_name}';").df()
                if len(exists) == 0:
                    QgsMessageLog.logMessage(cls.tr("Table '{table_name}' not found in duckdb at {duckdb_path}.").format(table_name=table_name, duckdb_path=scope.duckdb_path), level=Qgis.Warning)
                    return None, None

                # get columns names from duckdb
                columns = scopedb.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';").fetchall()
                columns = [col[0] for col in columns]

                try:
                    records = scopedb.execute(f"SELECT * EXCLUDE(geom), ST_AsWKB(geom) AS geom FROM '{table_name}'").fetchall()
                except Exception as e:
                    # in case no geom column is present or geom column is already in WKB format just ignore and keep original table                    if 'ST_AsWKB(WKB_BLOB)' in str(e):
                    QgsMessageLog.logMessage(cls.tr("Error: {e}").format(e=e), level=Qgis.Warning)
                    records = scopedb.execute(f"SELECT * FROM '{table_name}'").fetchall()

                return records, columns

            except Exception as e:
                QgsMessageLog.logMessage(cls.tr("Error reading {table_name} table from duckdb at {duckdb_path}: {e}").format(table_name=table_name, duckdb_path=scope.duckdb_path, e=e), level=Qgis.Critical)
                return None, None

    @classmethod
    def get_table_dataframe(cls, table_name: str = 'anncsu') -> Tuple[Optional[geopandas.GeoDataFrame], Optional[dict]]:
        """Get table with name "table_name" ("anncsu" by default or "geocoded_anncsu") from duckdb of
        current scope as geopandas dataframe.
        
        NOTE: anncsu or geocoded_anncsu DB table contain columns introduced by the plugin stating with: PLUGIN_*
        Returns:
            Tuple[Optional[geopandas.GeoDataFrame], Optional[dict]]: A tuple with the dataframe and a dict with original column types, or None if error occurs.
        """
        scope_id = cls.get_current_scope_id()
        scopes = cls.get_scopes()

        if not scope_id or (scope_id not in scopes):
            return None, None

        scope = scopes[scope_id]
        if scope.duckdb_path is None:
            return None, None

        # connect to duckdb and read anncsu table
        with duckdb.connect(database=str(scope.duckdb_path)) as scopedb:
            try:
                # check if table exists
                exists = scopedb.execute(f"SELECT * FROM information_schema.tables WHERE table_name = '{table_name}';").df()
                if len(exists) == 0:
                    QgsMessageLog.logMessage(cls.tr("Table '{table_name}' not found in duckdb at {duckdb_path}.").format(table_name=table_name, duckdb_path=scope.duckdb_path), level=Qgis.Warning)
                    return None, None

                scopedb.execute("INSTALL spatial;")
                scopedb.execute("LOAD spatial;")

                df = scopedb.execute(f"SELECT * FROM '{table_name}'").df()

                # clean 'nan' strings to None to avoid to have numeric columns with 'nan' string
                # values that cannot be converted to numeric types
                df = df.replace('nan', None)

                # save column types to preserve after confertions
                column_types = df.dtypes.to_dict()

                # change dtype of PROGRESSIVO_ACCESSO and PROGRESSIVO_NAZIONALE to int
                df['PROGRESSIVO_ACCESSO'] = pandas.to_numeric(df['PROGRESSIVO_ACCESSO'], errors='coerce').astype('Int64')
                df['PROGRESSIVO_NAZIONALE'] = pandas.to_numeric(df['PROGRESSIVO_NAZIONALE'], errors='coerce').astype('Int64')

                # change dtype of NUMERO_CIVICO, METRICO, PROGRESSIVO_SNC and METODO to int
                df['CIVICO'] = pandas.to_numeric(df['CIVICO'], errors='coerce').astype('Int64')
                df['METRICO'] = pandas.to_numeric(df['METRICO'], errors='coerce').astype('Int64')
                df['PROGRESSIVO_SNC'] = pandas.to_numeric(df['PROGRESSIVO_SNC'], errors='coerce').astype('Int64')
                df['METODO'] = pandas.to_numeric(df['METODO'], errors='coerce').astype('Int64')

                # change dtype of COORD_X_COMUNE and COORD_Y_COMUNE to float
                df['COORD_X_COMUNE'] = pandas.to_numeric(df['COORD_X_COMUNE'], errors='coerce').astype('Float64')
                df['COORD_Y_COMUNE'] = pandas.to_numeric(df['COORD_Y_COMUNE'], errors='coerce').astype('Float64')

                # change dtype of QUOTA to float
                df['QUOTA'] = pandas.to_numeric(df['QUOTA'], errors='coerce').astype('Float64')

                # clean numpy.NATypes to None.- This is necessary because pandas.to_numeric with errors='coerce' convert
                # non numeric values to NaN and the resto of python code assume a NA or NaN valus should be None, but pandas use 
                # numpy.NA that is not recognized as NA value by other libraries, so we need to convert it to None.
                df = df.replace({numpy.nan: None})
                # df = df.astype(column_types)  # restore original column types after conversions

                return (df, column_types)
            except Exception as e:
                QgsMessageLog.logMessage(cls.tr("Error reading {table_name} table from duckdb at {duckdb_path}: {e}").format(table_name=table_name, duckdb_path=scope.duckdb_path, e=e), level=Qgis.Critical)
                return None, None

    @classmethod
    def merge_geocoded_with_anncsu_dataframe(
        cls,
        geocoded_dataframe: geopandas.GeoDataFrame,
        anncsu_dataframe: geopandas.GeoDataFrame
    ) -> Optional[geopandas.GeoDataFrame]:
        """Merge geocoded dataframe with anncsu dataframe based on 'anncsu_id' field.

        Args:
            geocoded_dataframe (geopandas.GeoDataFrame): Geocoded dataframe 'address_id' and 'road_id' fields.
            anncsu_dataframe (geopandas.GeoDataFrame): Anncsu dataframe with 'PROGRESSIVO_ACCESSO' and 'PROGRESSIVO_NAZIONALE' fields.

        Returns:
            Optional[geopandas.GeoDataFrame]: Merged dataframe or None if error occurs.
        """
        try:
            merged_df = pandas.merge(
                geocoded_dataframe,
                anncsu_dataframe,
                left_on=["address_id", "road_id"],
                right_on=["PROGRESSIVO_ACCESSO", "PROGRESSIVO_NAZIONALE"],
                how="left"
            )

            # set COORD_X_COMUNE and COORD_Y_COMUNE from longitude and latitude
            if 'longitude' in merged_df.columns and 'latitude' in merged_df.columns:
                merged_df['COORD_X_COMUNE'] = merged_df['longitude']
                merged_df['COORD_Y_COMUNE'] = merged_df['latitude']
            
            # drop all  columns except geometry
            cols_to_drop = [col for col in geocoded_dataframe.columns if col != 'geom']
            merged_df = merged_df.drop(columns=cols_to_drop)

            # drop all automatic columns generated by pandas merge becase PK are "PROGRESSIVO_ACCESSO" and "PROGRESSIVO_NAZIONALE"
            merged_df = merged_df.drop(columns=['fid', 'id'], errors='ignore')

            # rename geometry to geometry
            merged_df = geopandas.GeoDataFrame(merged_df, geometry='geom', crs="EPSG:4326")

            return merged_df
        except Exception as e:
            QgsMessageLog.logMessage(cls.tr("Error merging geocoded dataframe with anncsu dataframe: {e}").format(e=e), level=Qgis.Critical)
            return None

    @classmethod
    def merge_geocoded_with_anncsu_dataframe(
        cls,
        geocoded_dataframe: geopandas.GeoDataFrame,
        anncsu_dataframe: geopandas.GeoDataFrame
    ) -> Optional[geopandas.GeoDataFrame]:
        """Merge geocoded dataframe with anncsu dataframe based on 'anncsu_id' field.

        Args:
            geocoded_dataframe (geopandas.GeoDataFrame): Geocoded dataframe 'address_id' and 'road_id' fields.
            anncsu_dataframe (geopandas.GeoDataFrame): Anncsu dataframe with 'PROGRESSIVO_ACCESSO' and 'PROGRESSIVO_NAZIONALE' fields.

        Returns:
            Optional[geopandas.GeoDataFrame]: Merged dataframe or None if error occurs.
        """
        try:
            merged_df = pandas.merge(
                geocoded_dataframe,
                anncsu_dataframe,
                left_on=["address_id", "road_id"],
                right_on=["PROGRESSIVO_ACCESSO", "PROGRESSIVO_NAZIONALE"],
                how="left"
            )

            # set COORD_X_COMUNE and COORD_Y_COMUNE from longitude and latitude
            if 'longitude' in merged_df.columns and 'latitude' in merged_df.columns:
                merged_df['COORD_X_COMUNE'] = merged_df['longitude']
                merged_df['COORD_Y_COMUNE'] = merged_df['latitude']
            
            # drop all  columns except geom
            cols_to_drop = [col for col in geocoded_dataframe.columns if col != 'geom']
            merged_df = merged_df.drop(columns=cols_to_drop)

            # drop all automatic columns generated by pandas merge becase PK are "PROGRESSIVO_ACCESSO" and "PROGRESSIVO_NAZIONALE"
            merged_df = merged_df.drop(columns=['fid', 'id'], errors='ignore')

            # make geodataframe
            merged_df = geopandas.GeoDataFrame(merged_df, geometry='geom', crs="EPSG:4326")

            return merged_df
        except Exception as e:
            QgsMessageLog.logMessage(cls.tr("Error merging geocoded dataframe with anncsu dataframe: {e}").format(e=e), level=Qgis.Critical)
            return None

    @classmethod
    def update_current_session(
        cls,
    ) -> bool:
        """Update current session data in SCOPES.

        This method checks if the current session is synchronized with the remote git repository
        and if the duckdb_path is changed, if so it warns the user about potential loss of
        unsynchronized changes.
        Then it merges the updated values with the current anncsu table and updates the current
        duckdb file. It also updates the update_date of the session in SCOPES and saves the updated
        SCOPES in QGIS settings.

        The update starts from the table "new_anncsu" dowunlaoded before the call of this function
        The update process leaves some backup of the previous anncsu table in case of errors during
        the update process, and it updates only the values of the geocoded_anncsu table that are
        present in the temp table generated during the update from merging,
        matching by PK (PROGRESSIVO_ACCESSO, PROGRESSIVO_NAZIONALE), if a row in temp table is
        not present in anncsu table, it is inserted.

        the backup tables are:
        - anncsu_backup: a backup of the anncsu table before the update.
        - previous_geocoded_anncsu: a table that contains the geocoded_anncsu data before the update.
        - source_geocoded_anncsu: a table that contains the geocoded_anncsu modified with new anncsu values.
        """
        scope_id: str = cls.get_current_scope_id()
        scopes: Dict[str, ScopeData] = cls.get_scopes()

        if not scope_id or (scope_id not in scopes):
            raise Exception("No current session to update.")

        scope: ScopeData = scopes[scope_id]

        # check if the current session is synched with remote git repo and
        # if duckdb_path is changed, if so warn user
        if not scope.syncked:
            reply = QMessageBox.question(
                iface.mainWindow(),
                QCoreApplication.translate("ANNCSUSettingsManager", "Continue update?"),
                QCoreApplication.translate("ANNCSUSettingsManager", "The current session is not synchronized with the remote git repository.\nIf you update the session data, you may lose unsynchronized changes."),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False

        # merge updated values with current anncsu table and update current duckdb file
        with duckdb.connect(database=str(scope.duckdb_path)) as conn:
            conn.execute("INSTALL spatial;")
            conn.execute("LOAD spatial;")

            # check if geocoded_anncsu table exists that is generated when updateing
            # from merging
            exists = conn.execute(f"SELECT * FROM information_schema.tables WHERE table_name = 'geocoded_anncsu';").df()
            if len(exists) == 0:
                QgsMessageLog.logMessage(cls.tr("Table 'geocoded_anncsu' not found in duckdb at {duckdb_path}. Cannot update session.").format(duckdb_path=scope.duckdb_path), level=Qgis.Warning)
                QMessageBox.warning(
                    iface.mainWindow(),
                    QCoreApplication.translate("ANNCSUSettingsManager", "Update not possible"),
                    QCoreApplication.translate("ANNCSUSettingsManager", "The 'geocoded_anncsu' table was not found in the session database.\nMake sure you have performed the update from Mergin.")
                )
                return False

            # start transaction
            conn.execute("BEGIN;")
            try:
                # save previous anncsu table as backup in case of errors during update
                conn.execute("CREATE OR REPLACE TABLE anncsu_backup AS SELECT * FROM anncsu;")

                # change from new_anncsu to anncsu ans source of truth
                conn.execute("CREATE OR REPLACE TABLE anncsu AS SELECT * FROM new_anncsu;")

                # drop new_anncsu table that is not needed anymore
                # was used to download new anncsu data
                conn.execute("DROP TABLE IF EXISTS new_anncsu;")

                # then work on current geocoded_anncsu table that is the table where operators
                # work on settin new geocoding values, so we need to update only the values of
                # this table that are present in temp table
                # loop over all rows of temp table and update anncsu table with new values,
                # matching by PK (PROGRESSIVO_ACCESSO, PROGRESSIVO_NAZIONALE)
                # if a row in temp table is not present in anncsu table, insert it
                # anncsu table has this scema:
                # ┌───────┬─────────────────────────┬─────────┬─────────┬────────────┬─────────┐
                # │  cid  │          name           │  type   │ notnull │ dflt_value │   pk    │
                # │ int32 │         varchar         │ varchar │ boolean │  varchar   │ boolean │
                # ├───────┼─────────────────────────┼─────────┼─────────┼────────────┼─────────┤
                # │     0 │ PLUGIN_COMUNE           │ VARCHAR │ false   │ NULL       │ false   │
                # │     1 │ PLUGIN_PROVINCIA        │ VARCHAR │ false   │ NULL       │ false   │
                # │     2 │ PLUGIN_REGIONE          │ VARCHAR │ false   │ NULL       │ false   │
                # │     3 │ CODICE_COMUNE           │ VARCHAR │ false   │ NULL       │ false   │
                # │     4 │ CODICE_ISTAT            │ VARCHAR │ false   │ NULL       │ false   │
                # │     5 │ PROGRESSIVO_NAZIONALE   │ BIGINT  │ false   │ NULL       │ false   │
                # │     6 │ CODICE_COMUNALE         │ VARCHAR │ false   │ NULL       │ false   │
                # │     7 │ ODONIMO                 │ VARCHAR │ false   │ NULL       │ false   │
                # │     8 │ LOCALITA'               │ VARCHAR │ false   │ NULL       │ false   │
                # │     9 │ DIZIONE_LINGUA1         │ VARCHAR │ false   │ NULL       │ false   │
                # │    10 │ DIZIONE_LINGUA2         │ VARCHAR │ false   │ NULL       │ false   │
                # │    11 │ PROGRESSIVO_ACCESSO     │ BIGINT  │ false   │ NULL       │ false   │
                # │    12 │ CODICE_COMUNALE_ACCESSO │ VARCHAR │ false   │ NULL       │ false   │
                # │    13 │ CIVICO                  │ BIGINT  │ false   │ NULL       │ false   │
                # │    14 │ ESPONENTE               │ VARCHAR │ false   │ NULL       │ false   │
                # │    15 │ SPECIFICITA             │ VARCHAR │ false   │ NULL       │ false   │
                # │    16 │ METRICO                 │ BIGINT  │ false   │ NULL       │ false   │
                # │    17 │ PROGRESSIVO_SNC         │ BIGINT  │ false   │ NULL       │ false   │
                # │    18 │ COORD_X_COMUNE          │ FLOAT   │ false   │ NULL       │ false   │
                # │    19 │ COORD_Y_COMUNE          │ FLOAT   │ false   │ NULL       │ false   │
                # │    20 │ QUOTA                   │ FLOAT   │ false   │ NULL       │ false   │
                # │    21 │ METODO                  │ BIGINT  │ false   │ NULL       │ false   │
                # ├───────┴─────────────────────────┴─────────┴─────────┴────────────┴─────────┤
                # │ 22 rows                                                          6 columns │
                #
                # added two new columns for local coordinates that are updated only if the source
                # db has coordinates,otherwise they maintain old values:
                # │    22 │ LOCAL_COORD_X_COMUNE    │ FLOAT   │ false   │ NULL       │ false   │
                # │    23 │ LOCAL_COORD_Y_COMUNE    │ FLOAT   │ false   │ NULL       │ false   │
                conn.execute("""
                    CREATE OR REPLACE TABLE updated_anncsu AS
                    SELECT
                        a.PLUGIN_COMUNE AS PLUGIN_COMUNE,
                        a.PLUGIN_PROVINCIA AS PLUGIN_PROVINCIA,
                        a.PLUGIN_REGIONE AS PLUGIN_REGIONE,
                        COALESCE(a.CODICE_COMUNE::VARCHAR, ga.CODICE_COMUNE::VARCHAR) AS CODICE_COMUNE,
                        COALESCE(a.CODICE_ISTAT::VARCHAR, ga.CODICE_ISTAT::VARCHAR) AS CODICE_ISTAT,
                        COALESCE(a.PROGRESSIVO_NAZIONALE::BIGINT, ga.PROGRESSIVO_NAZIONALE::BIGINT) AS PROGRESSIVO_NAZIONALE,
                        COALESCE(a.CODICE_COMUNALE::VARCHAR, ga.CODICE_COMUNALE::VARCHAR) AS CODICE_COMUNALE,
                        COALESCE(a.ODONIMO::VARCHAR, ga.ODONIMO::VARCHAR) AS ODONIMO,
                        COALESCE(a."LOCALITA'"::VARCHAR, ga."LOCALITA'"::VARCHAR) AS "LOCALITA'",
                        COALESCE(a.DIZIONE_LINGUA1::VARCHAR, ga.DIZIONE_LINGUA1::VARCHAR) AS DIZIONE_LINGUA1,
                        COALESCE(a.DIZIONE_LINGUA2::VARCHAR, ga.DIZIONE_LINGUA2::VARCHAR) AS DIZIONE_LINGUA2,
                        COALESCE(a.PROGRESSIVO_ACCESSO::BIGINT, ga.PROGRESSIVO_ACCESSO::BIGINT) AS PROGRESSIVO_ACCESSO,
                        COALESCE(a.CODICE_COMUNALE_ACCESSO::VARCHAR, ga.CODICE_COMUNALE_ACCESSO::VARCHAR) AS CODICE_COMUNALE_ACCESSO,
                        COALESCE(a.CIVICO::BIGINT, ga.CIVICO::BIGINT) AS CIVICO,
                        COALESCE(a.ESPONENTE::VARCHAR, ga.ESPONENTE::VARCHAR) AS ESPONENTE,
                        COALESCE(a.SPECIFICITA::VARCHAR, ga.SPECIFICITA::VARCHAR) AS SPECIFICITA,
                        COALESCE(a.METRICO::BIGINT, ga.METRICO::BIGINT) AS METRICO,
                        COALESCE(a.PROGRESSIVO_SNC::BIGINT, ga.PROGRESSIVO_SNC::BIGINT) AS PROGRESSIVO_SNC,
                        COALESCE(a.COORD_X_COMUNE::FLOAT, ga.COORD_X_COMUNE::FLOAT) AS COORD_X_COMUNE,
                        COALESCE(a.COORD_Y_COMUNE::FLOAT, ga.COORD_Y_COMUNE::FLOAT) AS COORD_Y_COMUNE,
                        COALESCE(ga.COORD_X_COMUNE::FLOAT, a.COORD_X_COMUNE::FLOAT) AS LOCAL_COORD_X_COMUNE,
                        COALESCE(ga.COORD_Y_COMUNE::FLOAT, a.COORD_Y_COMUNE::FLOAT) AS LOCAL_COORD_Y_COMUNE,
                        COALESCE(a.QUOTA::FLOAT, ga.QUOTA::FLOAT) AS QUOTA,
                        COALESCE(a.METODO::BIGINT, ga.METODO::BIGINT) AS METODO,
                        NULL::GEOMETRY AS geom
                    FROM geocoded_anncsu ga
                    FULL OUTER JOIN anncsu a
                        ON (ga.PROGRESSIVO_ACCESSO::BIGINT = a.PROGRESSIVO_ACCESSO::BIGINT);
                """)

                # collect all records where the anncsu coordinates are different from
                # the local table coordinates to warn user that some coordinates have been updated
                # where "different" mean anncsu coord differe of a maximum threshold of
                # 0.00001 degrees (approximately 1 meter) from local coords, to avoid warning user for
                # small differences that can be due to rounding or different geocoding
                threshold = cls.get_default_coordinate_distance_threshold()
                out_of_threshold = conn.execute("""
                    SELECT
                        PROGRESSIVO_NAZIONALE,
                        PROGRESSIVO_ACCESSO,
                        COORD_X_COMUNE AS ANNCSU_COORD_X,
                        COORD_Y_COMUNE AS ANNCSU_COORD_Y,
                        LOCAL_COORD_X_COMUNE,
                        LOCAL_COORD_Y_COMUNE
                    FROM updated_anncsu
                    WHERE
                        (COORD_X_COMUNE IS NOT NULL AND
                         LOCAL_COORD_X_COMUNE IS NOT NULL AND
                         ABS(COORD_X_COMUNE::FLOAT - LOCAL_COORD_X_COMUNE::FLOAT) > $1)
                        OR
                        (COORD_Y_COMUNE IS NOT NULL AND
                         LOCAL_COORD_Y_COMUNE IS NOT NULL AND
                         ABS(COORD_Y_COMUNE::FLOAT - LOCAL_COORD_Y_COMUNE::FLOAT) > $1)
                """, (threshold,)).df()

                # if there are records with coordinates different from local table,
                # warn user with a message box and detail of the records with different coordinates,
                # and ask if he want to proceed with update or not
                if len(out_of_threshold) > 0:

                    # create informative text to be displayed to the user
                    details = "\n".join([
                        f"Address {row['PROGRESSIVO_ACCESSO']} (PROGRESSIVO_NAZIONALE: {row['PROGRESSIVO_NAZIONALE']}): "
                        f"ANNCSU({row['ANNCSU_COORD_X']}, {row['ANNCSU_COORD_Y']}) -> "
                        f"Local({row['LOCAL_COORD_X_COMUNE']}, {row['LOCAL_COORD_Y_COMUNE']})"
                        for row in out_of_threshold.to_dict(orient="records")
                    ])
                    message = QCoreApplication.translate("ANNCSUSettingsManager", "Some addresses have updated coordinates compared to the local table.\nDo you want to proceed with updating the session data?\nDetails show addresses with updated coordinates.\n(Difference threshold: {threshold} degrees, approx. {meters:.2f} meters)").format(threshold=threshold, meters=threshold * 111000)
                    messsageBox = QMessageBox()
                    messsageBox.setIcon(QMessageBox.Warning)
                    messsageBox.setWindowTitle(QCoreApplication.translate("ANNCSUSettingsManager", "Update address coordinates?"))
                    messsageBox.setText(message)
                    messsageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    messsageBox.setDefaultButton(QMessageBox.Yes)
                    messsageBox.setDetailedText(details)
                    # resize basing on content because lit of details can be larger than default message box size
                    horizontalSpacer = QSpacerItem(1000, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
                    layout = messsageBox.layout()
                    layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())
                    # ask to the user if he want to proceed with update or not
                    reply = messsageBox.exec_()
                    if reply == QMessageBox.No:
                        conn.execute("ROLLBACK;")
                        return False

                # dropping local coordinates columns from updated_anncsu table
                # and keeping only anncsu coordinates to avoid confusion
                conn.execute("""
                    ALTER TABLE updated_anncsu
                    DROP COLUMN LOCAL_COORD_X_COMUNE;
                """)
                conn.execute("""
                    ALTER TABLE updated_anncsu
                    DROP COLUMN LOCAL_COORD_Y_COMUNE;
                """)


                # now update geom creating geometry point from official COORD_X_COMUNE and COORD_Y_COMUNE columns
                conn.execute("""
                    UPDATE
                        updated_anncsu
                    SET
                        geom = ST_Point(COORD_X_COMUNE, COORD_Y_COMUNE)
                    WHERE
                        COORD_X_COMUNE IS NOT NULL AND
                        COORD_Y_COMUNE IS NOT NULL;
                """)

                # save involved tables to trace modifications
                conn.execute("""
                    CREATE OR REPLACE TABLE previous_geocoded_anncsu AS
                    SELECT * FROM geocoded_anncsu;
                """)
                conn.execute("""
                    CREATE OR REPLACE TABLE source_updated_anncsu AS
                    SELECT * FROM updated_anncsu;
                """)

                # replace old anncsu table with updated_anncsu table
                conn.execute("DROP TABLE IF EXISTS geocoded_anncsu;")
                conn.execute("ALTER TABLE updated_anncsu RENAME TO geocoded_anncsu;")

            except Exception as e:
                conn.execute("ROLLBACK;")
                QgsMessageLog.logMessage(cls.tr("Error updating session with new anncsu data: {e}").format(e=e), level=Qgis.Critical)
                raise Exception(f"Error updating session with new anncsu data: {e}")
            
            else:
                conn.execute("COMMIT;")
                # update session data in SCOPES syncked status to false because
                # now the session is not syncked with remote git repo because of the new anncsu data
                scope.syncked = False
                scope.sync_changed.emit()
                scopes[scope_id] = scope
                ANNCSUSettingsManager.set_scopes(scopes)

            return True


    class populate_table_from_source_task(QgsTask):

        def __init__(self, 
                duckdb_path: Path,
                source_db: AnyUrl,
                table_name: str,
                municipality_data: MunicipalityData,
            ) -> None:
            super().__init__(f"Downloading updated ANNCSU for municipality {municipality_data.anncsu_id}", QgsTask.CanCancel)
            self.duckdb_path = duckdb_path
            self.source_db = source_db
            self.table_name = table_name
            self.municipality_data = municipality_data

            # task status
            self.exception = None
            self.result = None

        def run(self) -> bool:
            try:
                self.result = ANNCSUSettingsManager.populate_table_from_source(
                    duckdb_path=self.duckdb_path,
                    source_db=self.source_db,
                    table_name=self.table_name,
                    municipality_data=self.municipality_data
                )
            except Exception as e:
                self.exception = e
                QgsMessageLog.logMessage(self.tr("Error in populate_table_from_source_task: {e}").format(e=e), level=Qgis.Critical)
                self.result = False
            
            return self.result

        def finished(self, result: bool):
            if result:
                QgsMessageLog.logMessage(self.tr("Table {table_name} successfully populated from {source_db}").format(table_name=self.table_name, source_db=self.source_db), level=Qgis.Info)
            else:
                QgsMessageLog.logMessage(self.tr("Error populating table {table_name} from {source_db}").format(table_name=self.table_name, source_db=self.source_db), level=Qgis.Critical)

            return super().finished(result)


    @classmethod
    def populate_table_from_source(
        cls,
        duckdb_path: Path,
        source_db: AnyUrl,
        table_name: str,
        municipality_data: MunicipalityData,
    ) -> bool:
        """Populate anncsu table in duckdb from source database.

        This method handles two types of sources:
        1. Remote ZIP files from agenziaentrate.gov.it containing CSV data
        2. Local or remote DuckDB files with anncsu_global table

        Args:
            duckdb_path: Path to the DuckDB database where table will be created
            source_db: Source URL (ZIP file or DuckDB file)
            table_name: Name of the table to create in duckdb (e.g. "anncsu")
            municipality_data: Municipality data for filtering and enrichment

        Raises:
            Exception: If download fails or source_db format is invalid
        """
        with duckdb.connect(database=str(duckdb_path), read_only=False) as duckdb_conn:
            # load spatial extension
            duckdb_conn.execute("INSTALL spatial;")
            duckdb_conn.execute("LOAD spatial;")

            duckdb_conn.execute("BEGIN;")
            try:
                # depending if source_db is remote or local file path
                if 'agenziaentrate.gov.it' in str(source_db):
                    QgsMessageLog.logMessage(cls.tr("Connect remote DB: {source_db}").format(source_db=source_db), level=Qgis.Info)

                    # load extension to parse zip content
                    duckdb_conn.execute("INSTALL zipfs FROM community;")
                    duckdb_conn.execute("LOAD zipfs;")

                    # download source db because it is not possible to attach remote duckdb
                    # Get filename from Content-Disposition header or use fallback
                    response_head = requests.head(str(source_db))
                    fallout_temp_filename = f"fallout_anncsu.zip"
                    remote_filename = fallout_temp_filename
                    if response_head.status_code == 200 and response_head.headers.get('Content-Disposition'):
                        remote_filename = response_head.headers.get('Content-Disposition').split('filename=')[-1].strip('"')

                    temp_duckdb_path = cls.PLUGIN_PATH / "resources" / "data" / remote_filename

                    # Download file asynchronously with progress tracking in QGIS task manager
                    # download_task = download_file_async(str(source_db), temp_duckdb_path)
                    download_task = DownloadFileTask(str(source_db), temp_duckdb_path, f"Downloading {str(source_db)}")

                    # run dwonload
                    QgsApplication.taskManager().addTask(download_task)
                    while download_task.status() != QgsTask.Running:
                        QgsApplication.processEvents()
                    while download_task.status() == QgsTask.Running:
                        QgsApplication.processEvents()

                    # check if task has been terminated due to error or cancellation
                    if download_task.status() == QgsTask.Terminated:
                        error_msg = str(download_task.exception) if download_task.exception else "Download was cancelled or timed out"
                        ANNCSUMessageManager().show_message(
                            cls.tr("Failed to download source database: {error_msg}").format(error_msg=error_msg),
                            "error",
                        )
                        return False

                    # Wait for download to complete (shows progress in task manager, allows cancellation)
                    # if not download_task.waitForFinished():
                    #     error_msg = str(download_task.exception) if download_task.exception else "Download was cancelled or timed out"
                    #     raise Exception(f"Failed to download source database: {error_msg}")

                    # create local duckdb with only data for selected municipality_code
                    force_column_types = "{'CODICE_COMUNALE_ACCESSO': 'VARCHAR', 'QUOTA': 'FLOAT', 'COORD_X_COMUNE': 'FLOAT', 'COORD_Y_COMUNE': 'FLOAT'}"
                    duckdb_conn.execute(f"""
                        CREATE OR REPLACE TABLE {table_name} AS
                        SELECT
                            $tag$'{municipality_data.nome}'$tag$ as PLUGIN_COMUNE,
                            $tag$'{municipality_data.provincia}'$tag$ as PLUGIN_PROVINCIA,
                            $tag$'{municipality_data.regione}'$tag$ as PLUGIN_REGIONE,
                            *
                        FROM
                            READ_CSV_AUTO(
                                'zip://{str(temp_duckdb_path)}',
                                header = true,
                                delim=';',
                                thousands='.',
                                decimal_separator=',',
                                types={force_column_types}
                            )
                        WHERE codice_comune = '{municipality_data.anncsu_id}';
                    """)

                    # remove temporary downloaded duckdb
                    os.remove(temp_duckdb_path)

                else:
                    QgsMessageLog.logMessage(cls.tr("Connect local DB: {source_db}").format(source_db=source_db), level=Qgis.Info)

                    if not str(source_db).endswith(".duckdb"):
                        raise Exception(f"Source duckdb URL '{source_db}' is not a valid duckdb file (should end with .duckdb).")

                    # query from a remote duckdb
                    duckdb_conn.execute(f"ATTACH DATABASE '{str(source_db)}' AS indirizzarioItalia;")
                    duckdb_conn.execute(f"""
                        CREATE OR REPLACE TABLE {table_name} AS
                        SELECT
                            $tag$'{municipality_data.nome}'$tag$ as PLUGIN_COMUNE,
                            $tag$'{municipality_data.provincia}'$tag$ as PLUGIN_PROVINCIA,
                            $tag$'{municipality_data.regione}'$tag$ as PLUGIN_REGIONE,
                            *
                        FROM
                            indirizzarioItalia.anncsu_global
                        WHERE
                            CODICE_COMUNE == '{municipality_data.anncsu_id}';
                    """)
                    duckdb_conn.execute("DETACH DATABASE indirizzarioItalia;")

            except Exception as e:
                duckdb_conn.execute("ROLLBACK;")
                QgsMessageLog.logMessage(cls.tr("Error populating {table_name} table from source database: {e}").format(table_name=table_name, e=e), level=Qgis.Critical)
                raise e
            else:
                QgsMessageLog.logMessage(cls.tr("Populated {table_name} table from source database: {source_db}").format(table_name=table_name, source_db=source_db), level=Qgis.Info)
                duckdb_conn.execute("COMMIT;")
                return True


    @classmethod
    def create_new_session(
        cls,
        source_db: AnyUrl,
        municipality_data: MunicipalityData,
        feedback: ANNCSUProcessingFeedback,
    ) -> Tuple[Optional[str], Optional[ScopeData]]:
        """Create a new session and add it to SCOPES.

        Args:
            source_db (Optional[AnyUrl]): Source URL from where the duckdb has been extracted.
            municipality_data (MunicipalityData): Municipality data associated with this scope.
        Returns:
            scope: ScopeData"""
        QgsMessageLog.logMessage(cls.tr("Creating new session for municipality {anncsu_id} from source db {source_db}...").format(anncsu_id=municipality_data.anncsu_id, source_db=source_db), level=Qgis.Info)
        print(f"Creating new session for municipality {municipality_data.anncsu_id} from source db {str(source_db)}...")

        # create remote repo url where to save session make it's name a correct url
        remote_git_repo = str.lower(cls.get_default_session_repo_url().format(**municipality_data.to_dict()))
        repo_name = os.path.basename(remote_git_repo).replace(".git", "")
        local_path =cls.PLUGIN_PATH / "resources" / "data" / repo_name
        print(f"Using remote git repo URL: {remote_git_repo}")

        # check correctness of the url
        try:
            AnyUrl(remote_git_repo)
        except Exception as e:
            QgsMessageLog.logMessage(cls.tr("Invalid remote HTTP(S) git repo URL: {remote_git_repo} check if SSH. error: {e}").format(remote_git_repo=remote_git_repo, e=e), level=Qgis.Critical)
            parsed = urllib.parse.urlparse(remote_git_repo)
            if parsed.path == remote_git_repo and (parsed.scheme == "" or parsed.scheme is None):
                # possibly a git ssh url
                if "@" in remote_git_repo and ":" in remote_git_repo:
                    print(f"Assuming remote git repo is SSH URL: {remote_git_repo}")
                else:
                    QgsMessageLog.logMessage(cls.tr("Invalid remote git repo URL: {remote_git_repo}").format(remote_git_repo=remote_git_repo), level=Qgis.Critical)
                    return None, None
            else:
                return None, None

        # create unique duckdb path for the scope
        now = datetime.now()
        scope_name = f"{municipality_data.anncsu_id}_{now.strftime('%Y%m%d_%H%M%S')}"
        duckdb_path = local_path / f"{scope_name}.duckdb"

        # clone or pull remote git repository locally in separate thread becasuse
        # can takes time and not block the UI
        clone_repo_task = clone_or_pull_git_repo_task(
            remote_git_repo=remote_git_repo,
            local_path=local_path,
            git_user=cls.get_git_user(),
            git_password=cls.get_git_password(),
            git_token=cls.get_git_token(),
            ssh_key=cls.get_git_ssh_key()
        )
        QgsApplication.taskManager().addTask(clone_repo_task)
        while clone_repo_task.status() != QgsTask.Running:
            QgsApplication.processEvents()
        while clone_repo_task.status() == QgsTask.Running:
            QgsApplication.processEvents()

        if clone_repo_task.repo is None:
            return None, None

        QgsMessageLog.logMessage(cls.tr("Successfully cloned/pulled {remote_git_repo} into {local_path}").format(remote_git_repo=remote_git_repo, local_path=local_path), level=Qgis.Info)
        del clone_repo_task  # no more need to keep reference

        # update ANNCSU table in current session with source_db data, this operation can be time
        update_anncsu_task = ANNCSUSettingsManager.populate_table_from_source_task(
            duckdb_path=duckdb_path,
            source_db=source_db,
            table_name="anncsu",
            municipality_data=municipality_data
        )

        # run update current session time consuming task
        QgsApplication.taskManager().addTask(update_anncsu_task)
        while update_anncsu_task.status() != QgsTask.Running:
            QgsApplication.processEvents()
        while update_anncsu_task.status() == QgsTask.Running:
            QgsApplication.processEvents()

        # check if task has been terminated due to error or cancellation
        if update_anncsu_task.status() == QgsTask.Terminated:
            ANNCSUMessageManager().show_message(
                cls.tr("Error creating new session: {exception}").format(exception=str(update_anncsu_task.exception)),
                "error",
            )
            return None, None

        # populate scope session with subset of municipality data get from source_db
        # QgsMessageLog.logMessage(f"Creating local duckdb at {duckdb_path}...", level=Qgis.Info)
        with duckdb.connect(database=str(duckdb_path), read_only=False) as duckdb_conn:
            # load spatial extension
            duckdb_conn.execute("INSTALL spatial;")
            duckdb_conn.execute("LOAD spatial;")

            # now create geofence polygon table related to the current scope municipality
            # note that geofence source is in 32632 and anncsu data is in wgs84 and
            # x,y coorinates are inverted
            # feedback.setProgress(97)
            # QgsMessageLog.logMessage(f"Get geofence polygon for municipality '{municipality_data.nome}'...", level=Qgis.Info)
            # feedback.pushInfo(f"Get geofence polygon for municipality '{municipality_data.nome}'...")
            duckdb_conn.execute(f"""
                CREATE OR REPLACE TABLE geofence_polygon AS (
                    SELECT
                        ST_Transform(
                            geometry,
                            'EPSG:32632',
                            'EPSG:4326',
                            always_xy := true
                        ) as geom
                    FROM
                        read_parquet('{ANNCSUSettingsManager.get_geofence_polygons_source()}')
                    WHERE
                        COMUNE == '{municipality_data.nome}'
                );
            """)
            # QgsMessageLog.logMessage(f"Geofence polygon for municipality '{municipality_data.nome}' loaded into table 'geofence_polygon'.", level=Qgis.Info)
            # feedback.pushInfo(f"Geofence polygon for municipality '{municipality_data.nome}' loaded into table 'geofence_polygon'.")
        # feedback.setProgress(100)

        # generate and return scope data
        scope = ScopeData(
            duckdb_path=duckdb_path,
            remote_git_repo=remote_git_repo,
            syncked=True,
            municipality_data=municipality_data,
            source_db=source_db,
            creation_date=now,
            update_date=None,
            description=f"ANNCSU Data for municipality {municipality_data.anncsu_id} created on {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        scopes = cls.get_scopes()
        scopes[scope_name] = scope
        cls.set_scopes(scopes)
        cls.set_current_scope_id(scope_name)
        return scope_name, scope
