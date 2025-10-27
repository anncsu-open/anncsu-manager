import os

from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QDialog, QLabel, QWidget

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.misc_utils import PLUGIN_PATH

FORM_CLASS: QDialog = load_ui("wizard_about.ui")


class ANNCSUWizardAbout(QWidget, FORM_CLASS):

    gnu_logo_label: QLabel

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        anncsu_pixmap = QPixmap(os.path.join(PLUGIN_PATH, "resources/icons/anncsu_logo_smaller.png"))
        self.anncsu_logo_label.setPixmap(anncsu_pixmap)

        gnu_pixmap = QPixmap(os.path.join(PLUGIN_PATH, "resources/icons/gnu_logo.png"))
        self.gnu_logo_label.setPixmap(gnu_pixmap)
