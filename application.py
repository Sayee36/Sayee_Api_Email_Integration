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
            "You are an expert Email Developer. Generate a centered <table> with width='600' align='center'. "
            "STRICT RULES: "
            "1. NO HARDCODED IMAGES: Do not use specific flower or laptop links unless asked for flowers or laptops. "
            "2. DYNAMIC IMAGE LOGIC: You must build the <img> src URL by extracting the main subject of the user's prompt. "
            "Use this format: https://images.unsplash.com/photo-1500000000000?auto=format&fit=crop&w=600&h=250&q=80&sig={random_number}&keyword={subject} "
            "Replace {subject} with the specific person or object requested (e.g., 'old_man', 'flowers', 'car'). "
            "3. IMAGE TAG: Use <img width='600' height='250' style='display:block; width:100%; max-width:600px; height:auto; border:0; margin:0 auto;'>. "
            "4. NO ICONS: Do not add any secondary broken icons or small images in the body text. "
            "5. ALIGNMENT: Every <td> must have align='center' and style='text-align: center; font-family: Arial, sans-serif; padding: 20px;'. "
            f"6. PERSONALIZATION: Greeting: 'Hello {full_name}'. "
            "7. OUTPUT: Return ONLY raw <table> HTML. No markdown, no conversational filler."
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
