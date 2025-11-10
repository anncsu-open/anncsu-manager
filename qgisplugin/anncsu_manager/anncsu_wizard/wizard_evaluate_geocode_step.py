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

FORM_CLASS: QWizardPage = load_ui("wizard_evaluate_geocode_page.ui")


class ANNCSUWizardEvaluateGeocode(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, feedback: ANNCSUProcessingFeedback=ANNCSUProcessingFeedback()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # manage where to show mesages and progress
        self.feedback: ANNCSUProcessingFeedback = feedback
