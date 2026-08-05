"""
AI client wrappers - Gemini aur Claude dono ke liye.
Ye file API keys ko environment variables (GitHub Secrets) se uthati hai.
"""

import os
import json
import re
import google.generativeai as genai
from anthropic import Anthropic

# --- Setup clients using environment variables (GitHub Secrets se aate hain) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

claude_client = Anthropic(api_key=CLAUDE_API_KEY)


def _extract_json(text):
    """AI responses kabhi kabhi markdown ```json fences ke sath aate hain - clean karta hai."""
    text = text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object/array inside the text
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise


def gemini_text(prompt):
    """Gemini se simple text/JSON response lena (no image)."""
    response = gemini_model.generate_content(prompt)
    return response.text


def gemini_text_json(prompt):
    return _extract_json(gemini_text(prompt))


def gemini_vision_json(prompt, image_bytes_list):
    """
    Gemini ko images + prompt bhejna, JSON response lena.
    image_bytes_list: list of (mime_type, bytes) tuples
    """
    parts = [prompt]
    for mime_type, img_bytes in image_bytes_list:
        parts.append({"mime_type": mime_type, "data": img_bytes})
    response = gemini_model.generate_content(parts)
    return _extract_json(response.text)


def claude_text(prompt, max_tokens=1500):
    """Claude se simple text response lena."""
    message = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def claude_text_json(prompt, max_tokens=1500):
    return _extract_json(claude_text(prompt, max_tokens=max_tokens))


def claude_vision_json(prompt, image_bytes, mime_type="image/jpeg", max_tokens=1500):
    """Claude ko ek image + prompt bhejna, JSON response lena."""
    import base64
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    message = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": b64_image,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return _extract_json(message.content[0].text)
