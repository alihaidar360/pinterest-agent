"""
Etsy Open API v3 se products search karne ke liye.
NOTE: Etsy ko x-api-key header mein "keystring:shared_secret" dono chahiye,
sirf keystring nahi - warna 403 Forbidden aata hai.
"""

import os
import requests

ETSY_API_KEY = os.environ.get("ETSY_API_KEY")
ETSY_SHARED_SECRET = os.environ.get("ETSY_SHARED_SECRET")
BASE_URL = "https://openapi.etsy.com/v3/application"


def _auth_header():
    """x-api-key header banata hai - keystring:shared_secret format mein."""
    return {"x-api-key": f"{ETSY_API_KEY}:{ETSY_SHARED_SECRET}"}


def search_products(keyword, limit=8):
    """Etsy pe keyword se active listings search karta hai."""
    url = f"{BASE_URL}/listings/active"
    headers = _auth_header()
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
    headers = _auth_header()
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
    NOTE: Etsy ab Awin ki jagah Rakuten Advertising use karta hai (Awin pe
    Etsy program abhi inactive hai). Jab tak Rakuten approval na aaye aur
    unka proper deep-link format add na ho, plain Etsy URL use karo -
    wo hamesha kaam karta hai, sirf commission track nahi hota tab tak.
    """
    rakuten_sid = os.environ.get("RAKUTEN_SID", "")
    if rakuten_sid:
        # Rakuten approve hone ke baad yahan unka deep-link format add karenge
        # Example format: https://click.linksynergy.com/deeplink?id=SID&mid=MID&murl=ENCODED_URL
        pass
    return etsy_url
