from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QPushButton,
)
import duckdb

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback



# geocoders related imports
from geopy.geocoders import get_geocoder_for_service

FORM_CLASS: QWizardPage = load_ui("wizard_run_geocoders_page.ui")

class ANNCSUWizardRunGeocoders(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, feedback: ANNCSUProcessingFeedback=ANNCSUProcessingFeedback()) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.feedback: ANNCSUProcessingFeedback = feedback

        # actions
        self.run_geocoders_pb: QPushButton
        self.run_geocoders_pb.pressed.connect(self.run_geocoders)

    
    def run_geocoders(self):
        """Run the geocoding processes as per user settings in geocoders.json."""
        geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()

        # get current scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes.get(current_scope_id, {})
        self.feedback.push_info(f"Using scope: {current_scope_id}")
        if not current_scope:
            self.feedback.reportError("No scope is currently selected. Please select a scope in the settings before running geocoders.")
            return

        try:
            self.progressBar.setVisible(True)
            self.feedback.reset_progress()
            self.feedback.set_progress_maximum(100)

            # for eache enabled goecoder, run the process
            for gocoder_name, geocoder_config in geocoders_configs.items():
                # skip geocoder if not active
                if not geocoder_config.get("active", False):
                    continue

                duck_db_source = current_scope.get("duckdb_path", "")
                if not duck_db_source:
                    self.feedback.reportError("No DuckDB database path found in the current scope settings.")
                    return
                
                scopedb = duckdb.connect(duck_db_source)
                if scopedb is None:
                    self.feedback.reportError(f"Could not connect to DuckDB database at {duck_db_source}.")
                    return
                for to_geocode in scopedb.execute("SELECT * FROM anncsu").fetchall():
                    pass
                    # address_to_geocode = f"""{to_geocode["ODONIMO"]}  {to_geocode["CIVICO"]}, {to_geocode["COMUNE"] ()}
                    # geocoder_service_name = geocoder_config.get("service", "")
                    # GeocoderClass = get_geocoder_for_service(geocoder_service_name)
                    # if GeocoderClass is None:
                    #     self.feedback.reportError(f"Geocoder service '{geocoder_service_name}' is not supported.")
                    #     continue
                    # geocoder = GeocoderClass(**geocoder_config.get("params", {}))
                    # location = geocoder.geocode(address)
                    # if location:
                    #     self.feedback.push_info(f"Geocoded address '{address}' to coordinates: ({location.latitude}, {location.longitude})")
                    # else:
                    #     self.feedback.push_info(f"Could not geocode address '{address}'.")"""


            # Example of running a geocoding process
                # self.feedback.push_info("Running Nominatim Geocoder...")
                # # Here would be the code to run the Nominatim geocoder
                # # For example: NominatimGeocoder.run(self.feedback)
                # self.feedback.push_info("Nominatim Geocoder completed successfully.")


            self.feedback.push_info("All geocoding processes completed.")

        except QgsPluginException as e:
            self.feedback.reportError(f"An error occurred: {str(e)}")
        finally:
            self.progressBar.setVisible(False)

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)
