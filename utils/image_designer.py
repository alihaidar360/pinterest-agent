"""
Product image ko Pinterest ke ideal portrait shape (1000x1500) mein
design karta hai - CLEAN, BRIGHT boho aesthetic (Pinterest par best
perform karne wala style: product sabse prominent, minimal distraction).
"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

PIN_WIDTH = 1000
PIN_HEIGHT = 1500

# Soft, warm, boho-neutral palette - light background taaki product pop kare
CREAM_TOP = (250, 245, 236)
CREAM_BOTTOM = (238, 228, 210)
GOLD = (176, 141, 87)
TEXT_DARK = (54, 48, 40)
TEXT_MUTED = (128, 116, 98)


def _download_image(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _soft_gradient_background(w, h):
    bg = Image.new("RGB", (w, h), CREAM_TOP)
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        r = int(CREAM_TOP[0] + (CREAM_BOTTOM[0] - CREAM_TOP[0]) * t)
        g = int(CREAM_TOP[1] + (CREAM_BOTTOM[1] - CREAM_TOP[1]) * t)
        b = int(CREAM_TOP[2] + (CREAM_BOTTOM[2] - CREAM_TOP[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return bg


def _add_soft_shadow(base_img, product_img, position):
    """Product ke peeche ek subtle drop shadow daalta hai depth ke liye."""
    shadow = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    shadow_shape = Image.new("L", product_img.size, 60)
    shadow.paste(shadow_shape, (position[0] + 10, position[1] + 14), shadow_shape)
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base_img.paste(shadow, (0, 0), shadow)


def design_portrait_pin(product_image_url, brand_name="Lumière & Luxe", output_path="pin.png"):
    """
    Product image ko clean, bright, Pinterest-optimized portrait pin mein
    convert karta hai:
    - Soft cream/boho gradient background
    - Product image bada aur center mein, subtle shadow ke sath (no heavy border)
    - Chhota brand wordmark neeche, minimal aur non-distracting
    """
    canvas = _soft_gradient_background(PIN_WIDTH, PIN_HEIGHT).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    product_img = _download_image(product_image_url)

    # Product ko bada rakho - 90% width tak, taaki wahi hero ho
    max_w = int(PIN_WIDTH * 0.90)
    max_h = int(PIN_HEIGHT * 0.78)
    product_img = ImageOps.contain(product_img, (max_w, max_h))

    px = (PIN_WIDTH - product_img.width) // 2
    py = int(PIN_HEIGHT * 0.06)

    _add_soft_shadow(canvas, product_img, (px, py))
    canvas.paste(product_img, (px, py))

    # Fonts
    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 34)
        font_tagline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 20)
    except Exception:
        font_brand = font_tagline = ImageFont.load_default()

    # Thin gold divider line above brand name
    line_y = PIN_HEIGHT - 110
    draw.line([(PIN_WIDTH // 2 - 40, line_y), (PIN_WIDTH // 2 + 40, line_y)], fill=GOLD, width=2)

    # Brand name - small, elegant, not overpowering
    bbox = draw.textbbox((0, 0), brand_name, font=font_brand)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - tw) / 2, PIN_HEIGHT - 95), brand_name, font=font_brand, fill=TEXT_DARK)

    # Small tagline
    tagline = "925 Sterling Silver"
    bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - tw) / 2, PIN_HEIGHT - 50), tagline, font=font_tagline, fill=TEXT_MUTED)

    canvas.convert("RGB").save(output_path, "PNG")
    return output_path
