from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListView


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(
            QAbstractItemView.InternalMove
        )  # Enable drag and drop reordering
        self.setMovement(
            QListView.Snap
        )  # Set the movement to snap, so the items snap to grid

        self.setIconSize(QSize(164, 164))
        self.setResizeMode(QListWidget.Adjust)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # Handle dropping of URLs (e.g. images)
            # ...
        else:
            super().dropEvent(event)

            if event.source() == self:
                drop_index = self.indexAt(event.pos())
                if drop_index.isValid():
                    item = self.takeItem(self.currentRow())
                    self.insertItem(drop_index.row(), item)
