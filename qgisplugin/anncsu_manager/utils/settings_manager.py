import json
import os
import requests
import shutil
from git import Repo
from typing import Optional, Dict, Tuple
from pathlib import Path
from pydantic.dataclasses import dataclass
from pydantic import AnyUrl
from typing_extensions import Annotated
from datetime import datetime

import duckdb

from qgis.core import (
    QgsSettings,
    QgsMessageLog,
    Qgis
)

from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

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
    duckdb_path: Annotated[Path, "Path to local duckdb file"]
    remote_git_repo: Annotated[Optional[AnyUrl], "URL to remote git repo where store session"]
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


class ANNCSUSettingsManager:
    """
    A centralized interface for accessing and modifying settings of ANNCSU QGIS Plugin.
    
    A static class that does not need instantiation, i.e. it should be used like this: \n
    `env_selection = ANNCSUSettingsManager.get_environment_selection()`
    
    Settings are saved to QGIS project. This is the reason to no use pydantinc to manage
    settings because have to saved in QGIS.ini settings.
    """
    PLUGIN_PATH = Path(os.path.dirname(os.path.dirname(__file__)))

    DEFAULT_SESSION_REPO_URL = "https://github.com/luipir/ANNCSU_{nome}_{anncsu_id}.git"  # format with MunicipalityName and Anncsu code
    DEFAULT_GEOFENCE_POLYGONS_SOURCE = 'https://github.com/geobeyond/anncsu-data/raw/refs/heads/main/com01012025_wgs84.parquet'
    DEFAULT_GEOCODERS_JSON_PATH = PLUGIN_PATH / "resources" / "data" / "geocoders.json"
    # DEFAULT_ANNCSU_REPO_URL = "https://anncsu.open.agenziaentrate.gov.it/age-inspire/opendata/anncsu/getds.php?INDIR_ITA"
    DEFAULT_ANNCSU_REPO_URL = "https://github.com/geobeyond/anncsu-data/raw/refs/heads/main/indirizzarioItalia.duckdb"
    DEFAULT_MUNICIPALITY = "NoName"
    DEFAULT_MUNICIPALITY_CODE = "0000000"
    DEFAULT_GEOCODERS_CONFIGS = {
            "Nominatim": {
                "active": "True",
                "addressdetails": "True",
                "bounded": "False",
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
                "active": "True",
                "api_key": "",
                "boundary.circle.lat": "",
                "boundary.circle.lon": "",
                "boundary.circle.radius": "",
                "boundary.country": "",
                "boundary.rect.max_lat": "",
                "boundary.rect.max_lon": "",
                "boundary.rect.min_lat": "",
                "boundary.rect.min_lon": "",
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
                "active": "True",
                "dedupe": "True",
                "lang": "en",
                "limit": 10,
                "max_results": 5,
                "min_score": 0,
                "url": "https://photon.komoot.io/api/"
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
    SCOPES = {}

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

    DEFAULTS = {
        DEFAULT_SESSION_REPO_URL_KEY: DEFAULT_SESSION_REPO_URL,
        GEOFENCE_POLYGONS_SOURCE_KEY: DEFAULT_GEOFENCE_POLYGONS_SOURCE,
        GEOCODERS_JSON_PATH_KEY: str(DEFAULT_GEOCODERS_JSON_PATH),
        ANNCSU_REPO_URL_KEY: DEFAULT_ANNCSU_REPO_URL,
        MUNICIPALITY_KEY: DEFAULT_MUNICIPALITY,
        MUNICIPALITY_CODE_KEY: DEFAULT_MUNICIPALITY_CODE,
        GEOCODERS_CONFIGS_KEY: DEFAULT_GEOCODERS_CONFIGS,
        SCOPES_KEY: SCOPES,
        # A scope id has the following format: "<codice_municipio>_YYYYMMDD_HHMMSS"
        SCOPE_ID_KEY: "",
    }

    # GETTERS
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
                f"Failed to load default geocoder configs. Reset to default values. {e}",
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
        key = cls.SCOPES_KEY
        # Deserialize
        try:
            serialised = QgsSettings().value(key, cls.DEFAULTS[key])
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
            return scopes
        
        # If error, reset
        except (TypeError, json.JSONDecodeError) as e:
            ANNCSUMessageManager().show_message(
                f"Failed to load default scopes. Reset to default values. {e}",
                "error"
            )
            cls.reset_scopes()
            scopes = cls.get_scopes()

        return scopes

    # SETTERS
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
                f"Could not find geocoders.json at {path}. Reverting to default path.",
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
    def create_new_session(
        cls,
        task,
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
        QgsMessageLog.logMessage(f"Creating new session for municipality {municipality_data.anncsu_id} from source db {source_db}...", level=Qgis.Info)
        print(f"Creating new session for municipality {municipality_data.anncsu_id} from source db {str(source_db)}...")

        # create remote repo url where to save session make it's name a correct url
        remote_repo_url = cls.get_default_session_repo_url().format(**municipality_data.to_dict())
        remote_repo_url = remote_repo_url.replace(" ", "_").replace("-", "_")
        repo_name = os.path.basename(remote_repo_url).replace(".git", "")
        local_path =cls.PLUGIN_PATH / "resources" / "data" / repo_name

        # create unique duckdb path for the scope
        now = datetime.now()
        scope_name = f"{municipality_data.anncsu_id}_{now.strftime('%Y%m%d_%H%M%S')}"
        duckdb_path = local_path / f"{scope_name}.duckdb"

        # clone remote_repo_url locally
        try:
            if local_path.exists():
                # QgsMessageLog.logMessage(f"Local repository {local_path} already exists. Pulling latest changes...", level=Qgis.Info)
                repo = Repo(local_path)
                origin = repo.remotes.origin
                # NOTE: repo need to have at least 1 file otherwise git pull do not fetch any ref
                # and trigger error
                origin.pull()
            else:
                repo = Repo.clone_from(remote_repo_url, local_path)
        except Exception as e:
            # QgsMessageLog.logMessage(f"Error cloning git repository from {remote_repo_url}: {e}", level=Qgis.Critical)
            print(f"Error cloning git repository from {remote_repo_url}: {e}")
            return None, None
        QgsMessageLog.logMessage(f"Successfully cloned/pulled {remote_repo_url} into {local_path}", level=Qgis.Info)

        # populate scope session with subset of municipality data get from source_db
        # QgsMessageLog.logMessage(f"Creating local duckdb at {duckdb_path}...", level=Qgis.Info)
        duckdb_conn = duckdb.connect(database=duckdb_path, read_only=False)
        if duckdb_conn is None:
            raise Exception("Could not create local duckdb database.")

        # load spatial extension
        duckdb_conn.execute("INSTALL spatial;")
        duckdb_conn.execute("LOAD spatial;")

        # depending if source_db is remote or local file path
        # feedback.setProgress(10)
        if 'agenziaentrate.gov.it' in str(source_db):
            # load extension to parse zip content
            duckdb_conn.execute("INSTALL zipfs FROM community;")
            duckdb_conn.execute("LOAD zipfs;")

            # download file locally because do not support range requests
            # during download notify progress
            response = requests.get(str(source_db), stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download source duckdb from {source_db}. Status code: {response.status_code}")
            

            # download sourc db because it is not possible to attach remote duckdb
            follout_temp_filename = f"temp_{scope_name}.zip"
            remote_filename = response.headers.get('Content-Disposition').split('filename=')[-1] if response.headers.get('Content-Disposition') else follout_temp_filename
            temp_duckdb_path = cls.PLUGIN_PATH / "resources" / "data" / remote_filename.strip('"')

            # get amout of data to download
            chunk_size = 8192
            total_size = int(response.headers.get('content-length', 0))
            number_of_chunks = total_size // chunk_size
            if number_of_chunks == 0:
                number_of_chunks = 100  # avoid division by zero and reset progress bar to 100 steps
            downloaded_size = 0

            chunk_number = 0
            # feedback.setProgress(chunk_number)
            QgsMessageLog.logMessage(f"Downloading source duckdb from {source_db} to {temp_duckdb_path}...", level=Qgis.Info)
            print(f"Downloading source duckdb from {source_db} to {temp_duckdb_path}...")
            with open(temp_duckdb_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded_size += len(chunk)
                    progress = int(90 * (chunk_number / number_of_chunks))
                    # feedback.setProgress(progress)
                    file.write(chunk)
                    chunk_number += 1

            # duckdb_conn.execute(f"SELEC * '{str(temp_duckdb_path)}' AS source_db;")
            # create local duckdb with only data for selected municipality_code
            # feedback.setProgress(95)
            force_column_types = "{'CODICE_COMUNALE_ACCESSO': 'VARCHAR', 'QUOTA': 'VARCHAR'}"
            duckdb_conn.execute(f"""
                CREATE TABLE anncsu AS
                SELECT
                    $tag$'{municipality_data.nome}'$tag$ as COMUNE,
                    $tag$'{municipality_data.provincia}'$tag$ as PROVINCIA,
                    $tag$'{municipality_data.regione}'$tag$ as REGIONE,
                    *
                FROM
                    READ_CSV_AUTO(
                        'zip://{str(temp_duckdb_path)}',
                        header = true,
                        delim=';',
                        types={force_column_types}
                    )
                WHERE codice_comune = '{municipality_data.anncsu_id}';
            """)

            # remove temporary downloaded duckdb
            os.remove(temp_duckdb_path)

        else:
            if not str(source_db).endswith(".duckdb"):
                raise Exception(f"Source duckdb URL '{source_db}' is not a valid duckdb file (shoudl end with .duckdb).")

            # QgsMessageLog.logMessage(f"Source duckdb is local at {source_db}...", level=Qgis.Info)
            # feedback.pushInfo(f"Source duckdb is remote at {source_db}...")

            # query from a remote duckdb
            duckdb_conn.execute(f"ATTACH DATABASE '{str(source_db)}' AS indirizzarioItalia;")
            duckdb_conn.execute(f"""
                CREATE TABLE anncsu AS
                SELECT
                    $tag$'{municipality_data.nome}'$tag$ as COMUNE,
                    $tag$'{municipality_data.provincia}'$tag$ as PROVINCIA,
                    $tag$'{municipality_data.regione}'$tag$ as REGIONE,
                    *
                FROM
                    indirizzarioItalia.anncsu_global
                WHERE
                    CODICE_COMUNE == '{municipality_data.anncsu_id}';
            """)
            duckdb_conn.execute("DETACH DATABASE indirizzarioItalia;")

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
                    ) as geometry
                FROM
                    read_parquet('{ANNCSUSettingsManager.get_geofence_polygons_source()}')
                WHERE
                    COMUNE == '{municipality_data.nome}'
            );
        """)
        # QgsMessageLog.logMessage(f"Geofence polygon for municipality '{municipality_data.nome}' loaded into table 'geofence_polygon'.", level=Qgis.Info)
        # feedback.pushInfo(f"Geofence polygon for municipality '{municipality_data.nome}' loaded into table 'geofence_polygon'.")

        # all done => close connection
        duckdb_conn.close()
        # feedback.setProgress(100)

        # generate and return scope data
        scope = ScopeData(
            duckdb_path=duckdb_path,
            remote_git_repo=AnyUrl(remote_repo_url),
            syncked=False,
            municipality_data=municipality_data,
            source_db=source_db,
            creation_date=now,
            update_date=None,
            description=f"ANNCSU Data for municipality {municipality_data.anncsu_id} created on {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        scopes = cls.get_scopes()
        scopes[scope_name] = scope
        cls.set_scopes(scopes)
        return scope_name, scope