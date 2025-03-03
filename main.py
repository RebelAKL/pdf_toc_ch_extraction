import fitz
import re
import logging
import os
import pandas as pd
import argparse
from openpyxl import Workbook

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_findings_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        findings_text = ""
        in_findings = False
        pattern_findings = re.compile(r'^\s*\d+\.\s*FINDINGS\b', re.IGNORECASE | re.MULTILINE)
        pattern_next = re.compile(r'^\s*\d+\.\s*[A-Z]', re.MULTILINE)
        for page_num in range(len(doc)):
            page_text = doc[page_num].get_text()
            if not in_findings:
                m = pattern_findings.search(page_text)
                if m:
                    in_findings = True
                    findings_text += page_text[m.end():] + "\n"
            else:
                m_next = pattern_next.search(page_text)
                if m_next:
                    findings_text += page_text[:m_next.start()]
                    break
                else:
                    findings_text += page_text + "\n"
        return findings_text.strip()
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {str(e)}")
        return ""

def process_directory(pdf_dir, output_excel):
    results = []
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    for filename in pdf_files:
        pdf_path = os.path.join(pdf_dir, filename)
        text = extract_findings_from_pdf(pdf_path)
        if text:
            results.append({'PDF Name': filename, 'Findings Content': text})
            logging.info(f"Extracted FINDINGS from {filename}")
        else:
            logging.warning(f"No FINDINGS found in {filename}")
    if results:
        df = pd.DataFrame(results)
        for i, row in df.iterrows():
            content = row['Findings Content']
            if len(content) > 32000:
                parts = [content[j:j+32000] for j in range(0, len(content), 32000)]
                for j, part in enumerate(parts):
                    df.at[i + j, 'Findings Content'] = part
                    df.at[i + j, 'PDF Name'] = row['PDF Name'] if j == 0 else ""
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            worksheet.column_dimensions['A'].width = 40
            worksheet.column_dimensions['B'].width = 120
        logging.info(f"Saved results to {output_excel}")
    else:
        logging.warning("No results to save.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_dir", required=True)
    parser.add_argument("--output_excel", required=True)
    args = parser.parse_args()
    process_directory(args.pdf_dir, args.output_excel)

if __name__ == '__main__':
    main()
