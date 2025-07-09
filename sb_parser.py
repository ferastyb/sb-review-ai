import pdfplumber
from openai import OpenAI
import os
import time
import json
import re
from datetime import date

# Load API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Slice known sections
def slice_sections(text):
    labels = [
        "Effectivity", "Applicability", "Affected Aircraft",
        "Reason", "Background", "Description",
        "Compliance", "Action", "Accomplishment Instructions"
    ]
    sections = {}
    for i, label in enumerate(labels):
        try:
            start = text.index(label)
            end = text.index(labels[i + 1]) if i + 1 < len(labels) else len(text)
            sections[label] = text[start:end]
        except ValueError:
            continue
    return sections

# Summarize SB using GPT
def summarize_with_ai(text, delivery_date=None, aircraft_number=None, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values()) if sections else text

    prompt = f"""
You are an AI assistant that extracts structured information from aircraft service bulletins.

Return only **valid JSON** using the exact format below:

{{
  "aircraft": ["model1", "model2"],
  "ata": "ATA chapter number",
  "system": "Affected system or part",
  "action": "Brief action (e.g. modify, inspect, power cycle)",
  "compliance": "Compliance deadline or instructions",
  "reason": "Why this bulletin is issued",
  "sb_id": "Service Bulletin number",
  "group": "Group number if specified (e.g. Group 1)",
  "is_compliant": true or false
}}

Context:
- Aircraft Number: {aircraft_number}
- Delivery or Inspection Date: {delivery_date}
- Today’s Date: {date.today()}

You must:
- Identify the aircraft group based on number ranges if present.
- Extract and interpret compliance instructions.
- Set `is_compliant` based on whether this aircraft meets the compliance requirement.

Bulletin Text:
\"\"\"
{cleaned_text}
\"\"\"
"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a structured SB extraction engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            # Try parsing full response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try extracting a JSON block from the response
                match = re.search(r"\{[\s\S]*\}", content)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
                        return {"error": "Still invalid after cleanup"}
                return {"error": "Invalid JSON from GPT"}

        except Exception as e:
            print(f"⚠️ GPT call failed on attempt {attempt+1}: {e}")
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
