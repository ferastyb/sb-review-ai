import pdfplumber
from openai import OpenAI
import os
import time
import json

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
Extract the following fields from this aircraft service bulletin.
Return ONLY valid JSON in this format:

{{
  "aircraft": [],
  "ata": "",
  "system": "",
  "action": "",
  "compliance": "",
  "reason": "",
  "sb_id": ""
}}

Bulletin:
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
            print("🧠 GPT raw response:", content)

            try:
                json_data = json.loads(content)
                return json_data
            except json.JSONDecodeError:
                print("❌ Failed to parse GPT response. Returning empty dictionary.")
                return {"error": "Invalid JSON from GPT"}

        except Exception as e:
            print(f"⚠️ GPT request error: {e}")
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
