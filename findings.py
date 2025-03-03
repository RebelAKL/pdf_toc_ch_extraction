import os
import re
import pandas as pd
from io import StringIO
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage

def convert_pdf_to_text(pdf_path, txt_path):
    """Convert PDF file to text file with layout preservation."""
    try:
        rsrcmgr = PDFResourceManager()
        output_str = StringIO()
        laparams = LAParams(all_texts=True)
        device = TextConverter(rsrcmgr, output_str, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        with open(pdf_path, 'rb') as f:
            for page in PDFPage.get_pages(f):
                interpreter.process_page(page)
        
        text = output_str.getvalue()
        
        device.close()
        output_str.close()

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        return False

def is_toc_line(line):
    """Identify table of contents lines with improved accuracy."""
    toc_patterns = [
        r'^\s*\d+(\.\d+)*\s+.*?\.{3,}\s*\d+\s*$',  # Section numbers with dots
        r'^\s*.*?\b(page|pg|pág)\s+\d+\s*$',        # Page number references
        r'^\s*(table\s+of\s+contents|contents)\b',   # TOC headers
        r'^\s*\.{4,}\s*$',                          # Line of dots
        r'^\s*\d+\s*$',                             # Standalone page numbers
        r'^\s*(annex|appendix)\s+[a-z0-9]+\b',      # Annex/appendix references
    ]
    return any(re.search(p, line, re.IGNORECASE) for p in toc_patterns)

def is_section_header(line, patterns):
    """Check if a line matches any of the given section header patterns."""
    return any(re.search(pattern, line.lower()) for pattern in patterns)

def extract_findings_sections(text):
    """
    Extract the full 'Key findings' section from the text.
    Captures everything between 'Key findings' and the next major section header.
    """
    # Define patterns for section headers
    start_patterns = [
        r'^\s*\d*\.?\s*main\s+findings\b',
        r'^\s*\d*\.?\s*key\s+findings\b',
        r'^\s*\d*\.?\s*principal\s+hallazgos\b',
        r'^\s*findings\s+and\s+analysis\b',
        r'^\s*evaluation\s+results\b',
    ]
    
    end_patterns = [
        r'^\s*\d*\.?\s*recommendations\b',
        r'^\s*\d*\.?\s*conclusions?\b',
        r'^\s*\d*\.?\s*methodology\b',
        r'^\s*\d*\.?\s*approach\b',
        r'^\s*\d*\.?\s*next\s+steps\b',
        r'^\s*\d*\.?\s*references\b',
        r'^\s*\d*\.?\s*appendix\b',
        r'^\s*\d*\.?\s*annex\b',
    ]

    findings_sections = []
    lines = text.split('\n')
    current_section = []
    in_findings = False
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        
        # Skip empty lines at the start
        if not clean_line and not current_section:
            continue
            
        # Check if this is the start of a findings section
        if not in_findings and is_section_header(clean_line, start_patterns):
            if not is_toc_line(clean_line):
                in_findings = True
                current_section.append(clean_line)
                continue
        
        # If we're in a findings section, check if we've reached the end
        if in_findings:
            if is_section_header(clean_line, end_patterns):
                # Save the current section and reset
                if current_section:
                    findings_sections.append('\n'.join(current_section))
                current_section = []
                in_findings = False
            else:
                # Remove trailing page numbers and add the line if it's not a TOC line
                if not is_toc_line(clean_line):
                    clean_line = re.sub(r'\s*\d+\s*$', '', clean_line)
                    if clean_line:
                        current_section.append(clean_line)

    # Add the last section if we're still in findings
    if in_findings and current_section:
        findings_sections.append('\n'.join(current_section))
    
    return findings_sections

def process_documents(input_dir, output_dir):
    """Process all PDFs in the input directory and save the extraction results."""
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, 'temp_texts')
    os.makedirs(temp_dir, exist_ok=True)
    
    results = []
    
    # Convert PDFs to text files
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            txt_path = os.path.join(temp_dir, f"{os.path.splitext(filename)[0]}.txt")
            if convert_pdf_to_text(pdf_path, txt_path):
                print(f"Converted: {filename}")
    
    # Process each text file for the findings sections
    for txt_file in os.listdir(temp_dir):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(temp_dir, txt_file)
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            findings = extract_findings_sections(text)
            if findings:
                results.append({
                    'Document': txt_file,
                    'Main Findings': '\n\n'.join(findings)
                })
                print(f"Processed: {txt_file}")
            else:
                print(f"No findings extracted for: {txt_file}")
    
    # Save results to an Excel file if any findings were extracted
    if results:
        df = pd.DataFrame(results)
        output_path = os.path.join(output_dir, 'extracted_findings.xlsx')
        df.to_excel(output_path, index=False)
        print(f"Results saved to {output_path}")
        return df
    else:
        print("No findings extracted")
        return pd.DataFrame()

if __name__ == "__main__":
    input_directory = "files"       # Update with your PDF directory path
    output_directory = "results"    # Update with your desired output directory
    
    process_documents(input_directory, output_directory)