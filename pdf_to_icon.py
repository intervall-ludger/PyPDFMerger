import os
from typing import List

from PyPDF2 import PdfReader
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListWidgetItem

from utils import get_pdf_thumbnail


class PdfToIcon(QThread):
    """
    A QThread subclass that converts PDFs to icons.

    Attributes:
        finished (pyqtSignal): Signal emitted when the thread finishes.
    """
    finished = pyqtSignal()

    def __init__(self, window: 'QListWidget', pdfs: List[str]):
        """
        Initialize the PdfToIcon thread.

        Args:
            window (QListWidget): The QListWidget to add the items to.
            pdfs (List[str]): A list of paths to the PDF files.
        """
        super(PdfToIcon, self).__init__()
        self.window = window
        self.pdfs = pdfs

    def run(self) -> None:
        """
        The main function of the thread. Converts each page of each PDF to an icon and adds it to the QListWidget.
        """
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
