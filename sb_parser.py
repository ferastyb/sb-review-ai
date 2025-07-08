import pdfplumber
from openai import OpenAI
import os
import time
import json
import re
from datetime import datetime, timedelta

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

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

def parse_compliance_days(compliance_text):
    match = re.search(r"(\d+)\s*(calendar|flight)?\s*day", compliance_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def summarize_with_ai(text, inspection_date=None, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values()) if sections else text

    prompt = f"""
You are an AI assistant extracting structured data from aircraft service bulletins.

Return only valid JSON. Follow this structure exactly:

{{
  "aircraft": ["model1", "model2"],
  "ata": "ATA chapter number",
  "system": "Affected system or part",
  "action": "Brief action (e.g. modify, inspect, power cycle)",
  "compliance": "Compliance recommendation or deadline",
  "reason": "Reason for issuance",
  "sb_id": "Service Bulletin number"
}}

Text:
\"\"\"
{cleaned_text}
\"\"\"
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

            content = response.choices[0].message.content.strip()
            print("🧠 GPT Response:", content)

            match = re.search(r"\{[\s\S]*\}", content)
            if not match:
                return {"error": "Invalid JSON from GPT"}

            result = json.loads(match.group())

            # Try parsing compliance time
            compliance_text = result.get("compliance", "")
            days = parse_compliance_days(compliance_text)
            result["compliance_time_days"] = days

            # Optional: Check compliance if reference date is given
            if inspection_date and days:
                deadline = inspection_date + timedelta(days=days)
                result["is_compliant"] = datetime.today().date() <= deadline.date()
            else:
                result["is_compliant"] = None

            return result

        except Exception as e:
            print(f"⚠️ GPT call failed (attempt {attempt + 1}): {e}")
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
