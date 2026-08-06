"""
AI client wrappers - Gemini (trends) aur Groq (judging/content/optimizer) dono ke liye.
Claude hata diya gaya hai - poora system ab 100% free hai.
"""

import os
import json
import re
import base64
import google.generativeai as genai
from groq import Groq

# --- Setup clients using environment variables (GitHub Secrets se aate hain) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-flash-latest")

groq_client = Groq(api_key=GROQ_API_KEY)

GROQ_TEXT_MODEL = "openai/gpt-oss-120b"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _extract_json(text):
    """AI responses kabhi kabhi markdown ```json fences ke sath aate hain - clean karta hai."""
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise


# ---------------- GEMINI (sirf Agent 1 - Trend Scanner ke liye) ----------------

def gemini_text(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text


def gemini_text_json(prompt):
    return _extract_json(gemini_text(prompt))


# ---------------- GROQ (Agent 3+4+5 evaluator, Agent 6 optimizer) ----------------

def groq_text(prompt, max_tokens=1500):
    completion = groq_client.chat.completions.create(
        model=GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=max_tokens,
    )
    return completion.choices[0].message.content


def groq_text_json(prompt, max_tokens=1500):
    return _extract_json(groq_text(prompt, max_tokens=max_tokens))


def groq_vision_json(prompt, image_bytes, mime_type="image/jpeg", max_tokens=1500):
    """Groq ko ek image + prompt bhejna, JSON response lena."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    completion = groq_client.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        max_completion_tokens=max_tokens,
    )
    return _extract_json(completion.choices[0].message.content)
