"""
Product image ko Pinterest ke ideal portrait shape (1000x1500) mein
design karta hai - FULL-BLEED style: product photo edge-to-edge poore
canvas ko fill karta hai (crop karke), sirf neeche ek halka gradient
overlay hota hai jisme brand naam likha hota hai. Ye "card on background"
wale generic look se bachata hai - professional listing-photo jaisa lagta hai.
"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

PIN_WIDTH = 1000
PIN_HEIGHT = 1500

GOLD = (222, 196, 150)
WHITE = (255, 255, 255)


def _download_image(url):
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def design_portrait_pin(product_image_url, brand_name="Lumière & Luxe", output_path="pin.png"):
    """
    Product image ko full-bleed portrait pin mein convert karta hai:
    - Photo poore 1000x1500 canvas ko edge-to-edge cover karta hai (center-cropped)
    - Neeche ek subtle dark-to-transparent gradient overlay (text legibility ke liye)
    - Brand name + tagline us gradient ke upar, chhota aur elegant
    """
    product_img = _download_image(product_image_url)

    # Poore canvas ko cover karo (crop karke, koi khaali jagah/background nahi)
    canvas = ImageOps.fit(product_img, (PIN_WIDTH, PIN_HEIGHT), method=Image.LANCZOS, centering=(0.5, 0.42))
    canvas = canvas.convert("RGBA")

    # --- Bottom gradient overlay (sirf neeche ka ~22% hissa, text ke liye) ---
    overlay_height = int(PIN_HEIGHT * 0.22)
    gradient = Image.new("RGBA", (PIN_WIDTH, overlay_height), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(overlay_height):
        alpha = int(190 * (y / overlay_height) ** 1.3)
        grad_draw.line([(0, y), (PIN_WIDTH, y)], fill=(10, 10, 10, alpha))

    canvas.paste(gradient, (0, PIN_HEIGHT - overlay_height), gradient)

    draw = ImageDraw.Draw(canvas)

    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 40)
        font_tagline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 22)
    except Exception:
        font_brand = font_tagline = ImageFont.load_default()

    # Thin gold divider line
    line_y = PIN_HEIGHT - 95
    draw.line([(PIN_WIDTH // 2 - 45, line_y), (PIN_WIDTH // 2 + 45, line_y)], fill=GOLD, width=2)

    # Brand name
    bbox = draw.textbbox((0, 0), brand_name, font=font_brand)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - tw) / 2, PIN_HEIGHT - 78), brand_name, font=font_brand, fill=WHITE)

    # Small tagline
    tagline = "925 Sterling Silver"
    bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
    tw = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - tw) / 2, PIN_HEIGHT - 32), tagline, font=font_tagline, fill=(230, 225, 215))

    canvas.convert("RGB").save(output_path, "PNG")
    return output_path
