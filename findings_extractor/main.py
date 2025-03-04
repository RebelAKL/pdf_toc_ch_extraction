import os
import pandas as pd
from pdf_extractor import extract_probable_toc_pages
from llm_extraction import query_ollama

PDF_FOLDER = "PDF_FILES"
OUTPUT_FILE = "findings.xlsx"

def process_pdfs():

    results = []
    
    for pdf_file in os.listdir(PDF_FOLDER):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, pdf_file)
            print(f"Processing: {pdf_file}")
            extracted_text = extract_probable_toc_pages(pdf_path)

            if not extracted_text.strip():
                print(f"No text extracted from {pdf_file}. Skipping.")
                continue
            findings = query_ollama(extracted_text)
            results.append({"PDF Name": pdf_file, "Findings": "\n".join(findings)})


    if results:
        df = pd.DataFrame(results)
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"Results saved to {OUTPUT_FILE}")
    else:
        print("No findings extracted.")

if __name__ == "__main__":
    process_pdfs()
