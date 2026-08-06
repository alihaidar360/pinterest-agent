"""
AGENT 6 - Self-Optimizing Reviewer
Har 15 din baad chalta hai (alag GitHub Action schedule se).
Pichle 15 din ka Pinterest analytics + Sheet data dekh kar
Agents 1, 3, 5 ke prompts ko khud rewrite karta hai.
Ye looping self-improvement system hai.
"""

import json
from datetime import datetime
from utils.ai_clients import groq_text_json
from utils.pinterest_analytics import get_account_analytics, get_top_pins
from utils.sheets import get_recent_rows

PROMPTS_PATH = "config/prompts.json"


def load_prompts():
    with open(PROMPTS_PATH, "r") as f:
        return json.load(f)


def save_prompts(prompts):
    with open(PROMPTS_PATH, "w") as f:
        json.dump(prompts, f, indent=2)


def run():
    prompts = load_prompts()
    meta_prompt = prompts["optimizer_meta_prompt"]

    # Gather last 15 days of real data
    try:
        analytics = get_account_analytics(days=15)
    except Exception as e:
        print(f"[Agent 6] Could not fetch Pinterest analytics: {e}")
        analytics = {}

    try:
        top_pins = get_top_pins(days=15)
    except Exception as e:
        print(f"[Agent 6] Could not fetch top pins: {e}")
        top_pins = {}

    sheet_data = get_recent_rows(days=15)

    full_prompt = (
        f"{meta_prompt}\n\n"
        f"--- Last 15 days Pinterest account analytics ---\n{json.dumps(analytics)}\n\n"
        f"--- Last 15 days top-performing pins ---\n{json.dumps(top_pins)}\n\n"
        f"--- Last 15 days of pins this system generated (from Sheet) ---\n{json.dumps(sheet_data)}\n\n"
        f"--- Current prompts being used ---\n"
        f"trend_scanner_prompt: {prompts['trend_scanner_prompt']}\n\n"
        f"visual_judge_prompt: {prompts['visual_judge_prompt']}\n\n"
        f"content_writer_prompt: {prompts['content_writer_prompt']}\n"
    )

    updated = groq_text_json(full_prompt, max_tokens=3000)

    prompts["trend_scanner_prompt"] = updated.get("trend_scanner_prompt", prompts["trend_scanner_prompt"])
    prompts["visual_judge_prompt"] = updated.get("visual_judge_prompt", prompts["visual_judge_prompt"])
    prompts["content_writer_prompt"] = updated.get("content_writer_prompt", prompts["content_writer_prompt"])
    prompts["last_updated"] = datetime.utcnow().isoformat()
    prompts["update_count"] = prompts.get("update_count", 0) + 1

    save_prompts(prompts)
    print(f"[Agent 6] Prompts updated successfully. Update #{prompts['update_count']}")
    return prompts
