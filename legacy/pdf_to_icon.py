import os

from PyPDF2 import PdfReader
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from utils import get_pdf_thumbnail


class PdfToIcon(QThread):
    finished = pyqtSignal()

    def __init__(self, target_list: QListWidget, pdf_paths: list[str]):
        super().__init__()
        self.target_list = target_list
        self.pdf_paths = pdf_paths

    def run(self) -> None:
        for pdf_path in self.pdf_paths:
            reader = PdfReader(pdf_path)
            filename = os.path.basename(pdf_path)

            for page_num in range(len(reader.pages)):
                item = QListWidgetItem()
                item.setIcon(QIcon(get_pdf_thumbnail(pdf_path, page_num)))
                idx = self.target_list.count() + 1
                item.setText(f"{idx}. {filename}\nPage {page_num + 1}")
                item.setData(Qt.ItemDataRole.UserRole, (pdf_path, page_num))
                self.target_list.addItem(item)

        self.finished.emit()
