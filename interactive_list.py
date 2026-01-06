from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QRect, QSize, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QFontMetrics, QPainter, QPaintEvent, QPixmap
from PyQt6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QWidget

from utils import get_page_size

if TYPE_CHECKING:
    from pypdfmerger import PyPDFMerger


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        main_window: Optional[PyPDFMerger] = None,
    ):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setMovement(QListWidget.Movement.Snap)

        self.setIconSize(QSize(164, 164))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDropIndicatorShown(True)
        self.main_window = main_window

        self.itemEntered.connect(self.show_preview)
        viewport = self.viewport()
        if viewport:
            viewport.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        originalPixmap = QPixmap(os.path.join(bundle_dir, 'drag_and_drop.png')) # Load the icon you want to display
        self.emptyListPixmap = originalPixmap.scaled(QSize(100, 100), Qt.AspectRatioMode.KeepAspectRatio)

    def paintEvent(self, e: Optional[QPaintEvent]) -> None:
        super().paintEvent(e)

        if not self.count():
            viewport = self.viewport()
            if not viewport:
                return
            qp = QPainter(viewport)
            qp.setPen(Qt.GlobalColor.lightGray)
            font = QFont()
            font.setPointSize(12)
            font.setWeight(QFont.Weight.Bold)
            qp.setFont(font)

            # Draw the icon in the middle of the widget
            pixmap_rect = QRect(0, 0, self.emptyListPixmap.width(), self.emptyListPixmap.height())
            pixmap_rect.moveCenter(self.rect().center())
            qp.drawPixmap(pixmap_rect, self.emptyListPixmap)

            # Draw the text
            fm = QFontMetrics(qp.font())
            text = "Drag and Drop your pdf files here \n or use the add files button"
            text_width = fm.horizontalAdvance(text)
            text_rect = QRect(0, 0, text_width, 2 * fm.height())
            text_rect.moveCenter(self.rect().center())
            text_rect.moveTop(pixmap_rect.bottom() + 10)  # Move it just below the icon

            qp.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            qp.end()

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

    def dragEnterEvent(self, e: Optional[QDragEnterEvent]) -> None:
        if e is None:
            return
        mime_data = e.mimeData()
        if mime_data and mime_data.hasUrls():
            e.accept()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e: Optional[QDropEvent]) -> None:
        if e is None:
            return
        mime_data = e.mimeData()
        if mime_data and mime_data.hasUrls():
            urls = mime_data.urls()
            pdf_files: List[str] = []
            for url in urls:
                local_path = url.toLocalFile()
                if local_path.lower().endswith(".pdf"):
                    pdf_files.append(local_path)
            if pdf_files and self.main_window:
                self.main_window.upload_pdfs(pdf_files)
        else:
            super().dropEvent(e)
            if e.source() == self:
                drop_index = self.indexAt(e.position().toPoint())
                if drop_index.isValid():
                    item = self.takeItem(self.currentRow())
                    self.insertItem(drop_index.row(), item)
