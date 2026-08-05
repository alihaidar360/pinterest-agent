"""
AGENT 5 - Content Writer + Designer
Har confirmed product ke liye:
- Portrait-shape designed image banata hai
- SEO title, description (long-tail keywords + hashtags), alt-text, 10 tags banata hai
- Khud apna likha hua content dobara check karta hai (self-check)
"""

import json
import os
from utils.ai_clients import claude_text_json
from utils.image_designer import design_portrait_pin
from utils.etsy_client import build_affiliate_link

OUTPUT_DIR = "output_images"


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["content_writer_prompt"]


def _self_check(content):
    """Content ko dobara Claude se verify karwata hai - spelling/accuracy check."""
    check_prompt = (
        "Review this Pinterest pin content for spelling errors, factual issues, "
        "or misleading claims. If everything is fine, return it unchanged. "
        "Return ONLY corrected JSON in the same format:\n\n"
        f"{json.dumps(content)}"
    )
    try:
        return claude_text_json(check_prompt)
    except Exception:
        return content  # fallback to original if self-check fails


def run(products):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base_prompt = load_prompt()
    final_pins = []

    for i, product in enumerate(products):
        try:
            full_prompt = (
                f"{base_prompt}\n\n"
                f"Product title: {product.get('title')}\n"
                f"Source keyword: {product.get('source_keyword')}\n"
            )
            content = claude_text_json(full_prompt)
            content = _self_check(content)  # Layer 3 self-check

            # Design portrait image
            image_path = os.path.join(OUTPUT_DIR, f"pin_{i}.png")
            design_portrait_pin(product["image_url"], output_path=image_path)

            final_pins.append({
                "product_title": product.get("title"),
                "image_url": product.get("image_url"),
                "local_image_path": image_path,
                "affiliate_link": build_affiliate_link(product.get("url", "")),
                "seo_title": content.get("title", ""),
                "description": content.get("description", ""),
                "alt_text": content.get("alt_text", ""),
                "hashtags": content.get("hashtags", []),
                "visual_score": product.get("visual_score", ""),
                "cross_check_approved": product.get("cross_check_approved", ""),
            })
        except Exception as e:
            print(f"[Agent 5] Failed generating content for {product.get('title')}: {e}")

    print(f"[Agent 5] {len(final_pins)} pins fully ready with content + design")
    return final_pins
