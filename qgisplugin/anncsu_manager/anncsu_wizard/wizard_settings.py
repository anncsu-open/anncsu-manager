import json
from functools import partial
from pathlib import Path
from typing import Optional
import importlib
from pydantic import AnyUrl

import duckdb

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from qgis.core import Qgis, QgsMessageLog, QgsTask, QgsApplication
from qgis.PyQt.QtCore import Qt, pyqtSignal
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
    QPushButton,
)
from qgis.PyQt.QtGui import QIcon

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.anncsu_wizard.data_models.geocoder_model import GeocoderModel
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.utils.settings_manager import ScopeData, MunicipalityData
from anncsu_manager.factories.geocoder_factory import GeocoderFactory

FORM_CLASS: QDialog = load_ui("wizard_settings.ui")

CODICE_CATASTRO_DB_PATH = Path(PLUGIN_PATH) / "resources" / "data" / "Elenco-comuni-italiani.csv"

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
        self.create_new_session_task: Optional[QgsTask] = None  # necessary to track task state
        self.update_anncsu_task: Optional[QgsTask] = None  # necessary to track task state

        # binding var to UI elements
        self.anncsu_base_url: QLineEdit
        self.comune_cb: QComboBox
        self.geocodersTreeView: QTreeView
        self.session_url: QLabel

        self.sync_pb: QPushButton
        self.sync_pb.clicked.connect(lambda: self.sync_session())
        self.sync_pb.setStyleSheet("QPushButton { color: orange; }")

        # this comobobox store current session data
        # based on session name and scope id
        self.current_session: QComboBox
        self.update_session: QPushButton
        self.delete_session: QPushButton
        self.create_new_session: QPushButton

        # self.default_base_raster: QgsMapLayerComboBox
        self.minimal_menu_selection: QCheckBox

        self.settings_button_box: QDialogButtonBox

        # Connect signals
        self.current_session.currentIndexChanged.connect(
            lambda: self.manageSessionChange(
                self.current_session.currentText(),
                self.current_session.currentData() # ScopeData
            )
        )
        self.delete_session.clicked.connect(lambda: self.manageDeleteSession())
        self.update_session.clicked.connect(self.manageUpdateSession)
        self.create_new_session.clicked.connect(lambda: self.save_settings(force_creation_new_session=True))

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

        # for each scope register event to track sync changes
        # and register unlinked when class is destroyed
        for scope in self.scopes.values():
            scope.sync_changed.connect(self.update_sync_button_color)
        self.destroyed.connect(lambda: self.unlink_scopes_listeners())

        self.set_settings_gui()  # Initialize UI from settings

        # first synchecd updated basing on session
        self.manageSessionChange()

        # register geocoders in factory
        self.registerGeocoders()

    def unlink_scopes_listeners(self) -> None:
        # because self.scopes hold references to ScopeData singleton instances
        # linked signals have to be unlinked to avoid memory leaks
        # NOTE: do not delete scopes as they are used also in main wizard
        # and refer to cls instances of ScopeData singletones
        if self.scopes:
            for scope in self.scopes.values():
                scope.sync_changed.disconnect(self.update_sync_button_color)

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)

    def sync_session(self):
        """Sync current session with remote git repo."""
        current_scope: Optional[ScopeData] = self.current_session.currentData()
        if current_scope is None:
            ANNCSUMessageManager().show_message(
                "Nessuna sessione selezionata da sincronizzare.",
                "warning",
            )
            return

        self.feedback.progress_bar.show()
        self.feedback.progress_bar.setMinimum(0)
        self.feedback.progress_bar.setMaximum(0)

        try:
            current_scope.sync()

            # save again in combobox data because sync flag has been changed
            self.current_session.setItemData(
                self.current_session.currentIndex(),
                current_scope,
            )
            self.save_settings()  # save settings to persist sync flag

            ANNCSUMessageManager().show_message(
                f"Sessione '{self.current_session.currentText()}' sincronizzata con il repository remoto.",
                "success",
            )
        except Exception as e:
            ANNCSUMessageManager().show_message(
                f"Errore durante la sincronizzazione della sessione '{self.current_session.currentText()}': {str(e)}",
                "error",
            )
        finally:
            self.feedback.progress_bar.hide()

    def manageUpdateSession(self):
        """Manage update of current session.
        Update get the current anncsu remote db and update current session data
        with new updated records that are the ground thruth."""
        current_scope = self.current_session.currentData()
        if current_scope is None:
            ANNCSUMessageManager().show_message(
                "Nessuna sessione selezionata da aggiornare.",
                "warning",
            )
            return

        # update ANNCSU table in current session with source_db data, this operation can be time
        # consuming so run it in a separate thread with QgsTask
        # current_scope = self.current_session.currentData()
        # update_anncsu_function = partial(ANNCSUSettingsManager.populate_table_from_source,
        #     duckdb_path=current_scope.duckdb_path,
        #     source_db=current_scope.source_db,
        #     table_name="anncsu",
        #     municipality_data=current_scope.municipality_data,
        # )

        # self.update_anncsu_task = QgsTask.fromFunction(
        #     f"Scaricando ANNCSU aggiornato per comune {current_scope.municipality_data.anncsu_id}",
        #     update_anncsu_function,
        #     on_finished=self.manageUpdateSessionStep2,
        # )

        # # run update current session time consuming task
        update_anncsu_task = ANNCSUSettingsManager.populate_table_from_source_task(
            duckdb_path=current_scope.duckdb_path,
            source_db=current_scope.source_db,
            table_name="anncsu",
            municipality_data=current_scope.municipality_data
        )

        # run update current session time consuming task
        QgsApplication.taskManager().addTask(update_anncsu_task)
        while update_anncsu_task.status() != QgsTask.Running:
            QgsApplication.processEvents()
        while update_anncsu_task.status() == QgsTask.Running:
            QgsApplication.processEvents()

        # check if task has been terminated due to error or cancellation
        if update_anncsu_task.status() == QgsTask.Terminated:
            ANNCSUMessageManager().show_message(
                f"Errore durante la creazione della nuova sessione: {str(update_anncsu_task.exception)}",
                "error",
            )
            return
        QgsMessageLog.logMessage(f"Successfully updated ANNCSU table for session {self.current_session.currentText()}", level=Qgis.Info)

        # now update current session with update ANNCSU data
        res = ANNCSUSettingsManager.update_current_session()
        if not res:
            ANNCSUMessageManager().show_message(
                "Aggiornamento ANNCSU annullato.",
                "info",
            )
            return

        ANNCSUMessageManager().show_message(
            "ANNCSU Aggiornato con successo per la sessione selezionata.",
            "success",
        )

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
            
            print(f"Setting session for {current_scope_id} with scope {current_scope}")
            # set current_session dropbox pointing to current scope id
            index = self.current_session.findText(current_scope_id)
            if index != -1:
                self.current_session.setCurrentIndex(index)
            else:
                self.current_session.setCurrentIndex(0)
        else:
            print(f"Session changed to {current_scope_id} for {current_scope}")
        
        # set gui basing on current scope
        scope_id = self.current_session.currentText()
        scope = self.current_session.currentData()
        scope_dict = scope.to_dict() if scope else {}
        anncsu_repo = scope_dict.get("source_db", self.fallout_anncsu_repo)
        municipality_code = scope_dict.get("municipality_data", {}).get("anncsu_id", self.fallout_codice_comune)

        self.anncsu_base_url.setText(anncsu_repo)
        index = self.comune_cb.findText(municipality_code, Qt.MatchFlag.MatchContains)
        if index != -1:
            self.comune_cb.setCurrentIndex(index)
        else:
            self.comune_cb.setCurrentIndex(0)

            # no municipality is set yet, notity user to save settings to create a session
            ANNCSUMessageManager().show_message(
                "Nessun codice comune associato alla sessione selezionata.\n" \
                "Selezionane uno e salvare per creare una sessione di lavoro.",
                "warning",
            )

        remote_git_repo = scope_dict.get("remote_git_repo", None)
        if not remote_git_repo:
            # e.g. if None or empty string
            remote_git_repo = "N/A"
        self.session_url.setText(remote_git_repo)

        # depending on sync flag into current session
        # set color of sync_pb button
        self.update_sync_button_color()

        # update current session data in settings to be able to retrieve it in main wizard
        ANNCSUSettingsManager.set_current_scope_id(scope_id)

    def update_sync_button_color(self):
        """Update sync button color based on current session sync status."""
        if self.current_session.currentData() is not None:
            if self.current_session.currentData().syncked:
                # if synched then text color is green
                self.sync_pb.setStyleSheet("QPushButton { color: green; }")
            else:
                # if not synched then text color is red
                self.sync_pb.setStyleSheet("QPushButton { color: red; }")
        else:
            # no session selected, orange color
            self.sync_pb.setStyleSheet("QPushButton { color: orange; }")

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
        
        # populate codice_comune combobox
        # before populate need to suspend envnts to avoid triggering currentIndexChanged signal
        self.comune_cb.blockSignals(True)
        codice_catastro = duckdb.sql(f"""
            select
                "Progressivo del comune (2)" as id,
                "Denominazione in italiano" as nome,
                "Denominazione dell'Unità territoriale sovracomunale(valida a fini statistici)" as provincia,
                "Denominazione Regione" as regione,
                "Codice catastale del comune" as anncsu_id
            from read_csv(
                '{CODICE_CATASTRO_DB_PATH}',
                encoding='8859_1',
                delim=';',
                header = true)
            ORDER BY nome ASC;
        """)
                
        self.comune_cb.clear()
        self.comune_cb.addItem("Seleziona codice comune", "")
        for id, nome, provincia, regione, anncsu_id in codice_catastro.fetchall():
            municipality_data = MunicipalityData(
                id=id,
                nome=nome,
                provincia=provincia,
                regione=regione,
                anncsu_id=anncsu_id,
            )
            self.comune_cb.addItem(f"{nome} -- {anncsu_id}", municipality_data)
        self.comune_cb.blockSignals(False)
        
        # populate current_session combobox
        self.current_session.blockSignals(True)
        self.current_session.clear()
        self.current_session.addItem("Seleziona sessione", None)
        for scope_id, scope in self.scopes.items():
            self.current_session.addItem(scope_id, scope)
        self.current_session.blockSignals(False)

        self.update_sync_button_color()

    def registerGeocoders(self):
        """Register geocoder builders in GeocoderFactory based on geocoders.json configuration."""
        # clean all available geocoders first
        GeocoderFactory().reset_builders()

        # get configured geocoders and regiseter buloder if any and active
        geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()
        for geocoder_name, geocoder_config in geocoders_configs.items():
            # skip not active geocoders
            if geocoder_config.get("active", False) in [False, "False", "false"]:
                print(f"Skipping inactive geocoder {geocoder_name}...")
                continue

            # skip geocoder if not builder is specified (e.g. not implemented)
            builder_module_name = geocoder_config.get("builder_module", None)
            if builder_module_name is None:
                print(f"Skipping geocoder {geocoder_name} with no builder module specified...")
                continue  # no builder specified, skip registration

            builder_name = geocoder_config.get("builder", None)
            if builder_name is None:
                print(f"Skipping geocoder {geocoder_name} with no builder specified...")
                continue  # no builder specified, skip registration

            # Dynamically import the builder class
            try:
                module = importlib.import_module(f"anncsu_manager.factories.{builder_module_name.lower()}")
                importlib.reload(module) # to avoid to used cache one
                builder_class = getattr(module, builder_name)
                GeocoderFactory().register_geocoder(geocoder_name, builder_class())
                print(f"Registered geocoder {builder_name}")
            except (ImportError, AttributeError) as e:
                ANNCSUMessageManager().show_message(f"Could not register geocoder '{geocoder_name}': {e}", "error")

    def save_settings(self, force_creation_new_session: bool = False):
        """Save current selections and persist ANNCSU plugin settings.
        If the selected municipality code or ANNCSU repository URL differs from the
        current session, prompt the user to confirm creation of a new session. When
        confirmed, start a background task to create the new session; otherwise restore
        previous values and abort. If no change is detected (or when applicable), save
        geocoder configurations, repository URL, municipality code, scopes, and current
        scope identifier, then notify the user.
        Args:
            force_creation_new_session (bool): If True, force creation of a new session
                without checking whether the municipality code or repository changed.
        Returns:
            None
        """
        # get current session data from combobox
        current_scope = self.current_session.currentData()
        current_scope_dict = {}
        if current_scope is not None:
            current_scope_dict = current_scope.to_dict()
        
        # need a municipality code to proceed
        if self.comune_cb.currentData() is None:
            ANNCSUMessageManager().show_message(
                "Selezionare un codice comune per procedere.",
                "warning",
            )
            return

        municipality_data: MunicipalityData = self.comune_cb.currentData()
        current_municipality_code = current_scope_dict.get("municipality_data", {}).get("anncsu_id", "")
        if (
            self.anncsu_base_url.text() != current_scope_dict.get("source_db", "") or
            municipality_data.anncsu_id != current_municipality_code or
            force_creation_new_session
        ):
            # launch a new session creation with QgsTask to avoid GUI blocking
            if self.create_new_session_task is not None:
                # avoid multiple task creation
                ANNCSUMessageManager().show_message(
                    "Task di creazione nuova sessione già in esecuzione.",
                    "warning",
                )
                return

            if force_creation_new_session:
                message = "Forzando la creazione di una nuova sessione ANNCSU. Vuoi procedere?" \

            else:
                message = "Il codice comune o il database sorgente ANNCSU sono stati modificati rispetto alla sessione attuale.\n" \
                    "Verrà generata una nuova sessione ANNCSU. Vuoi procedere?"
            reply = QMessageBox.question(self,
                "DB sorgente ANNUCSU o codice comune modificati",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                # set back previous data
                self.anncsu_base_url.setText(current_scope_dict.get("source_db", ""))
                self.comune_cb.setCurrentIndex(
                    # todelete: self.comune_cb.findData(current_scope_dict.get("municipality_code", ""))
                    self.comune_cb.findText(current_municipality_code, Qt.MatchFlag.MatchContains)
                )

                ANNCSUMessageManager().show_message("Nessun cambio salvato", "success")
                return  # user cancelled, do not save settings

            # proceed to create new session
            self.feedback.progress_bar.show()
            self.feedback.progress_bar.setMinimum(0)
            self.feedback.progress_bar.setMaximum(0)

            # create the session (time consuming) task
            # self.create_new_session_task = QgsTask.fromFunction(
            #     f"Creazione nuova sessione per comune {municipality_data.anncsu_id}",
            #     ANNCSUSettingsManager.create_new_session,
            #     source_db=AnyUrl(self.anncsu_base_url.text()),
            #     municipality_data=municipality_data,
            #     feedback=self.feedback,
            #     on_finished=self.on_finished_create_new_session,
            # )

            # # run create new settion sime spending task
            # QgsApplication.taskManager().addTask(self.create_new_session_task)

            # create new session
            new_scope_id, new_scope = None, None
            try:
                new_scope_id, new_scope = ANNCSUSettingsManager.create_new_session(
                    source_db=AnyUrl(self.anncsu_base_url.text()),
                    municipality_data=municipality_data,
                    feedback=self.feedback,
                )
            except Exception as e:
                ANNCSUMessageManager().show_message(str(e), "error")

            finally:
                self.feedback.progress_bar.hide()
                if new_scope_id is None or new_scope is None:
                    ANNCSUMessageManager().show_message(
                        "Errore durante la creazione della nuova sessione",
                        "error",
                    )
                    return
                print(f"New session created: {new_scope_id} -> {new_scope}")

            # add new session to combobox and set it as current
            current_scope = new_scope
            current_scope.sync_changed.connect(self.update_sync_button_color)
            current_scope.sync_changed.emit()  # initial sync status
            self.current_session.addItem(new_scope_id, current_scope)
            self.current_session.setCurrentIndex(
                self.current_session.findText(new_scope_id)
            )

            # save settings
            # ANNCSUSettingsManager.set_geocoders_configs(self.geocodersTreeView.model().to_json())
            # self.registerGeocoders()
            # ANNCSUSettingsManager.set_anncsu_repo(self.anncsu_base_url.text())
            # ANNCSUSettingsManager.set_municipality_code(municipality_data.anncsu_id)
            # ANNCSUSettingsManager.set_current_scope_id(self.current_session.currentText())
            # ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings saved.", "success")

        # just save current settings
        ANNCSUSettingsManager.set_geocoders_configs(self.geocodersTreeView.model().to_json())
        self.registerGeocoders()
        ANNCSUSettingsManager.set_anncsu_repo(self.anncsu_base_url.text())
        ANNCSUSettingsManager.set_municipality_code(municipality_data.anncsu_id)
        scopes = ANNCSUSettingsManager.get_scopes()
        scopes[self.current_session.currentText()] = current_scope
        ANNCSUSettingsManager.set_scopes(scopes)
        ANNCSUSettingsManager.set_current_scope_id(self.current_session.currentText())
        ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings saved.", "success")

    def reset_settings_to_default(self):
        """Set selections to defaults. Does not save."""
        ANNCSUSettingsManager.reset_all()
        self.set_settings_gui()
        self.manageSessionChange()
        ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings reset.", "info")

    # def on_finished_create_new_session(self, exception, result=None):
    #     """Callback when finished creating a new session."""
    #     self.create_new_session_task = None  # reset task reference
    #     self.feedback.progress_bar.hide()

    #     if exception is not None:
    #         ANNCSUMessageManager().show_message(
    #             f"Errore durante la creazione della nuova sessione: {str(exception)}",
    #             "error",
    #         )
    #         return

    #     # save new sesstion data
    #     new_scope_id, new_scope = result if result is not None else (None, None)
    #     if new_scope_id is None or new_scope is None:
    #         ANNCSUMessageManager().show_message(
    #             "Errore durante la creazione della nuova sessione: dati sessione non validi.",
    #             "error",
    #         )
    #         return
    #     print(f"New session created: {new_scope_id} -> {new_scope} ---- {result}")

    #     # add new session to combobox and set it as current
    #     new_scope.sync_changed.connect(self.update_sync_button_color)
    #     new_scope.sync_changed.emit()  # initial sync status
    #     self.current_session.addItem(new_scope_id, new_scope)
    #     self.current_session.setCurrentIndex(
    #         self.current_session.findText(new_scope_id)
    #     )

    #     # save settings
    #     municipality_data: MunicipalityData = self.comune_cb.currentData()
    #     ANNCSUSettingsManager.set_geocoders_configs(self.geocodersTreeView.model().to_json())
    #     self.registerGeocoders()
    #     ANNCSUSettingsManager.set_anncsu_repo(self.anncsu_base_url.text())
    #     ANNCSUSettingsManager.set_municipality_code(municipality_data.anncsu_id)
    #     ANNCSUSettingsManager.set_current_scope_id(self.current_session.currentText())
    #     ANNCSUMessageManager().show_message("ANNCSU QGIS Plugin settings saved.", "success")
