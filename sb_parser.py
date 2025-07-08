import pdfplumber
from openai import OpenAI
import os
import time
import json
import re

# Initialize OpenAI client from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Extract full text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Try to extract specific SB sections to reduce GPT input size
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

# Call GPT to extract structured fields
def summarize_with_ai(text, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values())

    prompt = f"""
You are an AI assistant helping extract structured information from aircraft service bulletins.

Your task is to return only valid JSON (no explanation or text around it). Use this format exactly:

{{
  "aircraft": ["model1", "model2"],
  "ata": "ATA chapter number",
  "system": "Affected system or part",
  "action": "Brief action (e.g. modify, inspect, power cycle)",
  "compliance": "Compliance recommendation or deadline",
  "reason": "Why this bulletin is issued (e.g. safety, data update)",
  "sb_id": "Service Bulletin number"
}}

Respond ONLY with valid JSON. No commentary. No markdown.

Text to process:
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
            print("🧠 GPT Response:")
            print(content)

            # Try parsing full response as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try extracting JSON from within a noisy response
                match = re.search(r"\{[\s\S]*\}", content)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
                        return {"error": "Still invalid after cleanup"}
                return {"error": "Invalid JSON from GPT"}

        except Exception as e:
            print(f"⚠️ GPT call failed: {e}")
            time.sleep((2 ** attempt) + 1)

    return {"error": "Failed to summarize after retries."}
