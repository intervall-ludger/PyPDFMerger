# PyPDFMerger - A PyQt5 Application for Merging PDF Files

`PyPDFMerger` is a simple PyQt5 application for merging multiple PDF files into a single PDF file. It provides drag-and-drop functionality for adding PDF files to the list and reordering them. Users can select specific pages from each PDF to include in the final output file.

![](/assets/img.png)

### Getting Started
To use PDF Merger, you will need to have Python 3 and the following libraries installed:
- PyQt5
- PyPDF2
- pdf2image

You can install the required libraries using pip:

````bash
pip install PyQt5 PyPDF2 pdf2image pymupdf
````

or alternative with poetry:

````bash
poetry install
````

### Usage
To run PDF Merger, simply run the following command:

````bash
python pypdfmerger.py
````

or as executable file.

````bash
./dist/pypdfmerger.exe
````
**or use the traditional installer setup under windows.** (see for this below)

Once the application is running, you can add PDF files to the list by clicking the "Add Files" button or dragging and dropping files onto the list. You can rearrange the items in the list by dragging and dropping. The "Trash Can" button opens a dialog box where you can recover deleted items. Once you are ready to merge the PDF files, click the "Save" button and select a destination file for the new PDF.

You can download the standalone exe [here](/dist/pypdfmerger.exe).

The application can also be installed in the traditional way, by running the [InstallerSetup](/Output/PyPDFMergerSetup.exe) in Output and adding **PyPDFMerger** to your programs. If you want to uninstall it, you can do this directly as with other programs. 

### Licence

The application is available under the MIT License and contributions are welcome.
