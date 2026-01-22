import os
import sys
from typing import Callable, List, Optional

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication, QTranslator, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QWidget

from anncsu_manager.qgis_plugin_tools.tools.custom_logging import setup_logger, teardown_logger
from anncsu_manager.utils.misc_utils import PLUGIN_PATH

from .anncsu_wizard.wizard_main import ANNCSUWizardDialog
from .qgis_plugin_tools.tools.i18n import setup_translation

# Ensure plugin path is in sys.path for imports submodules
sys.path.append(PLUGIN_PATH)

class Plugin:
    """QGIS Plugin Implementation."""

    name = "ANNCSU QGIS Plugin"

    def __init__(self) -> None:
        setup_logger(Plugin.name)

        # initialize locale
        locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass

        self.actions: List[QAction] = []
        self.menu = Plugin.name
        self.iface: QgisInterface = iface

        # initialize locale
        locale = QgsApplication.locale()
        qmPath = f'{PLUGIN_PATH}/i18n/anncsu_manager_{locale}.qm'

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QCoreApplication.installTranslator(self.translator)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Callable,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: Optional[str] = None,
        whats_this: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self) -> None:  # noqa N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(PLUGIN_PATH, "resources/icons/icons8-country-house-64.png")  # A placeholder icon

        self.add_action(
            icon_path,
            text="",
            parent=self.iface.mainWindow(),
            callback=lambda: self.open_wizard(0),
            add_to_toolbar=True,
            add_to_menu=True,
        )

    def onClosePlugin(self) -> None:  # noqa N802
        """Cleanup necessary items here when plugin dockwidget is closed"""
        if self.wizard:
            self.wizard.deleteLater()
        self.wizard = None

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(Plugin.name, action)
            self.iface.removeToolBarIcon(action)
        teardown_logger(Plugin.name)

    def open_wizard(self, page):
        self.wizard = ANNCSUWizardDialog()

        # be sure to delete the widget on close and related C++ objects
        self.wizard.setAttribute(Qt.WA_DeleteOnClose)
        self.wizard.closeEvent = self.onClosePlugin

        self.wizard.show()
        self.wizard.content.menu_widget.setCurrentRow(page)
