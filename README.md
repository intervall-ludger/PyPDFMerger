# PyPDFMerger - A PyQt6 Application for Merging PDF Files

`PyPDFMerger` is a simple PyQt6 application for merging multiple PDF files into a single PDF file. It provides drag-and-drop functionality for adding PDF files to the list and reordering them. Users can select specific pages from each PDF to include in the final output file.

![](/assets/show.gif)

### Getting Started
To use PDF Merger, you will need to have Python 3 and the following libraries installed:
- PyQt6
- PyPDF2
- pdf2image

You can install the required libraries using pip:

````bash
pip install PyQt6 PyPDF2 pdf2image pymupdf
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

Once the application is running, you can add PDF files to the list by clicking the "Add Files" button or dragging and dropping files onto the list. You can rearrange the items in the list by dragging and dropping. The "Trash Can" button opens a dialog box where you can recover deleted items. Once you are ready to merge the PDF files, click the "Save" button and select a destination file for the new PDF.

We've also added support for creating standalone executables for easy distribution and use. Using the PyInstaller tool, we have included a script that creates a standalone executable file (.exe). This standalone executable is a self-contained application - it does not require a Python environment on your computer and can be run like any other program.

You can download the standalone exe [here](/dist/pypdfmerger.exe).

The application can also be installed in the traditional way, by running the [InstallerSetup](/Output/PyPDFMergerSetup.exe) in Output and adding **PyPDFMerger** to your programs. If you want to uninstall it, you can do this directly as with other programs. 

### Licence

The application is available under the MIT License and contributions are welcome.
