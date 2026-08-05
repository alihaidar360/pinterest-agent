"""
MAIN OPTIMIZER RUNNER
Har 15 din chalta hai (alag GitHub Action schedule) - Agent 6 ko run karta hai
jo poore account ka analysis kar ke prompts ko khud upgrade karta hai.
"""

from agents import optimizer


def main():
    print("=== 15-DAY SELF-OPTIMIZATION CYCLE START ===")
    optimizer.run()
    print("=== OPTIMIZATION COMPLETE - prompts updated for next cycle ===")


if __name__ == "__main__":
    main()
