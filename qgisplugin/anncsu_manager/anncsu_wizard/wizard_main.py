import os

from qgis.gui import QgsDockWidget, QgsMessageBar
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QProgressBar
)
from qgis.utils import iface

from anncsu_manager.anncsu_wizard.wizard_about import ANNCSUWizardAbout
from anncsu_manager.anncsu_wizard.wizard_settings import ANNCSUWizardSettings
from anncsu_manager.anncsu_wizard.wizard_manager import ANNCSUWizardManager
from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.misc_utils import PLUGIN_PATH


class ANNCSUWizardDialog(QDialog):

    def __init__(self) -> None:
        super().__init__()

        # Default size
        self.resize(1000, 850)

        self.content = ANNCSUWizard(with_message_bar = True)

        layout = QVBoxLayout()
        layout.addWidget(self.content)

        self.setLayout(layout)

        self.setWindowTitle("ANNCSU Wizard")


FORM_CLASS: QWidget = load_ui("wizard.ui")

class ANNCSUWizard(QWidget, FORM_CLASS):

    def __init__(self, with_message_bar: bool = False) -> None:
        super().__init__()
        self.setupUi(self)

        self.menu_widget: QListWidget
        self.pages_widget: QStackedWidget
        self.content_area_layout: QVBoxLayout
        self.progress_bar: QProgressBar
        self.progress_bar.setVisible(False)

        self.menu_items = [
            # Icon: <a href="https://img.icons8.com/arcade/64/country-house.png">Rock</a>
            # icon by <a target="_blank" href="https://icons8.com">Icons8</a>
            ("ANNCSU Manager", QIcon(os.path.join(PLUGIN_PATH, "resources/icons/icons8-country-house-64.png"))),
            
            # Icon by Icons8
            ("Settings", QIcon(os.path.join(PLUGIN_PATH, "resources/icons/settings.svg"))),

            # Icon by Icons8
            ("About", QIcon(os.path.join(PLUGIN_PATH, "resources/icons/about.svg"))),
        ]

        self.create_menu(minimize_text=False)

        if with_message_bar:
            self.message_bar = QgsMessageBar(self)
            self.content_area_layout.insertWidget(0, self.message_bar)
        else:
            self.message_bar = iface.messageBar()

        # instanciate singleton message manager where to send
        # all general messages as QgsMessageBar
        self.message_manager = ANNCSUMessageManager()
        self.message_manager.set_message_bar(self.message_bar)

        # Add pages

        # Create Settings page first
        self.manager_page = ANNCSUWizardManager(self, self.progress_bar)
        self.pages_widget.insertWidget(4, self.manager_page)

        self.settings_page = ANNCSUWizardSettings(self, self.progress_bar)
        self.pages_widget.insertWidget(5, self.settings_page)

        self.about_page = ANNCSUWizardAbout(self)
        self.pages_widget.insertWidget(6, self.about_page)

        # Set menu
        # self.menu_widget.setMinimumWidth(
        #     self.menu_widget.sizeHintForColumn(0) + 5)

        self.menu_widget.currentRowChanged['int'].connect(
            self.pages_widget.setCurrentIndex)

        self.menu_widget.setCurrentRow(0)

        # Connect settings signal
        self.settings_page.minimal_menu_setting_changed.connect(self.create_menu)


    def create_menu(self, minimize_text: bool = False):
        for i, (text, icon) in enumerate(self.menu_items):
            item: QListWidgetItem = self.menu_widget.item(i)
            item.setIcon(icon)
            if minimize_text:
                item.setText("")
                self.menu_widget.setMinimumWidth(45)
                self.menu_widget.setMaximumWidth(45)
            else:
                item.setText(text)
                self.menu_widget.setMinimumWidth(210)
                self.menu_widget.setMaximumWidth(210)
