from pathlib import Path
from qgis.utils import iface
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QProgressBar,
    QTextEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QMessageBox
)

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.anncsu_wizard.wizard_evaluate_geocode_step import ANNCUGeocodeResultTab
from anncsu_manager.qgis_plugin_tools.tools.layers import load_dataframe_as_layer, remove_layer_by_name

# add Mergin dependcies but do not  trigger error if Mergin is not installed
# the reason is to allow to check Mergin installed during plugin loading in a
# controlled way
try:
    from Mergin import utils as mergin_utils
except ImportError:
    pass

FORM_CLASS: QWizardPage = load_ui("wizard_generate_mergin_page.ui")
class ANNCUWizardGenerateMerginStep(QWizardPage, FORM_CLASS):
    """Class container to create mergin project starting from resuls of geocodings."""

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.add_to_mergin_pb: QPushButton
        self.add_to_mergin_pb.clicked.connect(self.add_to_mergin)
        self.progress_text: QTextEdit
        self.mergin_project_cb: QComboBox
        self.include_fails_ckb: QCheckBox
        self.include_fails_ckb.setChecked(True)
        self.include_out_of_geofence_ckb: QCheckBox
        self.include_out_of_geofence_ckb.setChecked(True)
        self.include_success_ckb: QCheckBox
        self.include_success_ckb.setChecked(False)
        self.include_geofence_ckb: QCheckBox
        self.include_geofence_ckb.setChecked(False)

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
        self.populate_mergin_projects()
        self.set_mergin_project()

    def populate_mergin_projects(self):
        """Populate Mergin projects combobox."""
        mergin_projects = mergin_utils.get_local_mergin_projects_info()

        self.mergin_project_cb.clear()
        self.mergin_project_cb.addItem("-- Seleziona Progetto Mergin --", None)
        for mergin_project in mergin_projects:
            path, workspace, project_name, project_server = mergin_project
            self.mergin_project_cb.addItem(project_name, mergin_project)
            self.feedback.pushInfo(f"info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.")

    def set_mergin_project(self):
        """Populate Mergin projects combobox."""
        mergin_projects = mergin_utils.get_local_mergin_projects_info()

        # if not mergin_projects then ask to setting up one before to proceed
        if not mergin_projects:
            ANNCSUMessageManager().show_message(
                "Nessun progetto Mergin locale trovato. Configurare Mergin prima di procedere.",
                "error",
            )

        # infer what is the current mergin project reading the current loaded project
        # and checking if it is among local mergin projects
        # then setup current configured project in the combobox
        cur_project = QgsProject.instance()

        # check if qgis project is among local mergin projects
        for path, workspace, project_name, project_server in mergin_projects:
            if project_name == cur_project.baseName():
                index = self.mergin_project_cb.findText(project_name)
                if index != -1:
                    self.feedback.pushInfo(f"info: Current QGIS project '{cur_project.baseName()}' matches Mergin project '{project_name}'.")
                    self.mergin_project_cb.setCurrentIndex(index)
                else:
                    self.mergin_project_cb.setCurrentIndex(0)
                break
        # if self.mergin_project_cb.currentData() is None:
        #     ANNCSUMessageManager().show_message(
        #         "Nessun progetto Mergin aperto. Aprirne uno prima di salvare.",
        #         "error",
        #     )

    def add_to_mergin(self):
        # get  select mergin project to get folder where to save results
        mergin_project_data = self.mergin_project_cb.currentData()
        if mergin_project_data is None:
            ANNCSUMessageManager().show_message(
                "Selezionare un progetto Mergin valido prima di procedere.",
                "error",
            )
            return
        
        # get mergin project info
        path, workspace, project_name, project_server = mergin_project_data
        out_path = Path(path)

        # check if selected mergin project refer to the current loaded qgis project
        cur_project = QgsProject.instance()
        if project_name != cur_project.baseName():
            # ask user to confirm to proceed anyway
            reply = QMessageBox.question(
                self,
                "Contnua il salvataggio?",
                f"Il progetto Mergin selezionato '{project_name}' non corrisponde al progetto QGIS aperto '{cur_project.baseName()}'. Procedere comunque?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # load anncsu table from DB to join with each geocoder results
        anncsu_df = ANNCSUSettingsManager.get_anncsu_table_dataframe()
        if anncsu_df is None:
            ANNCSUMessageManager().show_message(
                "Impossibile caricare la tabella ANNCSU. Assicurarsi che la tabella sia disponibile prima di procedere.",
                "error",
            )
            return

        # remove columns intrudiced by the plugin named "PLUGIN_*"
        anncsu_df = anncsu_df.loc[:, ~anncsu_df.columns.str.startswith("PLUGIN_")]

        # for each geocode tab in the related page of the parent ANNCSUWizardManager
        parent_wizard = self.wizard()
        geocode_page = parent_wizard.page(parent_wizard.evaluate_geocode_page_id)

        for i in range(geocode_page.geocoders_tabs.count()):
            tab: ANNCUGeocodeResultTab = geocode_page.geocoders_tabs.widget(i)
            geocoder_name = geocode_page.geocoders_tabs.tabText(i)
            layer_name_success = f"{geocoder_name}_success"
            layer_name_fails = f"{geocoder_name}_fails"
            layer_name_out_of_geofence = f"{geocoder_name}_out_of_geofence"
            layer_geofence_polygon = f"{geocoder_name}_geofence_polygon"

            # add before layer_geofence_polygon to remain under the other layers
            self.feedback.pushInfo(f"info: Preparing to add geocoding results for '{geocoder_name}' to Mergin project '{project_name}'.")
            self.feedback.pushInfo(f"info: Adding results into folder: {out_path}.")

            if self.include_geofence_ckb.isChecked():
                ANNCSUMessageManager().show_message(f"Loading: {layer_geofence_polygon}", level="info", duration=5)
                remove_layer_by_name(layer_geofence_polygon)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.geofence_polygon,
                    layer_name=layer_geofence_polygon,
                    geometry_column="geometry",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current Mergin local repo
                )
                self.feedback.pushInfo(f"info: Geofence polygon layer '{layer_geofence_polygon}' added to Mergin project '{project_name}'.")

            if self.include_success_ckb.isChecked():
                ANNCSUMessageManager().show_message(f"Loading: {layer_name_success}", level="info", duration=5)
                remove_layer_by_name(layer_name_success)

                # merge geocoded results with anncsu table
                merged_success_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.success,
                    anncsu_dataframe=anncsu_df
                )
                if merged_success_df is None:
                    self.feedback.pushInfo(f"error: Unable to merge geocoded results with anncsu table for geocoder '{geocoder_name}'. Skipping saving success layer.")
                    continue

                 # load merged success dataframe as layer into qgis and save into mergin project folder
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_success_df,
                    layer_name=layer_name_success,
                    geometry_column="geometry",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current Mergin local repo
                )
                self.feedback.pushInfo(f"info: Success layer '{layer_name_success}' added to Mergin project '{project_name}'.")

            if self.include_fails_ckb.isChecked():
                ANNCSUMessageManager().show_message(f"Loading: {layer_name_fails}", level="info", duration=5)
                remove_layer_by_name(layer_name_fails)

                # merge fails results with anncsu table
                merged_fails_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.fails,
                    anncsu_dataframe=anncsu_df
                )
                if merged_fails_df is None:
                    self.feedback.pushInfo(f"error: Unable to merge fails results with anncsu table for geocoder '{geocoder_name}'. Skipping saving fails layer.")
                    continue

                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_fails_df,
                    layer_name=layer_name_fails,
                    geometry_column="geometry",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current Mergin local repo
                )
                self.feedback.pushInfo(f"info: Fails layer '{layer_name_fails}' added to Mergin project '{project_name}'.")

            if self.include_out_of_geofence_ckb.isChecked():
                ANNCSUMessageManager().show_message(f"Loading: {layer_name_out_of_geofence}", level="info", duration=5)
                remove_layer_by_name(layer_name_out_of_geofence)

                # merge out of geofence results with anncsu table
                merged_out_of_geofence_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.out_of_geofence,
                    anncsu_dataframe=anncsu_df
                )
                if merged_out_of_geofence_df is None:
                    self.feedback.pushInfo(f"error: Unable to merge out of geofence results with anncsu table for geocoder '{geocoder_name}'. Skipping saving out of geofence layer.")
                    continue

                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_out_of_geofence_df,
                    layer_name=layer_name_out_of_geofence,
                    geometry_column="geometry",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current Mergin local repo
                )
                self.feedback.pushInfo(f"info: Out of geofence layer '{layer_name_out_of_geofence}' added to Mergin project '{project_name}'.")

            ANNCSUMessageManager().show_message(
                f"Added results for geocoder '{geocoder_name}' into Mergin project '{project_name}'.",
                level="success",
                duration=5
            )

        # create a copy of anncsu_df to update with best geocode results
        geocoded_anncsu_df = anncsu_df.copy()
        geocoded_anncsu_df['PLUGIN_SCORE'] = None
        geocoded_anncsu_df['PLUGIN_GEOCODER'] = None
        geocoded_anncsu_df['geometry'] = None

        # create a gocoded_anncsu table getting the geocode result from that with highest score for
        # each record in anncsu table
        for row in geocoded_anncsu_df.itertuples():
            address_id = row.PROGRESSIVO_ACCESSO
            road_id = row.PROGRESSIVO_NAZIONALE
            # find best geocode result among all geocoders tabs
            best_result = None
            best_geocoder_name = None
            best_score = -1
            for i in range(geocode_page.geocoders_tabs.count()):
                tab: ANNCUGeocodeResultTab = geocode_page.geocoders_tabs.widget(i)
                geocoder_name = geocode_page.geocoders_tabs.tabText(i)

                # get result only from success dataframe
                success_df = tab.success
                record = success_df[(success_df["address_id"] == address_id) & (success_df["road_id"] == road_id)]
                if not record.empty:
                    score = record.iloc[0]["score"]
                    if score > best_score:
                        best_score = score
                        best_result = record.iloc[0]
                        best_geocoder_name = geocoder_name

            if best_result is not None:
                # set geocode result from best_result to anncsu_df
                index = geocoded_anncsu_df.index[geocoded_anncsu_df["PROGRESSIVO_ACCESSO"] == address_id].tolist()[0]
                geocoded_anncsu_df.loc[index, 'COORD_X_COMUNE'] = best_result["longitude"]
                geocoded_anncsu_df.loc[index, 'COORD_Y_COMUNE'] = best_result["latitude"]
                geocoded_anncsu_df.loc[index, 'PLUGIN_SCORE'] = best_result["score"]
                geocoded_anncsu_df.loc[index, 'PLUGIN_GEOCODER'] = best_geocoder_name
                geocoded_anncsu_df.loc[index, 'geometry'] = best_result["geometry"]

        # save geocoded_anncsu_df as GPKG file into mergin project folder
        ANNCSUMessageManager().show_message(
            f"Saving geocoded ANNCSU table into Mergin project '{project_name}'.",
            level="info",
            duration=5
        )
        remove_layer_by_name("geocoded_anncsu")
        load_dataframe_as_layer(
            dataframe=geocoded_anncsu_df,
            layer_name="geocoded_anncsu",
            geometry_column="geometry",
            crs_epsg=4326,  # assuming WGS84, adjust as needed
            out_path=out_path  # save in current Mergin local repo
        )

    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)

    def update_feedback_text(self, text: str):
        if "success: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="success", duration=5)
        elif "info:" in text.lower():
            pass
        elif "warning:" in text.lower():
            ANNCSUMessageManager().show_message(text, level="warning", duration=5)
        elif "invalid: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="invalid", duration=10)
        elif "error:" in text.lower():
            ANNCSUMessageManager().show_message(text, level="error", duration=0)

        if self.feedback.text_edit is not None:
            if isinstance(self.feedback.text_edit, QTextEdit):
                self.feedback.text_edit.append(text)
            elif isinstance(self.feedback.text_edit, QLabel):
                self.feedback.text_edit.setText(text)

