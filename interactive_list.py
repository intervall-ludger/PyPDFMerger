from pathlib import Path

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QDropEvent, QDragEnterEvent
from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem

from utils import get_page_size


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(self, parent=None, main_window=None):
        """
        Initialize an InteractiveQListDragAndDrop instance.

        Args:
            parent (QWidget): The parent widget. Defaults to None.
            main_window (Optional[QWidget]): The main window widget. Defaults to None.
        """
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
        self.main_window = main_window

        self.itemEntered.connect(self.show_preview)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

    def show_preview(self, item: QListWidgetItem):
        """
        Show page preview.

        Args:
            item (QListWidgetItem): The item for which to show the page preview.
        """
        if item.icon():
            width, height = get_page_size()
            pixmap = item.icon().pixmap(QSize(width, height))
            image = pixmap.toImage()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            base64_data = byte_array.toBase64()
            item.setToolTip(
                f'<img src="data:image/png;base64,{base64_data.data().decode()}">'
            )
        else:
            item.setToolTip("")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Event triggered when a drag operation enters the widget.

        Args:
            event (QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        """
        Event triggered when a drop operation occurs on the widget.

        Args:
            event (QDropEvent): The drop event.
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            pdf_files: List[str] = []
            for url in urls:
                file_path = Path(url.path()[1:])
                if file_path.suffix == ".pdf":
                    pdf_files.append(file_path.as_posix())
            if len(pdf_files) > 0:
                self.main_window.upload_pdfs(pdf_files)

        else:
            super().dropEvent(event)

            if event.source() == self:
                drop_index = self.indexAt(event.position().toPoint())
                if drop_index.isValid():
                    item = self.takeItem(self.currentRow())
                    self.insertItem(drop_index.row(), item)
