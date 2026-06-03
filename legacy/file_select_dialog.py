import os
from typing import Optional

from PyQt6.QtCore import Qt, QStandardPaths, QSettings
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FileSelectDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select PDF Files")
        self.setMinimumSize(350, 300)

        self.settings = QSettings("PyPDFMerger", "FileSelectDialog")

        self.file_list = QListWidget()

        add_button = QPushButton("Add Files")
        add_button.clicked.connect(self._add_files)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(ok_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(self.file_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self._add_files()

    def _get_last_directory(self) -> str:
        return self.settings.value(
            "lastDirectory",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation),
        )

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            self._get_last_directory(),
            "PDF Files (*.pdf)",
        )
        if not files:
            return

        self.settings.setValue("lastDirectory", os.path.dirname(files[0]))

        for file_path in files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.file_list.addItem(item)

    def get_selected_files(self) -> list[str]:
        files: list[str] = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                files.append(item.data(Qt.ItemDataRole.UserRole))
        return files
