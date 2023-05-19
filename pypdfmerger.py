import sys

from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QProgressDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from file_select_dialog import FileSelectDialog
from interactive_list import InteractiveQListDragAndDrop
from pdf_to_icon import PdfToIcon


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

        # Add a tooltip to the remove_file_button
        self.remove_file_button.setToolTip("Press the 'Delete' key or click this button to remove an item.")

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

        # Add a shortcut for the delete key
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.remove_selected_item)

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


def main():
    app = QApplication(sys.argv)
    pdf_merger = PyPDFMerger()
    pdf_merger.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
