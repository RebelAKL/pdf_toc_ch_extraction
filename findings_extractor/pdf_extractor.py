from PyPDF2 import PdfReader

def extract_probable_toc_pages(pdf_path, start_page=2, end_page=12):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            num_pages = len(reader.pages)
            for i in range(start_page - 1, min(end_page, num_pages)):  
                text += reader.pages[i].extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text
