import time
from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QTabWidget,
    QProgressBar,
    QTextEdit,
    QWidget
)

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

import duckdb

FORM_CLASS_TAB: QWidget = load_ui("geocode_results_tab.ui")
class ANNCUGeocodeResultTab(QWidget, FORM_CLASS_TAB):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


FORM_CLASS: QWizardPage = load_ui("wizard_evaluate_geocode_page.ui")
class ANNCSUWizardEvaluateGeocode(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.geocoders_tabs: QTabWidget
        self.progress_text: QTextEdit

        # setup GUI feedback during geocoding
        self.feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback(
            text_edit=None,
            progress_bar=progress_bar,
        )
        self.feedback.text_edit = self.progress_text
        self.feedback.progress_signal.connect(self.update_feedback_progress)
        self.feedback.text_signal.connect(self.update_feedback_text)


    def initializePage(self):
        """Called when the page is about to be shown."""
        self.populate_geocoders_tabs()

    def populate_geocoders_tabs(self):
        """Populate the geocoders tabs with evaluation results."""
        geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()

        # get current scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes.get(current_scope_id, {})
        self.feedback.pushInfo(f"Using scope: {current_scope_id}")
        print(f"Current scope: {current_scope}")
        if not current_scope:
            self.feedback.reportError("No scope is currently selected. Please select a scope in the settings before running geocoders.")
            return

        duck_db_source = current_scope.to_dict().get("duckdb_path", "")
        if not duck_db_source:
            self.feedback.reportError("No DuckDB database path found in the current scope settings.")
            return

        scopedb = duckdb.connect(duck_db_source)
        if scopedb is None:
            self.feedback.reportError(f"Could not connect to DuckDB database at {duck_db_source}.")
            return

        # because source db could be changed, clear all tabs first
        self.geocoders_tabs.clear()

        for geocoder_name, geocoder_config in geocoders_configs.items():
            # check if results table exists
            result_table_name = f"geocoding_results_{geocoder_name}"
            try:
                scopedb.execute(f"SELECT * FROM {result_table_name} LIMIT 1;")
            except Exception as e:
                self.feedback.pushWarning(f"Results table '{result_table_name}' does not exist. Skipping evaluation for geocoder '{geocoder_name}'.")
                continue

            # create a new tab for this geocoder
            geocoder_tab = ANNCUGeocodeResultTab(parent=self)
            self.geocoders_tabs.addTab(geocoder_tab, geocoder_name)

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

