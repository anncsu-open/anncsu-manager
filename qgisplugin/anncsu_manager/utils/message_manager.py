from typing import Literal, Optional

from qgis.core import Qgis
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import QCoreApplication


class ANNCSUMessageManager:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ANNCSUMessageManager, cls).__new__(cls)
        return cls.instance

    def __del__(self) -> None:
        self.message_bar.deleteLater()
        self.message_bar = None

    def set_message_bar(self, message_bar: QgsMessageBar):
        self.message_bar = message_bar


    def show_message(
        self,
        text: str,
        level: Literal["success", "info", "warning", "invalid", "error"] = "info", 
        duration: Optional[int] = None
    ):
        if not self.message_bar:
            raise ValueError("Message bar not set for ANNCSUMessageManager.")

        if not duration:
            duration = -1

        if level == "success":
            self.message_bar.pushMessage(QCoreApplication.translate("ANNCSUMessageManager", "Success"), text, Qgis.MessageLevel.Success, duration)
        elif level == "info":
            self.message_bar.pushMessage(QCoreApplication.translate("ANNCSUMessageManager", "Info"), text, Qgis.MessageLevel.Info, duration)
        elif level == "warning":
            self.message_bar.pushMessage(QCoreApplication.translate("ANNCSUMessageManager", "Warning"), text, Qgis.MessageLevel.Warning, duration)
        elif level == "invalid":
            self.message_bar.pushMessage(text, Qgis.MessageLevel.Warning, duration)
        elif level == "error":
            self.message_bar.pushMessage(QCoreApplication.translate("ANNCSUMessageManager", "Error"), text, Qgis.MessageLevel.Critical, duration)
