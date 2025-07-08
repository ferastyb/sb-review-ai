import pdfplumber
import os
from openai import OpenAI

# Load key from environment variable or hardcoded (not recommended for production)
OPENAI_API_KEY = "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"


client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

import openai

import openai

def summarize_with_ai(text):
    prompt = f"Summarize the following aircraft service bulletin:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content  # ✅ move inside the try block

    except openai.RateLimitError:
        return "⚠️ Rate limit exceeded. Please wait and try again later."

    except openai.AuthenticationError:
        return "❌ Invalid API key. Please check your OpenAI credentials."

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"

