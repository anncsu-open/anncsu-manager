from pathlib import Path
import re
from typing import Dict
from qgis.core import QgsProject, QgsVectorLayer
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

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager, ScopeData
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

import duckdb

# add Mergin dependcies but do not  trigger error if Mergin is not installed
# the reason is to allow to check Mergin installed during plugin loading in a
# controlled way
mergin_available: bool = False
try:
    from Mergin import utils as mergin_utils
    mergin_available = True
except ImportError:
    pass

FORM_CLASS: QWizardPage = load_ui("wizard_update_from_project.ui")
class ANNCUWizardUpdateFromProjectStep(QWizardPage, FORM_CLASS):
    """Class container to create project starting from results of geocodings."""

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.update_from_project_pb: QPushButton
        self.update_from_project_pb.clicked.connect(self.update_from_project)
        self.progress_text: QTextEdit
        self.mergin_project_cb: QComboBox
        self.include_fails_ckb: QCheckBox
        self.include_fails_ckb.setChecked(True)
        self.include_out_of_geofence_ckb: QCheckBox
        self.include_out_of_geofence_ckb.setChecked(True)
        self.include_success_ckb: QCheckBox
        self.include_success_ckb.setChecked(False)

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
        cur_project: QgsProject = QgsProject.instance()

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

    def update_from_project(self):
        """Update geocoded results in the current scope duckdb database with modified layers
        in the selected Mergin project or current QGIS project if no Mergin project is selected.
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

            # check if selected mergin project refers to the current loaded qgis project
            cur_project = QgsProject.instance()
            get_from_mergin_folder: bool = False
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

                # remember to get the files from folder and not from project
                get_from_mergin_folder = True

        # get current scope
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes: Dict[str, ScopeData] = ANNCSUSettingsManager.get_scopes()
        if current_scope_id not in scopes:
            self.feedback.reportError(self.tr("Current scope id '{current_scope_id}' not found among defined scopes.").format(current_scope_id=current_scope_id))
            return
        current_scope: ScopeData = scopes[current_scope_id]
        self.feedback.pushInfo(self.tr("Using scope: {current_scope_id}").format(current_scope_id=current_scope_id))
        print(f"Current scope: {current_scope}")

        duck_db_source = current_scope.to_dict().get("duckdb_path", "")
        if not duck_db_source:
            self.feedback.reportError(self.tr("No DuckDB database path found in the current scope settings."))
            return

        with duckdb.connect(duck_db_source) as scopedb:
            self.feedback.pushInfo(self.tr("Updating DuckDB database at {duck_db_source} from Mergin project '{project_name}'.").format(duck_db_source=duck_db_source, project_name=project_name))
            if scopedb is None:
                self.feedback.reportError(self.tr("Could not connect to DuckDB database at {duck_db_source}.").format(duck_db_source=duck_db_source))
                return

            # start transaction
            scopedb.execute("BEGIN;")
            try:
                # load statial extension
                scopedb.execute("INSTALL spatial;")
                scopedb.execute("LOAD spatial;")

                geocoders_configs = ANNCSUSettingsManager.get_geocoders_configs()
                for geocoder_name, geocoder_config in geocoders_configs.items():
                    # skip geocoder tables if not acitve
                    if geocoder_config.get("active", False) in [False, "False", "false"]:
                        self.feedback.pushInfo(self.tr("info: Skipping inactive geocoder '{geocoder_name}'.").format(geocoder_name=geocoder_name))
                        continue

                    # set default layer names for a specific geocoder
                    layer_name_success = f"{geocoder_name}_success"
                    layer_name_fails = f"{geocoder_name}_fails"
                    layer_name_out_of_geofence = f"{geocoder_name}_out_of_geofence"

                    # for all layers
                    layer_names = [layer_name_success, layer_name_fails, layer_name_out_of_geofence]
                    for layer_name in layer_names:
                        self.feedback.pushInfo(self.tr("info: Processing layer '{layer_name}' for geocoder '{geocoder_name}'.").format(layer_name=layer_name, geocoder_name=geocoder_name))

                        # get layer file related to layer name
                        layers = QgsProject.instance().mapLayersByName(layer_name)
                        if not layers or len(layers) == 0:
                            if not get_from_mergin_folder:
                                self.feedback.pushInfo(self.tr("warning: Layer '{layer_name}' not found in the project. Skipping.").format(layer_name=layer_name))
                                continue
                            # try to load layer from project folder
                            layer_path = out_path / f"{layer_name}.gpkg"
                            if not layer_path.exists():
                                self.feedback.pushInfo(self.tr("warning: Layer file '{layer_path}' not found in project folder. Skipping.").format(layer_path=layer_path))
                                continue
                            layer = QgsVectorLayer(str(layer_path), layer_name, "ogr")
                            if layer is None:
                                self.feedback.pushInfo(self.tr("warning: Could not load layer from file '{layer_path}'. Skipping.").format(layer_path=layer_path))
                                continue
                            layers = [layer]
                            self.feedback.pushInfo(self.tr("info: Loaded layer '{layer_name}' from project folder.").format(layer_name=layer_name))
                        layer = layers[0]
                        layer_path = layer.source()

                        # dump geodataframe into duckdb table that has the same name of the layer
                        # the below code drop table and rebuild it assuming the structure is the same
                        table_name = f"{layer_name}"

                        # validate geocoder name to be used as table name in duckdb to
                        # avoid SQL injection and syntax errors
                        # if not valid break the loop and do not proceed with update from project
                        if not re.match(r"^[a-zA-Z_]\w*$", table_name):
                            self.feedback.reportError(self.tr("Invalid geocoder name: '{table_name}'. Skipping.").format(table_name=table_name))
                            return

                        # TODO: improve the code to be generic instead of hardcoding columns
                        scopedb.execute(f"""CREATE OR REPLACE TABLE "{table_name}" AS SELECT * FROM st_read('{layer_path}');""")  # nosec B608
                        # trick to force geom to be correct wkb that be read back from shapely and tobe recognized as geometry 
                        # by duckdb seems that st_read leave the geometry as that as defined in sqlite with
                        # srid header but then duckdb spatial extension does not recognize it as geometry and
                        # shapely wkb does not read it properly, so we need to convert it to wkb with st_aswkb")
                        try:
                            scopedb.execute(f"""CREATE OR REPLACE TABLE "{table_name}" AS SELECT * EXCLUDE(geom), ST_GeomFromWKB(geom) AS geom FROM "{table_name}";""")  # nosec B608
                        except Exception:  # nosec B110 - intentionally pass
                            # in case no geom column is present or geom column is already in WKB format just ignore and keep original table
                            pass
                        # drop the autogenerated id column if exists
                        try:
                            scopedb.execute(f"""ALTER TABLE "{table_name}" DROP COLUMN id;""")
                        except Exception:  # nosec B110 - intentionally pass
                            pass
                        self.feedback.pushInfo(self.tr("info: Dumped layer '{layer_name}' into DuckDB table '{table_name}' with {count} records.").format(layer_name=layer_name, table_name=table_name, count=layer.featureCount()))

                # add table from project if exists
                geocoded_anncsu_path = out_path / "geocoded_anncsu.gpkg"
                geocoded_anncsu_layer_name = "geocoded_anncsu"
                if geocoded_anncsu_path.exists():
                    # load layer just to count features
                    layer = QgsVectorLayer(str(geocoded_anncsu_path), geocoded_anncsu_layer_name, "ogr")
                    scopedb.execute(f"""CREATE OR REPLACE TABLE "geocoded_anncsu" AS SELECT * FROM st_read('{geocoded_anncsu_path}');""")  # nosec B608
                    # trick to force geom to be correct wkb that be read back from shapely
                    # and to be recognized as geometry by duckdb
                    # seems that st_read leave the geometry as that as defined in sqlite with srid header
                    # but then duckdb spatial extension does not recognize it as geometry and shapely wkb does not read it properly,
                    # so we need to convert it to wkb with st_aswkb
                    try:
                        scopedb.execute("CREATE OR REPLACE TABLE geocoded_anncsu AS SELECT * EXCLUDE(geom), ST_GeomFromWKB(geom) AS geom FROM geocoded_anncsu;")
                    except Exception:  # nosec B110 - intentionally pass
                        # in case no geom column is present or geom column is already in WKB format just ignore and keep original table
                        pass
                    # drop the autogenerated id column if exists
                    try:
                        scopedb.execute("ALTER TABLE geocoded_anncsu DROP COLUMN id;")
                    except Exception:  # nosec B110 - intentionally pass
                        pass
                    self.feedback.pushInfo(self.tr("info: Dumped layer 'geocoded_anncsu' into DuckDB table 'geocoded_anncsu' with {count} records.").format(count=layer.featureCount()))
                else:
                    self.feedback.pushInfo(self.tr("info: 'geocoded_anncsu.gpkg' file not found in Mergin project folder. Skipping."))

            except Exception as e:
                scopedb.execute("ROLLBACK;")
                self.feedback.reportError(self.tr("Error while updating from project: {error}").format(error=str(e)))
                return
            else:
                scopedb.execute("COMMIT;")

        # reopen duckdb to consolidate changes
        with duckdb.connect(duck_db_source) as scopedb:
            self.feedback.pushInfo(self.tr("info: Reopened DuckDB database to consolidate changes."))
            scopedb.execute("PRAGMA force_checkpoint;")
            scopedb.execute("CHECKPOINT;")

        self.feedback.pushInfo(self.tr("info: Update from project completed successfully."))

        # notify to sync the scope folder to push changes to server
        current_scope.syncked = False
        current_scope.sync_changed.emit()
        self.feedback.pushInfo(self.tr("warning:  Scope repo locally updated need to be synched to remote repo."))


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

