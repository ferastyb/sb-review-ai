import os
import pdfplumber
import re
import time
import json
from openai import OpenAI
from openai import OpenAIError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

def extract_json(text):
    try:
        text = text.strip("` \n")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception as e:
        print("❌ JSON parsing failed:", e)
        return None

def summarize_with_ai(text, max_retries=3):
    prompt = (
        "You are an AI assistant. Summarize the following aircraft service bulletin text into structured JSON.\n"
        "Extract these fields:\n"
        "- aircraft: list of affected aircraft models\n"
        "- ata: ATA chapter\n"
        "- system: system or part affected\n"
        "- action: type of action required (e.g. inspection, replacement)\n"
        "- compliance: compliance time or recommendation\n"
        "- reason: reason for the bulletin (optional)\n"
        "- sb_id: bulletin ID or number (optional)\n"
        "Return only valid JSON. Do not include any explanation or markdown.\n\n"
        f"Text: \n{text}"
    )

    for attempt in range(max_retries):
        try:
            print(f"⏳ GPT call attempt {attempt + 1}")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            print("🧠 GPT Response (raw):")
            print(content)

            result = extract_json(content)
            if result:
                return result

        except OpenAIError as e:
            print("❌ OpenAI API Error:", e)
        except Exception as e:
            print("❌ General Error:", e)

        time.sleep(2)  # wait before retry

    return {"error": "Failed to summarize after retries."}
