from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from qgis.PyQt.QtWidgets import (
    QWizard,
    QProgressBar
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

# wizard pages
from anncsu_manager.anncsu_wizard.wizard_geocoder_step import ANNCSUWizardRunGeocoders

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
        self.run_geocoders_page_id = self.addPage(self.run_geocoders_page)

        # activate first page to allow enable it's events
        self.setStartId(self.run_geocoders_page_id);

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)
