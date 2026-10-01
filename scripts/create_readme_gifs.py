"""Generate the animated README explainers.

The GIFs are deliberately drawn from project metrics rather than stock media so they
remain lightweight, accurate and readable when GitHub renders the README.

Run after installing Pillow:
    python scripts/create_readme_gifs.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# A dark, high-contrast palette that remains readable on GitHub's light/dark themes.
BG = "#071A2C"
PANEL = "#102D47"
PANEL_ACTIVE = "#0E6B78"
PANEL_EDGE = "#244866"
TEXT = "#F8FBFF"
MUTED = "#B8C9D9"
TEAL = "#2DD4BF"
BLUE = "#5AAAF7"
GOLD = "#F7B84B"
GREEN = "#39D98A"
PURPLE = "#B78CFF"
RED = "#F28787"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
REGULAR = FONT_DIR / "DejaVuSans.ttf"
BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else REGULAR), size)


def text_box(draw: ImageDraw.ImageDraw, box, text: str, fill, fnt, *, align="left", spacing=4):
    """Draw a multiline block vertically centred in a bounding box."""
    left, top, right, bottom = box
    text_bbox = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align=align)
    height = text_bbox[3] - text_bbox[1]
    if align == "center":
        anchor_x = (left + right) / 2
        draw.multiline_text((anchor_x, top + (bottom - top - height) / 2), text, font=fnt, fill=fill,
                            spacing=spacing, align="center", anchor="ma")
    else:
        draw.multiline_text((left, top + (bottom - top - height) / 2), text, font=fnt, fill=fill,
                            spacing=spacing)


def rounded(draw: ImageDraw.ImageDraw, box, fill, outline=None, width=1, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def dotted_arrow(draw: ImageDraw.ImageDraw, x1, y, x2, color, progress: float):
    """Animate dots travelling between pipeline cards."""
    draw.line((x1, y, x2, y), fill="#31556E", width=3)
    length = x2 - x1
    for i in range(5):
        phase = ((i / 5) + progress) % 1
        x = x1 + phase * length
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)
    draw.polygon([(x2, y), (x2 - 11, y - 7), (x2 - 11, y + 7)], fill=color)


def create_pipeline_gif():
    width, height = 1200, 650
    cards = [
        ("01", "Property data", "3,800 past\nsales", BLUE),
        ("02", "Prepare", "dates, IDs,\nfeatures", TEAL),
        ("03", "Train & tune", "5 model\napproaches", GOLD),
        ("04", "Validate", "CV + held-out\ntest", PURPLE),
        ("05", "Explain", "RMSE, R2\n& insights", GREEN),
    ]
    card_width, card_height = 204, 220
    start_x, card_y, gap = 54, 255, 27
    frames = []

    for frame_no in range(25):
        active = (frame_no // 5) % len(cards)
        pulse = 0.5 + 0.5 * ((frame_no % 5) / 4)
        image = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(image)

        # Accent orbs give the animation a little warmth without hurting legibility.
        draw.ellipse((-100, -160, 300, 240), fill="#0B3651")
        draw.ellipse((920, 425, 1330, 830), fill="#0A3C48")
        draw.rectangle((0, 0, width, 86), fill="#0B2339")
        draw.text((54, 25), "ROBUST REGRESSION ENGINE", font=font(18, True), fill=TEAL)
        draw.text((54, 116), "How one property becomes a\ntrusted price estimate", font=font(43, True),
                  fill=TEXT, spacing=5)
        draw.text((54, 218), "A repeatable machine-learning pipeline, from past sales to a measured prediction.",
                  font=font(18), fill=MUTED)

        for i, (number, title, body, accent) in enumerate(cards):
            x = start_x + i * (card_width + gap)
            is_active = i == active
            panel = PANEL_ACTIVE if is_active else PANEL
            edge = accent if is_active else PANEL_EDGE
            rounded(draw, (x, card_y, x + card_width, card_y + card_height), panel, edge, 3 if is_active else 1)
            # Number marker
            marker = 31 + int(4 * pulse) if is_active else 31
            draw.ellipse((x + 20, card_y + 20, x + 20 + marker, card_y + 20 + marker), fill=accent)
            number_bbox = draw.textbbox((0, 0), number, font=font(15, True))
            nw = number_bbox[2] - number_bbox[0]
            nh = number_bbox[3] - number_bbox[1]
            draw.text((x + 20 + (marker - nw) / 2, card_y + 20 + (marker - nh) / 2 - 2), number,
                      font=font(15, True), fill=BG)
            text_box(draw, (x + 20, card_y + 72, x + card_width - 18, card_y + 126), title, TEXT,
                     font(21, True), align="left")
            text_box(draw, (x + 20, card_y + 140, x + card_width - 18, card_y + 194), body, MUTED,
                     font(17), align="left")
            if i < len(cards) - 1:
                dotted_arrow(draw, x + card_width + 4, card_y + card_height / 2,
                             x + card_width + gap - 5, accent if i <= active else "#31556E", frame_no / 5)

        # The highlight becomes a clear narrative cue near the bottom.
        label = cards[active][1]
        detail = [
            "Capture useful history from recorded property sales.",
            "Make dates and columns safe for fair comparisons.",
            "Let different algorithms search for useful patterns.",
            "Check performance on examples the model did not learn from.",
            "Turn scores into a decision people can understand.",
        ][active]
        rounded(draw, (150, 540, 1050, 602), "#0B2D42", "#255A68", 1, 14)
        draw.text((180, 558), f"NOW: {label.upper()}", font=font(15, True), fill=cards[active][3])
        draw.text((390, 558), detail, font=font(15), fill=TEXT)
        draw.text((54, 618), "Animated project overview", font=font(12), fill="#7693A8")
        draw.text((1146, 618), f"{active + 1}/5", font=font(12, True), fill="#7693A8")
        frames.append(image.quantize(colors=96, method=Image.Quantize.MEDIANCUT))

    frames[0].save(
        ASSETS / "robust-regression-pipeline.gif",
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
        optimize=True,
        disposal=2,
    )


def create_scoreboard_gif():
    width, height = 1120, 660
    # Values from the notebook's recorded test run. Lower RMSE is better.
    models = [
        ("Random Forest", 2.387227, 0.9292, GREEN),
        ("Ridge", 2.539952, 0.9199, BLUE),
        ("Lasso", 2.542966, 0.9197, TEAL),
        ("Decision Tree", 2.866278, 0.8980, GOLD),
        ("SVR Linear", 8.939711, 0.0077, PURPLE),
        ("SVR RBF", 8.976954, -0.0006, RED),
    ]
    max_value = 9.2
    frames = []

    for frame_no in range(20):
        # Ease from 0 to 1; final four frames hold the finished comparison.
        progress = min(1.0, frame_no / 15)
        eased = 1 - (1 - progress) ** 3
        image = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(image)
        draw.ellipse((805, -165, 1305, 310), fill="#113753")
        draw.ellipse((-175, 470, 280, 900), fill="#0B3744")
        draw.rectangle((0, 0, width, 86), fill="#0B2339")
        draw.text((55, 25), "MODEL SCOREBOARD", font=font(18, True), fill=TEAL)
        draw.text((55, 116), "The engine compares models,\nnot guesses.", font=font(40, True), fill=TEXT, spacing=4)
        draw.text((55, 213), "Test RMSE in millions of INR  •  Lower is better", font=font(18), fill=MUTED)

        label_x, bar_x, bar_right = 55, 300, 976
        top, spacing, bar_h = 276, 51, 27
        for i, (name, score, r2, color) in enumerate(models):
            y = top + i * spacing
            is_best = i == 0 and progress > 0.75
            draw.text((label_x, y + 2), name, font=font(17, True if is_best else False),
                      fill=TEXT if is_best else MUTED)
            rounded(draw, (bar_x, y, bar_right, y + bar_h), "#173852", None, radius=9)
            shown = score * eased
            end = bar_x + (bar_right - bar_x) * (shown / max_value)
            rounded(draw, (bar_x, y, end, y + bar_h), color, None, radius=9)
            value_text = f"{score:.2f}M"
            draw.text((992, y + 1), value_text, font=font(17, True), fill=TEXT)
            if is_best:
                rounded(draw, (bar_x + 10, y + 4, bar_x + 117, y + bar_h - 4), "#0B4C42", None, radius=8)
                draw.text((bar_x + 21, y + 6), "BEST TEST FIT", font=font(11, True), fill=GREEN)

        if progress >= 0.75:
            rounded(draw, (55, 592, 1065, 640), "#0B3E3B", "#216E63", 1, 13)
            draw.text((78, 607), "Random Forest leads this run", font=font(16, True), fill=GREEN)
            draw.text((405, 607), "R2 0.9292  •  MAE INR 1.743M  •  Review stability and fairness before deployment",
                      font=font(14), fill=TEXT)
        else:
            draw.text((55, 614), "Scores animate from the notebook's recorded held-out test set.", font=font(13), fill="#7693A8")
        frames.append(image.quantize(colors=96, method=Image.Quantize.MEDIANCUT))

    frames[0].save(
        ASSETS / "model-comparison.gif",
        save_all=True,
        append_images=frames[1:],
        duration=150,
        loop=0,
        optimize=True,
        disposal=2,
    )


if __name__ == "__main__":
    create_pipeline_gif()
    create_scoreboard_gif()
    for gif in (ASSETS / "robust-regression-pipeline.gif", ASSETS / "model-comparison.gif"):
        print(f"Created {gif.relative_to(ROOT)} ({gif.stat().st_size / 1024:.1f} KiB)")
