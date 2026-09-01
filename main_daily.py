"""
MAIN DAILY ORCHESTRATOR
Roz chalta hai (GitHub Actions se scheduled).
Flow: Trend Scan (Gemini) -> Product Source (Etsy) -> DEDUPLICATE -> 
      Evaluate+Content (Groq) -> Design -> Sheet
"""

from agents import trend_scanner, product_sourcer, product_evaluator, content_writer
from utils.sheets import append_pin_row, get_used_listing_ids

TARGET_PIN_COUNT = 6  # Groq free tier daily token limit ke hisab se rakha hai


def main():
    print("=== DAILY PIN GENERATION PIPELINE START ===")

    # Agent 1: Trend Scanner (Gemini)
    keywords = trend_scanner.run()

    # Agent 2: Product Sourcer (Etsy)
    candidates = product_sourcer.run(keywords, per_keyword=2, max_total=15)

    # DEDUPLICATION: jo products pehle se Sheet mein hain, unko dobara process na karo
    used_ids = get_used_listing_ids()
    fresh_candidates = [
        p for p in candidates if str(p.get("listing_id", "")) not in used_ids
    ]
    skipped = len(candidates) - len(fresh_candidates)
    if skipped > 0:
        print(f"[Dedup] {skipped} already-used products skipped, {len(fresh_candidates)} fresh candidates remain")

    # Agent 3+4+5 combined: Evaluate + Judge + Write Content (Groq, one call per product)
    approved = product_evaluator.run(fresh_candidates, target_count=TARGET_PIN_COUNT)

    # Agent 5: Portrait image design
    final_pins = content_writer.run(approved)

    # Write everything to Google Sheet for human review
    for pin in final_pins:
        append_pin_row(pin)

    print(f"=== PIPELINE COMPLETE: {len(final_pins)} pins ready in Google Sheet ===")


if __name__ == "__main__":
    main()
