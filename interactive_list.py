from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QListView
from pathlib import Path
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QImage
from utils import get_page_size


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(self, parent=None, main_window=None):
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

        self.itemEntered.connect(self.show_large_icon)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

    def show_large_icon(self, item):
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            pdf_files = []
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
