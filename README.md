# PyPDFMerger - A PyQt6 Application for Merging PDF Files

`PyPDFMerger` is a simple PyQt6 application for merging multiple PDF files into a single PDF file. It provides drag-and-drop functionality for adding PDF files to the list and reordering them. Users can select specific pages from each PDF to include in the final output file.

![](/assets/show.gif)

## Getting Started

**Requirements:** Python 3.12+

Install dependencies with uv:

```bash
uv sync
```

## Usage

Run the application:

```bash
uv run pypdfmerger.py
```

Or use the standalone executable:

```bash
./dist/pypdfmerger.exe
```

The application can also be installed traditionally by running the [InstallerSetup](/Output/PyPDFMergerSetup.exe) and adding **PyPDFMerger** to your programs.

### Features

- Add PDF files via "Add Files" button or drag-and-drop
- Rearrange items by dragging and dropping
- Recover deleted items via "Trash Can" button
- Select specific pages from each PDF
- Merge and save to a new PDF file

## Build

To build the executable:

```bash
uv run --with pyinstaller pyinstaller pypdfmerger.py --onefile --windowed
```

## Licence

MIT License - contributions are welcome.
