"""Create the plain-language theory PDF for the Robust Regression Engine notebook.

Run with a Python environment that has ReportLab installed:
    python create_theory_pdf.py

The source values and reported model scores below are taken from
Robust_Reression_Engine.ipynb and Advanced_Regression_HousePrice_Dataset.csv.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Robust_Regression_Theory_Guide.pdf"

# Palette: high contrast when printed, but friendly on screen.
NAVY = HexColor("#102A43")
BLUE = HexColor("#1F5F99")
TEAL = HexColor("#137C8B")
MINT = HexColor("#E8F5F3")
SKY = HexColor("#EAF2FA")
GOLD = HexColor("#D99600")
PALE_GOLD = HexColor("#FFF5D6")
INK = HexColor("#1F2933")
MUTED = HexColor("#52606D")
LIGHT = HexColor("#F5F7FA")
LINE = HexColor("#D9E2EC")
WHITE = colors.white
RED = HexColor("#B42318")
GREEN = HexColor("#147D64")


class Rule(Flowable):
    """A thin horizontal rule."""

    def __init__(self, width: float, color=LINE, thickness: float = 0.8, space: float = 6):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.space = space
        self.height = thickness + 2 * space

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space, self.width, self.space)


class Callout(Flowable):
    """A wrapped, coloured callout card containing Platypus content."""

    def __init__(self, title: str, body: str, width: float, styles: dict, kind: str = "plain"):
        super().__init__()
        palette = {
            "plain": (SKY, BLUE),
            "tip": (MINT, TEAL),
            "warning": (PALE_GOLD, GOLD),
            "result": (HexColor("#EDF7F1"), GREEN),
        }
        self.background, self.accent = palette[kind]
        self.width = width
        self.title = Paragraph(title, styles["callout_title"])
        self.body = Paragraph(body, styles["callout_body"])
        self.pad = 9
        self.title.wrap(width - 2 * self.pad - 5, 1000)
        self.body.wrap(width - 2 * self.pad - 5, 1000)
        self.height = self.pad + self.title.height + 4 + self.body.height + self.pad

    def wrap(self, availWidth, availHeight):
        width = min(self.width, availWidth)
        self.width = width
        self.title.wrap(width - 2 * self.pad - 5, availHeight)
        self.body.wrap(width - 2 * self.pad - 5, availHeight)
        self.height = self.pad + self.title.height + 4 + self.body.height + self.pad
        return width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.background)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.roundRect(0, 0, 5, self.height, 3, fill=1, stroke=0)
        title_y = self.height - self.pad - self.title.height
        self.title.drawOn(c, self.pad + 6, title_y)
        self.body.drawOn(c, self.pad + 6, title_y - 4 - self.body.height)


class WorkflowDiagram(Flowable):
    """Simple end-to-end visual, drawn as vector shapes."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 122

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def draw(self):
        c = self.canv
        labels = [
            ("1", "Property\ndata", SKY, BLUE),
            ("2", "Clean and\nprepare", MINT, TEAL),
            ("3", "Train several\nmodels", PALE_GOLD, GOLD),
            ("4", "Test on\nnew data", HexColor("#F3E8FF"), HexColor("#7E22CE")),
            ("5", "Choose with\ncare", HexColor("#EDF7F1"), GREEN),
        ]
        gap = 13
        bw = (self.width - gap * (len(labels) - 1)) / len(labels)
        bh = 68
        y = 37
        for i, (number, label, fill, accent) in enumerate(labels):
            x = i * (bw + gap)
            c.setFillColor(fill)
            c.roundRect(x, y, bw, bh, 7, fill=1, stroke=0)
            c.setFillColor(accent)
            c.circle(x + 16, y + bh - 16, 9, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(x + 16, y + bh - 19, number)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 8.5)
            lines = label.split("\n")
            for j, line in enumerate(lines):
                c.drawCentredString(x + bw / 2, y + 27 - j * 11, line)
            if i < len(labels) - 1:
                sx = x + bw + 2
                ex = x + bw + gap - 3
                cy = y + bh / 2
                c.setStrokeColor(MUTED)
                c.setLineWidth(1.2)
                c.line(sx, cy, ex, cy)
                c.setFillColor(MUTED)
                c.setStrokeColor(MUTED)
                c.line(ex, cy, ex - 4, cy + 3)
                c.line(ex, cy, ex - 4, cy - 3)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 12, "The notebook follows this loop for house-price prediction.")


class ModelLandscape(Flowable):
    """Visual comparison of model families and their mental models."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 150

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def draw(self):
        c = self.canv
        cards = [
            ("Regularized\nlinear", "One weighted\nformula", SKY, BLUE),
            ("Decision\ntree", "A chain of\nif/then rules", MINT, TEAL),
            ("Random\nforest", "Many trees\nvote/average", PALE_GOLD, GOLD),
            ("SVR", "A best-fit\nquiet corridor", HexColor("#F3E8FF"), HexColor("#7E22CE")),
        ]
        gap = 12
        bw = (self.width - gap * 3) / 4
        bh = 109
        y = 23
        for i, (title, body, fill, accent) in enumerate(cards):
            x = i * (bw + gap)
            c.setFillColor(fill)
            c.roundRect(x, y, bw, bh, 7, fill=1, stroke=0)
            c.setFillColor(accent)
            c.roundRect(x, y + bh - 25, bw, 25, 7, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 8.4)
            for j, line in enumerate(title.split("\n")):
                c.drawCentredString(x + bw / 2, y + bh - 11 - j * 9, line)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8.5)
            for j, line in enumerate(body.split("\n")):
                c.drawCentredString(x + bw / 2, y + 43 - j * 11, line)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 7, "Different models look for useful patterns in different ways.")


class BarChart(Flowable):
    """A compact labelled horizontal bar chart (no third-party plotting required)."""

    def __init__(
        self,
        items: Sequence[tuple[str, float]],
        width: float,
        title: str,
        suffix: str = "",
        color=TEAL,
        value_format: str = ".2f",
        note: str | None = None,
    ):
        super().__init__()
        self.items = list(items)
        self.width = width
        self.title = title
        self.suffix = suffix
        self.color = color
        self.value_format = value_format
        self.note = note
        self.height = 40 + len(self.items) * 23 + (16 if note else 0)

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        self.height = 40 + len(self.items) * 23 + (16 if self.note else 0)
        return self.width, self.height

    def draw(self):
        c = self.canv
        left = 135
        right = 44
        top = self.height - 22
        chart_w = self.width - left - right
        max_value = max(value for _, value in self.items) or 1
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0, self.height - 12, self.title)
        for i, (label, value) in enumerate(self.items):
            y = top - i * 23
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8.3)
            c.drawRightString(left - 8, y + 3, label)
            c.setFillColor(LIGHT)
            c.roundRect(left, y - 4, chart_w, 11, 3, fill=1, stroke=0)
            c.setFillColor(self.color)
            c.roundRect(left, y - 4, chart_w * value / max_value, 11, 3, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(left + chart_w + 6, y, format(value, self.value_format) + self.suffix)
        if self.note:
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 7.5)
            c.drawString(0, 3, self.note)


class MetricMeter(Flowable):
    """A small four-part visual for model-result reading."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 116

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def draw(self):
        c = self.canv
        items = [
            ("MAE", "Typical miss\nin INR", "Lower is better", SKY, BLUE),
            ("MSE", "Squares each\nmiss", "Lower is better", HexColor("#F3E8FF"), HexColor("#7E22CE")),
            ("RMSE", "Typical miss,\nbig errors count", "Lower is better", PALE_GOLD, GOLD),
            ("R-squared", "Share of price\nvariation captured", "Higher is better", MINT, TEAL),
        ]
        gap = 10
        bw = (self.width - 3 * gap) / 4
        for i, (title, body, footer, fill, accent) in enumerate(items):
            x = i * (bw + gap)
            c.setFillColor(fill)
            c.roundRect(x, 8, bw, 98, 6, fill=1, stroke=0)
            c.setFillColor(accent)
            c.roundRect(x, 83, bw, 23, 6, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 8.2)
            c.drawCentredString(x + bw / 2, 92, title)
            c.setFillColor(INK)
            c.setFont("Helvetica", 7.8)
            for j, line in enumerate(body.split("\n")):
                c.drawCentredString(x + bw / 2, 60 - j * 10, line)
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 7.2)
            c.drawCentredString(x + bw / 2, 21, footer)


def make_styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10,
            leading=13, textColor=TEAL, alignment=TA_CENTER, spaceAfter=10,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=29,
            leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=9,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=13,
            leading=18, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", parent=base["Normal"], fontName="Helvetica", fontSize=9.3,
            leading=14, textColor=MUTED, alignment=TA_CENTER,
        ),
        "part": ParagraphStyle(
            "part", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=10,
            leading=13, textColor=TEAL, spaceBefore=4, spaceAfter=6, uppercase=True,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=21,
            leading=25, textColor=NAVY, spaceBefore=5, spaceAfter=10, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14.2,
            leading=18, textColor=BLUE, spaceBefore=15, spaceAfter=6, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.7,
            leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=3, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.45,
            leading=14.1, textColor=INK, spaceAfter=7,
        ),
        "body_small": ParagraphStyle(
            "body_small", parent=base["BodyText"], fontName="Helvetica", fontSize=8.45,
            leading=11.8, textColor=INK, spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["BodyText"], fontName="Helvetica", fontSize=9.35,
            leading=13.5, textColor=INK, leftIndent=15, firstLineIndent=-10, spaceAfter=4,
        ),
        "quote": ParagraphStyle(
            "quote", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=10,
            leading=14.5, textColor=NAVY, leftIndent=14, rightIndent=14, spaceBefore=5, spaceAfter=8,
        ),
        "formula": ParagraphStyle(
            "formula", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9.5,
            leading=14, textColor=NAVY, leftIndent=14, rightIndent=14, backColor=LIGHT,
            borderColor=LINE, borderWidth=0.4, borderPadding=7, spaceAfter=8,
        ),
        "callout_title": ParagraphStyle(
            "callout_title", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9.25,
            leading=11.2, textColor=NAVY,
        ),
        "callout_body": ParagraphStyle(
            "callout_body", parent=base["Normal"], fontName="Helvetica", fontSize=8.8,
            leading=12.3, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "table_head", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7.8,
            leading=9.3, textColor=WHITE,
        ),
        "table_cell": ParagraphStyle(
            "table_cell", parent=base["Normal"], fontName="Helvetica", fontSize=7.8,
            leading=10, textColor=INK,
        ),
        "table_cell_small": ParagraphStyle(
            "table_cell_small", parent=base["Normal"], fontName="Helvetica", fontSize=7.1,
            leading=8.6, textColor=INK,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=7.8,
            leading=10.5, textColor=MUTED, spaceBefore=3, spaceAfter=7,
        ),
        "toc": ParagraphStyle(
            "toc", parent=base["BodyText"], fontName="Helvetica", fontSize=10,
            leading=19, textColor=INK,
        ),
        "toc_num": ParagraphStyle(
            "toc_num", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=10,
            leading=19, textColor=TEAL,
        ),
        "glossary_term": ParagraphStyle(
            "glossary_term", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.8,
            leading=11.5, textColor=NAVY,
        ),
        "glossary_def": ParagraphStyle(
            "glossary_def", parent=base["BodyText"], fontName="Helvetica", fontSize=8.7,
            leading=11.7, textColor=INK,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName="Helvetica", fontSize=7.3,
            textColor=MUTED,
        ),
    }


S = make_styles()
CONTENT_WIDTH = A4[0] - 2 * 1.55 * cm


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: Iterable[str], style: str = "bullet") -> list[Paragraph]:
    return [p("&bull; " + item, style) for item in items]


def section(title: str, number: str | None = None) -> list:
    line = f"{number}. {title}" if number else title
    return [p(line, "h2")]


def make_table(rows, widths, *, small: bool = False, header: bool = True, alignments=None):
    cell_style = "table_cell_small" if small else "table_cell"
    data = []
    for r_i, row in enumerate(rows):
        data.append([p(str(v), "table_head" if header and r_i == 0 else cell_style) for v in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY),
        ]
        start = 1
    else:
        start = 0
    for r_i in range(start, len(rows)):
        if (r_i - start) % 2 == 0:
            commands.append(("BACKGROUND", (0, r_i), (-1, r_i), LIGHT))
    if alignments:
        for col, alignment in alignments.items():
            commands.append(("ALIGN", (col, 0), (col, -1), alignment))
    t.setStyle(TableStyle(commands))
    return t


def labelled_number(value: str, label: str, color=TEAL):
    data = [[p(value, "cover_title")], [p(label, "cover_meta")]]
    t = Table(data, colWidths=[3.35 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TEXTCOLOR", (0, 0), (0, 0), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def page_header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(doc.leftMargin, A4[1] - 1.1 * cm, A4[0] - doc.rightMargin, A4[1] - 1.1 * cm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawString(doc.leftMargin, A4[1] - 0.83 * cm, "ROBUST REGRESSION ENGINE | PLAIN-LANGUAGE THEORY GUIDE")
        canvas.setFont("Helvetica", 7.5)
        canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 0.83 * cm, "Notebook companion")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 1.15 * cm, A4[0] - doc.rightMargin, 1.15 * cm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(doc.leftMargin, 0.78 * cm, "Source: Robust_Reression_Engine.ipynb | Values shown are from its recorded run.")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.78 * cm, f"Page {doc.page}")
    canvas.restoreState()


def add_cover(story: list):
    story += [
        Spacer(1, 2.35 * cm),
        p("PLAIN-LANGUAGE THEORY GUIDE", "cover_kicker"),
        p("Robust Regression Engine", "cover_title"),
        p("How a notebook turns property details into a careful house-price estimate", "cover_subtitle"),
        Rule(CONTENT_WIDTH, TEAL, 1.4, 8),
        Spacer(1, 0.15 * cm),
        p(
            "This is a no-code companion to <b>Robust_Reression_Engine.ipynb</b>. "
            "It explains the ideas behind the project, the choices made in the notebook, "
            "and what the reported numbers do and do not mean.",
            "quote",
        ),
        Spacer(1, 0.28 * cm),
    ]
    cards = [[
        labelled_number("3,800", "property-sale records"),
        labelled_number("11", "input features after preparation", BLUE),
        labelled_number("5", "model families / approaches", GOLD),
    ]]
    t = Table(cards, colWidths=[CONTENT_WIDTH / 3] * 3, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [t, Spacer(1, 0.55 * cm)]
    story += [
        Callout(
            "Who this is for",
            "Anyone who wants to understand the project without needing to read Python. "
            "Technical words are introduced in everyday language first, then linked to the notebook term.",
            CONTENT_WIDTH, S, "tip",
        ),
        Spacer(1, 0.34 * cm),
        Callout(
            "One important promise",
            "A model is an evidence-based estimating tool, not a crystal ball. It learns from past examples. "
            "Its number should support a human decision, not replace judgement, local knowledge, or fairness checks.",
            CONTENT_WIDTH, S, "warning",
        ),
        Spacer(1, 1.75 * cm),
        p("Prepared from the notebook and included house-price CSV", "cover_meta"),
        p("All currency figures are Indian rupees (INR).", "cover_meta"),
        PageBreak(),
    ]


def add_contents(story: list):
    story += [p("How to use this guide", "part"), p("A quick map", "h1")]
    story += [
        p("You can read from front to back, or jump straight to a question you have. "
          "The <b>plain-language cards</b> are the shortest explanation; the paragraphs underneath add the why.", "body"),
        Callout(
            "Reading tip",
            "When you see a term in <b>bold</b>, it is a notebook concept. A compact glossary appears at the end. "
            "You do not need to memorise the formulas to understand the conclusions.",
            CONTENT_WIDTH, S, "plain",
        ),
        Spacer(1, 0.28 * cm),
    ]
    toc = [
        ("01", "The big picture: what is being predicted?"),
        ("02", "The data: what each property detail means"),
        ("03", "Preparation: turning a spreadsheet into model-ready input"),
        ("04", "Regularised linear models: Ridge and Lasso"),
        ("05", "Cross-validation: checking a model more than once"),
        ("06", "How model quality is measured"),
        ("07", "Decision trees and Random Forest"),
        ("08", "Support Vector Regression (SVR)"),
        ("09", "What the notebook results say"),
        ("10", "Limits, responsible use, glossary and FAQ"),
    ]
    toc_rows = []
    for number, name in toc:
        toc_rows.append([p(number, "toc_num"), p(name, "toc")])
    t = Table(toc_rows, colWidths=[1.1 * cm, CONTENT_WIDTH - 1.1 * cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [t, Spacer(1, 0.45 * cm), p("A note on the numbers", "h2")]
    story += [
        p("The performance figures in this guide are the outputs already recorded in the notebook. "
          "They are useful for explaining this experiment. If the data or code changes, rerun the notebook and update the report.", "body"),
        p("The notebook uses a fixed <b>random_state = 42</b> for its train/test split and some models. "
          "That is simply a repeatable starting seed: it lets another run reproduce the same random choices.", "body"),
        PageBreak(),
    ]


def add_big_picture(story: list):
    story += [p("Part 1 | Start here", "part"), p("1. The big picture: a prediction problem", "h1")]
    story += [
        p("The project asks a practical question: <b>given the known details of a property, what sale price would be a reasonable estimate?</b> "
          "It answers this by studying thousands of past property-sale examples.", "body"),
        p("This is called <b>supervised machine learning</b>. "
          "'Supervised' means the examples come with an answer already known - here, the recorded house price. "
          "The model looks for patterns linking property details to those answers.", "body"),
        Callout(
            "Everyday analogy",
            "Imagine asking an experienced estate agent to price a home. They would compare size, location, age and nearby amenities with past sales. "
            "The model does a similar comparison, but it learns the pattern from a table of examples rather than personal memory.",
            CONTENT_WIDTH, S, "tip",
        ),
        Spacer(1, 0.18 * cm),
        WorkflowDiagram(CONTENT_WIDTH),
        Spacer(1, 0.18 * cm),
        p("Regression vs classification", "h2"),
        p("<b>Regression</b> predicts a number on a continuous scale, such as a price, temperature or travel time. "
          "<b>Classification</b> predicts a category, such as 'approved / not approved' or 'low / medium / high'. "
          "Because house price is a number, this notebook is a regression project.", "body"),
        p("A prediction is not the same as a guaranteed selling price. It is the model's best estimate based on patterns in the data it has seen. "
          "A real sale can also be affected by negotiation, property condition, market shocks and information that is not in the table.", "body"),
        p("The two roles in the data", "h2"),
        make_table([
            ["Role", "Notebook name", "Plain-language meaning"],
            ["Feature / input", "X", "A clue supplied to the model: area, bedrooms, location score, etc."],
            ["Target / output", "y", "The answer the model tries to learn: <b>house_price_inr</b>."],
            ["Prediction", "y_hat", "The price estimated by the fitted model for a property."],
            ["Residual / error", "actual - predicted", "How far the estimate missed for one sale."],
        ], [3.05*cm, 3.2*cm, CONTENT_WIDTH-6.25*cm]),
        p("The notebook creates <b>X</b> by dropping <b>house_price_inr</b> from the prepared table, then stores that price column separately as <b>y</b>. "
          "This separation matters: a model must not be allowed to peek at the answer while learning.", "body"),
        PageBreak(),
    ]


def add_data(story: list):
    story += [p("Part 2 | Understand the evidence", "part"), p("2. The data: a row is one past sale", "h1")]
    story += [
        p("The CSV contains <b>3,800</b> property-sale records. Each row represents one property, and each column records one detail. "
          "There are no missing values recorded in the notebook's initial check, so the workflow does not need to fill in blanks.", "body"),
        p("The source table has 12 columns. After the date is converted into useful parts and the ID is removed, the model receives 11 input features plus the price target.", "body"),
        p("Data dictionary", "h2"),
        make_table([
            ["Source column", "What it means in everyday language", "How the notebook uses it"],
            ["property_id", "A record label for the property.", "Removed. An ID is not a meaningful property characteristic."],
            ["sale_date", "Date on which the sale was recorded.", "Changed into <b>sale_year</b> and <b>sale_month</b>, then the original date is removed."],
            ["area_sqft", "Indoor/property size in square feet.", "Numeric input. Range: 500 to 3,776 sq ft."],
            ["bedrooms", "Number of bedrooms.", "Numeric count."],
            ["bathrooms", "Number of bathrooms.", "Numeric count."],
            ["location_score", "A supplied rating of the location.", "Numeric score from 1 to 10."],
            ["property_age", "Age of the property (years).", "Numeric input. Range: 1 to 80 years."],
            ["distance_city_km", "Distance from the city in kilometres.", "Numeric input."],
            ["near_school", "Whether a school is nearby.", "Binary flag: 1 means yes; 0 means no."],
            ["near_metro", "Whether a metro connection is nearby.", "Binary flag: 1 means yes; 0 means no."],
            ["crime_rate_index", "A supplied local crime-rate index.", "Numeric input. It is an index, not a direct count."],
            ["house_price_inr", "Recorded sale price in Indian rupees.", "The target the model tries to estimate."],
        ], [3.25*cm, 7.1*cm, CONTENT_WIDTH-10.35*cm], small=True),
        p("Range and scale at a glance", "h2"),
        make_table([
            ["Quantity", "Observed summary from the CSV", "Why it helps a reader"],
            ["House price", "INR 1.51M to INR 59.30M; average INR 20.72M", "Shows the size of the prediction task."],
            ["Area", "500 to 3,776 sq ft; average 1,716.93 sq ft", "A large numerical range compared with simple counts."],
            ["Bedrooms", "1 to 7; average 3.43", "A small count, not a money value."],
            ["Location score", "1 to 10; average 6.50", "A rating with a very different scale from area."],
            ["Sale date", "168 distinct month-level dates in the source", "Potentially captures time-related price changes."],
        ], [3.1*cm, 7.25*cm, CONTENT_WIDTH-10.35*cm], small=True),
        Callout(
            "Important interpretation rule",
            "A column can help prediction without being a cause. For example, a location score may stand in for many unmeasured local qualities. "
            "A model finding a pattern is not proof that changing one number will cause a price to change.",
            CONTENT_WIDTH, S, "warning",
        ),
        PageBreak(),
    ]


def add_preparation(story: list):
    story += [p("Part 3 | Prepare before predicting", "part"), p("3. Preparation: making the table model-ready", "h1")]
    story += [
        p("Models are not clever enough to fix unclear or unsuitable inputs by themselves. Data preparation makes the comparison fair and prevents accidental shortcuts. "
          "The notebook uses several common preparation steps.", "body"),
        p("3.1 Read, inspect and check", "h2"),
        make_table([
            ["Notebook action", "What it checks", "Plain-language purpose"],
            ["<b>pd.read_csv(...)</b>", "Reads the CSV into a table called <b>df</b>.", "Opens the data so it can be inspected and used."],
            ["<b>df.head()</b>", "First few rows.", "A quick sanity check: do columns and values look plausible?"],
            ["<b>df.info()</b>", "Row count, non-null counts and data types.", "Checks whether a column is text, a number, or has missing entries."],
            ["<b>df.describe()</b>", "Typical values, spread, smallest and largest values.", "Finds surprising ranges that may signal data-entry problems."],
            ["<b>df.isnull().sum()</b>", "Blank / missing values per column.", "Shows where a model could otherwise fail or become biased."],
        ], [4.25*cm, 5.15*cm, CONTENT_WIDTH-9.4*cm], small=True),
        p("3.2 Turn a date into useful clues", "h2"),
        p("A date written as text (for example, 2019-12-01) is awkward for many basic models. "
          "The notebook converts <b>sale_date</b> into a date object, extracts <b>sale_year</b> and <b>sale_month</b>, and then removes the original date column. "
          "This allows a model to ask simple questions such as 'were later sales generally more expensive?' or 'is there a month pattern?'.", "body"),
        Callout(
            "A useful nuance",
            "Months wrap around: December (12) is next to January (1), not far away. A basic month number is a reasonable first step, but a mature seasonal model may encode this cycle more carefully or add richer market-time features.",
            CONTENT_WIDTH, S, "plain",
        ),
        p("3.3 Remove a record label", "h2"),
        p("<b>property_id</b> is dropped. An ID usually tells us which row this is, not what the home is worth. "
          "Keeping it could let a model learn accidental ordering patterns that will not help with a genuinely new property. This is sometimes called a <b>spurious shortcut</b>.", "body"),
        p("3.4 Keep training and test data separate", "h2"),
        p("The notebook uses <b>train_test_split(..., test_size=0.2, random_state=42)</b>. "
          "This creates an 80% training set (3,040 sales) and a 20% test set (760 sales). The training examples are the study material; the test examples are a final, held-back exam.", "body"),
        make_table([
            ["Stage", "Records", "What happens here"],
            ["Training set", "3,040 (80%)", "Models learn their patterns and tuning choices are explored here."],
            ["Test set", "760 (20%)", "Final estimates are compared with the held-back known prices."],
        ], [3.0*cm, 3.0*cm, CONTENT_WIDTH-6*cm]),
        p("Why not train and test on the same rows? Because a student who memorises the answer key can look perfect on that key yet fail a new exam. "
          "A held-back test is a check on <b>generalisation</b>: whether a model can work on new, unseen examples.", "body"),
        PageBreak(),
        p("3.5 Scale numerical features when a method needs it", "h2"),
        p("The notebook uses <b>StandardScaler</b> for Ridge, Lasso and SVR. Scaling places numerical features onto a comparable measuring stick. "
          "Without it, an area measured in thousands of square feet could dominate a bedroom count simply because its raw numbers are larger - even when its real predictive value is not.", "body"),
        p("Standardisation for each numeric value: <b>scaled value = (value - training average) / training standard deviation</b>.", "formula"),
        p("A scaled value of 0 means 'around the training average.' A value of +1 means 'about one typical spread above the average.' "
          "This changes the units used by the model; it does not erase the original information.", "body"),
        Callout(
            "Why 'fit' only on training data?",
            "The scaler learns the average and spread from the training rows with <b>fit_transform</b>. It then applies those same settings to the test rows with <b>transform</b>. "
            "Letting the test set influence those settings would leak future exam information into study time.",
            CONTENT_WIDTH, S, "warning",
        ),
        p("Tree-based models do not need this scaling step. A decision tree asks questions such as 'is area below 1,800?', and scaling preserves the order of values. "
          "A threshold changes its numeric label after scaling, but it divides the homes in the same order.", "body"),
        p("3.6 A Pipeline keeps steps together", "h2"),
        p("For cross-validation and SVR, the notebook uses a <b>Pipeline</b>. Think of it as a sealed conveyor belt: each training fold first learns its own scaler, then fits the model. "
          "This prevents a subtle form of data leakage and makes the exact steps repeatable.", "body"),
        PageBreak(),
    ]


def add_regularization(story: list):
    story += [p("Part 4 | Linear models with guardrails", "part"), p("4. Regularised linear models: Ridge and Lasso", "h1")]
    story += [
        p("A <b>linear regression</b> model starts with a simple idea: add up the contributions of the input features. "
          "For example, it can learn that more area usually raises the estimate while greater distance from the city usually lowers it, with all other inputs held constant.", "body"),
        p("A plain-language version of the model is: <b>estimated price = starting price + area contribution + location contribution + age contribution + ...</b>. "
          "The learned multipliers are called <b>coefficients</b>. A positive coefficient raises the estimate when the feature rises; a negative coefficient lowers it.", "body"),
        p("4.1 What is a loss function?", "h2"),
        p("A model needs a score that says how wrong its estimates are. Its <b>loss function</b> is that score during training. "
          "For ordinary linear regression, a common choice is the sum of squared errors: larger misses are punished more strongly. The training process searches for coefficients that make this loss small.", "body"),
        p("Error for one sale = actual price - predicted price. Squared-error loss = add up (error x error) across training sales.", "formula"),
        p("4.2 Why add regularisation?", "h2"),
        p("A model can become overly eager to explain every quirk in the training rows. It may assign very large, fragile coefficients that look good on old data but behave badly on new homes. "
          "<b>Regularisation</b> adds a cost for complexity, encouraging steadier coefficients. It is a guardrail, not a replacement for good data.", "body"),
        Callout(
            "Everyday analogy",
            "If several reviewers are trying to estimate a price, regularisation is a rule that says: 'Do not make an extreme claim unless the evidence is strong.' "
            "It nudges the model toward simpler, more stable explanations.",
            CONTENT_WIDTH, S, "tip",
        ),
        p("Regularisation is particularly helpful with <b>multicollinearity</b>: inputs that overlap in what they tell the model. "
          "For example, bedrooms, bathrooms and area can be related. Without a guardrail, a small data change can make the model shift a lot of credit from one related feature to another.", "body"),
        p("4.3 Ridge regression: shrink, but keep every feature", "h2"),
        p("<b>Ridge regression</b> adds an L2 penalty: it adds the squares of the coefficients to the usual error score, multiplied by a tuning setting called <b>alpha</b>. "
          "Squaring makes especially large coefficients expensive. Ridge normally makes coefficients smaller, but does not set them exactly to zero.", "body"),
        p("Ridge objective = squared prediction error + alpha x sum of (coefficient squared).", "formula"),
        p("In the notebook, Ridge is fitted after scaling. Its cross-validated best alpha is <b>1.0</b> and its test R-squared is about <b>0.9199</b>.", "body"),
        p("4.4 Lasso regression: shrink and sometimes remove", "h2"),
        p("<b>Lasso regression</b> adds an L1 penalty: it adds the absolute sizes of the coefficients. "
          "This has a special effect: some coefficients can become exactly zero. In other words, Lasso can make a compact feature-selection decision inside the model.", "body"),
        p("Lasso objective = squared prediction error + alpha x sum of absolute coefficient sizes.", "formula"),
        p("The notebook's selected Lasso alpha is <b>15,199.11</b>. It makes the <b>near_school</b> coefficient exactly zero in this fitted model.", "body"),
        PageBreak(),
        p("Ridge and Lasso side by side", "h2"),
        make_table([
            ["Question", "Ridge (L2)", "Lasso (L1)"],
            ["Penalty", "Squares of coefficients.", "Absolute sizes of coefficients."],
            ["What happens to coefficients?", "They are pulled closer to zero.", "They are pulled closer to zero; some can become exactly zero."],
            ["Feature selection?", "No: it normally retains all supplied features.", "Yes: zeroed coefficients are excluded by the fitted formula."],
            ["A useful strength", "Stable with overlapping / correlated features.", "Produces a simpler formula when only some inputs appear useful."],
            ["A limitation", "Does not itself reduce the feature list.", "With correlated features, it may choose one and discard another similar clue somewhat arbitrarily."],
        ], [4.1*cm, 6.15*cm, CONTENT_WIDTH-10.25*cm]),
        Callout(
            "Do not over-read a zero",
            "Lasso setting <b>near_school</b> to zero does not mean schools have no real-world value. "
            "It means that, in this dataset, with these other features and this alpha, the model did not need that column to improve its formula enough to keep it.",
            CONTENT_WIDTH, S, "warning",
        ),
        p("4.5 Alpha: the regularisation dial", "h2"),
        p("<b>Alpha</b> controls the strength of the penalty. Very small alpha behaves more like ordinary linear regression and can overfit. "
          "Very large alpha can flatten useful effects so much that the model <b>underfits</b>. The notebook tests 100 alpha values spread from 0.0001 to 100,000 on a logarithmic scale - a wide search that samples orders of magnitude.", "body"),
        p("Alpha values are not universal quality scores. Their best value depends on the units, target scale, model and data. "
          "The important practice is choosing alpha by cross-validation rather than by guessing from the test set.", "body"),
        p("4.6 What the fitted coefficients suggest", "h2"),
        p("Because the linear-model inputs were standardised, each coefficient below is approximately the estimated INR change associated with a one-standard-deviation increase in that feature, <i>holding the other supplied features constant</i>. "
          "It is a model interpretation, not a causal claim.", "body"),
        make_table([
            ["Feature", "Ridge coefficient", "Lasso coefficient", "Plain reading"],
            ["area_sqft", "+ INR 6.95M", "+ INR 6.95M", "The largest positive linear contribution in this run."],
            ["location_score", "+ INR 3.68M", "+ INR 3.67M", "A strong positive association in the data."],
            ["property_age", "- INR 0.65M", "- INR 0.64M", "Older homes tend to have lower estimated price after the other listed inputs are considered."],
            ["bedrooms", "+ INR 0.30M", "+ INR 0.29M", "Small positive contribution compared with area."],
            ["near_school", "+ INR 0.02M", "INR 0", "Retained by Ridge; removed by the selected Lasso formula."],
        ], [3.1*cm, 3.1*cm, 3.1*cm, CONTENT_WIDTH-9.3*cm], small=True),
        PageBreak(),
    ]


def add_cv(story: list):
    story += [p("Part 5 | Test before trusting", "part"), p("5. Cross-validation: several practice exams", "h1")]
    story += [
        p("A single training/test split is useful, but it can be lucky or unlucky depending on which records land in the test set. "
          "<b>Cross-validation (CV)</b> gives a steadier estimate by repeating a train/validation process across several slices of the data.", "body"),
        p("Do not confuse the final <b>test set</b> with a CV <b>validation fold</b>. The test set is the final exam held back from model selection. "
          "Validation folds are practice exams inside the training-and-tuning process.", "body"),
        Callout(
            "The core CV routine",
            "Split the available training data into parts. Train on most parts, validate on the held-out part, rotate until every part has been held out once, then average the scores. "
            "A model that stays good across the rotations is more credible than one that is good only once.",
            CONTENT_WIDTH, S, "tip",
        ),
        p("5.1 K-Fold cross-validation", "h2"),
        p("In <b>5-fold CV</b>, the data is divided into five groups. The model trains on four groups and validates on the remaining group; it repeats this five times. "
          "The notebook uses a shuffled 5-fold split with <b>random_state = 42</b>. Its Ridge pipeline has a mean validation RMSE of <b>INR 2.500M</b>.", "body"),
        p("5.2 Stratified K-Fold for a price target", "h2"),
        p("Stratification tries to keep the mix of important values similar in every fold. It is straightforward for categories, but price is continuous. "
          "The notebook therefore divides price into roughly equal-frequency <b>bins</b> using <b>pd.qcut</b>, then makes each fold contain a similar mixture of low, middle and high price bands. This is a pragmatic regression technique, not a magic requirement.", "body"),
        p("The stratified 5-fold Ridge result has the lowest mean RMSE of the shown CV strategies: <b>INR 2.499M</b>. "
          "The difference from ordinary K-Fold is tiny - only about INR 111 in the displayed averages - so the key conclusion is stability, not a dramatic win.", "body"),
        p("5.3 Leave-One-Out cross-validation (LOOCV)", "h2"),
        p("<b>LOOCV</b> uses one record as validation and all remaining records for training, repeating once per record. It makes excellent use of data, but it can be expensive. "
          "For 3,800 records, this means <b>3,800 separate model fits</b>. The notebook explains that cost rather than running the full scoring loop.", "body"),
        p("5.4 Time Series Split", "h2"),
        p("When time matters, random shuffling can accidentally let a model learn from the future before predicting the past. "
          "<b>TimeSeriesSplit</b> respects order: train on an earlier block and validate on a later block, then move forward. It better imitates 'predict the next period using what was known before.'", "body"),
        Callout(
            "Chronology check",
            "The notebook identifies <b>sale_year</b> and <b>sale_month</b> but applies TimeSeriesSplit to the current row order. In a real deployment, explicitly sort records by the original sale date before a time split and keep the latest period as the final test. Otherwise the rows may not be truly chronological.",
            CONTENT_WIDTH, S, "warning",
        ),
        PageBreak(),
        p("What this notebook's CV results mean", "h2"),
        make_table([
            ["Validation strategy", "Mean RMSE", "Plain-language reading"],
            ["K-Fold (5 folds)", "INR 2.500M", "A stable random-slice check."],
            ["Stratified K-Fold (5 folds)", "INR 2.499M", "Keeps price bands balanced across the folds; almost identical to K-Fold here."],
            ["Time Series Split (5 splits)", "INR 2.523M", "Slightly higher error; closer to a forward-looking scenario if records are properly ordered."],
            ["LOOCV", "Not run as a full score", "Would require 3,800 fits, so it is less practical here."],
        ], [5.25*cm, 3.2*cm, CONTENT_WIDTH-8.45*cm]),
        BarChart(
            [("K-Fold", 2.499566), ("Stratified K-Fold", 2.499455), ("Time Series Split", 2.523275)],
            CONTENT_WIDTH,
            "Mean validation RMSE (millions of INR)",
            suffix="M",
            color=BLUE,
            value_format=".3f",
            note="Lower is better. Values are close, which is a reassuring sign of similar performance across these checks.",
        ),
        p("5.5 Hyperparameter tuning uses CV too", "h2"),
        p("A <b>hyperparameter</b> is a setting chosen before the model is fitted, such as Ridge alpha, tree depth or SVR C. "
          "The notebook uses <b>RidgeCV</b>, <b>LassoCV</b> and <b>GridSearchCV</b> to compare candidate settings by CV score. This is safer than trying settings until the final test score looks best.", "body"),
        p("The word <b>negative</b> in scoring names such as <b>neg_mean_squared_error</b> is a library convention: scikit-learn wants higher scores to be better, so it negates an error that we naturally want to minimise. "
          "The notebook reverses the sign before taking the square root and reporting RMSE.", "body"),
        PageBreak(),
    ]


def add_metrics(story: list):
    story += [p("Part 6 | Read model scores", "part"), p("6. How model quality is measured", "h1")]
    story += [
        p("Every model predicts the same held-back test set, then its estimates are compared with the actual prices. "
          "The notebook uses four common regression metrics. No single metric tells the whole story, so reading more than one is good practice.", "body"),
        MetricMeter(CONTENT_WIDTH),
        p("6.1 Mean Absolute Error (MAE)", "h2"),
        p("<b>MAE</b> is the average size of the mistakes, ignoring whether the estimate was too high or too low. "
          "If MAE is INR 1.74M, think: 'on average, the prediction missed by about INR 1.74M.' It is easy to explain because it uses the same unit as the price.", "body"),
        p("MAE = average of |actual price - predicted price|.", "formula"),
        p("6.2 Mean Squared Error (MSE)", "h2"),
        p("<b>MSE</b> squares each mistake before averaging. A large miss therefore matters much more than a small miss. "
          "It is useful for training and comparison, but its unit is 'rupees squared', which is hard to explain directly. That is why RMSE is often easier to communicate.", "body"),
        p("MSE = average of (actual price - predicted price) squared.", "formula"),
        p("6.3 Root Mean Squared Error (RMSE)", "h2"),
        p("<b>RMSE</b> is the square root of MSE. It returns to INR, while still giving extra weight to expensive mistakes. "
          "In this project, RMSE is a key comparison measure: lower means the model's errors are smaller, with a stronger penalty for large misses.", "body"),
        p("RMSE = square root of MSE.", "formula"),
        p("6.4 R-squared (R2)", "h2"),
        p("<b>R-squared</b> compares the model with a very simple baseline that always predicts the average house price. "
          "A value of 1 would be perfect. A value of 0 means no better than always guessing the average. A negative value means worse than that baseline on the test set.", "body"),
        p("R2 = 1 - (model squared error / baseline squared error).", "formula"),
        Callout(
            "How to read the Random Forest score",
            "Its test R2 is 0.9292. In this test set, the model captures roughly 93% of the variation in recorded prices relative to the average-price baseline. "
            "That is a strong fit for this experiment, but it is not '93% accurate' and it is not a 93% probability that any one price is correct.",
            CONTENT_WIDTH, S, "result",
        ),
        PageBreak(),
    ]


def add_trees(story: list):
    story += [p("Part 7 | Rule-based model families", "part"), p("7. Decision trees and Random Forest", "h1")]
    story += [
        p("The notebook also tries <b>tree-based</b> models. Instead of using one weighted formula, a tree repeatedly divides properties into groups using yes/no questions. "
          "For example: 'is area below a chosen threshold?' Then within each answer group, it asks another question. A final group (a <b>leaf</b>) makes a price estimate based on the examples inside it.", "body"),
        ModelLandscape(CONTENT_WIDTH),
        p("7.1 Decision Tree Regressor", "h2"),
        p("A <b>DecisionTreeRegressor</b> learns thresholds that reduce the variation in price within a group. Trees handle bends and interactions naturally: perhaps area matters differently in high- and low-location-score homes. "
          "But an unrestricted tree can keep splitting until it memorises the training data, which is a classic route to overfitting.", "body"),
        make_table([
            ["Notebook setting", "Value", "Why it is a guardrail"],
            ["max_depth", "6", "Limits how many layers of questions a tree may ask."],
            ["min_samples_split", "10", "Requires at least 10 examples before a group may be split."],
            ["min_samples_leaf", "5", "Requires at least 5 examples in a final leaf; avoids a price based on one or two unusual homes."],
            ["random_state", "42", "Makes any random choices repeatable."],
        ], [4.5*cm, 2.55*cm, CONTENT_WIDTH-7.05*cm]),
        p("With those limits, the single decision tree has test MAE <b>INR 2.115M</b>, RMSE <b>INR 2.866M</b> and R2 <b>0.8980</b>.", "body"),
        p("7.2 Random Forest Regressor", "h2"),
        p("A <b>Random Forest</b> builds many decision trees and averages their predictions. Each tree is exposed to a slightly different view of the training data and feature choices. "
          "Averaging many imperfect but diverse trees usually reduces the tendency of a single tree to chase noise. This is an <b>ensemble</b>: a team of models rather than one model.", "body"),
        make_table([
            ["Notebook setting", "Value", "Plain-language meaning"],
            ["n_estimators", "300", "Build 300 trees, then average them."],
            ["max_depth", "10", "Permit deeper trees than the single-tree model, but still cap complexity."],
            ["min_samples_split", "5", "A group needs at least 5 records before splitting."],
            ["min_samples_leaf", "2", "A leaf needs at least 2 records."],
            ["n_jobs", "-1", "Use available processor cores to build trees faster; it does not change the statistical idea."],
        ], [4.5*cm, 2.55*cm, CONTENT_WIDTH-7.05*cm]),
        p("The forest is the notebook's best test-set performer: MAE <b>INR 1.743M</b>, RMSE <b>INR 2.387M</b> and R2 <b>0.9292</b>.", "body"),
        PageBreak(),
        p("7.3 Feature importance: useful, not causal", "h2"),
        p("Random Forest feature importance asks how much the model's splits, on average, reduced training error using each feature. "
          "It is a model-specific clue about reliance, not a causal statement and not a guarantee that the same ordering will repeat in every sample.", "body"),
        BarChart(
            [
                ("area_sqft", 0.753722),
                ("location_score", 0.208241),
                ("property_age", 0.010136),
                ("distance_city_km", 0.006779),
                ("crime_rate_index", 0.006175),
                ("sale_year", 0.004623),
            ],
            CONTENT_WIDTH,
            "Random Forest feature importance from the notebook",
            suffix="",
            color=TEAL,
            value_format=".3f",
            note="The remaining five inputs each have importance below 0.004. Importances add to 1 across all features.",
        ),
        p("In this run, area and location score dominate the forest's split-based importance. This makes intuitive sense for house prices, but there are important cautions:", "body"),
        *bullets([
            "Importance does <b>not</b> show whether a feature raises or lowers price; it only shows how much the forest used it to split.",
            "Correlated clues can share or trade importance. If area and bedrooms overlap, the model may lean on one more even when both matter in reality.",
            "A feature that was historically useful may be unfair, outdated or unavailable at prediction time. Check appropriateness before deployment.",
        ]),
        Callout(
            "Why trees do not need scaling",
            "A tree cares about order and thresholds. Whether area is written as 1,700 sq ft or as a scaled number, the same homes are above or below a proposed cut-point. "
            "Distance-based and coefficient-based methods are more sensitive to raw scale.",
            CONTENT_WIDTH, S, "plain",
        ),
        PageBreak(),
    ]


def add_svr(story: list):
    story += [p("Part 8 | A different geometric idea", "part"), p("8. Support Vector Regression (SVR)", "h1")]
    story += [
        p("<b>Support Vector Regression</b> tries to draw a function through the data while ignoring small misses inside an acceptable margin. "
          "Imagine a quiet corridor around the prediction line: errors inside the corridor are treated as acceptable, and points outside it push the model to adjust. The especially influential examples are called <b>support vectors</b>.", "body"),
        p("SVR can use a <b>kernel</b>, a mathematical way to represent curved relationships without manually adding every curve as a new column. The notebook compares three kernels.", "body"),
        make_table([
            ["Kernel in notebook", "What it can represent", "Everyday analogy"],
            ["linear", "A straight, weighted relationship in the scaled feature space.", "A flat ruler through the points."],
            ["poly (degree 2)", "Polynomial curves and feature combinations of the chosen degree.", "A smoothly bent ruler."],
            ["rbf", "Flexible local curves based on nearby examples.", "Many small zones of influence around examples."],
        ], [4.0*cm, 6.45*cm, CONTENT_WIDTH-10.45*cm]),
        p("8.1 The three main SVR controls", "h2"),
        make_table([
            ["Control", "Plain-language role", "What a larger value tends to do"],
            ["C", "How strongly the model cares about points outside its acceptable corridor.", "Penalises misses more strongly; can fit training data more tightly and overfit if pushed too far."],
            ["epsilon", "Half-width of the corridor in target units (INR here).", "Ignores a wider range of small errors; may produce a smoother, less sensitive fit."],
            ["gamma (RBF)", "How local each example's influence is.", "Makes influence more local and potentially more wiggly; too high can overfit."],
        ], [2.9*cm, 7.55*cm, CONTENT_WIDTH-10.45*cm]),
        p("The notebook starts with C=10 and epsilon=0.1 for linear and polynomial SVR, and C=100, gamma='scale', epsilon=0.1 for RBF. "
          "It correctly wraps each SVR in a scaling Pipeline because SVR is highly sensitive to feature scale.", "body"),
        Callout(
            "Units matter for epsilon",
            "The target is measured in INR, where prices are in millions. Epsilon=0.1 is tiny relative to a multi-million-rupee price. "
            "Feature scaling helps the inputs, but the notebook does not scale the target. When revisiting SVR, consider target scaling or an epsilon/C search expressed at a meaningful price scale.",
            CONTENT_WIDTH, S, "warning",
        ),
        p("8.2 GridSearchCV: an organised settings search", "h2"),
        p("For RBF SVR, <b>GridSearchCV</b> tries every combination in its supplied grid: 3 values of C x 3 values of gamma x 3 values of epsilon = <b>27 combinations</b>. "
          "With 5-fold CV, it evaluates about 135 validation fits, then refits the best setting. The selected setting is C=100, epsilon=0.01, gamma='scale'.", "body"),
        p("The double underscore in names such as <b>svr__C</b> means 'the C setting of the step named svr inside the Pipeline.'", "body"),
        p("8.3 What happened here?", "h2"),
        p("Every shown SVR variant is much weaker here. The tuned RBF model has RMSE <b>INR 8.977M</b> and R2 <b>-0.0006</b>, worse than the average-price baseline. "
          "This says the chosen feature representation and settings did not suit SVR; it does not make SVR a poor model in every setting.", "body"),
        *bullets([
            "Potential next checks: inspect outliers, scale or transform the target, broaden C and epsilon ranges, and validate a carefully designed chronological split.",
            "Always compare a more complex method with a simple baseline. A complicated kernel is not automatically better.",
        ]),
        PageBreak(),
    ]


def add_results(story: list):
    story += [p("Part 9 | Bring the evidence together", "part"), p("9. What the experiment results say", "h1")]
    story += [
        p("The table below puts the recorded test-set results on one page. Lower MAE and RMSE are better; higher R2 is better. "
          "M means million INR. The models all see the same held-back test rows, which makes this comparison meaningful within this experiment.", "body"),
        make_table([
            ["Model", "MAE", "RMSE", "R2", "Short reading"],
            ["Random Forest", "INR 1.743M", "INR 2.387M", "0.9292", "Best reported test result."],
            ["Ridge (tuned)", "INR 1.945M", "INR 2.540M", "0.9199", "Strong and stable linear baseline."],
            ["Lasso (tuned)", "INR 1.947M", "INR 2.543M", "0.9197", "Nearly Ridge-level accuracy, with one zeroed coefficient."],
            ["Decision Tree", "INR 2.115M", "INR 2.866M", "0.8980", "Useful nonlinear model, but weaker than its forest."],
            ["SVR Linear", "INR 6.956M", "INR 8.940M", "0.0077", "Very weak on this representation."],
            ["SVR RBF (tuned)", "INR 6.985M", "INR 8.977M", "-0.0006", "Worse than average-price baseline on this test."],
            ["SVR Polynomial", "INR 6.994M", "INR 8.987M", "-0.0030", "Also very weak here."],
        ], [4.0*cm, 2.4*cm, 2.4*cm, 1.45*cm, CONTENT_WIDTH-10.25*cm], small=True),
        BarChart(
            [
                ("Random Forest", 2.387227),
                ("Ridge", 2.539952),
                ("Lasso", 2.542966),
                ("Decision Tree", 2.866278),
                ("SVR Linear", 8.939711),
                ("SVR RBF", 8.976954),
            ],
            CONTENT_WIDTH,
            "Test RMSE comparison (millions of INR)",
            suffix="M",
            color=BLUE,
            value_format=".2f",
            note="Lower is better. SVR's large bars make the difference easy to see; do not infer a causal reason from this chart alone.",
        ),
        p("9.1 Best model in this notebook", "h2"),
        p("By the reported test metrics, <b>Random Forest</b> is the best model: it has the lowest MAE and RMSE, and the highest R2. "
          "Its flexibility appears to capture non-linear relationships in these property records better than the linear formulas did.", "body"),
        Callout(
            "Best does not mean automatic choice",
            "The forest is the accuracy leader in this run, but Ridge and Lasso are easier to explain feature-by-feature and show a much smaller train/test gap. "
            "The right production choice depends on the cost of error, the need for explanation, stability over time, speed, and fairness - not only one leaderboard score.",
            CONTENT_WIDTH, S, "result",
        ),
        p("9.2 Train versus test: spotting overfitting and underfitting", "h2"),
        p("<b>Overfitting</b> means a model learns peculiarities of its training examples and then drops noticeably on new examples. "
          "<b>Underfitting</b> means it is too simple, too constrained or poorly configured to learn the important pattern even in training. The <b>generalisation gap</b> is test RMSE minus train RMSE; a large positive gap is a warning sign.", "body"),
        make_table([
            ["Model", "Train RMSE", "Test RMSE", "Gap", "Notebook interpretation"],
            ["Random Forest", "INR 1.344M", "INR 2.387M", "INR 1.044M", "Some overfitting, despite best test score."],
            ["Ridge", "INR 2.482M", "INR 2.540M", "INR 0.058M", "Very stable generalisation."],
            ["Lasso", "INR 2.483M", "INR 2.543M", "INR 0.060M", "Very stable generalisation."],
            ["Decision Tree", "INR 2.437M", "INR 2.866M", "INR 0.429M", "Moderate overfitting."],
            ["SVR RBF", "INR 8.657M", "INR 8.977M", "INR 0.320M", "High error on both: underfitting / poor fit."],
        ], [3.0*cm, 2.25*cm, 2.25*cm, 1.8*cm, CONTENT_WIDTH-9.3*cm], small=True),
        p("The gap is a diagnostic, not a final verdict. A low train error is not impressive if the test error is poor; a modest gap is desirable only when the test error itself is also acceptable.", "body"),
        p("9.3 A sensible decision path", "h2"),
        *bullets([
            "Use the <b>Random Forest</b> as the current accuracy benchmark, then validate it on newer, truly chronological data before deployment.",
            "Keep <b>Ridge or Lasso</b> as transparent reference models. When a forest estimate seems surprising, a simple model can help explain broad drivers.",
            "Do not deploy SVR from this notebook as-is; it is not competitive in the recorded results. Revisit it only with a justified redesign and validation plan.",
            "Report uncertainty and a price range, not just a single point estimate. The current notebook evaluates average error but does not yet calculate prediction intervals.",
        ]),
        PageBreak(),
    ]


def add_limits_and_glossary(story: list):
    story += [p("Part 10 | Use the result responsibly", "part"), p("10. Limits, responsible use and next steps", "h1")]
    story += [
        p("A good model evaluation is not the end of the work. Before anyone relies on a house-price estimate, check whether the data, process and use case are appropriate.", "body"),
        p("10.1 What this notebook does not establish", "h2"),
        *bullets([
            "<b>Causation:</b> The model detects patterns in recorded sales; it does not prove that changing one feature causes the price change the model estimates.",
            "<b>Future market certainty:</b> A train/test split measures performance on held-back historical rows, not on an unknown future market shock.",
            "<b>All property details:</b> The table has no visible information about condition, renovations, exact neighbourhood, legal status, floor level, views or negotiation context. Missing information limits any estimate.",
            "<b>Fairness:</b> Location-linked variables can reflect historic inequalities. Review inputs and outcomes by relevant groups and use the tool as decision support, not an unchallengeable authority.",
            "<b>Individual guarantee:</b> An average error such as MAE does not say the error for one particular home will be that exact amount.",
        ]),
        p("10.2 Practical improvements for a future version", "h2"),
        make_table([
            ["Improvement", "Why it matters"],
            ["Chronological holdout", "Sort by sale date; train on earlier sales and test on the latest period to mirror real forecasting."],
            ["Data-quality review", "Check duplicate properties, outliers, changing definitions and whether input values would be known at prediction time."],
            ["Uncertainty intervals", "Provide a plausible range around a price, not only a point estimate."],
            ["Feature engineering", "Consider price per area patterns, non-linear age effects, local market indicators and well-justified date seasonality."],
            ["Explainability checks", "Use local explanations and permutation/holdout checks; avoid treating one feature-importance chart as proof."],
            ["Monitoring", "After deployment, compare estimates with later sales and watch for performance drift."],
        ], [5.15*cm, CONTENT_WIDTH-5.15*cm]),
        Callout(
            "A healthy production question",
            "Ask: 'Would we have known every input at the moment we make this prediction, and would we be comfortable explaining this estimate to the person affected by it?' "
            "If the answer is no, improve the process before use.",
            CONTENT_WIDTH, S, "warning",
        ),
        p("10.3 The key takeaway", "h2"),
        p("The notebook provides a thoughtful model comparison for a house-price task. In the recorded run, Random Forest has the strongest test metrics, while Ridge and Lasso provide highly competitive, more transparent alternatives. "
          "The most important skill is not memorising model names; it is keeping data preparation, validation, interpretation and responsible use connected.", "body"),
        PageBreak(),
        p("Plain-language glossary", "h1"),
        p("These short definitions are designed for quick reference while reading the notebook.", "body"),
    ]
    glossary = [
        ("Alpha", "The regularisation strength in Ridge and Lasso. It is a complexity dial chosen by validation."),
        ("Baseline", "A simple reference prediction. Here, the average price is a baseline for R-squared."),
        ("Coefficient", "A learned weight in a linear model that changes the estimated price when an input changes."),
        ("Cross-validation", "Repeated train/validate rotations used to check a model and select settings."),
        ("Data leakage", "Using information during training that would not be available when making a real future prediction."),
        ("Feature", "An input clue supplied to a model, such as area or bedrooms."),
        ("Generalisation", "How well a model works on new data that it did not use to learn."),
        ("Hyperparameter", "A setting chosen before fitting, such as tree depth, alpha, C or gamma."),
        ("Kernel", "An SVR mechanism for representing relationships that may not be straight lines."),
        ("Lasso / L1", "A regularised linear model that can shrink some coefficients exactly to zero."),
        ("Loss", "The numeric score a training process tries to minimise; lower means the fit is better by that definition."),
        ("MAE", "Average absolute miss, expressed in the original unit (INR)."),
        ("Model", "A learned rule that turns inputs into an estimated output."),
        ("Overfitting", "Learning the training examples too specifically, then performing worse on new data."),
        ("Pipeline", "A bundled sequence of repeatable steps, such as scaling followed by model fitting."),
        ("R2 / R-squared", "A comparison with an average-only baseline; 1 is perfect, 0 matches baseline, negative is worse."),
        ("Random Forest", "An ensemble that averages many decision trees."),
        ("Regularisation", "A penalty that discourages overly complicated or extreme model behaviour."),
        ("Residual", "The difference between a real value and the model's prediction."),
        ("RMSE", "Square-rooted average squared miss; in INR and more sensitive to large errors than MAE."),
        ("Ridge / L2", "A regularised linear model that shrinks coefficients while usually keeping every feature."),
        ("Scaling", "Putting numeric inputs on comparable ranges; StandardScaler uses the training average and spread."),
        ("Target", "The answer a supervised model is trying to estimate; here, house_price_inr."),
        ("Underfitting", "Failing to learn useful patterns, resulting in poor performance even on training data."),
        ("Validation fold", "The held-out part of one cross-validation rotation, used for a practice evaluation."),
    ]
    gl_rows = []
    for term, definition in glossary:
        gl_rows.append([p(term, "glossary_term"), p(definition, "glossary_def")])
    gl_table = Table(gl_rows, colWidths=[3.5*cm, CONTENT_WIDTH-3.5*cm], repeatRows=0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    for i in range(len(glossary)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    gl_table.setStyle(TableStyle(commands))
    story += [gl_table, PageBreak()]


def add_faq_and_traceability(story: list):
    story += [p("Close with confidence", "part"), p("Frequently asked questions", "h1")]
    faqs = [
        ("Can I say the model is 93% accurate?", "No. The best R2 is 0.9292, which describes how much of the test-set price variation the model captures relative to an average-price baseline. It is not a percentage of individual prices that are correct."),
        ("Why is the best model still wrong by millions of INR?", "House prices themselves range from about INR 1.51M to INR 59.30M, and the data does not include every influence on a sale. An average error also hides a spread: some estimates will be much closer and some much farther away."),
        ("Why keep Ridge or Lasso if Random Forest wins?", "They are strong benchmarks with simple, inspectable coefficients and much smaller train/test gaps. A small accuracy trade-off may be worthwhile when explanation, auditability or stability matters."),
        ("Does a high feature importance prove what causes price?", "No. It only reports how the fitted forest used a feature to reduce error on this data. Correlation, omitted details and related variables mean causal claims need a different study design."),
        ("Why use a test set and cross-validation both?", "Cross-validation helps choose models and settings without leaning on one lucky split. The held-back test is the final independent check after those choices."),
        ("What should happen before use on current listings?", "Validate on recent chronologically later sales, audit inputs and fairness, decide an acceptable error range, explain uncertainty to users, and monitor performance after release."),
    ]
    for question, answer in faqs:
        story += [p(question, "h3"), p(answer, "body")]
    story += [p("Notebook-to-guide traceability", "h2")]
    story += [
        p("This guide is a theory companion, not a replacement for the notebook. The following map helps readers connect explanations back to the code.", "body"),
        make_table([
            ["Notebook area", "Guide explanation"],
            ["Part A", "Regularisation, Ridge vs Lasso, CV basics, and why tree models do not need scaling."],
            ["Part B", "Dataset dictionary, date transformation, ID removal, feature/target split, train/test split and scaling."],
            ["Part C", "Linear loss, Ridge/Lasso penalties, alpha search, fitted coefficients and feature selection."],
            ["Part D", "K-Fold, stratified price bins, LOOCV cost, Time Series Split and CV results."],
            ["Part E", "Decision Tree controls, Random Forest ensemble and feature importance cautions."],
            ["Part F", "SVR kernels, C/gamma/epsilon, Pipeline and GridSearchCV."],
            ["Parts G-H", "MAE/MSE/RMSE/R2, model comparison, train/test gaps and final conclusions."],
        ], [4.0*cm, CONTENT_WIDTH-4.0*cm]),
        Spacer(1, 0.32*cm),
        Callout(
            "Final thought",
            "A useful prediction system is not just an algorithm with a high score. It is clear about its evidence, honest about uncertainty, tested on the right future-like data, and used with human judgement.",
            CONTENT_WIDTH, S, "result",
        ),
        Spacer(1, 0.45 * cm),
        p("End of guide", "cover_meta"),
    ]


def build_pdf() -> Path:
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=1.55 * cm,
        rightMargin=1.55 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.55 * cm,
        title="Robust Regression Engine - Plain-Language Theory Guide",
        author="Robust Regression Engine project",
        subject="Non-technical explanation of the Robust_Reression_Engine notebook",
    )
    story: list = []
    add_cover(story)
    add_contents(story)
    add_big_picture(story)
    add_data(story)
    add_preparation(story)
    add_regularization(story)
    add_cv(story)
    add_metrics(story)
    add_trees(story)
    add_svr(story)
    add_results(story)
    add_limits_and_glossary(story)
    add_faq_and_traceability(story)
    doc.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)
    return OUTPUT


if __name__ == "__main__":
    output = build_pdf()
    print(f"Created {output}")
