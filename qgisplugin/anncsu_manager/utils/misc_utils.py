import os
from typing import Optional

from qgis.core import (
    QgsApplication,
    QgsProject,
)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtWidgets import QComboBox

from anncsu_manager.qgis_plugin_tools.tools.resources import resources_path

TEMPORARY_OUTPUT = 'TEMPORARY_OUTPUT'
PLUGIN_PATH = os.path.dirname(os.path.dirname(__file__))

class EventSource:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        self.listeners.append(listener)
        return self

    def emit(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)

def get_output_path(file_widget: QgsFileWidget) -> str:
    fp = file_widget.filePath()
    return fp if fp != "" else TEMPORARY_OUTPUT

def get_output_layer_name(output_raster_path: QgsFileWidget, default_output_name: str) -> str:
    if get_output_path(output_raster_path) == 'TEMPORARY_OUTPUT':
        layer_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        unique_name = default_output_name
        suffix = 1
        while unique_name in layer_names:
            unique_name = f"{default_output_name}_{suffix}"
            suffix += 1
        return unique_name
    else:
        return os.path.splitext(os.path.basename(output_raster_path.filePath()))[0]


def add_output_layer_to_group(layer, group_name: str, subgroup_name: Optional[str] = None):
    QgsProject.instance().addMapLayer(layer, False)
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    if not group:
        group = root.addGroup(group_name)

    if subgroup_name is not None:
        subgroup = group.findGroup(subgroup_name)
        if not subgroup:
            subgroup = group.addGroup(subgroup_name)

        subgroup.addLayer(layer)
    else:
        group.addLayer(layer)


def find_index_for_text_combobox(
    combo_box: QComboBox, text: str, case_sensitive: bool = False
) -> Optional[int]:
    for index in range(combo_box.count()):
        if case_sensitive:
            if combo_box.itemText(index) == text:
                return index
        else:
            if combo_box.itemText(index).lower() == text.lower():
                return index
    return None


def check_duplicate_names(names: list) -> list:
    name_count = {}
    unique_names = []
    for name in names:
        if name in name_count:
            name_count[name] += 1
            new_name = f"{name}_{name_count[name]}"
        else:
            name_count[name] = 1
            new_name = name
        
        unique_names.append(new_name)
    
    return unique_names


def get_user_data_directory() -> str:
    """
    Returns the directory path where user-defined data is stored.
    Ensures the directory exists.
    """
    # Use QGIS settings directory to store persistent data
    user_data_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), "anncsu_plugin_user_data")
    # Ensure the directory exists
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    return user_data_dir

