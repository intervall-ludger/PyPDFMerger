import os
from typing import List

from PyPDF2 import PdfReader
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from utils import get_pdf_thumbnail


class PdfToIcon(QThread):
    finished = pyqtSignal()

    def __init__(self, window: QListWidget, pdfs: List[str]):
        super().__init__()
        self.window = window
        self.pdfs = pdfs

    def run(self) -> None:
        for file_path in self.pdfs:
            reader = PdfReader(file_path)
            pdf_page_count = len(reader.pages)
            for page_num in range(pdf_page_count):
                item = QListWidgetItem()
                item.setIcon(QIcon(get_pdf_thumbnail(file_path, page_num=page_num)))
                item.setText(os.path.basename(file_path) + f"\n page: {page_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, (file_path, page_num))
                self.window.addItem(item)
        self.finished.emit()
