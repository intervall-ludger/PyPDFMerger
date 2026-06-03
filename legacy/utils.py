import fitz
import screeninfo
from PyQt6.QtGui import QPixmap


def get_pdf_thumbnail(file_path: str, page_num: int = 0) -> QPixmap:
    doc = fitz.open(file_path)
    try:
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), dpi=100)
        img_data = pix.tobytes("jpeg")
    finally:
        doc.close()

    pixmap = QPixmap()
    pixmap.loadFromData(img_data, "JPEG")
    return pixmap


def get_start_size() -> tuple[int, int, int, int]:
    monitor = screeninfo.get_monitors()[0]
    width = min(500, monitor.width)
    height = min(800, int(0.85 * monitor.height))
    x = max(0, monitor.x + 100)
    y = max(0, monitor.y + 50)
    return x, y, width, height


def get_page_size() -> tuple[int, int]:
    monitor = screeninfo.get_monitors()[0]
    height = int(0.6 * monitor.height)
    width = int(0.7 * height)
    return width, height
