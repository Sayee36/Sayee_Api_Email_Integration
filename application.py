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
# Request Model (Strictly using your AEP Schema fields)
# -----------------------------
class EmailRequest(BaseModel):
    user_prompt: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    dob: Optional[str] = ""

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

        # System Prompt: Forces Table Layout & Personalization
        system_instructions = (
            "You are an expert AJO Developer. Generate professional HTML using <table> layouts. "
            "Return ONLY raw HTML. No markdown. No <html>, <head>, or <body> tags. "
            "Use inline CSS for maximum compatibility (Outlook/Gmail). "
            f"1. Greeting: Write 'Hello {request.first_name} {request.last_name}' directly in the HTML. "
            f"2. Personalization: Use the DOB ({request.dob}) to customize the message if relevant. "
            "3. Image Logic: If the user prompt mentions an image or a theme (like Birthday), "
            "include a professional 600px wide <img> tag with a relevant high-quality URL. "
            "4. Sign off: Always sign off as 'The YanIT Solutions Team'."
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Topic: {request.user_prompt}"}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {response.text}")

        result = response.json()
        html_output = result["choices"][0]["message"]["content"]
        html_output = html_output.replace("```html", "").replace("```", "").strip()

        return {"html_email": html_output}

    except Exception as e:
        logging.error(f"Failed to generate email: {str(e)}")
        return {
            "html_email": f"<table><tr><td>Hello {request.first_name}, content failed to load.</td></tr></table>",
            "error": str(e)
        }

@app.get("/health")
def health():
    return {"status": "API is online"}