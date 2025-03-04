# main.py
import os
import pandas as pd
from pdf_extractor import extract_toc_pages, extract_pages
from llm_toc_parser import query_ollama_for_boundaries, FINDINGS_TERMS

PDF_FOLDER = "PDF_FILES"
OUTPUT_FILE = "findings_extracted.xlsx"
MAX_CELL_LENGTH = 32000  

def split_text_into_chunks(text, max_length=MAX_CELL_LENGTH):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def process_pdfs():
    results = []
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        print(f"Processing: {pdf_file}")
        
        toc_text = extract_toc_pages(pdf_path)
        if not toc_text.strip():
            print(f"TOC extraction failed for {pdf_file}. Skipping.")
            continue
        boundaries = query_ollama_for_boundaries(toc_text)
        if not boundaries:
            print(f"No section boundaries extracted for {pdf_file}. Skipping.")
            continue
        findings_boundaries = []
        for item in boundaries:
            section_name = item.get("section", "")
            if any(term.lower() in section_name.lower() for term in FINDINGS_TERMS):
                findings_boundaries.append(item)
        
        if not findings_boundaries:
            print(f"No findings sections detected in {pdf_file}.")
            results.append({
                "PDF Name": pdf_file,
                "Section": "FINDINGS",
                "Content Part 1": "No findings section extracted."
            })
            continue
    
        for item in findings_boundaries:
            section_name = item.get("section", "FINDINGS")
            start_page = item.get("start_page", 0)
            end_page = item.get("end_page", 0)
            if start_page == 0 or end_page == 0 or start_page > end_page:
                print(f"Invalid boundaries for section '{section_name}' in {pdf_file}. Skipping section.")
                continue
            section_text = extract_pages(pdf_path, start_page, end_page)
            chunks = split_text_into_chunks(section_text)
            row = {"PDF Name": pdf_file, "Section": section_name}
            for i, chunk in enumerate(chunks):
                row[f"Content Part {i+1}"] = chunk
            results.append(row)
    
    if results:
        df = pd.DataFrame(results)
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"Results saved to {OUTPUT_FILE}")
    else:
        print("No findings extracted from any PDFs.")

if __name__ == "__main__":
    process_pdfs()
