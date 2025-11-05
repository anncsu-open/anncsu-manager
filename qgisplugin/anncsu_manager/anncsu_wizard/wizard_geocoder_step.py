import importlib
import sys
import time
from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QPushButton,
    QTextEdit,
)

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

import duckdb

# geocoders related imports
from geopy.geocoders import get_geocoder_for_service
from whereabouts.Matcher import Matcher

FORM_CLASS: QWizardPage = load_ui("wizard_run_geocoders_page.ui")


class ANNCSUWizardRunGeocoders(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, feedback: ANNCSUProcessingFeedback=ANNCSUProcessingFeedback()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # manage where to show mesages and progress
        self.progress_text: QTextEdit
        self.feedback: ANNCSUProcessingFeedback = feedback
        self.feedback.text_edit = self.progress_text

        # actions
        print("Connecting run_geocoders_pb.clicked to run_geocoders method")
        self.run_geocoders_pb: QPushButton
        self.run_geocoders_pb.clicked.connect(self.run_geocoders)

    
    def run_geocoders(self):
        print("Running geocoders...")

        """Run the geocoding processes as per user settings in geocoders.json."""
        geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()

        # get current scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes.get(current_scope_id, {})
        self.feedback.pushInfo(f"Using scope: {current_scope_id}")
        if not current_scope:
            self.feedback.reportError("No scope is currently selected. Please select a scope in the settings before running geocoders.")
            return

        try:
            self.feedback.progress_bar.setVisible(True)

            # for eache enabled goecoder, run the process
            for geocoder_name, geocoder_config in geocoders_configs.items():
                # skip geocoder if not active
                if geocoder_config.get("active", False) in [False, "False", "false"]:
                    self.feedback.pushInfo(f"Skiping inactive geocoder {geocoder_name}...")
                    continue

                duck_db_source = current_scope.to_dict().get("duckdb_path", "")
                if not duck_db_source:
                    self.feedback.reportError("No DuckDB database path found in the current scope settings.")
                    return
                
                scopedb = duckdb.connect(duck_db_source)
                if scopedb is None:
                    self.feedback.reportError(f"Could not connect to DuckDB database at {duck_db_source}.")
                    return

                # isntanciate geocoder
                whereabouts_matcher = Matcher(
                    db_name=geocoder_config.get("matcher_db", "italia_whereabouts"),
                    how=geocoder_config.get("how", ["standard"]),
                    threshold=geocoder_config.get("threshold", 0.5),
                )

                addresses_to_geocode = []
                field_names = ("COMUNE", "PROVINCIA", "REGIONE", "CODICE_COMUNE", "CODICE_ISTAT", "PROGRESSIVO_NAZIONALE", "CODICE_COMUNALE", "ODONIMO", 'LOCALITA\'', "DIZIONE_LINGUA1", "DIZIONE_LINGUA2", "PROGRESSIVO_ACCESSO", "CODICE_COMUNALE_ACCESSO", "CIVICO", "ESPONENTE", "SPECIFICITA", "METRICO", "PROGRESSIVO_SNC", "COORD_X_COMUNE", "COORD_Y_COMUNE", "QUOTA", "METODO")
                for to_geocode in scopedb.execute("SELECT * FROM anncsu").fetchall():
                    to_geocode_dict = dict(zip(field_names, to_geocode))
                    address_to_geocode = f"""{to_geocode_dict["ODONIMO"]} {to_geocode_dict["CIVICO"]}, {to_geocode_dict["COMUNE"].strip("'")} ({to_geocode_dict["PROVINCIA"].strip("'")}), Italia"""
                    addresses_to_geocode.append(address_to_geocode)

                self.feedback.progress_signal.emit(0)
                self.feedback.progress_bar.setRange(0, len(addresses_to_geocode))
                self.feedback.pushInfo(f"Geocoding {len(addresses_to_geocode)} addresses using {geocoder_name}...")

                if geocoder_name == "WhereAbouts":
                    # do bulk geocode using WhereAbouts to do it faster
                    self.feedback.pushInfo(f"Geocoding {len(addresses_to_geocode)} bulk addresses to speedup process. ")
                    start = time.time()
                    geocoded = whereabouts_matcher.geocode(addresses=addresses_to_geocode)
                    end = time.time()
                    self.feedback.pushInfo(f"Geocoded {len(addresses_to_geocode)} addresses in {end - start} seconds using {geocoder_name}. ")

                    # add spatial extension to duckdb
                    scopedb.execute("INSTALL spatial;")
                    scopedb.execute("LOAD spatial;")

                    # save results in a result table
                    scopedb.execute("""
                        CREATE OR REPLACE TABLE geocoding_results (
                            address_id INTEGER,
                            input_address TEXT,
                            address_matched TEXT,
                            suburb TEXT,
                            postcode TEXT,
                            latitude DOUBLE,
                            longitude DOUBLE,
                            score DOUBLE,
                            geometry GEOMETRY
                        )
                    """)
                    for idx, result in enumerate(geocoded):
                        self.feedback.progress_signal.emit(idx + 1)
                        if result:
                            scopedb.execute("""
                                    INSERT INTO geocoding_results (address_id, input_address, address_matched, suburb, postcode, latitude, longitude, score, geometry)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ST_Point(?, ?))
                                """, (
                                    result.get("address_id", idx),
                                    result.get("address", ""),
                                    result.get("address_matched", ""),
                                    result.get("suburb", ""),
                                    result.get("postcode", ""),
                                    result.get("latitude", None),
                                    result.get("longitude", None),
                                    result.get("similarity", 0.0),
                                    result.get("latitude", 0.0),
                                    result.get("longitude", 0.0),
                                )
                            )

                            message = f"Geocoded {result.get('address_id', idx)}: '{result.get('address', '')}' to: ({result.get('latitude', None)}, {result.get('longitude', None)}) score: {result.get('similarity', 0.0)}"
                            self.feedback.pushInfo(message)

                    # geocoder_service_name = geocoder_config.get("service", "")
                    # GeocoderClass = get_geocoder_for_service(geocoder_service_name)
                    # if GeocoderClass is None:
                    #     self.feedback.reportError(f"Geocoder service '{geocoder_service_name}' is not supported.")
                    #     continue
                    # geocoder = GeocoderClass(**geocoder_config.get("params", {}))
                    # location = geocoder.geocode(address)
                    # if location:
                    #     self.feedback.pushInfo(f"Geocoded address '{address}' to coordinates: ({location.latitude}, {location.longitude})")
                    # else:
                    #     self.feedback.pushInfo(f"Could not geocode address '{address}'.")


            self.feedback.progress_signal.emit(100)
            self.feedback.pushInfo("All geocoding processes completed.")

        except QgsPluginException as e:
            self.feedback.reportError(f"An error occurred: {str(e)}")
        finally:
            self.feedback.progress_bar.setVisible(False)

