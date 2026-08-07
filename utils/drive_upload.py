"""
Designed portrait pin images ko Google Drive pe upload karta hai
aur ek public-viewable direct image link return karta hai - taaki
Sheet mein asli designed image dikhe, Etsy ki original (non-portrait) nahi.
Isi service account ka use karta hai jo Sheets ke liye bana tha.
"""

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

_drive_service = None


def _get_service():
    global _drive_service
    if _drive_service is None:
        creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


def upload_image_and_get_link(local_path, filename):
    """
    Local image file ko Drive pe upload karta hai, "anyone with link can view"
    permission deta hai, aur ek direct-viewable image URL return karta hai.
    """
    service = _get_service()

    file_metadata = {"name": filename}
    media = MediaFileUpload(local_path, mimetype="image/png")

    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    file_id = uploaded.get("id")

    # Public view permission do
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # Direct-viewable image URL (Pinterest/Sheet mein image ki tarah dikhega)
    return f"https://drive.google.com/uc?export=view&id={file_id}"
