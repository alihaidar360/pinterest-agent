"""
Pinterest API se account analytics khींचता hai - Agent 6 (Optimizer) ke liye.
NOTE: Pinterest Business API access aur access token generate karna padta hai
developers.pinterest.com se (README mein steps hain).
"""

import os
import requests
from datetime import datetime, timedelta

PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN")
BASE_URL = "https://api.pinterest.com/v5"


def get_account_analytics(days=15):
    """Pichle N din ka overall account analytics laata hai."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    url = f"{BASE_URL}/user_account/analytics"
    headers = {"Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "metric_types": "IMPRESSION,PIN_CLICK,SAVE,OUTBOUND_CLICK",
    }
    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def get_top_pins(days=15, limit=25):
    """Pichle N din ke top-performing pins laata hai."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    url = f"{BASE_URL}/user_account/analytics/top_pins"
    headers = {"Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "sort_by": "IMPRESSION",
        "num_of_pins": limit,
    }
    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    return response.json()
