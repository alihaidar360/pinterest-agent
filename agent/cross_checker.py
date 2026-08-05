"""
AGENT 4 - Cross Checker
Claude independently dobara check karta hai jo Agent 3 ne pass kiya.
Agar disagree kare, product reject hota hai. (Two-AI agreement system)
"""

import json
from utils.ai_clients import claude_text_json


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["cross_checker_prompt"]


def run(products, target_count=10):
    base_prompt = load_prompt()
    final_approved = []

    for product in products:
        if len(final_approved) >= target_count:
            break
        try:
            full_prompt = (
                f"{base_prompt}\n\n"
                f"Product title: {product.get('title')}\n"
                f"Visual judge score: {product.get('visual_score')}\n"
                f"Visual judge reason: {product.get('visual_reason')}\n"
            )
            result = claude_text_json(full_prompt)
            product["cross_check_approved"] = result.get("approved", False)
            product["cross_check_reason"] = result.get("reason", "")

            if result.get("approved"):
                final_approved.append(product)
        except Exception as e:
            print(f"[Agent 4] Cross-check failed for {product.get('title')}: {e}")

    print(f"[Agent 4] {len(final_approved)} products confirmed by both AIs")
    return final_approved
