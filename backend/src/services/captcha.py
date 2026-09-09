import io
import random
import string
from PIL import Image, ImageDraw, ImageFont
from src.config.settings import settings


def generate_captcha_text(length: int = None) -> str:
    length = length or settings.CAPTCHA_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text: str) -> io.BytesIO:
    width = settings.CAPTCHA_WIDTH
    height = settings.CAPTCHA_HEIGHT

    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 40)
        except (OSError, IOError):
            font = ImageFont.load_default()

    for i, char in enumerate(text):
        x = 20 + i * 35
        y = random.randint(10, 30)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, font=font, fill=color)

    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    for _ in range(100):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.point((x, y), fill=color)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
