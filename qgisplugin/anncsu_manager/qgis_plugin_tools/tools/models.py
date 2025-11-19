__copyright__ = "Copyright 2025-2026, GeoBeyond.it"
__license__ = "GPL version 3"
__email__ = "info@geobeyond.it"
__revision__ = "$Format:%H$"

from qgis.PyQt.QtCore import QAbstractTableModel, Qt
from qgis.PyQt import QtGui
import numpy

class DataFrameModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._data.iloc[index.row(), index.column()]
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

class GeocodeResultDataFrameModel(DataFrameModel):

    SortRole = Qt.UserRole + 1000

    def __init__(self, data, score_threshold=0.8):
        QAbstractTableModel.__init__(self)
        self._data = data
        self.score_threshold = score_threshold

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            value = self._data.iloc[index.row(), index.column()]

            if role == Qt.DisplayRole:
                return str(value)

            if role == Qt.TextAlignmentRole:
                if isinstance(value, int) or isinstance(value, float):
                    # Align right, vertical middle.
                    return Qt.AlignVCenter + Qt.AlignRight

            if role == Qt.ForegroundRole:
                # change color depending on score value
                value = self._data.iloc[index.row(), self._data.columns.get_loc('score')]
                if type(value) in {int, float, numpy.float64, numpy.int64, numpy.int32}:
                    if value >= self.score_threshold:
                        return QtGui.QColor('green')
                    elif value >= 0 and value < self.score_threshold:
                        return QtGui.QColor('orange')
                    else:
                        return QtGui.QColor('red')

            if role == GeocodeResultDataFrameModel.SortRole:
                if type(value) in {int, float, numpy.float64, numpy.int64, numpy.int32}:
                    return float(value)
                else:
                    return str(value)
            
        return None

