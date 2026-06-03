from __future__ import annotations
import os
import sys
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    QPoint,
)
from PyQt6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QFontMetrics,
    QPainter,
    QPaintEvent,
    QPixmap,
    QColor,
)
from PyQt6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QWidget, QGraphicsOpacityEffect

if TYPE_CHECKING:
    from pypdfmerger import PyPDFMerger


class InteractiveQListDragAndDrop(QListWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        main_window: Optional[PyPDFMerger] = None,
    ):
        super().__init__(parent)
        self.main_window = main_window
        self._drop_indicator_row = -1
        self._animations: list[QPropertyAnimation] = []

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setMovement(QListWidget.Movement.Snap)
        self.setIconSize(QSize(140, 140))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDropIndicatorShown(False)
        self.setSpacing(4)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        self._load_empty_state_pixmap()

    def _load_empty_state_pixmap(self) -> None:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        pixmap_path = os.path.join(bundle_dir, "drag_and_drop.png")
        original = QPixmap(pixmap_path)
        self._empty_pixmap = original.scaled(
            QSize(80, 80), Qt.AspectRatioMode.KeepAspectRatio
        )

    def paintEvent(self, e: Optional[QPaintEvent]) -> None:
        super().paintEvent(e)

        if self.count() > 0:
            return

        viewport = self.viewport()
        if not viewport:
            return

        painter = QPainter(viewport)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()

        if not self._empty_pixmap.isNull():
            pixmap_rect = QRect(0, 0, self._empty_pixmap.width(), self._empty_pixmap.height())
            pixmap_rect.moveCenter(center)
            pixmap_rect.moveTop(pixmap_rect.top() - 40)
            painter.setOpacity(0.4)
            painter.drawPixmap(pixmap_rect, self._empty_pixmap)
            painter.setOpacity(1.0)
            text_top = pixmap_rect.bottom() + 20
        else:
            text_top = center.y() - 20

        painter.setPen(Qt.GlobalColor.darkGray)
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)

        fm = QFontMetrics(painter.font())
        text = "Drop PDFs here"
        text_rect = QRect(0, text_top, self.width(), fm.height() * 2)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, text)

        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.gray)
        hint_rect = QRect(0, text_top + fm.height() + 8, self.width(), fm.height())
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "Double-click to preview")

        painter.end()


    def dragEnterEvent(self, e: Optional[QDragEnterEvent]) -> None:
        if e is None:
            return
        mime_data = e.mimeData()
        if mime_data and mime_data.hasUrls():
            e.accept()
        else:
            self._drop_indicator_row = -1
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e) -> None:
        if e is None:
            return
        pos = e.position().toPoint()
        index = self.indexAt(pos)

        if index.isValid():
            rect = self.visualRect(index)
            if pos.y() > rect.center().y():
                self._drop_indicator_row = index.row() + 1
            else:
                self._drop_indicator_row = index.row()
        else:
            self._drop_indicator_row = self.count()

        viewport = self.viewport()
        if viewport:
            viewport.update()
        super().dragMoveEvent(e)

    def dragLeaveEvent(self, e) -> None:
        self._drop_indicator_row = -1
        viewport = self.viewport()
        if viewport:
            viewport.update()
        super().dragLeaveEvent(e)

    def dropEvent(self, e: Optional[QDropEvent]) -> None:
        if e is None:
            return

        self._drop_indicator_row = -1
        viewport = self.viewport()
        if viewport:
            viewport.update()

        mime_data = e.mimeData()
        if mime_data and mime_data.hasUrls():
            pdf_files = [
                url.toLocalFile()
                for url in mime_data.urls()
                if url.toLocalFile().lower().endswith(".pdf")
            ]
            if pdf_files and self.main_window:
                self.main_window.upload_pdfs(pdf_files)
        else:
            source_row = self.currentRow()
            drop_index = self.indexAt(e.position().toPoint())

            if drop_index.isValid() and e.source() == self:
                target_row = drop_index.row()
                if source_row != target_row:
                    item = self.takeItem(source_row)
                    if item:
                        if source_row < target_row:
                            target_row -= 1
                        self.insertItem(target_row, item)
                        self.setCurrentItem(item)
                        self._animate_item(target_row)
            else:
                super().dropEvent(e)

    def _animate_item(self, row: int) -> None:
        item = self.item(row)
        if not item:
            return

        widget = self.itemWidget(item)
        if widget:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(200)
            anim.setStartValue(0.3)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            self._animations.append(anim)

        viewport = self.viewport()
        if viewport:
            viewport.update()

    def paintEvent(self, e: Optional[QPaintEvent]) -> None:
        super().paintEvent(e)

        viewport = self.viewport()
        if not viewport:
            return

        model = self.model()
        if self._drop_indicator_row >= 0 and self.count() > 0 and model:
            painter = QPainter(viewport)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            pen_color = QColor("#42a5f5")
            painter.setPen(pen_color)
            painter.setBrush(pen_color)

            if self._drop_indicator_row < self.count():
                rect = self.visualRect(model.index(self._drop_indicator_row, 0))
                y = rect.top() - 2
            else:
                rect = self.visualRect(model.index(self.count() - 1, 0))
                y = rect.bottom() + 2

            painter.drawRoundedRect(8, y - 2, viewport.width() - 16, 4, 2, 2)
            painter.end()

        if self.count() > 0:
            return
