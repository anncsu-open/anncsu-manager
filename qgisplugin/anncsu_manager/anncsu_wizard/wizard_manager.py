from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from qgis.PyQt.QtWidgets import (
    QWizard,
    QProgressBar,
    QPushButton,
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

# wizard pages
from .wizard_geocoder_step import ANNCSUWizardRunGeocoders

FORM_CLASS: QWizard = load_ui("wizard_manager.ui")

class ANNCSUWizardManager(QWizard, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # DECLARE TYPES

        # set progress bar and feedback manager for long operations
        self.progressBar: QProgressBar = progress_bar if progress_bar is not None else QProgressBar()
        self.progressBar.setVisible(False)
        self.feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback(
            text_edit=None,
            progress_bar=self.progressBar,
        )
        self.feedback.progress_signal.connect(self.update_feedback_progress)

        # add run geocoder wizard page
        self.run_geocoders_page = ANNCSUWizardRunGeocoders(parent=self, feedback=self.feedback)
        self.addPage(self.run_geocoders_page)
    
    # def run_geocoders(self):
    #     """Run the geocoding processes as per user settings in geocoders.json."""
    #     geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()

    #     try:
    #         self.progressBar.setVisible(True)
    #         self.feedback.reset_progress()
    #         self.feedback.set_progress_maximum(100)

    #         # for eache enabled goecoder, run the process
    #         for gocoder_name, geocoder_config in geocoders_configs.items():
    #             # skip geocoder if not active
    #             if not geocoder_config.get("active", False):
    #                 continue
                


    #         # Example of running a geocoding process
    #             # self.feedback.push_info("Running Nominatim Geocoder...")
    #             # # Here would be the code to run the Nominatim geocoder
    #             # # For example: NominatimGeocoder.run(self.feedback)
    #             # self.feedback.push_info("Nominatim Geocoder completed successfully.")


    #         self.feedback.push_info("All geocoding processes completed.")

    #     except QgsPluginException as e:
    #         self.feedback.reportError(f"An error occurred: {str(e)}")
    #     finally:
    #         self.progressBar.setVisible(False)

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)
