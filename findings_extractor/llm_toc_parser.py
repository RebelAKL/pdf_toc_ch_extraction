# llm_toc_parser.py
import json
import subprocess
import tempfile

FINDINGS_TERMS = [
    "FINDINGS", "MAIN FINDINGS", "FINDINGS OF THE EVALUATION", "FINDINGS AND ANALYSIS",
    "CROSS-CUTTING ISSUES", "HALLAZGOS Y ANÁLISIS DE DATOS", "HALLAZGOS DE LA EVALUACIÓN",
    "HALLAZGOS", "CRITÈRES DE L’ÉVALUATION", "RESULTADOS O HALLAZGOS DE LA EVALUACIÓN",
    "UM PANORAMA DAS PERCEPÇÕES E DESCOBERTAS", "EM DESTAQUE", "RESULTADOS E CONCLUSÕES PRELIMINARES",
    "CADRE DE L’ÉVALUATION ET MÉTHODES"
]

def query_ollama_for_boundaries(toc_text):
    """
    Sends the TOC text to Ollama (DeepSeek-R1:8b) to get the start and end pages for sections
    matching our keywords. The LLM should return a JSON array of objects like:
      { "section": "<Section Name>", "start_page": <number>, "end_page": <number> }
    """
    prompt = f"""
You are an expert document analyzer. Given the following Table of Contents (TOC) text extracted from a PDF,
identify the start and end page numbers for each section that corresponds to one of these headings:
{', '.join(FINDINGS_TERMS)}.
For each matching section, output an object with:
  - "section": the section heading as it appears in the document.
  - "start_page": the page number where the section begins.
  - "end_page": the page number where the section ends (i.e. one page before the next section starts,
    or the end of the document if it is the last section).
Return the output as a JSON array.
TOC Text:
\"\"\"{toc_text}\"\"\"
"""
    try:
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as temp_file:
            temp_file.write(prompt)
            temp_file.seek(0)
            process = subprocess.Popen(
                ["ollama", "run", "deepseek-r1:8b"],
                stdin=temp_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate()
        if error:
            print(f"Ollama error: {error}")
        try:
            boundaries = json.loads(output.strip())
            return boundaries
        except json.JSONDecodeError:
            print("Error: Unable to parse LLM response as JSON.")
            return []
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return []
