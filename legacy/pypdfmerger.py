import sys
from typing import Optional

from PyPDF2 import PdfReader, PdfWriter
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QKeySequence, QIcon, QShortcut, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QProgressDialog,
    QWidget,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QDialog,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QListWidgetItem,
    QSizePolicy,
    QLabel,
)

from file_select_dialog import FileSelectDialog
from interactive_list import InteractiveQListDragAndDrop
from pdf_to_icon import PdfToIcon
from utils import get_start_size, get_page_size

STYLE = """
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 13px;
}

QPushButton {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #e5e5e5;
    border-color: #c0c0c0;
}

QPushButton:pressed {
    background-color: #d5d5d5;
}

QPushButton#primary {
    background-color: #0066cc;
    border: none;
    color: white;
}

QPushButton#primary:hover {
    background-color: #0055aa;
}

QPushButton#primary:pressed {
    background-color: #004488;
}

QListWidget {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px;
}

QListWidget::item {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    padding: 6px;
    margin: 3px;
}

QListWidget::item:selected {
    background-color: #e3f2fd;
    border: 2px solid #42a5f5;
}

QListWidget::item:hover {
    background-color: #f8f9fa;
    border-color: #bdbdbd;
}

QLabel#hint {
    color: #888888;
    font-size: 11px;
}

QDialog {
    background-color: #ffffff;
}
"""


class PreviewDialog(QDialog):
    def __init__(self, pixmap: QPixmap, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()


class TrashCanDialog(QDialog):
    item_restored = pyqtSignal(QListWidgetItem)

    def __init__(
        self, deleted_items: list[QListWidgetItem], parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Deleted Pages")
        self.setMinimumSize(300, 400)

        self.deleted_items_list = QListWidget()
        self.deleted_items_list.setIconSize(QSize(100, 100))
        for item in deleted_items:
            self.deleted_items_list.addItem(item.clone())

        self.restore_button = QPushButton("Restore")
        self.restore_button.clicked.connect(self.restore_deleted_item)
        self.restore_button.setEnabled(False)
        self.deleted_items_list.itemSelectionChanged.connect(self._update_button_state)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.deleted_items_list)
        layout.addWidget(self.restore_button)
        self.setLayout(layout)

    def _update_button_state(self) -> None:
        self.restore_button.setEnabled(bool(self.deleted_items_list.currentItem()))

    def restore_deleted_item(self) -> None:
        selected_item = self.deleted_items_list.takeItem(
            self.deleted_items_list.currentRow()
        )
        if selected_item:
            self.item_restored.emit(selected_item.clone())
            self.close()


class PyPDFMerger(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Merger")
        x, y, width, height = get_start_size()
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(400, 500)

        self.deleted_items: list[QListWidgetItem] = []
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self) -> None:
        self.file_list = InteractiveQListDragAndDrop(main_window=self)
        self.file_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)

        model = self.file_list.model()
        if model:
            model.rowsInserted.connect(self._update_item_numbers)
            model.rowsRemoved.connect(self._update_item_numbers)
            model.rowsMoved.connect(self._update_item_numbers)

        hint_label = QLabel("Drag to reorder")
        hint_label.setObjectName("hint")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete")
        self.trash_button = QPushButton("Trash")
        self.save_button = QPushButton("Save PDF")
        self.save_button.setObjectName("primary")

        self.delete_button.setToolTip("Delete or Backspace")

        self.add_button.clicked.connect(self.show_file_select_dialog)
        self.delete_button.clicked.connect(self.remove_selected_item)
        self.trash_button.clicked.connect(self.show_trashcan_dialog)
        self.save_button.clicked.connect(self.save_file)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.trash_button)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)
        main_layout.addWidget(self.file_list, 1)
        main_layout.addWidget(hint_label)
        main_layout.addSpacing(4)
        main_layout.addLayout(button_row)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def _update_item_numbers(self) -> None:
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data:
                    file_path, page_num = data
                    filename = file_path.split("/")[-1].split("\\")[-1]
                    item.setText(f"{i + 1}. {filename}\nPage {page_num + 1}")

    def _setup_shortcuts(self) -> None:
        delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        delete_shortcut.activated.connect(self.remove_selected_item)

        backspace_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        backspace_shortcut.activated.connect(self.remove_selected_item)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        if item.icon():
            width, height = get_page_size()
            pixmap = item.icon().pixmap(QSize(width, height))
            dialog = PreviewDialog(pixmap, "Page Preview", self)
            dialog.exec()

    def remove_selected_item(self) -> None:
        selected_item = self.file_list.takeItem(self.file_list.currentRow())
        if selected_item:
            self.deleted_items.append(selected_item)

    def show_trashcan_dialog(self) -> None:
        dialog = TrashCanDialog(self.deleted_items, self)
        dialog.item_restored.connect(self.restore_deleted_item)
        dialog.exec()

    def restore_deleted_item(self, item: QListWidgetItem) -> None:
        for deleted_item in self.deleted_items:
            if deleted_item.text() == item.text():
                self.file_list.addItem(deleted_item)
                self.deleted_items.remove(deleted_item)
                break

    def show_file_select_dialog(self) -> None:
        dialog = FileSelectDialog(self)
        if dialog.exec():
            selected_files = dialog.get_selected_files()
            if selected_files:
                self.upload_pdfs(selected_files)

    def upload_pdfs(self, files: list[str]) -> None:
        if not files:
            return

        worker = PdfToIcon(self.file_list, files)

        progress = QProgressDialog("Loading PDFs...", None, 0, 0, self)
        progress.setWindowTitle("Loading")
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)

        worker.finished.connect(progress.close)
        progress.show()
        worker.start()

        while worker.isRunning():
            QApplication.processEvents()

    def save_file(self) -> None:
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "PDF Merger", "No pages to save.")
            return

        writer = PdfWriter()
        for i in range(self.file_list.count()):
            page_item = self.file_list.item(i)
            if not page_item:
                continue
            file_path, page_num = page_item.data(Qt.ItemDataRole.UserRole)
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                writer.add_page(reader.pages[page_num])

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        try:
            with open(file_path, "wb") as f:
                writer.write(f)
            QMessageBox.information(self, "PDF Merger", "PDF saved successfully.")
        except OSError as e:
            QMessageBox.critical(self, "PDF Merger", f"Could not save file:\n{e}")


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setWindowIcon(QIcon("icon.ico"))

    window = PyPDFMerger()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
