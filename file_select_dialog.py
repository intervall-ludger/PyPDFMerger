import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


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
