"""
AGENT 1 - Trend Scanner
Gemini se Western-audience trending jewelry keywords nikalta hai.
"""

import json
from utils.ai_clients import gemini_text_json


def load_prompt():
    with open("config/prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["trend_scanner_prompt"]


def run():
    prompt = load_prompt()
    keywords = gemini_text_json(prompt)
    print(f"[Agent 1] {len(keywords)} trending keywords found: {keywords}")
    return keywords
