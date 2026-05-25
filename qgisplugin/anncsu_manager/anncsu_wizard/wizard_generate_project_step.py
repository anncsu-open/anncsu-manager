import math
from pathlib import Path

import shapely
from qgis.core import (
    QgsProject,
    QgsDefaultValue
)
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

from anncsu_manager.utils.misc_utils import tuple_to_dataframe
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.anncsu_wizard.wizard_evaluate_geocode_step import ANNCUGeocodeResultTab
from anncsu_manager.qgis_plugin_tools.tools.layers import load_dataframe_as_layer, remove_layer_by_name

# add Mergin dependencies but do not  trigger error if Mergin is not installed
# the reason is to allow to check Mergin installed during plugin loading in a
# controlled way
mergin_available = False
try:
    from Mergin import utils as mergin_utils
    mergin_available = True
except ImportError:
    pass

FORM_CLASS: QWizardPage = load_ui("wizard_generate_project_page.ui")
class ANNCUWizardGenerateProjectStep(QWizardPage, FORM_CLASS):
    """Class container to create mergin project starting from resuls of geocodings."""

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.add_to_project_pb: QPushButton
        self.add_to_project_pb.clicked.connect(self.add_to_project)
        self.progress_text: QTextEdit
        self.mergin_project_cb: QComboBox
        if not mergin_available:
            self.mergin_project_cb.setEnabled(False)
        self.include_fails_ckb: QCheckBox
        self.include_fails_ckb.setChecked(True)
        self.include_out_of_geofence_ckb: QCheckBox
        self.include_out_of_geofence_ckb.setChecked(True)
        self.include_success_ckb: QCheckBox
        self.include_success_ckb.setChecked(False)
        self.include_geofence_ckb: QCheckBox
        self.include_geofence_ckb.setChecked(False)
        self.include_geocoded_ckb: QCheckBox
        self.include_geocoded_ckb.setChecked(True)

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
        if mergin_available:
            self.populate_mergin_projects()
            self.set_mergin_project()

    def populate_mergin_projects(self):
        """Populate Mergin projects combobox."""
        mergin_projects = mergin_utils.get_local_mergin_projects_info()

        self.mergin_project_cb.clear()
        self.mergin_project_cb.addItem(self.tr("-- Select Mergin Project --"), None)
        for mergin_project in mergin_projects:
            path, workspace, project_name, project_server = mergin_project
            self.mergin_project_cb.addItem(project_name, mergin_project)
            self.feedback.pushInfo(self.tr("info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.").format(project_name=project_name, workspace=workspace, path=path, project_server=project_server))

    def set_mergin_project(self):
        """Populate Mergin projects combobox."""
        mergin_projects = mergin_utils.get_local_mergin_projects_info()

        # if not mergin_projects then ask to setting up one before to proceed
        if not mergin_projects:
            ANNCSUMessageManager().show_message(
                self.tr("No local Mergin project found. Configure Mergin before proceeding."),
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
                    self.feedback.pushInfo(self.tr("info: Current QGIS project '{cur_project}' matches Mergin project '{project_name}'.").format(cur_project=cur_project.baseName(), project_name=project_name))
                    self.mergin_project_cb.setCurrentIndex(index)
                else:
                    self.mergin_project_cb.setCurrentIndex(0)
                break

    def add_to_project(self):
        """Add layers to the selected Mergin project or to the
        current loaded project if no Mergin project is selected.
        """
        cur_project: QgsProject = QgsProject.instance()
        if not mergin_available or self.mergin_project_cb.currentData() is None:
            out_path = cur_project.homePath()
            if out_path == "":
                ANNCSUMessageManager().show_message(
                    self.tr("Current project does not have a valid home path. Please save the project before proceeding."),
                    "error",
                )
                return
            out_path = Path(out_path)
            project_name = cur_project.baseName()
        else:
            # get  select mergin project to get folder where to save results
            mergin_project_data = self.mergin_project_cb.currentData()
            if mergin_project_data is None:
                ANNCSUMessageManager().show_message(
                    self.tr("Select a valid Mergin project before proceeding."),
                    "error",
                )
                return
            
            # get mergin project info
            path, workspace, project_name, project_server = mergin_project_data
            out_path = Path(path)

            # check if selected mergin project refer to the current loaded qgis project
            if project_name != cur_project.baseName():
                # ask user to confirm to proceed anyway
                reply = QMessageBox.question(
                    self,
                    self.tr("Continue saving?"),
                    self.tr("The selected Mergin project '{project_name}' does not match the open QGIS project '{cur_project}'. Proceed anyway?").format(project_name=project_name, cur_project=cur_project.baseName()),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

        # load anncsu table from DB to join with each geocoder results
        anncsu_records, columns = ANNCSUSettingsManager.get_table(table_name="anncsu")
        if anncsu_records is None:
            ANNCSUMessageManager().show_message(
                self.tr("Unable to load the ANNCSU table. Make sure the table is available before proceeding."),
                "error",
            )
            return

        # remove columns introduced by the plugin named "PLUGIN_*"
        anncsu_df = tuple_to_dataframe(anncsu_records, columns)
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
            layer_geofence_polygon = "geofence_polygon"

            # add before layer_geofence_polygon to remain under the other layers
            self.feedback.pushInfo(self.tr("info: Preparing to add geocoding results for '{geocoder_name}' to project '{project_name}'.").format(geocoder_name=geocoder_name, project_name=project_name))
            self.feedback.pushInfo(self.tr("info: Adding results into folder: {out_path}.").format(out_path=out_path))

            if self.include_geofence_ckb.isChecked():
                # avoid to add layer with same name multiple times checking if layer is
                # already in the qgis project
                if QgsProject.instance().mapLayersByName(layer_geofence_polygon) == []:
                    ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_geofence_polygon), level="info", duration=5)
                    remove_layer_by_name(layer_geofence_polygon)
                    tab.geofenceLayer = load_dataframe_as_layer(
                        dataframe=tab.geofence_polygon,
                        layer_name=layer_geofence_polygon,
                        column_types={},
                        geometry_column="geom",
                        crs_epsg=4326,  # assuming WGS84, adjust as needed
                        out_path=out_path  # save in current local repo
                    )
                    self.feedback.pushInfo(self.tr("info: Geofence polygon layer '{layer_geofence_polygon}' added to project '{project_name}'.").format(layer_geofence_polygon=layer_geofence_polygon, project_name=project_name))

            if self.include_success_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_success), level="info", duration=5)
                remove_layer_by_name(layer_name_success)

                # merge geocoded results with anncsu table
                merged_success_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.success,
                    anncsu_dataframe=anncsu_df
                )
                if merged_success_df is None:
                    self.feedback.pushInfo(self.tr("error: Unable to merge geocoded results with anncsu table for geocoder '{geocoder_name}'. Skipping saving success layer.").format(geocoder_name=geocoder_name))
                    continue

                 # load merged success dataframe as layer into qgis and save into project folder
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_success_df,
                    layer_name=layer_name_success,
                    column_types={},
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Success layer '{layer_name_success}' added to project '{project_name}'.").format(layer_name_success=layer_name_success, project_name=project_name))

            if self.include_fails_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_fails), level="info", duration=5)
                remove_layer_by_name(layer_name_fails)

                # merge fails results with anncsu table
                merged_fails_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.fails,
                    anncsu_dataframe=anncsu_df
                )
                if merged_fails_df is None:
                    self.feedback.pushInfo(self.tr("error: Unable to merge fails results with anncsu table for geocoder '{geocoder_name}'. Skipping saving fails layer.").format(geocoder_name=geocoder_name))
                    continue

                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_fails_df,
                    layer_name=layer_name_fails,
                    column_types={},
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Fails layer '{layer_name_fails}' added to project '{project_name}'.").format(layer_name_fails=layer_name_fails, project_name=project_name))

            if self.include_out_of_geofence_ckb.isChecked():
                ANNCSUMessageManager().show_message(self.tr("Loading: {layer_name}").format(layer_name=layer_name_out_of_geofence), level="info", duration=5)
                remove_layer_by_name(layer_name_out_of_geofence)

                # merge out of geofence results with anncsu table
                merged_out_of_geofence_df = ANNCSUSettingsManager.merge_geocoded_with_anncsu_dataframe(
                    geocoded_dataframe=tab.out_of_geofence,
                    anncsu_dataframe=anncsu_df
                )
                if merged_out_of_geofence_df is None:
                    self.feedback.pushInfo(self.tr("error: Unable to merge out of geofence results with anncsu table for geocoder '{geocoder_name}'. Skipping saving out of geofence layer.").format(geocoder_name=geocoder_name))
                    continue

                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=merged_out_of_geofence_df,
                    layer_name=layer_name_out_of_geofence,
                    column_types={},
                    geometry_column="geom",
                    crs_epsg=4326,  # assuming WGS84, adjust as needed
                    out_path=out_path  # save in current local repo
                )
                self.feedback.pushInfo(self.tr("info: Out of geofence layer '{layer_name_out_of_geofence}' added to project '{project_name}'.").format(layer_name_out_of_geofence=layer_name_out_of_geofence, project_name=project_name))

            ANNCSUMessageManager().show_message(
                self.tr("Added results for geocoder '{geocoder_name}' into project '{project_name}'.").format(geocoder_name=geocoder_name, project_name=project_name),
                level="success",
                duration=5
            )

        if self.include_geocoded_ckb.isChecked():
            # get geocoded_anncsu dataframe from DB if aleady present due to previous editing sessions
            # or set it from scratch as copy of anncsu table
            geocoded_anncsu_records, geocoded_anncsu_columns = ANNCSUSettingsManager.get_table(table_name="geocoded_anncsu")
            if geocoded_anncsu_records is None:
                # create a copy of anncsu_df to update with best geocode results
                geocoded_anncsu_df = anncsu_df.copy()
                geocoded_anncsu_df['PLUGIN_SCORE'] = None
                geocoded_anncsu_df['PLUGIN_GEOCODER'] = None
                geocoded_anncsu_df['geom'] = None

                # align geocoded_anncsu_column_types with anncsu_column_types and add new columns
                # geocoded_anncsu_column_types = anncsu_column_types.copy()
                # geocoded_anncsu_column_types['PLUGIN_SCORE'] = 'float64'
                # geocoded_anncsu_column_types['PLUGIN_GEOCODER'] = 'string'
                # geocoded_anncsu_column_types['geom'] = 'geom'
            else:
                geocoded_anncsu_df = tuple_to_dataframe(list_of_tuples=geocoded_anncsu_records, columns=geocoded_anncsu_columns) if geocoded_anncsu_records is not None else None

            # cast SCORE to float
            if 'PLUGIN_SCORE' in geocoded_anncsu_df.columns:
                geocoded_anncsu_df['PLUGIN_SCORE'] = geocoded_anncsu_df['PLUGIN_SCORE'].astype(float)
            else:
                geocoded_anncsu_df['PLUGIN_SCORE'] = None
            if 'PLUGIN_GEOCODER' not in geocoded_anncsu_df.columns:
                geocoded_anncsu_df['PLUGIN_GEOCODER'] = None
            if 'geom' not in geocoded_anncsu_df.columns:
                geocoded_anncsu_df['geom'] = None

            # cast COORD_X_COMUNE and COORD_Y_COMUNE to float
            # that is STR f it is loaded from table geocoded_anncsu instead of clone from anncsu_df
            geocoded_anncsu_df['COORD_X_COMUNE'] = geocoded_anncsu_df['COORD_X_COMUNE'].astype(float)
            geocoded_anncsu_df['COORD_Y_COMUNE'] = geocoded_anncsu_df['COORD_Y_COMUNE'].astype(float)

            # create a geocoded_anncsu table getting the geocode result from that with highest score for
            # each record in anncsu table OR mantain the geocoded record if alreay present in anncsu table
            for index, row in enumerate(geocoded_anncsu_df.itertuples()):
                address_id = row.PROGRESSIVO_ACCESSO
                road_id = row.PROGRESSIVO_NAZIONALE

                # if already geocoded, mantain geocodig source and score
                if row.COORD_X_COMUNE is not None and row.COORD_Y_COMUNE is not None:
                    # manage if nan
                    if not math.isnan(row.COORD_X_COMUNE) and not math.isnan(row.COORD_Y_COMUNE):
                        # if source is annscu an not geocoder set it as "ANNCSU" and score to 1.0
                        # e.g. source of coords is the ground truth and not a geocoder result
                        if row.PLUGIN_GEOCODER is None:
                            geocoded_anncsu_df.loc[index, 'PLUGIN_SCORE'] = 1.0
                            geocoded_anncsu_df.loc[index, 'PLUGIN_GEOCODER'] = "ANNCSU"
                            geocoded_anncsu_df.loc[index, 'geom'] = shapely.geometry.Point(row.COORD_X_COMUNE, row.COORD_Y_COMUNE)
                        continue

                # find best geocode result among all geocoders tabs if the address has not been already geocoded
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
                    geocoded_anncsu_df.loc[index, 'COORD_X_COMUNE'] = float(best_result["longitude"])
                    geocoded_anncsu_df.loc[index, 'COORD_Y_COMUNE'] = float(best_result["latitude"])
                    geocoded_anncsu_df.loc[index, 'PLUGIN_SCORE'] = float(best_result["score"])
                    geocoded_anncsu_df.loc[index, 'PLUGIN_GEOCODER'] = best_geocoder_name
                    geocoded_anncsu_df.loc[index, 'geom'] = best_result["geom"]

            # save geocoded_anncsu_df as GPKG file into project folder
            ANNCSUMessageManager().show_message(
                self.tr("Saving geocoded ANNCSU table into project '{project_name}'.").format(project_name=project_name),
                level="info",
                duration=5
            )
            remove_layer_by_name("geocoded_anncsu")
            load_dataframe_as_layer(
                dataframe=geocoded_anncsu_df,
                layer_name="geocoded_anncsu",
                column_types={},
                geometry_column="geom",
                crs_epsg=4326,  # assuming WGS84, adjust as needed
                out_path=out_path  # save in current local repo
            )

            # setup default values for repetetive columns in geocoded_anncsu to facilitate manual editing
            self.setup_default_values_for_geocoded_anncsu()

    def setup_default_values_for_geocoded_anncsu(self):
        """This function sets up default QGIS form values for the geocoded_anncsu layer."""
        # get layer named "geocoded_anncsu"
        layer = QgsProject.instance().mapLayersByName("geocoded_anncsu")
        if not layer:
            return
        layer = layer[0]

        # for each field set default value from the previous record value for a set of columns
        field_names = [
            "PLUGIN_COMUNE",
            "PLUGIN_PROVINCIA",
            "PLUGIN_REGIONE",
            "CODICE_COMUNE",
            "CODICE_ISTAT",
            "CODICE_COMUNALE",
        ]
        for field in field_names:
            default_value = QgsDefaultValue()
            default_value.setApplyOnUpdate(True)  # do not allow modification of default value
            default_value.setExpression(f"attribute(get_feature_by_id(@layer, maximum(@id)), '{field}')")
            field_index = layer.fields().indexFromName(field)

            # Set the default value for the specific field
            layer.setDefaultValueDefinition(field_index, default_value)

        # set default value for PLUGIN_SCORE and PLUGIN_GEOCODER
        score_default_value = QgsDefaultValue()
        score_default_value.setExpression("0.99")
        score_field_index = layer.fields().indexFromName("PLUGIN_SCORE")

        layer.setDefaultValueDefinition(score_field_index, score_default_value)
        geocoder_default_value = QgsDefaultValue()
        geocoder_default_value.setExpression("'MANUAL'")
        geocoder_field_index = layer.fields().indexFromName("PLUGIN_GEOCODER")
        layer.setDefaultValueDefinition(geocoder_field_index, geocoder_default_value)

        # set "COORD_X_COMUNE", "COORD_Y_COMUNE" from geom if not already set
        x_default_value = QgsDefaultValue()
        x_default_value.setApplyOnUpdate(True)
        x_default_value.setExpression("x($geometry)")
        x_field_index = layer.fields().indexFromName("COORD_X_COMUNE")
        layer.setDefaultValueDefinition(x_field_index, x_default_value)

        y_default_value = QgsDefaultValue()
        y_default_value.setApplyOnUpdate(True)
        y_default_value.setExpression("y($geometry)")
        y_field_index = layer.fields().indexFromName("COORD_Y_COMUNE")
        layer.setDefaultValueDefinition(y_field_index, y_default_value)

        # set rundom negative values for "PROGRESSIVO_ACCESSO" and "PROGRESSIVO_NAZIONALE" to avoid
        # conflicts with existing values during editing
        accesso_default_value = QgsDefaultValue()
        accesso_default_value.setExpression("rand(-100000, -1)")
        accesso_field_index = layer.fields().indexFromName("PROGRESSIVO_ACCESSO")
        layer.setDefaultValueDefinition(accesso_field_index, accesso_default_value)

        nazionale_default_value = QgsDefaultValue()
        nazionale_default_value.setExpression("rand(-100000, -1)")
        nazionale_field_index = layer.fields().indexFromName("PROGRESSIVO_NAZIONALE")
        layer.setDefaultValueDefinition(nazionale_field_index, nazionale_default_value)

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

