from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from qgis.PyQt.QtWidgets import (
    QWizard,
    QProgressBar,
    QTextEdit,
    QLabel,
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

# wizard pages
from anncsu_manager.anncsu_wizard.wizard_geocoder_step import ANNCSUWizardRunGeocoders
from anncsu_manager.anncsu_wizard.wizard_evaluate_geocode_step import ANNCSUWizardEvaluateGeocode

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
        self.feedback.text_signal.connect(self.update_feedback_text)

        # add run geocoder wizard page
        self.run_geocoders_page = ANNCSUWizardRunGeocoders(parent=self, feedback=self.feedback)
        self.run_geocoders_page_id = self.addPage(self.run_geocoders_page)

        # add evaluate geocode wizard page
        self.evaluate_geocode_page = ANNCSUWizardEvaluateGeocode(parent=self, feedback=self.feedback)
        self.evaluate_geocode_page_id = self.addPage(self.evaluate_geocode_page)

        # activate first page to allow enable it's events
        self.setStartId(self.run_geocoders_page_id);

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

