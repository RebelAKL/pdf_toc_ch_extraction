# PDF Chapter Extractor

## Overview
This project automates the extraction of a specific chapter ("FINDINGS") from multiple PDFs, identifies its start and end pages, and saves the extracted content into an Excel file while handling large text properly.

## Features
- Extracts text from PDFs (pages 2-10) to identify the Table of Contents.
- Uses regex to locate the start and end pages of the "FINDINGS" chapter.
- Extracts the full content of the chapter, including tables.
- Supports multilingual PDFs.
- Stores extracted content in an Excel file, handling long text across multiple cells.

## Requirements
- Python 3.8+
- Dependencies: Install via `pip install -r requirements.txt`

## Usage
1. Place PDFs in the `PDF_FILES` folder.
2. Run the script:
   ```sh
   python main.py
   ```
3. Output will be saved in `output.xlsx`.

## Folder Structure
```
.
├── PDF_FILES/        # Folder containing input PDFs
├── output.xlsx       # Final extracted data
├── requirements.txt  # Dependencies
├── main.py           # Main script
├── README.md         # Project documentation
```

## License
MIT License

