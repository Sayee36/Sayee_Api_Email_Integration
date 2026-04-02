import logging
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AJO AI Email Generator", version="2.0")

# -----------------------------
# GROQ CONFIGURATION
# -----------------------------
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# -----------------------------
# Request Model (AJO Payload)
# -----------------------------
class EmailRequest(BaseModel):
    user_prompt: str
    first_name: Optional[str] = "Valued"
    last_name: Optional[str] = "Customer"
    dob: Optional[datetime] = None

# -----------------------------
# API ENDPOINT
# -----------------------------
@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Handling potential empty fields gracefully
        full_name = f"{request.first_name} {request.last_name}".strip()
        dob_info = f"Date of Birth: {request.dob}" if request.dob else "Date of Birth: Not provided"

        # System Prompt: Forces Table Layout & Personalization
        system_instructions = (
            "You are an expert AJO Developer. Generate professional HTML using <table> layouts. "
            "Return ONLY raw HTML. No markdown code blocks. No <html>, <head>, or <body> tags. "
            "Use inline CSS for maximum compatibility (Outlook/Gmail). "
            f"1. Greeting: Write 'Hello {full_name}' directly in the HTML. "
            f"2. Personalization: Note {dob_info}. If it's their birthday month/day based on the prompt, mention it. "
            "3. Layout: Include a Header, Body, and Footer. "
            "4. Image Logic: Include a professional 600px wide <img> tag with a high-quality relevant URL. "
            "5. Sign off: Always sign off as 'The YanIT Solutions Team'. "
            "CRITICAL: Do not include any conversational text before or after the HTML."
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Topic: {request.user_prompt}"}
            ],
            "temperature": 0.4, # Slightly lower for more consistent HTML structure
            "max_tokens": 1500
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {response.text}")

        result = response.json()
        html_output = result["choices"][0]["message"]["content"]
        
        # Enhanced Cleaning: Removes markdown and any accidental lead-in text
        if "table" in html_output.lower():
            # Find the first occurrence of <table and the last occurrence of </table>
            start_index = html_output.lower().find("<table")
            end_index = html_output.lower().rfind("</table>") + 8
            if start_index != -1 and end_index != -1:
                html_output = html_output[start_index:end_index]

        return {"html_email": html_output}

    except Exception as e:
        logging.error(f"Failed to generate email: {str(e)}")
        return {
            "html_email": f"<table width='100%'><tr><td>Hello {request.first_name}, something went wrong.</td></tr></table>",
            "error": str(e)
        }

@app.get("/health")
def health():
    return {"status": "API is online"}
