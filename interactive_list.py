from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QListView


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove
        )  # Enable drag and drop reordering
        self.setMovement(
            QListWidget.Movement.Snap
        )  # Set the movement to snap, so the items snap to grid

        self.setIconSize(QSize(164, 164))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
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
                drop_index = self.indexAt(event.position().toPoint())
                if drop_index.isValid():
                    item = self.takeItem(self.currentRow())
                    self.insertItem(drop_index.row(), item)
