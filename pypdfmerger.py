import io
import os
import sys

from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPushButton,
    QMessageBox,
    QDialog,
    QAbstractItemView,
    QListView,
)
from pdf2image import convert_from_path
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QProgressDialog

class PdfToIcon(QThread):
    finished = pyqtSignal()
    def __init__(self, window, pdfs):
        super(PdfToIcon, self).__init__()
        self.window = window
        self.pdfs = pdfs

    def run(self):
        for file_path in self.pdfs:
            for page_num in range(len(convert_from_path(file_path))):
                item = QListWidgetItem()
                item.setIcon(
                    QIcon(get_pdf_thumbnail(file_path, page_num=page_num + 1))
                )
                item.setText(os.path.basename(file_path) + f"\n page: {page_num + 1}")
                item.setData(Qt.UserRole, (file_path, page_num))
                self.window.addItem(item)
        self.finished.emit()

class FileSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize the file selection dialog
        self.file_dialog = QFileDialog(self)
        self.file_dialog.setFileMode(QFileDialog.ExistingFiles)
        self.file_dialog.setNameFilter("PDF Files (*.pdf)")

        # Create the widgets
        self.file_list = QListWidget()

        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.show_file_dialog)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        # Create the layout
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.file_list)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.add_files_button)
        self.horizontal_layout.addWidget(self.ok_button)

        self.vertical_layout.addLayout(self.horizontal_layout)

        # Set the main layout
        self.setLayout(self.vertical_layout)
        self.show_file_dialog()

    def show_file_dialog(self):
        # Show the file selection dialog
        if self.file_dialog.exec_():
            # Add the selected files to the list
            selected_files = self.file_dialog.selectedFiles()
            for file_path in selected_files:
                if file_path.endswith(".pdf"):
                    item = QListWidgetItem()
                    item.setText(os.path.basename(file_path))
                    item.setData(Qt.UserRole, file_path)
                    self.file_list.addItem(item)

    def get_selected_files(self):
        # Return the selected file paths
        file_paths = []
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            file_paths.append(item.data(Qt.UserRole))
        return file_paths


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


class PyPDFMerger(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the main window
        self.setWindowTitle("Py PDF Merger")
        self.setGeometry(100, 100, 400, 800)

        # Create the widgets
        self.file_list = InteractiveQListDragAndDrop()

        self.remove_file_button = QPushButton("Delete")
        self.save_button = QPushButton("Save")

        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.show_file_select_dialog)

        # Create the layout
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.file_list)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.add_files_button)
        self.vertical_layout.addWidget(self.remove_file_button)
        self.vertical_layout.addWidget(self.save_button)

        # Set the main layout
        self.setLayout(self.vertical_layout)

        # Connect the signals and slots
        self.remove_file_button.clicked.connect(self.remove_selected_item)
        self.save_button.clicked.connect(self.save_file)

    def show_file_select_dialog(self):
        file_select_dialog = FileSelectDialog(self)
        if file_select_dialog.exec_():
            selected_files = file_select_dialog.get_selected_files()
            worker = PdfToIcon(self.file_list, selected_files)

            loading = QProgressDialog("Loading...", None, 0, 0)
            loading.setWindowTitle("PDF Reader")
            loading.setCancelButton(None)
            loading.setWindowModality(2)

            worker.finished.connect(loading.close)

            loading.show()

            worker.start()

            while worker.isRunning():
                QApplication.processEvents()

    def remove_selected_item(self):
        # Remove the selected file from the list
        selected_item = self.file_list.currentItem()
        if selected_item:
            self.file_list.takeItem(self.file_list.currentRow())

    def save_file(self):
        # Create a PdfFileWriter object and add the pages from the selected PDF files in the new order
        writer = PdfWriter()
        for i in range(self.file_list.count()):
            page_item = self.file_list.item(i)
            file_path, page_num = page_item.data(Qt.UserRole)

            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                page = reader.pages[page_num]
                writer.add_page(page)

        # Open a file dialog to select a destination file for the new PDF
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("pdf")
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        if file_dialog.exec_():
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


def get_pdf_thumbnail(file_path, page_num=1):
    # Convert the PDF file to a JPEG image using pdf2image
    images = convert_from_path(file_path, dpi=50)
    img_bytes = io.BytesIO()
    if page_num <= len(images):
        images[page_num - 1].save(img_bytes, format="JPEG")
    else:
        return None

    # Convert the JPEG image to a QPixmap
    img_bytes.seek(0)
    img_data = img_bytes.read()
    qimg = QPixmap()
    qimg.loadFromData(img_data)
    return qimg


def main():
    app = QApplication(sys.argv)
    pdf_merger = PyPDFMerger()
    pdf_merger.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
