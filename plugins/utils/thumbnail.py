import io
import os
import random
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "Assets/welcome.jpeg"
NAME_FONT_PATH = "Assets/namefont.ttf"
INFO_FONT_PATH = "Assets/fonts.ttf"

TEMP_DIR = "Assets/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

END_LINES = [
    "Glad to have you with us 🐾",
    "Make yourself comfortable 💜",
    "Let the journey begin ✨",
    "Welcome aboard 🌸",
    "You’re among friends now 🐼"
]


def make_circle(img: Image.Image, size: int):
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=285)
    img.putalpha(mask)
    return img


async def generate_welcome_image(client, user):
    # ── Load template
    base = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # ── Fonts
    name_font = ImageFont.truetype(NAME_FONT_PATH, 46)
    info_font = ImageFont.truetype(INFO_FONT_PATH, 30)
    small_font = ImageFont.truetype(INFO_FONT_PATH, 32)

    # ── Text data
    name = user.first_name or "New Member"
    uid = str(user.id)
    username = f"@{user.username}" if user.username else "None"


    # ── Text placement (tuned to your template)
    draw.text((300, 270), name, font=name_font, fill=(235, 235, 245))
    draw.text((340, 365), uid, font=info_font, fill=(200, 200, 210))
    draw.text((400, 445), username, font=info_font, fill=(200, 200, 210))


    # ── Download real user profile photo
    avatar_path = f"{TEMP_DIR}/{user.id}.jpg"

    try:
        if user.photo:
            await client.download_media(
                user.photo.big_file_id,
                file_name=avatar_path
            )
            avatar = Image.open(avatar_path).convert("RGBA")
        else:
            raise Exception("No profile photo")

    except Exception:
        avatar = Image.new("RGBA", (420, 420), (180, 180, 180, 255))

    avatar = make_circle(avatar, 470)

    # ── Paste avatar (right side)
    base.paste(avatar, (835, 119), avatar)

    # ── Export image
    output = io.BytesIO()
    output.name = "welcome.png"
    base.save(output, format="PNG")
    output.seek(0)

    # Cleanup
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

    return output
