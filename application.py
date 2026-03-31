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
# 1. REPLACE THIS WITH YOUR ACTUAL GROQ KEY
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# -----------------------------
# Request Model (AJO Payload)
# -----------------------------
class EmailRequest(BaseModel):
    user_prompt: str
    first_name: Optional[str] = "{{profile.person.name.firstName}}"

# -----------------------------
# API ENDPOINT
# -----------------------------
@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    try:
        # 2. Setup Headers for Groq
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # 3. Construct Payload with AJO Personalization
        payload = {
            "model": "llama-3.3-70b-versatile", # ✅ Latest supported model
            "messages": [
                {
                    "role": "system", 
                    "content": (
                        "You are a professional email developer. "
                        "Return ONLY raw HTML. No markdown code blocks. "
                        "Use table-based layout and inline CSS. "
                        f"Greeting must be: Hello {request.first_name}"
                    )
                },
                {"role": "user", "content": f"Topic: {request.user_prompt}"}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }

        # 4. Make the request to Groq
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {response.text}")

        result = response.json()
        html_output = result["choices"][0]["message"]["content"]

        # 5. Clean AI artifacts (backticks/markdown tags)
        html_output = html_output.replace("```html", "").replace("```", "").strip()

        return {
            "html_email": html_output
        }

    except Exception as e:
        logging.error(f"Failed to generate email: {str(e)}")
        # Fallback HTML for AJO safety
        return {
            "html_email": f"<table><tr><td>Hello {request.first_name}, something went wrong.</td></tr></table>",
            "error": str(e)
        }

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health():
    return {"status": "API is online"}