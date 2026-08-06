"""
AGENT 5 - Image Designer
Content (title/description/tags) ab Product Evaluator se aata hai (Groq).
Ye agent sirf portrait-shape image design karta hai har approved product ke liye.
"""

import os
from utils.image_designer import design_portrait_pin
from utils.etsy_client import build_affiliate_link

OUTPUT_DIR = "output_images"


def run(approved_products):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_pins = []

    for i, product in enumerate(approved_products):
        try:
            image_path = os.path.join(OUTPUT_DIR, f"pin_{i}.png")
            design_portrait_pin(product["image_url"], output_path=image_path)

            final_pins.append({
                "product_title": product.get("title"),
                "image_url": product.get("image_url"),
                "local_image_path": image_path,
                "affiliate_link": build_affiliate_link(product.get("url", "")),
                "seo_title": product.get("seo_title", ""),
                "description": product.get("description", ""),
                "alt_text": product.get("alt_text", ""),
                "hashtags": product.get("hashtags", []),
                "visual_score": product.get("visual_score", ""),
                "cross_check_approved": product.get("cross_check_approved", ""),
            })
        except Exception as e:
            print(f"[Agent 5] Failed designing image for {product.get('title')}: {e}")

    print(f"[Agent 5] {len(final_pins)} pins fully designed and ready")
    return final_pins
