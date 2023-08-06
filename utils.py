import fitz
import screeninfo
from PyQt6.QtGui import QPixmap


def get_pdf_thumbnail(file_path, page_num=0):  # PyMuPDF uses zero-based page numbering
    # Open the PDF file with PyMuPDF
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)

    # Render the page to a pixmap, scale it, and get the image data
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))  # Adjust the matrix values to scale the image
    img_data = pix.tobytes("jpeg")

    # Convert the image data to a QPixmap
    qimg = QPixmap()
    qimg.loadFromData(img_data, "JPEG")
    return qimg

def get_start_size():
    monitor_info = screeninfo.get_monitors()[0]
    return 100, min(100, int(0.9 * monitor_info.height)), min(400, monitor_info.width), min(800, int(0.9 * monitor_info.height))

def get_page_size():
    # A4 - 210 x 297
    monitor_info = screeninfo.get_monitors()[0]
    size_ = int(0.6 * monitor_info.height)
    return int(0.7 * size_), size_
