import io

from PyQt5.QtGui import QPixmap
from pdf2image import convert_from_path


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
