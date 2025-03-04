import json
import subprocess
import tempfile

FINDINGS_ALIASES = [
    "FINDINGS", "MAIN FINDINGS", "FINDINGS OF THE EVALUATION", "FINDINGS AND ANALYSIS",
    "CROSS-CUTTING ISSUES", "HALLAZGOS Y ANÁLISIS DE DATOS", "HALLAZGOS DE LA EVALUACIÓN",
    "HALLAZGOS", "CRITÈRES DE L’ÉVALUATION", "RESULTADOS O HALLAZGOS DE LA EVALUACIÓN",
    "UM PANORAMA DAS PERCEPÇÕES E DESCOBERTAS", "EM DESTAQUE", "RESULTADOS E CONCLUSÕES PRELIMINARES",
    "CADRE DE L’ÉVALUATION ET MÉTHODES"
]

def query_ollama(text):
    prompt = f"""
    You are an expert document processor. Your task is to extract sections related to the following keywords:
    {', '.join(FINDINGS_ALIASES)}.

    Given the following document text, extract all relevant sections:
    \"\"\"{text}\"\"\"

    Return a JSON object with "findings": ["... extracted text ..."].
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
            response = json.loads(output.strip())
            return response.get("findings", ["No relevant findings found."])
        except json.JSONDecodeError:
            return ["Error: Unable to parse LLM response."]

    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return ["Error extracting findings."]
