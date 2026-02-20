__copyright__ = "Copyright 2025-2026, GeoBeyond.it"
__license__ = "GPL version 3"
__email__ = "info@geobeyond.it"
__revision__ = "$Format:%H$"

from typing import Optional
from pathlib import Path
import geopandas
from pandas import Float64Dtype, Int64Dtype
from shapely.geometry import Point

from qgis.core import (
    Qgis,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsFeature,
    QgsVectorFileWriter,
    QgsMessageLog
)
from qgis.PyQt.QtCore import QVariant, QMetaType

from anncsu_manager.utils.misc_utils import PLUGIN_PATH
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager

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
    # columns = [field.name() for field in layer.fields()] + ['geometry']
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




def load_dataframe_as_layer(
        dataframe: geopandas.GeoDataFrame,
        layer_name: str,
        column_types: dict,
        geometry_column: str = "geometry",
        crs_epsg: int = 4326,
        out_path: Optional[Path] = None) -> QgsVectorLayer:
    """Load a DataFrame as a QGIS vector layer.

    Args:
        dataframe: The pandas DataFrame to load.
        layer_name: The name of the layer in QGIS.
        column_types: A dictionary mapping column names to their data types (e.g., int, float, bool, str).
        geometry_column: The name of the column containing geometry data (WKT format). "geometry" by default.
        crs_epsg: The EPSG code for the coordinate reference system. 4326 (WGS84) by default.
    Returns:
        QgsVectorLayer: The created QGIS vector layer.
    """
    # get geometry type from the first valid geometry
    first_valid_geom = None
    for geom in dataframe[geometry_column]:
        if geom is not None and not geom.is_empty:
            first_valid_geom = geom
            break
    if first_valid_geom is None:
        # do not raise an error, just create a point layer with default geometry type
        # raise ValueError("No valid geometries found in the specified geometry column.")
        QgsMessageLog.logMessage(
            "No valid geometries found in the specified geometry column. Assuming Point layer!",
            level=Qgis.Warning
        )
        first_valid_geom = Point()

    vl = QgsVectorLayer(f"{first_valid_geom.geom_type}?crs=epsg:{crs_epsg}", layer_name, "memory")
    provider = vl.dataProvider()
    if provider is None:
        raise ValueError("Could not get data provider for the vector layer.")

    # Add fields to the layer
    integers = ['int64', 'int32', 'int16', 'Int8', Int64Dtype()]
    floats = ['float64', 'float32', 'float16', 'double', 'decimal', Float64Dtype()]

    for col in dataframe.columns:
        if col == geometry_column:
            continue
        if col not in vl.fields().names():
            # get type of the dataframe column
            dataframe_col_type = dataframe[col].dtype
            if (dataframe_col_type in integers or column_types.get(col) in integers):
                provider.addAttributes([QgsField(col, QMetaType.Int)])
            elif (dataframe_col_type in floats or column_types.get(col) in floats):
                provider.addAttributes([QgsField(col, QMetaType.Double)])
            elif dataframe_col_type == 'bool':  
                provider.addAttributes([QgsField(col, QMetaType.Bool)])
            else:
                provider.addAttributes([QgsField(col, QMetaType.QString)])
    vl.updateFields()

    # Add features to the layer
    feats = []
    for _, row in dataframe.iterrows():
        # convert <NA> to None otherwise feat.setAttribute will fail
        row_copy = row.copy()
        row_copy[row_copy.isna()] = None

        # add feature to layer
        feat = QgsFeature()
        feat.setFields(vl.fields())
        for col in dataframe.columns:
            if col == geometry_column:
                if row_copy[col] is not None:
                    feat.setGeometry(QgsGeometry.fromWkt(row_copy[col].wkt))
            else:
                feat.setAttribute(col, row_copy[col])
        feats.append(feat)

    # add all features at once to improve performance
    provider.addFeatures(feats)
    vl.updateExtents()

    # save layer to the current Mergin project as parquet file if requested
    if out_path is not None:
        # session_folder = ANNCSUSettingsManager.get_session_repo_local_path()
        # if session_folder is None:
        #     raise ValueError("No active session found. Please select a session before materializing the layer.")
        output_file_path = out_path / f"{layer_name}.gpkg"

        # Materialize layer as Parquet file
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.fileEncoding = 'UTF-8'
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        options.driverName = 'GPKG'
        options.layerName = layer_name
        options.saveMetadata = True
        options.symbolExport = QgsVectorFileWriter.FeatureSymbology

        write_result, error_message, new_file, new_layer = QgsVectorFileWriter.writeAsVectorFormatV3(
                    vl,
                    str(output_file_path),
                    QgsProject.instance().transformContext(),
                    options)
        if write_result != QgsVectorFileWriter.NoError:
            raise IOError(f"Error saving layer '{layer_name}' to file '{output_file_path}': {error_message}")
        else:
            vl = QgsVectorLayer(str(output_file_path), layer_name, "ogr")

    # apply related style if exists
    named_style_path = Path(PLUGIN_PATH) / "resources" / "styles" / f"{layer_name}_style.qml"
    vl.updateExtents()
    if named_style_path.exists():
        vl.loadNamedStyle(str(named_style_path))
    else:
        print(f"Style file not found: {named_style_path}")

    # show the layer in QGIS
    QgsProject.instance().addMapLayer(vl)

    return vl
