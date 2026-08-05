"""
Product image ko Pinterest ke ideal portrait shape (1000x1500) mein
design karta hai - brand-consistent background aur subtle framing ke saath.
"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

PIN_WIDTH = 1000
PIN_HEIGHT = 1500

GOLD = (196, 164, 100)
BG_TOP = (10, 10, 10)
BG_BOTTOM = (12, 34, 28)


def _download_image(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _gradient_background(w, h):
    bg = Image.new("RGB", (w, h), BG_TOP)
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return bg


def design_portrait_pin(product_image_url, brand_name="Lumière & Luxe", output_path="pin.png"):
    """
    Product image ko brand-consistent portrait pin mein convert karta hai:
    - Gradient background (brand colors)
    - Product image center mein, thin gold border ke sath
    - Brand name chhota sa bottom mein
    """
    canvas = _gradient_background(PIN_WIDTH, PIN_HEIGHT)
    draw = ImageDraw.Draw(canvas)

    product_img = _download_image(product_image_url)

    # Product image ko fit karo (max 85% width, center mein), aspect ratio maintain
    max_w = int(PIN_WIDTH * 0.85)
    max_h = int(PIN_HEIGHT * 0.72)
    product_img = ImageOps.contain(product_img, (max_w, max_h))

    px = (PIN_WIDTH - product_img.width) // 2
    py = int(PIN_HEIGHT * 0.08)

    # Thin gold border around product image
    border_pad = 8
    draw.rectangle(
        [px - border_pad, py - border_pad,
         px + product_img.width + border_pad, py + product_img.height + border_pad],
        outline=GOLD, width=2
    )
    canvas.paste(product_img, (px, py))

    # Brand name at bottom
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 42)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), brand_name, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - tw) / 2, PIN_HEIGHT - 130), brand_name, font=font, fill=(224, 197, 140))

    canvas.save(output_path, "PNG")
    return output_path
