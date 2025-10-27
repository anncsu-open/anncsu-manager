import json
from pathlib import Path
from typing import Optional

import duckdb

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from qgis.gui import QgsMessageBar
from qgis.core import Qgis
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QWidget,
    QLineEdit,
    QTreeView,
    QMessageBox,
    QProgressBar,
    QLabel,
    QPushButton
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.anncsu_wizard.data_models.geocoder_model import GeocoderModel
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.utils.settings_manager import ScopeData

FORM_CLASS: QDialog = load_ui("wizard_settings.ui")

CODICE_COMUNE_DB_PATH = Path(PLUGIN_PATH) / "resources" / "data" / "CODICE_COMUNE.parquet"

class ANNCSUWizardSettings(QWidget, FORM_CLASS):

    minimal_menu_setting_changed = pyqtSignal(bool)

    def __init__(self, parent=None, progress_bar: QProgressBar=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # DECLARE TYPES
        # self.settings_tabs: QTabWidget

        # set progress bar and feedback manager for long operations
        self.progressBar: QProgressBar = progress_bar if progress_bar is not None else QProgressBar()
        self.progressBar.setVisible(False)
        self.feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback(
            text_edit=None,
            progress_bar=self.progressBar,
        )
        self.feedback.progress_signal.connect(self.update_feedback_progress)

        # binding var to UI elements
        self.anncsu_base_url: QLineEdit
        self.codice_comune: QComboBox
        self.geocodersTreeView: QTreeView
        self.session_url: QLabel
        # this comobobox store current session data
        # based on session name and scope id
        self.current_session: QComboBox
        self.delete_session: QPushButton

        # self.default_base_raster: QgsMapLayerComboBox
        self.minimal_menu_selection: QCheckBox

        self.settings_button_box: QDialogButtonBox

        # Connect signals
        self.current_session.currentIndexChanged.connect(
            lambda: self.manageSessionChange(
                self.current_session.currentText(),
                self.current_session.currentData()
            )
        )
        self.delete_session.clicked.connect(lambda: self.manageDeleteSession())

        self.settings_button_box.button(
            QDialogButtonBox.RestoreDefaults
        ).clicked.connect(self.reset_settings_to_default)
        self.settings_button_box.button(QDialogButtonBox.RestoreDefaults).setAutoDefault(False)
        self.settings_button_box.button(QDialogButtonBox.Save).clicked.connect(self.save_settings)

        # Initialize
        # current configured repo and codice_comune to check if changed and
        # setup a new session basing on this
        # if session is available use always data stored in the session
        self.fallout_anncsu_repo = ANNCSUSettingsManager.get_anncsu_repo()
        if not self.fallout_anncsu_repo:
            ANNCSUSettingsManager.reset_anncsu_repo()
            self.fallout_anncsu_repo = ANNCSUSettingsManager.get_anncsu_repo()
        self.fallout_codice_comune = ANNCSUSettingsManager.get_municipality_code()
        self.scopes = ANNCSUSettingsManager.get_scopes()
        self.current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        # current_scope = self.scopes.get(current_scope_id, None)
        # self.current_session = SessionData(
        #     scope_id=current_scope_id,
        #     scope=current_scope,
        # )
        # # session modification evetn have to be explicitly emitted when changing current_scope_id
        # self.current_session.modified.connect(
        #     lambda: self.manageSessionChange()
        # )

        self.set_settings_gui()  # Initialize UI from settings

        # first synchecd updated basing on session
        self.manageSessionChange()

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)

    # def update_feedback_text(self, text: str):
    #     self.feedback.text_edit.append(text)

    def manageDeleteSession(self):
        """Manage deletion of current session."""
        current_scope = self.current_session.currentData()
        if current_scope is None:
            ANNCSUMessageManager().show_message(
                "Nessuna sessione selezionata da eliminare.",
                "warning",
            )
            return

        reply = QMessageBox.question(self,
            "Eliminazione sessione ANNCSU",
            f"Sei sicuro di voler eliminare la sessione '{self.current_session.currentText()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.No:
            return  # user cancelled, do not delete session

        ANNCSUSettingsManager.delete_session(
            scope_id=self.current_session.currentText()
        )

        # remove from combobox
        index = self.current_session.currentIndex()
        self.current_session.removeItem(index)

        # set to first session available
        self.current_session.setCurrentIndex(self.current_session.count() - 1) # index 0 is "select session"
        self.current_scope_id = self.current_session.currentText()
        self.manageSessionChange()

        ANNCSUMessageManager().show_message(
            f"Sessione '{self.current_session.currentText()}' eliminata.",
            "success",
        )

    def manageSessionChange(self,
                            current_scope_id: Optional[str] = None,
                            current_scope: Optional[ScopeData] = None):
        """Manage change of session_name selection."""

        # when not triggered by signal set the GUI basing on configured session_scope_id
        if current_scope_id is None and current_scope is None:
            current_scope_id = self.current_scope_id # get from configured settings
            current_scope = self.scopes.get(current_scope_id, None)
            
            # set current_session dropbox pointing to current scope id
            index = self.current_session.findText(current_scope_id)
            if index != -1:
                self.current_session.setCurrentIndex(index)
            else:
                self.current_session.setCurrentIndex(0)
        
        # set gui basing on current scope
        scope = self.current_session.currentData()
        scope_dict = scope.to_dict() if scope else {}
        anncsu_repo = scope_dict.get("source_db", self.fallout_anncsu_repo)
        municipality_code = scope_dict.get("municipality_code", self.fallout_codice_comune)

        self.anncsu_base_url.setText(anncsu_repo)
        index = self.codice_comune.findData(municipality_code)
        if index != -1:
            self.codice_comune.setCurrentIndex(index)
        else:
            self.codice_comune.setCurrentIndex(0)

            # no municipality is set yet, notity user to save settings to create a session
            ANNCSUMessageManager().show_message(
                "Nessun codice comune associato alla sessione selezionata.\n" \
                "Selezionane uno e salvare per creare una sessione di lavoro.",
                "warning",
            )

        remote_duckdb_url = scope_dict.get("remote_duckdb_url", None)
        if not remote_duckdb_url:
            # e.g. if None or empty string
            remote_duckdb_url = "N/A"
        self.session_url.setText(remote_duckdb_url)

    def set_settings_gui(self):
        """Load settings and set selections accordingly."""
        # get geocodes configs
        geocoders_json_path = ANNCSUSettingsManager.get_geocoders_json_path()
        if not Path(geocoders_json_path).exists():
            raise QgsPluginException(f"Could not find geocoders.json at {geocoders_json_path}")
        model = GeocoderModel()
        self.geocodersTreeView.setModel(model)
        with open(geocoders_json_path) as file:
            document = json.load(file)
            model.load(document)
        
        # get source of ANNCSU data
        # self.anncsu_base_url.setText(self.current_anncsu_repo)

        # populate codice_comune combobox
        # before populate need to suspend envnts to avoid triggering currentIndexChanged signal
        self.codice_comune.blockSignals(True)
        comuni = duckdb.read_parquet(str(CODICE_COMUNE_DB_PATH))
        self.codice_comune.clear()
        self.codice_comune.addItem("Seleziona codice comune", "")
        for codice_comune in comuni.fetchall():
            self.codice_comune.addItem(f"{codice_comune[0]}", codice_comune[0])
        self.codice_comune.blockSignals(False)
        
        # set configure codice_comune in combobox
        # index = self.codice_comune.findData(self.current_codice_comune)
        # if index != -1:
        #     self.codice_comune.setCurrentIndex(index)
        # else:
        #     self.codice_comune.setCurrentIndex(0)

        # populate current_session combobox
        self.current_session.blockSignals(True)
        self.current_session.clear()
        self.current_session.addItem("Seleziona sessione", None)
        for scope_id, scope in self.scopes.items():
            self.current_session.addItem(scope_id, scope)

        # set current scope id and related repo
        # index = self.current_session.findText(self.current_session.current_scope_id)
        # if index != -1:
        #     self.current_session.setCurrentIndex(index)
        # else:
        #     self.current_session.setCurrentIndex(0)
        self.current_session.blockSignals(False)

        # remote_duckdb_url = self.current_scope.to_dict().get("remote_duckdb_url", None)
        # if not remote_duckdb_url:
        #     # e.g. if None or empty string
        #     remote_duckdb_url = "N/A"
        # self.session_url.setText(remote_duckdb_url)


    def save_settings(self):
        """Save current selections.
        If codice_comune or anncsu repo changed, warning the user that a new session will be created.
        If user accepts, a new session will be created and settings saved."""
        # get current session data from combobox
        current_scope = self.current_session.currentData()
        current_scope_dict = {}
        if current_scope is not None:
            current_scope_dict = current_scope.to_dict()
        
        # need a municipality code to proceed
        if self.codice_comune.currentData() == "":
            ANNCSUMessageManager().show_message(
                "Selezionare un codice comune per procedere.",
                "warning",
            )
            return

        if (
            self.anncsu_base_url.text() != current_scope_dict.get("source_db", "") or
            self.codice_comune.currentData() != current_scope_dict.get("municipality_code", "")
        ):
            reply = QMessageBox.question(self,
                "DB sorgente ANNUCSU o codice comune modificati",
                "Verrà generata una nuova sessione ANNCSU. Vuoi procedere?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                # set back previous data
                self.anncsu_base_url.setText(current_scope_dict.get("source_db", ""))
                self.codice_comune.setCurrentIndex(
                    self.codice_comune.findData(current_scope_dict.get("municipality_code", ""))
                )

                ANNCSUMessageManager().show_message("Nessun cambio salvato", "success")
                return  # user cancelled, do not save settings
            else:
                # proceed to create new session
                self.feedback.progress_bar.show()
                mew_scope_id, new_scope = ANNCSUSettingsManager.create_new_session(
                    source_db=self.anncsu_base_url.text(),
                    municipality_code=self.codice_comune.currentData(),
                    feedback=self.feedback,
                )
                self.feedback.progress_bar.hide()

                # then add new session to combobox and set it as current
                self.current_session.addItem(mew_scope_id, new_scope)
                self.current_session.setCurrentIndex(
                    self.current_session.findText(mew_scope_id)
                )

        ANNCSUSettingsManager.set_geocoders_configs(self.geocodersTreeView.model().to_json())
        ANNCSUSettingsManager.set_anncsu_repo(self.anncsu_base_url.text())
        ANNCSUSettingsManager.set_municipality_code(self.codice_comune.currentData())
        ANNCSUSettingsManager.set_current_scope_id(self.current_session.currentText())
        ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings saved.", "success")


    def reset_settings_to_default(self):
        """Set selections to defaults. Does not save."""
        ANNCSUSettingsManager.reset_all()
        self.set_settings_gui()
        self.manageSessionChange()
        ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings reset.", "info")
