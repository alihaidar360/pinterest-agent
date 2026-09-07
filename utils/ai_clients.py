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
        if isinstance(text, list):
            text = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in text
            )
        else:
            text = str(text)

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

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

def groq_text(prompt, max_tokens=1800):
    completion = groq_client.chat.completions.create(
        model=GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        extra_body={"reasoning_effort": "low"},
    )
    return completion.choices[0].message.content


def groq_text_json(prompt, max_tokens=1800):
    return _extract_json(groq_text(prompt, max_tokens=max_tokens))


def groq_vision_json(prompt, image_bytes, mime_type="image/jpeg", max_tokens=900):
    """Groq ko ek image + prompt bhejna, JSON response lena.
    NOTE: max_tokens 1000 se KAM rakhna zaroori hai - Groq ka is model ke
    free tier pe output-tokens-per-minute (OTPM) hard limit hi 1000 hai,
    isliye ek single request bhi 1000 se zyada maang nahi sakti."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    completion = groq_client.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt + "\n\nRespond with ONLY valid JSON, no other text, no markdown, no explanation. Keep the description concise."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        max_tokens=max_tokens,
        extra_body={"reasoning_effort": "none"},
    )
    result = _extract_json(completion.choices[0].message.content)
    if isinstance(result, list) and len(result) > 0:
        result = result[0]
    return result
