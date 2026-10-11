from pathlib import Path

import fitz
from PIL import Image, ImageDraw


ROOT = Path("attached_assets")
OUT = Path(".agents/outputs/attached-pdf-review")
OUT.mkdir(parents=True, exist_ok=True)

names = [
    "aurorastay_booking_terms_and_cancellation_policy_1791758753654.pdf",
    "aurorastay_guest_conduct_accessibility_and_resolution_guidelin_1791758753655.pdf",
    "aurorastay_refunds_and_additional_charges_guide_1791758753656.pdf",
    "aurorastay_room_and_property_information_1791758753658.pdf",
    "Deploying_RAG_Application_Using_GitHub_Codespaces_1791758726827.pdf",
]
cards = []
for name in names:
    doc = fitz.open(ROOT / name)
    page = doc[0]
    image_path = OUT / f"{Path(name).stem}-page1.png"
    page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1), alpha=False).save(image_path)
    image = Image.open(image_path).convert("RGB")
    image.thumbnail((360, 250))
    card = Image.new("RGB", (380, 290), "white")
    card.paste(image, ((380 - image.width) // 2, 8))
    draw = ImageDraw.Draw(card)
    draw.text((10, 265), Path(name).stem[:48], fill="#183757")
    cards.append(card)

cols = 2
rows = (len(cards) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 380, rows * 290), "#e9eef3")
for i, card in enumerate(cards):
    sheet.paste(card, ((i % cols) * 380, (i // cols) * 290))
sheet.save(OUT / "attached-pdf-contact-sheet.png")
print(f"Rendered first pages of {len(names)} PDFs to {OUT}")
