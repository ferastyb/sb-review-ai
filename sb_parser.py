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

def summarize_with_ai(text, delivery_date=None, aircraft_number=None, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values()) if sections else text

    prompt = f'''
You are an AI assistant helping extract structured data from aircraft service bulletins. 
Return only valid JSON in this format:

{{
  "aircraft": ["model1", "model2"],
  "ata": "ATA chapter number",
  "system": "Affected system or part",
  "action": "Brief action (e.g. inspect, modify, power cycle)",
  "compliance": {{
    "raw": "original compliance text",
    "due_date": "YYYY-MM-DD" (if mentioned),
    "days_after_delivery": number of days (if deadline is relative)
  }},
  "reason": "Why this SB was issued",
  "sb_id": "Service Bulletin identifier"
}}

If a date is relative (e.g. "within 30 days of delivery"), extract it as `days_after_delivery`. 
If an exact due date is mentioned (e.g. "by 2025-10-01"), extract it as `due_date`.

Text:
"""
{cleaned_text}
"""
'''

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a structured SB parsing engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content.strip()

            print("\n📤 GPT-4 raw output:\n", content)

            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                match = re.search(r"\{[\s\S]*\}", content)
                if match:
                    result = json.loads(match.group())
                else:
                    return {"error": "Invalid JSON from GPT-4"}

            # Compliance math
            if delivery_date and isinstance(result.get("compliance"), dict):
                delivery_dt = datetime.strptime(delivery_date, "%Y-%m-%d")
                compliance = result["compliance"]
                if "days_after_delivery" in compliance:
                    result["compliance"]["calculated_due"] = (
                        delivery_dt + timedelta(days=compliance["days_after_delivery"])
                    ).strftime("%Y-%m-%d")
                elif "due_date" in compliance:
                    result["compliance"]["calculated_due"] = compliance["due_date"]

                if "calculated_due" in result["compliance"]:
                    result["compliance"]["is_due"] = datetime.today().date() >= datetime.strptime(result["compliance"]["calculated_due"], "%Y-%m-%d").date()

            return result

        except Exception as e:
            print(f"⚠️ GPT-4 call failed on attempt {attempt+1}: {e}")
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
