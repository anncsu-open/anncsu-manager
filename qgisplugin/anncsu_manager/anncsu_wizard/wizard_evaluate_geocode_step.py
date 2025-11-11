import time
from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QTabWidget,
    QProgressBar,
    QTextEdit,
    QWidget,
    QLabel,
    QTableView
)

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.qgis_plugin_tools.tools.models import DataFrameModel

import duckdb

FORM_CLASS_TAB: QWidget = load_ui("geocode_results_tab.ui")
class ANNCUGeocodeResultTab(QWidget, FORM_CLASS_TAB):
    def __init__(self,
                 parent=None,
                 scopedb: duckdb.DuckDBPyConnection = None,
                 result_table_name: str = "",
                 feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.scopedb = scopedb
        self.result_table_name = result_table_name

        # setup UI elements
        self.feedback = feedback
        self.geocodes_tv: QTableView
        self.statistics_geocode_score: QLabel
        self.statistics_num_of_records: QLabel
        self.statistics_num_of_success: QLabel
        self.statistics_num_of_fails: QLabel
        self.statistics_num_of_out_of_geofence: QLabel

        self.load_results()
    
    def load_results(self):
        """Load geocoding results from the database and display them in the text edit."""
        try:
            query = f"SELECT * FROM {self.result_table_name};"
            results = self.scopedb.execute(query).df()

            # show results in table view
            model = DataFrameModel(results)
            self.geocodes_tv.setModel(model)

            # Display statistics
            success_score_threshold = 0.8  # example threshold

            total_records = len(results)
            success = results.query(f"geometry != None and score >= {success_score_threshold}", inplace=False)
            num_of_success = len(success)
            fails = results.query(f"geometry == None or score < {success_score_threshold}", inplace=False)
            num_of_fails = len(fails)
            num_of_out_of_geofence = len(results[results['score'] == 'out_of_geofence'])

            self.statistics_num_of_records.setText(str(total_records))
            self.statistics_num_of_success.setText(str(num_of_success))
            self.statistics_num_of_fails.setText(str(num_of_fails))
            self.statistics_num_of_out_of_geofence.setText(str(num_of_out_of_geofence))
            if total_records > 0:
                success_rate = (num_of_success / total_records) * 100
            else:
                success_rate = 0.0
            self.statistics_geocode_score.setText(f"{success_rate:.2f}%")

        except Exception as e:
            self.feedback.reportError(f"Error loading results: {str(e)}")


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
            geocoder_tab = ANNCUGeocodeResultTab(
                parent=self,
                scopedb=scopedb,
                result_table_name=result_table_name,
                feedback=self.feedback
            )
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

