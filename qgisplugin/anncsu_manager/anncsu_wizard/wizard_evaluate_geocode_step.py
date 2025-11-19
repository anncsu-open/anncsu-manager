import geopandas
from qgis.utils import iface
from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QTabWidget,
    QProgressBar,
    QTextEdit,
    QWidget,
    QLabel,
    QTableView,
    QPushButton,
)
from qgis.PyQt.QtCore import QSortFilterProxyModel

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.qgis_plugin_tools.tools.exceptions import QgsPluginException
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback
from anncsu_manager.qgis_plugin_tools.tools.models import GeocodeResultDataFrameModel
from anncsu_manager.qgis_plugin_tools.tools.layers import load_dataframe_as_layer, remove_layer_by_name

import duckdb

FORM_CLASS_TAB: QWidget = load_ui("geocode_results_tab.ui")
class ANNCUGeocodeResultTab(QWidget, FORM_CLASS_TAB):
    """Class container for the results of geocoding for a specific geocoder."""

    def __init__(self,
                 parent=None,
                 scopedb: duckdb.DuckDBPyConnection = None,
                 result_table_name: str = "",
                 geocoder_config: dict = {},
                 feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.scopedb = scopedb
        self.result_table_name = result_table_name
        self.geocoder_config = geocoder_config

        # setup UI elements
        self.feedback = feedback
        self.geocodes_tv: QTableView
        self.statistics_geocode_score: QLabel
        self.statistics_num_of_records: QLabel
        self.statistics_num_of_success: QLabel
        self.statistics_num_of_fails: QLabel
        self.statistics_num_of_out_of_geofence: QLabel

        # load results
        self.geofence_polygon = geopandas.GeoDataFrame
        self.results: geopandas.GeoDataFrame
        self.success: geopandas.GeoDataFrame
        self.fails: geopandas.GeoDataFrame
        self.out_of_geofence: geopandas.GeoDataFrame
        self.successLayer: QgsVectorLayer
        self.failsLayer: QgsVectorLayer
        self.outOfGeofenceLayer: QgsVectorLayer
        self.load_results()
    
    def load_results(self):
        """Load geocoding results from the database and display them in the text edit."""
        try:
            # display results basing on configured threshold
            success_score_threshold = self.geocoder_config.get("threshold", 0.88)

            # get geocoded result as GeoDataFrame and to do this have to convert internal spatial format to WKT
            results_df = self.scopedb.execute(f"SELECT *, ST_AsText(geometry) as newgeom FROM {self.result_table_name};").df()
            results_df.drop(columns=["geometry"], inplace=True)
            results_df.rename(columns={"newgeom": "geometry"}, inplace=True)
            results_df['geometry'] = geopandas.GeoSeries.from_wkt(results_df['geometry'])
            self.results = geopandas.GeoDataFrame(results_df, geometry='geometry', crs="EPSG:4326")

            # show results in table view
            # passed threshold will be use dot set background color for score values
            model = GeocodeResultDataFrameModel(self.results, score_threshold=success_score_threshold)

            # enable sort of the table view
            proxyModel = QSortFilterProxyModel()
            proxyModel.setSourceModel(model)
            proxyModel.setSortRole(GeocodeResultDataFrameModel.SortRole)

            # show the table
            self.geocodes_tv.setModel(proxyModel)

            # get  geofence polygon
            geofence_df = self.scopedb.execute(f"""
                SELECT
                    ST_AsText(geometry) as geometry
                FROM
                    geofence_polygon
                LIMIT 1;
            """).df()
            geofence_df['geometry'] = geopandas.GeoSeries.from_wkt(geofence_df['geometry'])
            self.geofence_polygon = geopandas.GeoDataFrame(geofence_df, geometry='geometry', crs="EPSG:4326")

            # mark as out_of_geofence all records that are outside geofence_polygon layer if defined
            if not self.geofence_polygon.empty:
                geofence_geom = self.geofence_polygon.iloc[0].geometry
                outside_geofence_mask = ~self.results.within(geofence_geom)
                self.results.loc[outside_geofence_mask, 'score'] = -1  # mark score as -1 for out_of_geofence

            # calculate and display statistics
            total_records = len(self.results)
            self.success = self.results.query(f"geometry != None and score >= {success_score_threshold}", inplace=False)
            num_of_success = len(self.success)
            self.fails = self.results.query(f"geometry == None or (score >= 0 and score < {success_score_threshold})", inplace=False)
            num_of_fails = len(self.fails)
            self.out_of_geofence = self.results.query("score == -1", inplace=False)
            num_of_out_of_geofence = len(self.out_of_geofence)

            self.statistics_num_of_records.setText(str(total_records))
            self.statistics_num_of_success.setText(str(num_of_success))
            self.statistics_num_of_fails.setText(str(num_of_fails))
            self.statistics_num_of_out_of_geofence.setText(str(num_of_out_of_geofence))
            if total_records > 0:
                success_rate = (num_of_success / total_records) * 100
            else:
                success_rate = 0.0
            self.statistics_geocode_score.setText(f"{success_rate:.2f}% (Threshoold: {success_score_threshold})")

        except Exception as e:
            self.feedback.reportError(f"Error loading results: {str(e)}")


FORM_CLASS: QWizardPage = load_ui("wizard_evaluate_geocode_page.ui")
class ANNCSUWizardEvaluateGeocode(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # gui elements
        self.load_all_layers: QPushButton
        self.load_all_layers.clicked.connect(self.load_geocodings_into_qgis)
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

    def load_geocodings_into_qgis(self):
        """Load all geocoded results as layers into QGIS.
        Get results from stored one saved in the shown tabls."""

        for i in range(self.geocoders_tabs.count()):
            tab: ANNCUGeocodeResultTab = self.geocoders_tabs.widget(i)
            geocoder_name = self.geocoders_tabs.tabText(i)
            layer_name_success = f"{geocoder_name}_success"
            layer_name_fails = f"{geocoder_name}_fails"
            layer_name_out_of_geofence = f"{geocoder_name}_out_of_geofence"
            layer_geofence_polygon = f"{geocoder_name}_geofence_polygon"

            # load geofence polygon layer as first layer to avoid to cover other layers
            if not tab.geofence_polygon.empty:
                ANNCSUMessageManager().show_message(f"Loading layer: {layer_geofence_polygon}", level="info", duration=5)
                remove_layer_by_name(layer_geofence_polygon)
                tab.geofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.geofence_polygon,
                    layer_name=layer_geofence_polygon,
                    geometry_column="geometry",
                    crs_epsg=4326  # assuming WGS84, adjust as needed
                )

            # load success layer
            if tab.success is not None and not tab.success.empty:
                ANNCSUMessageManager().show_message(f"Loading layer: {layer_name_success}", level="info", duration=5)
                remove_layer_by_name(layer_name_success)
                tab.successLayer = load_dataframe_as_layer(
                    dataframe=tab.success,
                    layer_name=layer_name_success,
                    geometry_column="geometry",
                    crs_epsg=4326  # assuming WGS84, adjust as needed
                )

                # zoom to the layer extent
                canvas = iface.mapCanvas()
                canvas.setExtent(tab.successLayer.extent())
                canvas.refresh()

            # load fails layer
            if tab.fails is not None and not tab.fails.empty:
                ANNCSUMessageManager().show_message(f"Loading layer: {layer_name_fails}", level="info", duration=5)
                remove_layer_by_name(layer_name_fails)
                tab.failsLayer = load_dataframe_as_layer(
                    dataframe=tab.fails,
                    layer_name=layer_name_fails,
                    geometry_column="geometry",  # BEAWARE could contain None geometries
                    crs_epsg=4326  # assuming WGS84, adjust as needed
                )

            # load out_of_geofence layer
            if tab.out_of_geofence is not None and not tab.out_of_geofence.empty:
                ANNCSUMessageManager().show_message(f"Loading layer: {layer_name_out_of_geofence}", level="info", duration=5)
                remove_layer_by_name(layer_name_out_of_geofence)
                tab.outOfGeofenceLayer = load_dataframe_as_layer(
                    dataframe=tab.out_of_geofence,
                    layer_name=layer_name_out_of_geofence,
                    geometry_column="geometry",  # BEAWARE could contain None geometries
                    crs_epsg=4326  # assuming WGS84, adjust as needed
                )


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

        # load statial extension
        scopedb.execute("INSTALL spatial;")
        scopedb.execute("LOAD spatial;")

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
                geocoder_config=geocoder_config,
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

