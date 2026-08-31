"""
AGENT 6 - Self-Optimizing Reviewer
Har 15 din baad chalta hai (alag GitHub Action schedule se).
Pichle 15 din ka Pinterest analytics + Sheet data dekh kar
Agents 1, 3, 5 ke prompts ko khud rewrite karta hai.

NOTE: Sheet data aur analytics ko is prompt mein bhejne se pehle SUMMARIZE/
TRUNCATE kiya jata hai - warna raw data itna bada ho jata hai ke Groq ka
per-minute token limit (TPM) phat jata hai aur call fail ho jati hai.
"""

import json
from datetime import datetime
from utils.ai_clients import groq_text_json
from utils.pinterest_analytics import get_account_analytics, get_top_pins
from utils.sheets import get_recent_rows

PROMPTS_PATH = "config/prompts.json"
MAX_ROWS_TO_SUMMARIZE = 20  # itni hi rows bhejo taaki prompt chhota rahe


def load_prompts():
    with open(PROMPTS_PATH, "r") as f:
        return json.load(f)


def save_prompts(prompts):
    with open(PROMPTS_PATH, "w") as f:
        json.dump(prompts, f, indent=2)


def _summarize_sheet_rows(rows):
    """
    Poori row (lambi description, alt-text, waghera) bhejne ki jagah,
    sirf zaroori fields ka chhota summary banata hai - taaki token count
    control mein rahe.
    """
    summary = []
    for row in rows[-MAX_ROWS_TO_SUMMARIZE:]:
        summary.append({
            "date": row.get("Date", ""),
            "title": (row.get("Product Title", "") or "")[:80],
            "score": row.get("Visual Judge Score", ""),
            "hashtags": (row.get("Hashtags", "") or "")[:150],
        })
    return summary


def _summarize_analytics(analytics_data):
    """Analytics response bhi truncate karta hai agar bohot bada ho."""
    text = json.dumps(analytics_data)
    if len(text) > 2000:
        text = text[:2000] + "...(truncated)"
    return text


def run():
    prompts = load_prompts()
    meta_prompt = prompts["optimizer_meta_prompt"]

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
    condensed_sheet = _summarize_sheet_rows(sheet_data)

    full_prompt = (
        f"{meta_prompt}\n\n"
        f"--- Last 15 days Pinterest analytics (may be empty if token expired) ---\n"
        f"{_summarize_analytics(analytics)}\n\n"
        f"--- Last 15 days top-performing pins (may be empty if token expired) ---\n"
        f"{_summarize_analytics(top_pins)}\n\n"
        f"--- Summary of last {len(condensed_sheet)} pins this system generated ---\n"
        f"{json.dumps(condensed_sheet)}\n\n"
        f"--- Current prompts being used ---\n"
        f"trend_scanner_prompt: {prompts['trend_scanner_prompt'][:400]}\n\n"
        f"visual_judge_prompt: {prompts.get('visual_judge_prompt', '')[:400]}\n\n"
        f"content_writer_prompt: {prompts.get('content_writer_prompt', prompts.get('combined_agent_prompt', ''))[:400]}\n"
    )

    updated = groq_text_json(full_prompt, max_tokens=2000)

    if "trend_scanner_prompt" in updated:
        prompts["trend_scanner_prompt"] = updated["trend_scanner_prompt"]
    if "visual_judge_prompt" in updated:
        prompts["visual_judge_prompt"] = updated["visual_judge_prompt"]
    if "content_writer_prompt" in updated:
        prompts["content_writer_prompt"] = updated["content_writer_prompt"]
    if "combined_agent_prompt" in updated:
        prompts["combined_agent_prompt"] = updated["combined_agent_prompt"]

    prompts["last_updated"] = datetime.utcnow().isoformat()
    prompts["update_count"] = prompts.get("update_count", 0) + 1

    save_prompts(prompts)
    print(f"[Agent 6] Prompts updated successfully. Update #{prompts['update_count']}")
    return prompts
