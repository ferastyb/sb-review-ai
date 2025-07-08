import pdfplumber
from openai import OpenAI
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def slice_sections(text):
    labels = ["Effectivity", "Reason", "Description", "Compliance", "Accomplishment Instructions"]
    sections = {}
    for i, label in enumerate(labels):
        try:
            start = text.index(label)
            end = text.index(labels[i + 1]) if i + 1 < len(labels) else len(text)
            sections[label] = text[start:end]
        except ValueError:
            continue
    return sections

def summarize_with_ai(text, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values())

    prompt = f"""
You are an AI assistant helping aircraft technical services engineers extract service bulletin details.

Please return the following fields in JSON format:

- "aircraft": list of models affected
- "ata": ATA chapter number
- "system": affected system or part
- "action": short description of the required action (e.g. inspect, modify, power cycle)
- "compliance": deadline or compliance condition
- "reason": why the SB was issued (safety, reliability, etc.)
- "sb_id": service bulletin reference if available

Bulletin content:
{cleaned_text}
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a structured SB extraction engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content
            json_data = eval(content) if content.strip().startswith("{") else {}
            return json_data

        except Exception as e:
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
