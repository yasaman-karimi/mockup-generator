import os
from io import BytesIO
from typing import List, Tuple

from celery import shared_task
from django.conf import settings
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from .models import Mockup, MockupJob


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _load_font(font_name: str | None, size: int) -> ImageFont.ImageFont:
    # Try to load a TrueType font if provided; fall back to default
    if font_name:
        # look within assets/fonts first
        assets_font_path = os.path.join(
            settings.BASE_DIR, "assets", "fonts", f"{font_name}.ttf"
        )
        if os.path.exists(assets_font_path):
            try:
                return ImageFont.truetype(assets_font_path, size=size)
            except Exception:
                pass
        # try a common system font if available
        for candidate in [
            f"{font_name}.ttf",
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
            "Arial.ttf",
            "arial.ttf",
        ]:
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                continue
    # default bitmap font
    return ImageFont.load_default()


def _load_base_image(color: str, size=(800, 800)) -> Image.Image:
    # Try to load provided base shirt image; else, create a simple colored canvas
    base_path = os.path.join(settings.BASE_DIR, "assets", "tshirts", f"{color}.png")
    if os.path.exists(base_path):
        try:
            return Image.open(base_path).convert("RGBA")
        except Exception:
            pass
    # fallback: solid color background approximating shirt color
    color_map = {
        "yellow": (255, 230, 90),
        "black": (20, 20, 20),
        "white": (240, 240, 240),
        "blue": (70, 130, 180),
    }
    img = Image.new("RGBA", size, color_map.get(color, (200, 200, 200)))
    return img


def _draw_centered_text(
    img: Image.Image,
    text: str,
    font: ImageFont.ImageFont,
    text_rgb: Tuple[int, int, int],
):
    draw = ImageDraw.Draw(img)
    # Calculate text position for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (img.width - text_w) // 2
    y = (img.height - text_h) // 2
    draw.text((x, y), text, fill=text_rgb + (255,), font=font)


@shared_task(bind=True)
def generate_mockups_task(self, job_id: int):
    job = MockupJob.objects.get(id=job_id)
    job.status = "STARTED"
    job.save(update_fields=["status"])

    colors: List[str] = job.shirt_colors or ["yellow", "black", "white", "blue"]
    text_rgb = _hex_to_rgb(job.text_color or "#000000")

    output_dir = os.path.join(settings.MEDIA_ROOT, "mockups")
    os.makedirs(output_dir, exist_ok=True)

    try:
        with transaction.atomic():
            for color in colors:
                base = _load_base_image(color)
                font = _load_font(job.font, size=48)
                _draw_centered_text(base, job.text, font, text_rgb)

                filename = f"job{job.id}_{color}.png"
                file_path = os.path.join(output_dir, filename)
                base.save(file_path, format="PNG")

                rel_path = os.path.join("mockups", filename)
                Mockup.objects.create(
                    job=job,
                    text=job.text,
                    font=job.font,
                    text_color=job.text_color,
                    shirt_color=color,
                    image=rel_path,
                )

        job.status = "SUCCESS"
        job.save(update_fields=["status"])
        return {"job_id": job.id, "count": len(colors)}

    except Exception as exc:
        job.status = "FAILURE"
        job.save(update_fields=["status"])
        raise exc
