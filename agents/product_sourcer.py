"""
AGENT 2 - Product Sourcer
Etsy API se trending keywords ke hisab se candidate products dhoondta hai.
"""

from utils.etsy_client import search_products


def run(keywords, per_keyword=3, max_total=20):
    all_products = []
    for kw in keywords:
        if len(all_products) >= max_total:
            break
        try:
            products = search_products(kw, limit=per_keyword)
            for p in products:
                p["source_keyword"] = kw
            all_products.extend(products)
        except Exception as e:
            print(f"[Agent 2] Etsy search failed for '{kw}': {e}")

    print(f"[Agent 2] {len(all_products)} candidate products sourced")
    return all_products[:max_total]
