import logging
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from datetime import date

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="AJO AI Email Generator", version="2.0")

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class EmailRequest(BaseModel):
    user_prompt: str
    first_name: str = "Valued"
    last_name: str = "Customer"
    dob: Optional[Union[date, str]] = "Not Provided"

@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        full_name = f"{request.first_name} {request.last_name}".strip()
        dob_val = request.dob.strftime("%Y-%m-%d") if isinstance(request.dob, date) else "Not provided"
        dob_info = f"Date of Birth: {dob_val}"

        # THE ULTIMATE COMPATIBILITY PROMPT
        system_instructions = (
            "You are an expert Email Developer. Generate a single <table> (max-width: 600px). "
            "STRICT RULES: "
            "1. NO <style> tags. All CSS MUST be inline (e.g., <td style='padding:20px;'>). "
            "2. Use 'mso-table-lspace:0pt; mso-table-rspace:0pt;' for Outlook compatibility. "
            "3. IMAGE: Use <img src='...' width='600' style='display:block; width:100%; max-width:600px; height:auto; border:0;'>. "
            "4. For flowers/anniversary, use: https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=600&q=80 "
            "5. CONTENT: Center all text. Use a clean sans-serif font (Arial, sans-serif). "
            f"6. PERSONALIZATION: Start with 'Hello {full_name}'. Mention {dob_info} only if relevant. "
            "7. SIGN OFF: 'The YanIT Solutions Team'. "
            "8. OUTPUT: Return ONLY the <table> code. No markdown, no intro text."
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Topic: {request.user_prompt}"}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        html_output = result["choices"][0]["message"]["content"]
        
        # Clean markdown if AI ignores instructions
        if "```html" in html_output:
            html_output = html_output.split("```html")[1].split("```")[0].strip()

        return {"html_email": html_output}

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {"html_email": "<table><tr><td>Content Error</td></tr></table>", "error": str(e)}

@app.get("/health")
def health():
    return {"status": "API is online"}
