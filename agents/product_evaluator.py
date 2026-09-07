"""
AGENT: Product Evaluator (Visual Judge + Cross-Check + Content Writer combined)
Groq vision model se ek hi call mein: product ko judge karta hai, approve/reject
karta hai, aur agar approve ho to SEO title/description/alt-text/hashtags bhi
usi call mein bana deta hai.

NOTE: Groq free tier ka daily token budget (TPD) aur per-minute output limit
(OTPM) dono limited hain, isliye products ki count control mein rakhi gayi hai.
"""

import json
import requests
from utils.ai_clients import groq_vision_json

MIN_SCORE = 7
MAX_PRODUCTS_TO_TRY = 10


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["combined_agent_prompt"]


def _fetch_image_bytes(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.content


def run(products, target_count=8):
    base_prompt = load_prompt()
    approved_pins = []

    for product in products[:MAX_PRODUCTS_TO_TRY]:
        if len(approved_pins) >= target_count:
            break
        if not product.get("image_url"):
            continue
        try:
            image_bytes = _fetch_image_bytes(product["image_url"])
            full_prompt = (
                f"{base_prompt}\n\n"
                f"Product title: {product.get('title')}\n"
                f"Source keyword: {product.get('source_keyword')}\n"
            )
            # max_tokens explicitly NAHI pass kar rahe - ai_clients.py ka safe
            # default (900, jo Groq ke 1000 OTPM limit se kam hai) use hoga
            result = groq_vision_json(full_prompt, image_bytes, mime_type="image/jpeg")

            if not isinstance(result, dict):
                print(f"[Evaluator] Unexpected response shape for {product.get('title')}, skipping")
                continue

            score = result.get("score", 0)
            approved = result.get("approved", False)

            if approved and score >= MIN_SCORE:
                product["visual_score"] = score
                product["cross_check_approved"] = True
                product["seo_title"] = result.get("title", "")
                product["description"] = result.get("description", "")
                product["alt_text"] = result.get("alt_text", "")
                product["hashtags"] = result.get("hashtags", [])
                approved_pins.append(product)
        except Exception as e:
            print(f"[Evaluator] Failed for {product.get('title')}: {e}")

    print(f"[Evaluator] {len(approved_pins)}/{min(len(products), MAX_PRODUCTS_TO_TRY)} products approved with content ready")
    return approved_pins
