from pathlib import Path
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QProgressBar,
    QTextEdit,
    QLabel,
    QPushButton,
    QCheckBox
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.anncsu_wizard.wizard_evaluate_geocode_step import ANNCUGeocodeResultTab
from anncsu_manager.qgis_plugin_tools.tools.layers import load_dataframe_as_layer, remove_layer_by_name

FORM_CLASS: QWizardPage = load_ui("wizard_materialise_layers.ui")
class ANNCUWizardMaterialiseLayersStep(QWizardPage, FORM_CLASS):
    """Class container to save geocoded data from scope db to gpkg layers in the scope repo folder."""

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.materialize_layers_pb: QPushButton
        self.materialize_layers_pb.clicked.connect(self.meterialise_layers)
        self.progress_text: QTextEdit
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
        pass

    def meterialise_layers(self):
        """Materialize geocoding results layers into the selected Mergin project repo."""
        self.feedback.reset()

        # get local repo path of the current Scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes[current_scope_id] if current_scope_id in scopes else None
        self.feedback.pushInfo(self.tr("Using scope: {current_scope_id}").format(current_scope_id=current_scope_id))
        if not current_scope:
            self.feedback.reportError(self.tr("No scope is currently selected. Please select a scope in the settings before running geocoders."))
            return

        # get local repo folder where to save layers
        out_path = current_scope.get_local_repo_path()
        if not out_path or not Path(out_path).exists():
            self.feedback.reportError(self.tr("Scope local repo path '{out_path}' does not exist. Please check your scope settings.").format(out_path=out_path))
            return

        # collect all files to sync after added to the local repo
        files_to_sync: list[Path] = []

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
            self.feedback.pushInfo(self.tr("info: Preparing to add geocoding results for '{geocoder_name}' to local scope folder.").format(geocoder_name=geocoder_name))
            self.feedback.pushInfo(self.tr("info: Adding results into folder: {out_path}.").format(out_path=out_path))

            if self.include_geofence_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_geofence_polygon), level="info", duration=5)
                remove_layer_by_name(layer_geofence_polygon)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.geofence_polygon,
                    layer_name=layer_geofence_polygon,
                    column_types={},  # infer column types automatically
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Geofence polygon layer '{layer_geofence_polygon}' added to local git repo.").format(layer_geofence_polygon=layer_geofence_polygon))

                # add geofence polygon file to the list of files to sync
                geofence_file_path = Path(tab.geofenceLayer.source().split("|")[0])
                files_to_sync.append(geofence_file_path)

            if self.include_fails_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_fails), level="info", duration=5)
                remove_layer_by_name(layer_name_fails)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.fails,
                    layer_name=layer_name_fails,
                    column_types={},  # infer column types automatically
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Fails layer '{layer_name_fails}' added to local git repo.").format(layer_name_fails=layer_name_fails))

                # add fails file to the list of files to sync
                fails_file_path = Path(tab.geofenceLayer.source().split("|")[0])
                files_to_sync.append(fails_file_path)

            if self.include_out_of_geofence_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_out_of_geofence), level="info", duration=5)
                remove_layer_by_name(layer_name_out_of_geofence)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.out_of_geofence,
                    layer_name=layer_name_out_of_geofence,
                    column_types={},  # infer column types automatically
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Out of geofence layer '{layer_name_out_of_geofence}' added to local git repo.").format(layer_name_out_of_geofence=layer_name_out_of_geofence))

                # add out_of_geofence file to the list of files to sync
                out_of_geofence_file_path = Path(tab.geofenceLayer.source().split("|")[0])
                files_to_sync.append(out_of_geofence_file_path)

            if self.include_success_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_success), level="info", duration=5)
                remove_layer_by_name(layer_name_success)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.success,
                    layer_name=layer_name_success,
                    column_types={},  # infer column types automatically
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Success layer '{layer_name_success}' added to local git repo.").format(layer_name_success=layer_name_success))

                # add success file to the list of files to sync
                success_file_path = Path(tab.geofenceLayer.source().split("|")[0])
                files_to_sync.append(success_file_path)

            # sync all added files to the remote git repo of the current scope
            try:
                self.feedback.pushInfo(self.tr("info: Commit and push layers into git repo."))
                current_scope.sync(files_to_sync=files_to_sync)
            except Exception as e:
                raise QgsPluginException(f"Failed to sync geocoding results for geocoder '{geocoder_name}' to remote repo: {str(e)}") from e

            ANNCSUMessageManager().show_message(
                self.tr("Added results for geocoder '{geocoder_name}' into git repo.").format(geocoder_name=geocoder_name),
                level="success",
                duration=5
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

