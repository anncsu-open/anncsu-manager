__copyright__ = "Copyright 2025-2026, GeoBeyond.it"
__license__ = "GPL version 3"
__email__ = "info@geobeyond.it"
__revision__ = "$Format:%H$"

from typing import Optional
from pathlib import Path
import geopandas

from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsField, QgsFeature
from qgis.PyQt.QtCore import QVariant

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


def load_dataframe_as_layer(
        dataframe: geopandas.GeoDataFrame,
        layer_name: str,
        geometry_column: str = "geometry",
        crs_epsg: int = 4326,
        materialize: bool = True) -> QgsVectorLayer:
    """Load a DataFrame as a QGIS vector layer.

    Args:
        dataframe: The pandas DataFrame to load.
        layer_name: The name of the layer in QGIS.
        geometry_column: The name of the column containing geometry data (WKT format). "geometry" by default.
        crs_epsg: The EPSG code for the coordinate reference system. 4326 (WGS84) by default.
    Returns:
        QgsVectorLayer: The created QGIS vector layer.
    """
    if geometry_column and geometry_column in dataframe.columns:
        # Convert the DataFrame to GeoJSON format
        geojson_str = dataframe.to_json()

        # Create a QGIS vector layer from the GeoJSON string
        vl = QgsVectorLayer(geojson_str, layer_name, "ogr")

        # Set the geometry column if specified
        if crs_epsg:
            vl.setCrs(QgsCoordinateReferenceSystem(f"EPSG:{crs_epsg}"))
    else:
        # If no geometry column is provided, create a non-spatial layer
        vl = QgsVectorLayer("None", layer_name, "memory")
        provider = vl.dataProvider()

        # Add fields to the layer
        fields = [QgsField(col, QVariant.String) for col in dataframe.columns]
        provider.addAttributes(fields)
        vl.updateFields()

        # Add features to the layer
        for _, row in dataframe.iterrows():
            feat = QgsFeature()
            feat.setFields(vl.fields())
            for col in dataframe.columns:
                feat.setAttribute(col, str(row[col]))
            provider.addFeature(feat)

    # save layer to the current Mergin project as parquet file if requested
    if materialize:
        session_folder = ANNCSUSettingsManager.get_current_session_folder()
        if session_folder is None:
            raise ValueError("No active session found. Please select a session before materializing the layer.")

        output_file_path = session_folder / f"{layer_name}.gpkg"

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
