import json
import os
import requests
from typing import Optional, Dict, Tuple
from pathlib import Path
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, FilePath, ValidationError
from pydantic.types import PathType
from pydantic import AnyUrl
from typing_extensions import Annotated
from datetime import datetime

import duckdb

from qgis.core import (
    # QgsProject,
    # QgsRasterLayer,
    QgsSettings,
)
# from qgis.PyQt.QtCore import pyqtSignal, QObject

from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

@dataclass
class ScopeData:
    duckdb_path: Annotated[Path, "Path to local duckdb file"]
    remote_duckdb_url: Annotated[Optional[AnyUrl], "URL to remote duckdb file"]
    syncked: Annotated[bool, "Whether the local duckdb is syncked with remote"]
    municipality_code: Annotated[str, "Municipality code associated with this scope"]
    source_db: Annotated[Optional[AnyUrl], "Source URL from where the duckdb has been extracted"]
    creation_date: datetime
    update_date: Optional[datetime]
    description: Optional[str]

    def to_dict(self):
        return {
            "duckdb_path": str(self.duckdb_path),
            "remote_duckdb_url": str(self.remote_duckdb_url) if self.remote_duckdb_url else None,
            "syncked": self.syncked,
            "municipality_code": self.municipality_code,
            "source_db": str(self.source_db) if self.source_db else None,
            "creation_date": self.creation_date.isoformat(),
            "update_date": self.update_date.isoformat() if self.update_date else None,
            "description": self.description,
        }
    
    def toJson(self) -> str:
        return json.dumps(self.to_dict())


# class SessionData(QObject):
#     """Container class to manage session changes using pyqt framework
#     """
#     modified = pyqtSignal()
#     scope_id: Annotated[str, "Current active scope id"]
#     scope: Optional[Annotated[ScopeData, "Current active scope data"]]

#     def __init__(self, scope_id: str, scope: Optional[ScopeData]):
#         super().__init__()
#         self.scope_id = scope_id
#         self.scope = scope

#     def to_dict(self):
#         return {
#             "scope_id": self.scope_id,
#             "scope": self.scope.to_dict() if self.scope else None,
#         }

#     def toJson(self) -> str:
#         return json.dumps(self.to_dict())


class ANNCSUSettingsManager:
    """
    A centralized interface for accessing and modifying settings of ANNCSU QGIS Plugin.
    
    A static class that does not need instantiation, i.e. it should be used like this: \n
    `env_selection = ANNCSUSettingsManager.get_environment_selection()`
    
    Settings are saved to QGIS project. This is the reason to no use pydantinc to manage
    settings because have to saved in QGIS.ini settings.
    """
    PLUGIN_PATH = Path(os.path.dirname(os.path.dirname(__file__)))

    DEFAULT_GEOCODERS_JSON_PATH = PLUGIN_PATH / "resources" / "data" / "geocoders.json"
    DEFAULT_ANNCSU_REPO_URL = "https://anncsu.open.agenziaentrate.gov.it/age-inspire/opendata/anncsu/getds.php?INDIR_ITA"
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
    #         "remote_duckdb_url": "https://geodata.civictech.it/anncsu/OOOOOO_20251008.duckdb",
    #         "municipality_code": "0000000",
    #         "creation_date": "2025-10-08",
    #         "update_date": "2025-10-08",
    #         "description": "Italy - National (2025-10-08)",
    #     }
    # }
    SCOPES = {}

    SCOPES_KEY = "anncsu_manager/geocoders_json_path"
    GEOCODERS_JSON_PATH_KEY = "anncsu_manager/geocoders_json_path"
    ANNCSU_REPO_URL_KEY = "anncsu_manager/anncsu_repo_url"
    MUNICIPALITY_CODE_KEY = "anncsu_manager/default_municipality_code"
    GEOCODERS_CONFIGS_KEY = "anncsu_manager/geocoders_configs" # unused in QGIS.ini because saved in geocoders.json
    SCOPES_KEY = "anncsu_manager/scopes"
    SCOPE_ID_KEY = "anncsu_manager/current_scope_id"

    DEFAULTS = {
        GEOCODERS_JSON_PATH_KEY: str(DEFAULT_GEOCODERS_JSON_PATH),
        ANNCSU_REPO_URL_KEY: DEFAULT_ANNCSU_REPO_URL,
        MUNICIPALITY_CODE_KEY: DEFAULT_MUNICIPALITY_CODE,
        GEOCODERS_CONFIGS_KEY: DEFAULT_GEOCODERS_CONFIGS,
        SCOPES_KEY: SCOPES,
        # A scope id has the following format: "<codice_municipio>_YYYYMMDD_HHMMSS"
        SCOPE_ID_KEY: "",
    }

    # GETTERS
    @classmethod
    def get_geocoders_json_path(cls) -> str:
        key = cls.GEOCODERS_JSON_PATH_KEY
        return QgsSettings().value(key, str(cls.DEFAULTS[key]))

    @classmethod
    def get_anncsu_repo(cls) -> str:
        key = cls.ANNCSU_REPO_URL_KEY
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
                # parse dates
                creation_date = datetime.fromisoformat(scope_data["creation_date"])
                update_date = datetime.fromisoformat(scope_data["update_date"]) if scope_data["update_date"] else None
                scopes[scope_id] = ScopeData(
                    duckdb_path=Path(scope_data["duckdb_path"]),
                    remote_duckdb_url=scope_data["remote_duckdb_url"],
                    syncked=scope_data["syncked"],
                    municipality_code=scope_data["municipality_code"],
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
    def reset_anncsu_repo(cls):
        QgsSettings().setValue(cls.ANNCSU_REPO_URL_KEY, cls.DEFAULTS[cls.ANNCSU_REPO_URL_KEY])

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
        cls.reset_anncsu_repo()
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
                os.remove(scope.duckdb_path)
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
        source_db: AnyUrl,
        municipality_code: str,
        feedback: ANNCSUProcessingFeedback,
    ) -> Tuple[str, ScopeData]:
        """Create a new session and add it to SCOPES.

        Args:
            source_db (Optional[AnyUrl]): Source URL from where the duckdb has been extracted.
            municipality_code (str): Municipality code associated with this scope.
        Returns:
            scope: ScopeData"""
        now = datetime.now()
        scope_name = f"{municipality_code}_{now.strftime('%Y%m%d_%H%M%S')}"
        duckdb_path = cls.PLUGIN_PATH / "resources" / "data" / f"{scope_name}.duckdb"

        # populate scope session with subset of municipality data get from source_db
        duckdb_conn = duckdb.connect(database=duckdb_path, read_only=False)
        if duckdb_conn is None:
            raise Exception("Could not create local duckdb database.")
        
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
        feedback.setProgress(chunk_number)
        print(f"Downloading source duckdb from {source_db} to {temp_duckdb_path}...")
        with open(temp_duckdb_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                downloaded_size += len(chunk)
                progress = int(90 * (chunk_number / number_of_chunks))
                feedback.setProgress(progress)
                file.write(chunk)
                chunk_number += 1

        # duckdb_conn.execute(f"SELEC * '{str(temp_duckdb_path)}' AS source_db;")
        # create local duckdb with only data for selected municipality_code
        feedback.setProgress(95)
        force_column_types = "{'CODICE_COMUNALE_ACCESSO': 'VARCHAR', 'QUOTA': 'VARCHAR'}"
        duckdb_conn.execute(f"""
            CREATE TABLE anncsu AS
            SELECT * FROM READ_CSV_AUTO('zip://{str(temp_duckdb_path)}', header = true, delim=';', types={force_column_types})
            WHERE codice_comune = '{municipality_code}';
        """)
        duckdb_conn.close()

        # remove temporary downloaded duckdb
        os.remove(temp_duckdb_path)
        feedback.setProgress(100)

        # generate and return scope data
        scope = ScopeData(
            duckdb_path=duckdb_path,
            remote_duckdb_url=None,
            syncked=False,
            municipality_code=municipality_code,
            source_db=source_db,
            creation_date=now,
            update_date=None,
            description=f"ANNCSU Data for municipality {municipality_code} created on {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        scopes = cls.get_scopes()
        scopes[scope_name] = scope
        cls.set_scopes(scopes)
        return scope_name, scope