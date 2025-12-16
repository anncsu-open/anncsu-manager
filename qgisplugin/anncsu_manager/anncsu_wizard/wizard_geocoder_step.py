import importlib
import sys
import time
from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QProgressBar
)

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

import duckdb

# geocoders related imports
from geopy.geocoders import get_geocoder_for_service
# from whereabouts.Matcher import Matcher
from anncsu_manager.factories.geocoder_factory import GeocoderFactory

ANNCSU_TABLE_FIELDS = ("COMUNE", "PROVINCIA", "REGIONE", "CODICE_COMUNE", "CODICE_ISTAT", "PROGRESSIVO_NAZIONALE", "CODICE_COMUNALE", "ODONIMO", 'LOCALITA\'', "DIZIONE_LINGUA1", "DIZIONE_LINGUA2", "PROGRESSIVO_ACCESSO", "CODICE_COMUNALE_ACCESSO", "CIVICO", "ESPONENTE", "SPECIFICITA", "METRICO", "PROGRESSIVO_SNC", "COORD_X_COMUNE", "COORD_Y_COMUNE", "QUOTA", "METODO")

FORM_CLASS: QWizardPage = load_ui("wizard_run_geocoders_page.ui")


class ANNCSUWizardRunGeocoders(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # manage where to show mesages and progress
        self.progress_text: QTextEdit
        self.show_details_cb: QCheckBox
        self.show_details_cb.checked = False
        self.clear_log_pb: QPushButton
        self.clear_log_pb.clicked.connect(lambda: self.progress_text.clear())

        # setup GUI feedback during geocoding
        self.feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback(
            text_edit=None,
            progress_bar=progress_bar,
        )
        self.feedback.text_edit = self.progress_text
        self.feedback.progress_signal.connect(self.update_feedback_progress)
        self.feedback.text_signal.connect(self.update_feedback_text)

        # actions
        self.run_geocoders_pb: QPushButton
        self.run_geocoders_pb.clicked.connect(self.run_geocoders)

    
    def run_geocoders(self):
        print("Running geocoders...")

        """Run the geocoding processes as per user settings in geocoders.json."""
        geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()

        # get current scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes[current_scope_id] if current_scope_id in scopes else None
        self.feedback.pushInfo(f"Using scope: {current_scope_id}")
        if not current_scope:
            self.feedback.reportError("No scope is currently selected. Please select a scope in the settings before running geocoders.")
            return

        duck_db_source = current_scope.to_dict().get("duckdb_path", "")
        if not duck_db_source:
            self.feedback.reportError("No DuckDB database path found in the current scope settings.")
            return

        with duckdb.connect(duck_db_source) as scopedb:
            if scopedb is None:
                self.feedback.reportError(f"Could not connect to DuckDB database at {duck_db_source}.")
                return

            # load statial extension
            scopedb.execute("INSTALL spatial;")
            scopedb.execute("LOAD spatial;")

            # do geocoding
            try:
                self.feedback.progress_bar.setVisible(True)

                # for eache enabled goecoder, run the process
                for geocoder_name, geocoder_config in geocoders_configs.items():
                    # skip geocoder if not active
                    if geocoder_config.get("active", False) in [False, "False", "false"]:
                        self.feedback.pushInfo(f"Skiping inactive geocoder {geocoder_name}...")
                        continue

                    # isntanciate geocoder
                    geocoder = GeocoderFactory().get_geocoder(
                        geocoder_name,
                        **geocoder_config
                    )
                    if geocoder is None:
                        self.feedback.reportError(f"Could not instantiate geocoder '{geocoder_name}'.")
                        continue
                    # geocoder = Matcher(
                    #     db_name=geocoder_config.get("matcher_db", "italia_whereabouts"),
                    #     how=geocoder_config.get("how", ["standard"]),
                    #     threshold=geocoder_config.get("threshold", 0.5),
                    # )

                    addresses_to_geocode = []
                    anncsu_addresses = []
                    for to_geocode in scopedb.execute("SELECT * FROM anncsu").fetchall():
                        to_geocode_dict = dict(zip(ANNCSU_TABLE_FIELDS, to_geocode))
                        anncsu_addresses.append(to_geocode_dict)

                        address_to_geocode = f"""{to_geocode_dict["ODONIMO"]} {to_geocode_dict["CIVICO"]}, {to_geocode_dict["COMUNE"].strip("'")} ({to_geocode_dict["PROVINCIA"].strip("'")}), Italia"""
                        addresses_to_geocode.append(address_to_geocode)

                    self.feedback.progress_signal.emit(0)
                    self.feedback.progress_bar.setRange(0, len(addresses_to_geocode))
                    self.feedback.pushInfo(f"Geocoding {len(addresses_to_geocode)} addresses using {geocoder_name}...")

                    # do bulk geocode using WhereAbouts to do it faster
                    self.feedback.pushInfo(f"Geocoding {len(addresses_to_geocode)} bulk addresses to speedup process. ")
                    start = time.time()
                    geocoded = geocoder.geocode(addresses=addresses_to_geocode)
                    end = time.time()
                    self.feedback.pushInfo(f"Geocoded {len(addresses_to_geocode)} addresses in {end - start} seconds using {geocoder_name}. ")

                    # combine geocoded results with anncsu addresses to mantain relation with
                    # anncsu unique identifications
                    for idx, result in enumerate(geocoded):
                        result["address_id"] = anncsu_addresses[idx].get("PROGRESSIVO_ACCESSO", idx)
                        result["road_id"] = anncsu_addresses[idx].get("PROGRESSIVO_NAZIONALE", idx)

                    # save results in a result table where result table is related with geocoder name
                    result_table_name = f"geocoding_results_{geocoder_name}"
                    scopedb.execute(f"""
                        CREATE OR REPLACE TABLE {result_table_name} (
                            address_id INTEGER,
                            road_id INTEGER,
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

                    self.feedback.pushInfo(f"Saving geocoding results into table {result_table_name}...")
                    for idx, result in enumerate(geocoded):
                        self.feedback.progress_signal.emit(idx + 1)
                        if result:
                            scopedb.execute(f"""
                                    INSERT INTO {result_table_name} (
                                        address_id,
                                        road_id,
                                        input_address,
                                        address_matched,
                                        suburb,
                                        postcode,
                                        latitude,
                                        longitude,
                                        score,
                                        geometry
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ST_Point(?, ?))
                                """, (
                                    result.get("address_id", idx),
                                    result.get("road_id", idx),
                                    result.get("address", ""),
                                    result.get("address_matched", ""),
                                    result.get("suburb", ""),
                                    result.get("postcode", ""),
                                    result.get("latitude", None),
                                    result.get("longitude", None),
                                    result.get("similarity", 0.0),
                                    result.get("longitude", 0.0),
                                    result.get("latitude", 0.0),
                                )
                            )

                            if self.show_details_cb.isChecked():
                                message = f"Geocoded {result.get('address_id', idx)}: '{result.get('address', '')}' to: ({result.get('latitude', None)}, {result.get('longitude', None)}) score: {result.get('similarity', 0.0)}"
                                self.feedback.pushInfo(message)

                    self.feedback.pushInfo(f"Geocoder '{geocoder_name}': Geocodings saved into table {result_table_name}.")

                self.feedback.progress_signal.emit(100)
                self.feedback.pushInfo("All geocoding processes completed.")

                # because of new results mark scope as ditry that need synchronization
                current_scope.syncked = False
                current_scope.sync_changed.emit()

                # then save scope in settings to remember modifications
                scopes[current_scope_id] = current_scope
                ANNCSUSettingsManager.set_scopes(scopes)

            except QgsPluginException as e:
                self.feedback.reportError(f"An error occurred: {str(e)}")
            finally:
                self.feedback.progress_bar.setVisible(False)

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)

    def update_feedback_text(self, text: str):
        if "success: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="success", duration=5)
        elif "info: " in text.lower():
            pass
        elif "warning: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="warning", duration=5)
        elif "invalid: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="invalid", duration=10)
        elif "error: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="error", duration=0)

        if self.feedback.text_edit is not None:
            if isinstance(self.feedback.text_edit, QTextEdit):
                self.feedback.text_edit.append(text)
            elif isinstance(self.feedback.text_edit, QLabel):
                self.feedback.text_edit.setText(text)

