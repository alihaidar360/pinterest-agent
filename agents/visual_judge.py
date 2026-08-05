"""
AGENT 3 - Visual Judge
Gemini vision se har candidate product ki image ko brand-reference se
compare karta hai. Sirf 7+/10 score wale pass hote hain (self-check).
"""

import json
import requests
from utils.ai_clients import gemini_vision_json

MIN_SCORE = 7
REFERENCE_IMAGE_PATHS = [
    "assets/reference_pin_1.jpg",
    "assets/reference_pin_2.jpg",
]


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["visual_judge_prompt"]


def _fetch_image_bytes(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.content


def run(products):
    prompt = load_prompt()
    approved = []

    # Load reference image (top-performing pin) once
    reference_bytes = None
    try:
        with open(REFERENCE_IMAGE_PATHS[0], "rb") as f:
            reference_bytes = f.read()
    except FileNotFoundError:
        print("[Agent 3] WARNING: reference image not found, judging without reference")

    for product in products:
        if not product.get("image_url"):
            continue
        try:
            candidate_bytes = _fetch_image_bytes(product["image_url"])
            image_list = []
            if reference_bytes:
                image_list.append(("image/jpeg", reference_bytes))
            image_list.append(("image/jpeg", candidate_bytes))

            result = gemini_vision_json(prompt, image_list)
            score = result.get("score", 0)
            product["visual_score"] = score
            product["visual_reason"] = result.get("reason", "")

            if score >= MIN_SCORE:
                approved.append(product)
        except Exception as e:
            print(f"[Agent 3] Failed judging product {product.get('title')}: {e}")

    print(f"[Agent 3] {len(approved)}/{len(products)} products passed visual check")
    return approved
