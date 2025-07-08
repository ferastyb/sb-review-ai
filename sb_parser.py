import pdfplumber
import re
import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def slice_sections(text):
    section_patterns = {
        "effectivity": r"(Effectivity|Applicability)",
        "reason": r"(Reason|Background|Purpose)",
        "compliance": r"(Compliance|Compliance Recommendation)",
        "accomplishment": r"(Accomplishment Instructions|Instructions|Implementation)",
        "description": r"(Description|Summary)"
    }

    found_sections = {}
    for section, pattern in section_patterns.items():
        match = re.search(f"{pattern}.*?(?=\n[A-Z][^\n]{0,100}\n|$)", text, re.IGNORECASE | re.DOTALL)
        if match:
            found_sections[section] = match.group().strip()

    print(f"📑 Sections extracted: {list(found_sections.keys())}")
    return found_sections

def summarize_with_ai(full_text):
    sections = slice_sections(full_text)

    if not sections:
        return {"error": "No recognizable sections found in the SB."}

    prompt = (
        "You are an aircraft technical documentation assistant. Extract the following fields from the provided SB text:\n"
        "- aircraft model\n"
        "- ATA chapter\n"
        "- affected system or parts\n"
        "- type of action (e.g., inspection, replacement)\n"
        "- compliance recommendation\n"
        "- reason for the bulletin\n"
        "- service bulletin ID (if mentioned)\n\n"
        "Return your answer as JSON.\n\n"
        "### SERVICE BULLETIN TEXT ###\n"
    )

    for title, content in sections.items():
        prompt += f"\n## {title.upper()}\n{content}\n"

    for attempt in range(2):
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
            print("🧠 GPT Response (raw):")
            print(content)

            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in response.")

            import json
            return json.loads(match.group())

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed:", e)
            time.sleep(1)

    return {"error": "Failed to summarize after retries."}
