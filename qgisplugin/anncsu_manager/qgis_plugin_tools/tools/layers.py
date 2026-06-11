__copyright__ = "Copyright 2025-2026, GeoBeyond.it"
__license__ = "GPL version 3"
__email__ = "info@geobeyond.it"
__revision__ = "$Format:%H$"

from typing import Optional
from pathlib import Path
import geopandas
import pandas
import shapely

from qgis.core import (
    Qgis,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsField,
    QgsFeature,
    QgsVectorFileWriter,
    QgsMessageLog,
    QgsTask,
    QgsApplication,
)
from qgis.PyQt.QtCore import QMetaType

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.utils.message_manager import ANNCSUMessageManager

def remove_layer_by_name(layer_name: str) -> None:
    """Remove a layer from QGIS by its name.

    Args:
        layer_name: The name of the layer to remove.
    """
    layers = QgsProject.instance().mapLayersByName(layer_name)
    for layer in layers:
        QgsProject.instance().removeMapLayer(layer.id())

def convert_layer_to_geopandas(layer: QgsVectorLayer) -> geopandas.GeoDataFrame:
    """Convert a QGIS vector layer to a GeoPandas GeoDataFrame.

    Args:
        layer: The QGIS vector layer to convert.

    Returns:
        A GeoPandas GeoDataFrame representing the layer's data.
    """
    # option 1
    # Export the layer to a temporary GeoJSON file
    # temp_geojson_path = Path(ANNCSUSettingsManager.get_temp_folder()) / f"{layer.name()}_temp.geojson"
    # options = QgsVectorFileWriter.SaveVectorOptions()
    # options.driverName = "GeoJSON"
    # options.fileEncoding = 'UTF-8'
    # options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

    # write_result, error_message, new_file, new_layer = QgsVectorFileWriter.writeAsVectorFormatV3(
    #             layer,
    #             str(temp_geojson_path),
    #             QgsProject.instance().transformContext(),
    #             options)
    # if write_result != QgsVectorFileWriter.NoError:
    #     raise IOError(f"Error exporting layer '{layer.name()}' to GeoJSON: {error_message}")

    # # Read the GeoJSON file into a GeoPandas GeoDataFrame
    # gdf = geopandas.read_file(temp_geojson_path)

    # # Optionally, remove the temporary file
    # try:
    #     temp_geojson_path.unlink()
    # except Exception as e:
    #     print(f"warning: Could not delete temporary file '{temp_geojson_path}': {e}")

    # return gdf

    # option 2
    # Directly convert layer to GeoDataFrame using QgsVectorLayer's data provider
    # features = layer.getFeatures()
    # records = []
    # for feature in features:
    #     record = feature.attributes()
    #     geom = feature.geometry()
    #     record.append(geom.asWkt() if geom else None)
    #     records.append(record)
    # columns = [field.name() for field in layer.fields()] + ['geom']
    # gdf = geopandas.GeoDataFrame(records, columns=columns)
    # if layer.crs().isValid():
    #     gdf.set_crs(layer.crs().authid(), inplace=True)
    # return gdf

    # option 3
    # gdf = geopandas.GeoDataFrame(
    #     [feat.attributes() for feat in layer.getFeatures()],
    #     columns=[field.name() for field in layer.fields()],
    #     geometry=[feat.geometry() for feat in layer.getFeatures()]
    # )

    # option 4 (need layer as file-based layer)
    gdf = geopandas.read_file(layer.source())
    return gdf

def _bytearray_to_geom(geom_bytes: bytes) -> Optional[QgsGeometry]:
    """Convert a byte array to a QgsGeometry object.

    Args:
        geom_bytes: The byte array representing the geometry (WKB format).

    Returns:
        A QgsGeometry object if conversion is successful, or None if it fails.
    """
    try:
        return QgsGeometry.fromWkb(geom_bytes)
    except Exception as e:
        QgsMessageLog.logMessage(
            f"Error converting byte array to geometry: {e}. Skipping this geometry.",
            level=Qgis.Warning
        )
        return None


def load_dataframe_as_layer(
        dataframe: pandas.DataFrame,
        layer_name: str,
        column_types: dict,
        geometry_column: str = "geom",
        crs_epsg: int = 4326,
        out_path: Optional[Path] = None) -> QgsVectorLayer:
    """Load a DataFrame as a QGIS vector layer.

    Args:
        dataframe: The pandas DataFrame to load.
        layer_name: The name of the layer in QGIS.
        column_types: A dictionary mapping column names to their data types (e.g., int, float, bool, str).
        geometry_column: The name of the column containing geometry data (WKT format). "geom" by default.
        crs_epsg: The EPSG code for the coordinate reference system. 4326 (WGS84) by default.
    Returns:
        QgsVectorLayer: The created QGIS vector layer.
    """
    task = load_dataframe_as_layer_task(
        dataframe=dataframe,
        layer_name=layer_name,
        column_types=column_types,
        geometry_column=geometry_column,
        crs_epsg=crs_epsg,  # assuming WGS84, adjust as needed
        out_path=out_path  # save in current local repo
    )

    # run update current session time consuming task
    QgsApplication.taskManager().addTask(task=task)
    while task.status() != QgsTask.Running:
        QgsApplication.processEvents()
    while task.status() == QgsTask.Running:
        QgsApplication.processEvents()

    # check if task has been terminated due to error or cancellation
    if task.status() == QgsTask.Terminated:
        ANNCSUMessageManager().show_message(
            task.tr(f"Error loading layer: {layer_name}"),
            "error",
        )

    return task.vector_layer

class load_dataframe_as_layer_task(QgsTask):

    def __init__(self,
            dataframe: pandas.DataFrame,
            layer_name: str,
            column_types: dict,
            geometry_column: str = "geom",
            crs_epsg: int = 4326,
            out_path: Optional[Path] = None
        ) -> None:
        super().__init__(f"Loading DataFrame as layer '{layer_name}'", QgsTask.CanCancel)
        self.dataframe = dataframe
        self.layer_name = layer_name
        self.column_types = column_types
        self.geometry_column = geometry_column
        self.crs_epsg = crs_epsg
        self.out_path = out_path
        self.vector_layer = None

        # task status
        self.exception = None
        self.result = None

    def run(self) -> bool:
        try:
            # temporary fix to avoid error when geometry column is missing.
            # due to changed whay to create into duckdb that can have geometry o geom
            if self.geometry_column not in self.dataframe.columns:
                QgsMessageLog.logMessage(
                    f"Geometry column '{geometry_column}' not found in the DataFrame. Assuming 'geom' as geometry column.",
                    level=Qgis.Warning
                )
                geometry_column = "geom"

            # get geometry type from the first valid geometry
            first_valid_geom = None
            for geom in self.dataframe[self.geometry_column]:
                if geom is not None:
                    # check if geometry is wkb or wkt and convert to shapely geometry
                    if isinstance(geom, str):
                        try:
                            first_valid_geom = shapely.from_wkt(geom)
                            break
                        except Exception as e:
                            QgsMessageLog.logMessage(
                                f"Error parsing WKT geometry: {e}. Skipping this geometry.",
                                level=Qgis.Warning
                            )
                            continue
                    elif isinstance(geom, bytes):
                        try:
                            first_valid_geom = shapely.from_wkb(geom)
                            break
                        except Exception:
                            # check if it is a QgsGeometry in byte format
                            try:
                                newgeom = QgsGeometry()
                                QgsGeometry.fromWkb(newgeom, geom)
                                if newgeom.isGeosValid():
                                    first_valid_geom = newgeom
                                    break
                            except Exception as e:
                                QgsMessageLog.logMessage(
                                    f"Error parsing WKB geometry: {e}. Skipping this geometry.",
                                    level=Qgis.Warning
                                )
                                continue
                    elif isinstance(geom, shapely.geometry.base.BaseGeometry):
                        first_valid_geom = geom
                        break
                    else:
                        continue

            if first_valid_geom is None:
                # do not raise an error, just create a point layer with default geometry type
                # raise ValueError("No valid geometries found in the specified geometry column.")
                QgsMessageLog.logMessage(
                    "No valid geometries found in the specified geometry column. Assuming Point layer!",
                    level=Qgis.Warning
                )
                first_valid_geom = shapely.geometry.Point()

            vl = QgsVectorLayer(f"{first_valid_geom.geom_type}?crs=epsg:{self.crs_epsg}", self.layer_name, "memory")
            provider = vl.dataProvider()
            if provider is None:
                raise ValueError("Could not get data provider for the vector layer.")

            # Add fields to the layer
            integers = ['int64', 'int32', 'int16', 'Int8', pandas.Int64Dtype()]
            floats = ['float64', 'float32', 'float16', 'double', 'decimal', pandas.Float64Dtype()]

            for col in self.dataframe.columns:
                if col == self.geometry_column:
                    continue
                if col not in vl.fields().names():
                    # get type of the dataframe column
                    dataframe_col_type = self.dataframe[col].dtype
                    if (dataframe_col_type in integers or self.column_types.get(col) in integers):
                        provider.addAttributes([QgsField(col, QMetaType.Int)])
                    elif (dataframe_col_type in floats or self.column_types.get(col) in floats):
                        provider.addAttributes([QgsField(col, QMetaType.Double)])
                    elif dataframe_col_type == 'bool':
                        provider.addAttributes([QgsField(col, QMetaType.Bool)])
                    else:
                        provider.addAttributes([QgsField(col, QMetaType.QString)])
            vl.updateFields()

            # Add features to the layer
            feats = []
            for _, row in self.dataframe.iterrows():
                # convert <NA> to None otherwise feat.setAttribute will fail
                row_copy = row.copy()
                row_copy[row_copy.isna()] = None

                # add feature to layer
                feat = QgsFeature()
                feat.setFields(vl.fields())
                for col in self.dataframe.columns:
                    if col == self.geometry_column:
                        if row_copy[col] is not None:
                            if isinstance(row_copy[col], str):
                                feat.setGeometry(QgsGeometry.fromWkt(row_copy[col]))
                            elif isinstance(row_copy[col], bytes):
                                geom = QgsGeometry()
                                QgsGeometry.fromWkb(geom, row_copy[col])
                                if geom.isGeosValid():
                                    feat.setGeometry(geom)
                                else:
                                    QgsMessageLog.logMessage(
                                        f"Invalid geometry for feature with attributes {row_copy.to_dict()}. Skipping this geometry.",
                                        level=Qgis.Warning
                                    )
                            elif isinstance(row_copy[col], shapely.geometry.base.BaseGeometry):
                                feat.setGeometry(QgsGeometry.fromWkt(row_copy[col].wkt))
                            else:
                                QgsMessageLog.logMessage(
                                    f"Unsupported geometry format for feature with attributes {row_copy.to_dict()}. Skipping this geometry.",
                                    level=Qgis.Warning
                                )
                        else:
                            QgsMessageLog.logMessage(
                                f"Missing geometry for feature with attributes {row_copy.to_dict()}. Skipping this geometry.",
                                level=Qgis.Warning
                            )
                    else:
                        feat.setAttribute(col, row_copy[col])
                feats.append(feat)

            # add all features at once to improve performance
            provider.addFeatures(feats)
            vl.updateExtents()

            # save layer to the current project as GeoPackage file if requested
            if self.out_path is not None:
                # session_folder = ANNCSUSettingsManager.get_session_repo_local_path()
                # if session_folder is None:
                #     raise ValueError("No active session found. Please select a session before materializing the layer.")
                output_file_path = self.out_path / f"{self.layer_name}.gpkg"

                # Materialize layer as GeoPackage file
                # Use CreateOrOverwriteLayer instead of CreateOrOverwriteFile to avoid
                # PermissionError on Windows when the GPKG is held open by a QgsVectorLayer
                # that lives outside QgsProject (e.g. stored on a wizard tab). GPKG/SQLite
                # WAL mode allows a writer to coexist with active readers so no pre-deletion
                # is needed.
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.fileEncoding = 'UTF-8'
                options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                options.driverName = 'GPKG'
                options.layerName = self.layer_name
                options.saveMetadata = True
                options.symbolExport = QgsVectorFileWriter.FeatureSymbology

                write_result, error_message, new_file, new_layer = QgsVectorFileWriter.writeAsVectorFormatV3(
                            vl,
                            str(output_file_path),
                            QgsProject.instance().transformContext(),
                            options)
                if write_result != QgsVectorFileWriter.NoError:
                    raise IOError(f"Error saving layer '{self.layer_name}' to file '{output_file_path}': {error_message}")
                else:
                    vl = QgsVectorLayer(str(output_file_path), self.layer_name, "ogr")

            # apply related style if exists where style is composed by
            # <geocoder>_[fail|success|outs_of_geofence]_style.qml or
            # geofence_polygon_style.qml for geofence polygon layer
            if "geofence_polygon" in self.layer_name:
                named_style = "geofence_polygon_style.qml"
                named_style_path = Path(PLUGIN_PATH) / "resources" / "styles" / named_style
            else:
                geocoder_name = self.layer_name.split("_")[0]
                named_style = "_".join(self.layer_name.split("_")[1:]) + "_style.qml"
                named_style_path = Path(PLUGIN_PATH) / "resources" / "styles" / geocoder_name / named_style
            vl.updateExtents()
            if not named_style_path.exists():
                print(f"Style file not found: {named_style_path} applying fallback for '{self.layer_name}'")
                named_style_path = Path(PLUGIN_PATH) / "resources" / "styles" / "Fallback" / named_style

            print(f"Applying style from file: {named_style_path} to layer '{self.layer_name}'")
            vl.loadNamedStyle(str(named_style_path))

            # show the layer in QGIS
            QgsProject.instance().addMapLayer(vl)

            self.vector_layer = vl
            self.result = True

        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(self.tr("Error in populate_table_from_source_task: {e}").format(e=e), level=Qgis.Critical)
            self.result = False

        return self.result

    def finished(self, result: bool):
        if result:
            QgsMessageLog.logMessage(self.tr("Layer '{layer_name}' successfully created.").format(layer_name=self.layer_name), level=Qgis.Info)
        else:
            QgsMessageLog.logMessage(self.tr("Error creating layer '{layer_name}'.").format(layer_name=self.layer_name), level=Qgis.Critical)

        return super().finished(result)
