"""
Etsy Open API v3 se products search karne ke liye.
"""

import os
import requests

ETSY_API_KEY = os.environ.get("ETSY_API_KEY")
BASE_URL = "https://openapi.etsy.com/v3/application"


def search_products(keyword, limit=8):
    """Etsy pe keyword se active listings search karta hai."""
    url = f"{BASE_URL}/listings/active"
    headers = {"x-api-key": ETSY_API_KEY}
    params = {
        "keywords": keyword,
        "limit": limit,
        "sort_on": "score",
        "sort_order": "desc",
    }
    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    products = []
    for listing in data.get("results", []):
        listing_id = listing.get("listing_id")
        title = listing.get("title", "")
        etsy_url = listing.get("url", "")

        # Fetch image separately
        img_url = get_listing_image(listing_id)

        products.append({
            "listing_id": listing_id,
            "title": title,
            "url": etsy_url,
            "image_url": img_url,
        })
    return products


def get_listing_image(listing_id):
    url = f"{BASE_URL}/listings/{listing_id}/images"
    headers = {"x-api-key": ETSY_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            return results[0].get("url_fullxfull", "")
    except Exception:
        pass
    return ""


def build_affiliate_link(etsy_url):
    """
    NOTE: Asli affiliate link Etsy Affiliate Program (Awin ke through) se milta hai.
    Awin dashboard se apna publisher ID lekar is function ko update karna hoga.
    Filhaal ye plain Etsy URL return karta hai - AWIN_PUBLISHER_ID set karke
    isko wrap kiya ja sakta hai.
    """
    awin_id = os.environ.get("AWIN_PUBLISHER_ID", "")
    if awin_id:
        return f"https://www.awin1.com/cread.php?awinmid=6220&awinaffid={awin_id}&clickref=&p={etsy_url}"
    return etsy_url
