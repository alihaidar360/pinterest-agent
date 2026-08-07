"""
AGENT 5 - Image Designer
Content (title/description/tags) Product Evaluator se aata hai (Groq).
Ye agent portrait-shape image design karta hai. Image ko GitHub repo mein hi
commit kiya jata hai (workflow ka agla step) aur uska raw.githubusercontent.com
link Sheet mein daala jata hai - Drive use nahi karte kyunki service accounts
ki apni storage quota nahi hoti (Google restriction).
"""

import os
from utils.image_designer import design_portrait_pin
from utils.etsy_client import build_affiliate_link

OUTPUT_DIR = "output_images"


def _build_github_raw_url(filename):
    """GitHub Actions automatically GITHUB_REPOSITORY env deta hai (owner/repo)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    if not repo:
        return ""  # local testing ke liye, workflow ke bahar
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{OUTPUT_DIR}/{filename}"


def run(approved_products):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_pins = []

    for i, product in enumerate(approved_products):
        try:
            filename = f"pin_{product.get('listing_id', i)}.png"
            image_path = os.path.join(OUTPUT_DIR, filename)
            design_portrait_pin(product["image_url"], output_path=image_path)

            github_image_url = _build_github_raw_url(filename)

            final_pins.append({
                "product_title": product.get("title"),
                "image_url": github_image_url,
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
