import pdfplumber
from openai import OpenAI
import os
import time
import json
import re

# Load API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Extract text from all pages in PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Try to extract relevant sections from the PDF text
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

# Use GPT to summarize extracted SB text into structured JSON
def summarize_with_ai(text, max_retries=3):
    sections = slice_sections(text)
    cleaned_text = "\n\n".join(sections.values()) if sections else text

    prompt = f"""
You are an AI assistant helping extract structured information from aircraft service bulletins.

Your task is to return only valid JSON (no explanation or commentary). Use this format exactly:

{{
  "aircraft": ["model1", "model2"],
  "ata": "ATA chapter number",
  "system": "Affected system or part",
  "action": "Brief action (e.g. modify, inspect, power cycle)",
  "compliance": "Compliance recommendation or deadline",
  "reason": "Why this bulletin is issued (e.g. safety, data update)",
  "sb_id": "Service Bulletin number"
}}

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

            # 🔍 DEBUG: Show what GPT returned
            print("🧠 GPT Response (raw):")
            print(content)

            # Try parsing the full response as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON block from a noisy response
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
