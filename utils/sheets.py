"""
Google Sheets se connect karne ke liye utility.
Ek hi continuous sheet use hoti hai - roz naye rows add hote hain.
Ab "Listing ID" column bhi hai taaki DUPLICATE products dobara na aayein.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

HEADERS = [
    "Date", "Status", "Listing ID", "Product Title", "Image URL", "Etsy Affiliate Link",
    "SEO Title", "Description", "Alt Text", "Hashtags",
    "Visual Judge Score", "Cross Check Approved",
]


def _get_client():
    creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet():
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet("Pins")
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Pins", rows=2000, cols=len(HEADERS))
        worksheet.append_row(HEADERS)
        return worksheet

    # Agar purani sheet mein "Listing ID" column nahi hai (purana format), add karo
    existing_headers = worksheet.row_values(1)
    if "Listing ID" not in existing_headers:
        worksheet.update_cell(1, 3, "Listing ID")
        # Purani rows ka listing ID khali rahega - koi masla nahi, naya data sahi trackega

    return worksheet


def get_used_listing_ids():
    """
    Sheet mein pehle se maujood sab listing_ids nikalta hai - taaki wahi
    product dobara na process ho, na dobara pin bane.
    """
    worksheet = get_worksheet()
    all_rows = worksheet.get_all_records()
    used_ids = set()
    for row in all_rows:
        lid = row.get("Listing ID", "")
        if lid:
            used_ids.add(str(lid))
    return used_ids


def append_pin_row(pin_data: dict):
    """Ek naya pin row add karta hai sheet mein."""
    worksheet = get_worksheet()
    row = [
        datetime.utcnow().strftime("%Y-%m-%d"),
        "Not Posted",
        str(pin_data.get("listing_id", "")),
        pin_data.get("product_title", ""),
        pin_data.get("image_url", ""),
        pin_data.get("affiliate_link", ""),
        pin_data.get("seo_title", ""),
        pin_data.get("description", ""),
        pin_data.get("alt_text", ""),
        ", ".join(pin_data.get("hashtags", [])),
        pin_data.get("visual_score", ""),
        pin_data.get("cross_check_approved", ""),
    ]
    worksheet.append_row(row, value_input_option="USER_ENTERED")


def get_recent_rows(days=15):
    """Pichle N din ke rows nikalta hai (Agent 6 ke liye)."""
    worksheet = get_worksheet()
    all_rows = worksheet.get_all_records()
    cutoff = datetime.utcnow()
    recent = []
    for row in all_rows:
        try:
            row_date = datetime.strptime(row["Date"], "%Y-%m-%d")
            if (cutoff - row_date).days <= days:
                recent.append(row)
        except Exception:
            continue
    return recent
