from PyPDF2 import PdfReader

def extract_pages(pdf_path, start_page, end_page):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            num_pages = len(reader.pages)
            for i in range(start_page - 1, min(end_page, num_pages)):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def extract_toc_pages(pdf_path, toc_start=2, toc_end=12):
    return extract_pages(pdf_path, toc_start, toc_end)
