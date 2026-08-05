"""
MAIN DAILY ORCHESTRATOR
Roz chalta hai (GitHub Actions se scheduled) - Agents 1 se 5 tak
sequence mein chalata hai, aur final ready pins ko Google Sheet mein daal deta hai.
"""

from agents import trend_scanner, product_sourcer, visual_judge, cross_checker, content_writer
from utils.sheets import append_pin_row

TARGET_PIN_COUNT = 8  # 6-10 ke beech, adjust kar sakte hain


def main():
    print("=== DAILY PIN GENERATION PIPELINE START ===")

    # Agent 1: Trend Scanner
    keywords = trend_scanner.run()

    # Agent 2: Product Sourcer
    candidates = product_sourcer.run(keywords, per_keyword=3, max_total=25)

    # Agent 3: Visual Judge (self-check included)
    visually_approved = visual_judge.run(candidates)

    # Agent 4: Cross Checker (independent Claude verification)
    confirmed = cross_checker.run(visually_approved, target_count=TARGET_PIN_COUNT)

    # Agent 5: Content Writer + Designer (self-check included)
    final_pins = content_writer.run(confirmed)

    # Write everything to Google Sheet for human review
    for pin in final_pins:
        append_pin_row(pin)

    print(f"=== PIPELINE COMPLETE: {len(final_pins)} pins ready in Google Sheet ===")


if __name__ == "__main__":
    main()
