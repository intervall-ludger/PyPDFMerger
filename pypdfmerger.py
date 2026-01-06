import sys
from typing import List, Optional

from PyPDF2 import PdfReader, PdfWriter
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QKeySequence, QIcon, QShortcut
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
)

from file_select_dialog import FileSelectDialog
from interactive_list import InteractiveQListDragAndDrop
from pdf_to_icon import PdfToIcon
from utils import get_start_size


class TrashCanDialog(QDialog):
    """
    A dialog representing a trash can where deleted items are temporarily stored.
    Provides the ability to restore deleted items.
    """

    # item_restored: pyqtSignal[QListWidgetItem] = pyqtSignal(QListWidgetItem)
    item_restored = pyqtSignal(QListWidgetItem)

    def __init__(
        self, deleted_items: List[QListWidgetItem], parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize the TrashCanDialog.

        Args:
            deleted_items (List[QListWidgetItem]): List of items that were deleted.
            parent (Optional[QWidget], optional): Parent widget. Defaults to None.
        """
        super(TrashCanDialog, self).__init__(parent)

        self.setWindowTitle("TrashCan")
        geometry = get_start_size()
        self.setGeometry(geometry[0] + 400, geometry[1], geometry[2], geometry[3])

        self.deleted_items = QListWidget()
        for item in deleted_items:
            self.deleted_items.addItem(item.clone())

        self.restore_button = QPushButton("Restore")
        self.restore_button.clicked.connect(self.restore_deleted_item)

        layout = QVBoxLayout()
        layout.addWidget(self.deleted_items)
        layout.addWidget(self.restore_button)
        self.setLayout(layout)

        self.deleted_items.setIconSize(QSize(164, 164))

    def restore_deleted_item(self) -> None:
        """
        Restore the selected deleted item and close the dialog.
        """
        selected_item = self.deleted_items.takeItem(self.deleted_items.currentRow())
        if selected_item:
            self.item_restored.emit(selected_item.clone())
            self.close()


class PyPDFMerger(QWidget):
    """Main widget for the Py PDF Merger application."""

    def __init__(self) -> None:
        """Initialize the PyPDFMerger widget."""
        super().__init__()

        # Initialize the main window
        self.setWindowTitle("Py PDF Merger")

        geometry = get_start_size()
        self.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])

        # Create the widgets
        self.file_list = InteractiveQListDragAndDrop(main_window=self)

        # Define a list to store the deleted items
        self.deleted_items = []

        self.remove_file_button = QPushButton("Delete")
        self.trashcan_button = QPushButton("Trash")
        self.save_button = QPushButton("Save")

        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.show_file_select_dialog)

        self.remove_file_button.clicked.connect(self.remove_selected_item)
        self.trashcan_button.clicked.connect(self.show_trashcan_dialog)
        self.save_button.clicked.connect(self.save_file)

        # Create the layout
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.file_list)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.add_files_button)
        self.vertical_layout.addWidget(self.remove_file_button)
        self.vertical_layout.addWidget(self.trashcan_button)
        self.vertical_layout.addWidget(self.save_button)

        # Add a tooltip to the remove_file_button
        self.remove_file_button.setToolTip(
            "Press the 'Delete' key or click this button to remove an item."
        )

        # Add a shortcut for the delete key
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.remove_selected_item)

        # Set the main layout
        self.setLayout(self.vertical_layout)

    def remove_selected_item(self) -> None:
        """Remove the selected item from the file list."""
        selected_item = self.file_list.takeItem(self.file_list.currentRow())
        if selected_item:
            self.deleted_items.append(selected_item)

    def show_trashcan_dialog(self) -> None:
        """Open the trash can dialog to view and potentially restore deleted items."""
        self.trashcan_dialog = TrashCanDialog(self.deleted_items, self)
        self.trashcan_dialog.item_restored.connect(self.restore_deleted_item)
        self.trashcan_dialog.exec()

    def restore_deleted_item(self, item) -> None:
        """
        Restore a deleted item to the file list.

        Args:
            item: The item to restore.
        """
        # Search for the item in self.deleted_items by comparing text
        for deleted_item in self.deleted_items:
            if deleted_item.text() == item.text():
                self.file_list.addItem(deleted_item)
                self.deleted_items.remove(deleted_item)
                break

    def show_file_select_dialog(self) -> None:
        """Open the file selection dialog."""
        file_select_dialog = FileSelectDialog(self)
        if file_select_dialog.exec():
            selected_files = file_select_dialog.get_selected_files()
            self.upload_pdfs(selected_files)

    def upload_pdfs(self, files: List[str]) -> None:
        """
        Upload PDFs and display them in the widget.

        Args:
            files (List[str]): List of file paths to upload.
        """
        worker = PdfToIcon(self.file_list, files)

        loading = QProgressDialog("Loading...", None, 0, 0, self)
        loading.setWindowTitle("PDF Reader")
        loading.setCancelButton(None)
        loading.setWindowModality(Qt.WindowModality.ApplicationModal)

        worker.finished.connect(loading.close)

        loading.show()

        worker.start()

        while worker.isRunning():
            QApplication.processEvents()

    def save_file(self) -> None:
        writer = PdfWriter()
        for i in range(self.file_list.count()):
            page_item = self.file_list.item(i)
            if not page_item:
                continue
            file_path, page_num = page_item.data(Qt.ItemDataRole.UserRole)

            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                page = reader.pages[page_num]
                writer.add_page(page)

        # Open a file dialog to select a destination file for the new PDF
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix("pdf")
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        if file_dialog.exec():
            # Get the selected file path and extension
            file_path = file_dialog.selectedFiles()[0]
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"

            # Write the new PDF file
            try:
                with open(file_path, "wb") as f:
                    writer.write(f)
                QMessageBox.information(
                    self, "PDF Merger", "PDF file successfully saved."
                )
            except:
                QMessageBox.critical(
                    self, "PDF Merger", "Error occurred while saving the PDF file."
                )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("icon.ico"))
    pdf_merger = PyPDFMerger()
    pdf_merger.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
