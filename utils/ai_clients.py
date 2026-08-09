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
GROQ_VISION_MODEL = "qwen/qwen3.6-27b"


def _extract_json(text):
    """
    AI responses kabhi kabhi markdown ```json fences, <think>...</think> reasoning
    blocks, ya extra text ke sath aate hain - sab clean karta hai.
    """
    if not isinstance(text, str):
        # Kabhi content list of blocks ke roop mein aata hai - text nikaal lo
        if isinstance(text, list):
            text = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in text
            )
        else:
            text = str(text)

    # <think>...</think> ya similar reasoning tags hata do
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: sabse bada { } ya [ ] block dhoondo text mein
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except json.JSONDecodeError:
            pass

    arr_match = re.search(r"\[.*\]", text, re.DOTALL)
    if arr_match:
        return json.loads(arr_match.group(0))

    raise ValueError(f"Could not extract JSON from response: {text[:200]}")


# ---------------- GEMINI (sirf Agent 1 - Trend Scanner ke liye) ----------------

def gemini_text(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text


def gemini_text_json(prompt):
    return _extract_json(gemini_text(prompt))


# ---------------- GROQ (Agent 3+4+5 evaluator, Agent 6 optimizer) ----------------

def groq_text(prompt, max_tokens=2000):
    completion = groq_client.chat.completions.create(
        model=GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        extra_body={"reasoning_effort": "low"},
    )
    return completion.choices[0].message.content


def groq_text_json(prompt, max_tokens=2500):
    return _extract_json(groq_text(prompt, max_tokens=max_tokens))


def groq_vision_json(prompt, image_bytes, mime_type="image/jpeg", max_tokens=1200):
    """Groq ko ek image + prompt bhejna, JSON response lena.
    NOTE: reasoning_effort="none" se Qwen ka "thinking mode" band ho jata hai -
    warna model pehle lambi <think> reasoning likhta hai jo token limit khatam
    kar deti hai asli JSON answer se pehle hi."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    completion = groq_client.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt + "\n\nRespond with ONLY valid JSON, no other text, no markdown, no explanation."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        max_tokens=max_tokens,
        extra_body={"reasoning_effort": "none"},
    )
    result = _extract_json(completion.choices[0].message.content)
    # Kabhi model JSON ko ek list ke andar wrap kar deta hai - unwrap kar lo
    if isinstance(result, list) and len(result) > 0:
        result = result[0]
    return result
