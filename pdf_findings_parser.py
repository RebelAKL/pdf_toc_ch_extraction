import pymupdf, fitz
import re
import pandas as pd
import os

EXCEL_CHAR_LIMIT = 32767  

FINDINGS_TERMS = [
    "FINDINGS", "MAIN FINDINGS", "FINDINGS OF THE EVALUATION", "FINDINGS AND ANALYSIS",
    "CROSS-CUTTING ISSUES", "HALLAZGOS Y ANÁLISIS DE DATOS", "HALLAZGOS DE LA EVALUACIÓN",
    "HALLAZGOS", "CRITÈRES DE L’ÉVALUATION", "RESULTADOS O HALLAZGOS DE LA EVALUACIÓN",
    "UM PANORAMA DAS PERCEPÇÕES E DESCOBERTAS", "EM DESTAQUE", "RESULTADOS E CONCLUSÕES PRELIMINARES",
    "CADRE DE L’ÉVALUATION ET MÉTHODES"
]

def extract_text_from_pdf(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page - 1, end_page):
        text += doc[page_num].get_text("text") + "\n\n"
    return text

def find_chapter_pages(toc_text):
    pattern = r'^\s*(\d*\.*\s*)?([A-Z][A-Z\s\-]+)\s*[\.…]*\s*(\d+)\s*$'
    matches = re.findall(pattern, toc_text, re.MULTILINE)
    
    chapters = []
    for match in matches:
        _, title, page = match
        title = title.strip()
        page = int(page)
        chapters.append((title, page))
    
    start_page = end_page = None
    for i, (title, page) in enumerate(chapters):
        if any(title.lower() == term.lower() for term in FINDINGS_TERMS):
            start_page = page
            if i + 1 < len(chapters):
                end_page = chapters[i + 1][1] - 1 
            break

    return start_page, end_page

def split_text_into_cells(text, max_length=EXCEL_CHAR_LIMIT):
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    return chunks

def process_pdfs(pdf_folder, output_excel):
    data = []
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        toc_text = extract_text_from_pdf(pdf_path, 2, 10)
        start_page, end_page = find_chapter_pages(toc_text)
        if start_page and end_page:
            findings_text = extract_text_from_pdf(pdf_path, start_page, end_page)
            print(f"Processed {pdf_file}: Findings from page {start_page} to {end_page}")
        else:
            findings_text = "Findings section not found."
            print(f"Skipping {pdf_file}: Findings section not detected")
        text_chunks = split_text_into_cells(findings_text)
        row_data = [pdf_file] + text_chunks
        data.append(row_data)
    max_columns = max(len(row) for row in data) 
    column_names = ["PDF Name"] + [f"Extracted Text (Part {i})" for i in range(1, max_columns)]

    df = pd.DataFrame(data, columns=column_names)
    
    df.to_excel(output_excel, index=False)
    print(f"Results saved to {output_excel}")

pdf_folder = "PDF_FILES"
output_excel = "findings_extracted.xlsx"

process_pdfs(pdf_folder, output_excel)
