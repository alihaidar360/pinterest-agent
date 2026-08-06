"""
AGENT: Product Evaluator (Visual Judge + Cross-Check + Content Writer combined)
Groq vision model se ek hi call mein: product ko judge karta hai, approve/reject
karta hai, aur agar approve ho to SEO title/description/alt-text/hashtags bhi
usi call mein bana deta hai. Ye Claude wale purane 3-agent design ka
Groq-friendly, kam-calls-wala version hai.
"""

import json
import requests
from utils.ai_clients import groq_vision_json

MIN_SCORE = 7


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["combined_agent_prompt"]


def _fetch_image_bytes(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.content


def run(products, target_count=10):
    base_prompt = load_prompt()
    approved_pins = []

    for product in products:
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
            result = groq_vision_json(full_prompt, image_bytes, mime_type="image/jpeg")

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

    print(f"[Evaluator] {len(approved_pins)}/{len(products)} products approved with content ready")
    return approved_pins
