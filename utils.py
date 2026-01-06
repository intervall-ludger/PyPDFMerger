import fitz
import screeninfo
from PyQt6.QtGui import QPixmap
from typing import Tuple


def get_pdf_thumbnail(file_path: str, page_num: int = 0) -> QPixmap:
    """
    Generate a thumbnail of a specific page in a PDF file.

    Args:
        file_path (str): The path to the PDF file.
        page_num (int, optional): The page number to generate a thumbnail for. Defaults to 0.

    Returns:
        QPixmap: The QPixmap object of the thumbnail.
    """
    # Open the PDF file with PyMuPDF
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)

    # Render the page to a pixmap, scale it, and get the image data
    pix = page.get_pixmap(
        matrix=fitz.Matrix(1, 1), dpi=100
    )  # Adjust the matrix values to scale the image
    img_data = pix.tobytes("jpeg")

    # Convert the image data to a QPixmap
    qimg = QPixmap()
    qimg.loadFromData(img_data, "JPEG")
    return qimg


def get_start_size() -> Tuple[int, int, int, int]:
    monitor_info = screeninfo.get_monitors()[0]
    width = min(400, monitor_info.width)
    height = min(800, int(0.9 * monitor_info.height))
    x = max(0, monitor_info.x + 100)
    y = max(0, monitor_info.y + 100)
    return (x, y, width, height)


def get_page_size() -> Tuple[int, int]:
    """
    Get the size of the page.

    Returns:
        Tuple[int, int]: A tuple containing the width and height of the page.
    """
    # A4 - 210 x 297
    monitor_info = screeninfo.get_monitors()[0]
    size_ = int(0.6 * monitor_info.height)
    return int(0.7 * size_), size_
