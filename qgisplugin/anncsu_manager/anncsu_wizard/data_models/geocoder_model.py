from __future__ import annotations

from typing import Any, Optional, Union

from qgis.PyQt.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt


class TreeItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: Optional[TreeItem] = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = None
        self._children = []

    def appendChild(self, item: TreeItem):
        self._children.append(item)

    def child(self, row: int) -> TreeItem:
        return self._children[row]

    def parent(self) -> Optional[TreeItem]:
        return self._parent

    def childCount(self) -> int:
        return len(self._children)

    def row(self) -> int:
        return self._parent._children.index(self) if self._parent else 0

    @classmethod
    def _infer_type(cls, value: Union[str, int, float, bool, dict, list, None]) -> type:
        if value is None:
            return type(None)
        elif isinstance(value, str) and value.lower() in ("true", "false"):
            return bool

        if isinstance(value, str):
            value = value.strip()
            try:
                int(value)
                return int
            except ValueError:
                pass
            try:
                float(value)
                return float
            except ValueError:
                pass

        return type(value)

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str):
        self._key = key

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def value_type(self):
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        self._value_type = value

    @classmethod
    def load(
        cls,
        value: list | dict,
        parent: Optional[TreeItem] = None,
        sort=True
    ) -> TreeItem:
        """Create a 'root' TreeItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = TreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            TreeItem: TreeItem
        """
        rootItem = TreeItem(parent)

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = cls._infer_type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = str(index)
                child.value_type = cls._infer_type(value)
                rootItem.appendChild(child)

        else:
            rootItem.key = "root"
            rootItem.value = value
            rootItem.value_type = cls._infer_type(value)
        
        return rootItem


class GeocoderModel(QAbstractItemModel):
    """ An editable model of Geocoder populated from Json data """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("Parameter", "Value")

    def clear(self):
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(  # nosec B101 - intentionally use assert for type checking
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()
        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)
        self.endResetModel()

        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(GeocoderModel, self).flags(index)

        if index.column() == 0:
            flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable | flags

        if index.column() == 1:
            if index.internalPointer().value_type is bool:
                # do not allow editing bool values directly, use checkbox instead
                flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable | flags
            else:
                flags = Qt.ItemFlag.ItemIsEditable | flags

        return flags

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None
        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key

            # allow setting value manually for any field BUT bools managed by checkbox
            if index.column() == 1 and not item.value_type is bool:
                return item.value

        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1 and not item.value_type is bool:
                return item.value

        elif role == Qt.ItemDataRole.CheckStateRole:
            # add checkbox for upper level items
            if index.column() == 0 and not index.parent().isValid():
                # get the state from "active" children boolean value
                # and set upper level value basing on it's state
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child.key == "active":
                        if child.value in (True, "true", "True"):
                            return Qt.CheckState.Checked
                        else:
                            return Qt.CheckState.Unchecked

            # add checkbox for boolean values in inner childrens
            if index.column() == 1:
                if item.value_type is bool:
                    if item.value in (True, "true", "True"):
                        return Qt.CheckState.Checked
                    else:
                        return Qt.CheckState.Unchecked


    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if not index.isValid():
            return None
        item = index.internalPointer()

        if role == Qt.ItemDataRole.CheckStateRole:
            # if the checkbox is in the first column and it is an upper level item
            if index.column() == 0 and not index.parent().isValid():
                # set the state to "active" children boolean value
                for i in range(item.childCount()):
                    childIndex = index.child(i, 1)
                    child = item.child(i)
                    if child.key == "active":
                        if child.value in (True, "true", "True"):
                            child.value = "False"
                            state = Qt.CheckState.Unchecked
                        else:
                            child.value = "True"
                            state = Qt.CheckState.Checked
                        # trigger dataChanged for the parent and child checkbox
                        self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                        self.dataChanged.emit(childIndex, childIndex, [Qt.ItemDataRole.EditRole])
                        return state

            # if the checkbox is in the second column and it is a boolean value
            if index.column() == 1 and index.parent().isValid():
                if item.value_type is bool:
                    # toggle the value
                    if item.value in (True, "true", "True"):
                        item.value = "False"
                        state = Qt.CheckState.Unchecked
                    else:
                        item.value = "True" # Qt.CheckState.Checked
                        state = Qt.CheckState.Checked
                    # trigger dataChanged for the index and it's parent checkbox
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    self.dataChanged.emit(index.parent(), index.parent(), [Qt.ItemDataRole.EditRole])
                    return state
        elif role == Qt.ItemDataRole.EditRole:
            # manage editing of threshild values as float
            if index.column() == 1:
                if item.value_type in (int, float):
                    try:
                        if item.value_type is int:
                            item.value = int(value)
                        else:
                            item.value = float(value)
                        self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                        return True
                    except ValueError:
                        return False
                else:
                    item.value = value
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
        return False

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def to_json(self, item=None):

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value