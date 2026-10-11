from pathlib import Path

import fitz
from PIL import Image, ImageOps, ImageDraw


source = Path(".agents/outputs/pdf-final/Project_3_Delivery_Exception_Resolution_Presentation.pdf")
output_dir = Path(".agents/outputs/pdf-review")
output_dir.mkdir(parents=True, exist_ok=True)

document = fitz.open(source)
thumbs = []
for index, page in enumerate(document):
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    image_path = output_dir / f"page-{index + 1:02d}.png"
    pixmap.save(image_path)
    thumb = Image.open(image_path).convert("RGB")
    thumb.thumbnail((480, 270))
    card = Image.new("RGB", (500, 300), "white")
    card.paste(thumb, ((500 - thumb.width) // 2, 10))
    draw = ImageDraw.Draw(card)
    draw.text((16, 278), f"Page {index + 1}", fill="#183757")
    thumbs.append(card)

cols = 3
rows = (len(thumbs) + cols - 1) // cols
contact = Image.new("RGB", (cols * 500, rows * 300), "#e6edf2")
for index, image in enumerate(thumbs):
    contact.paste(image, ((index % cols) * 500, (index // cols) * 300))
contact_path = output_dir / "contact-sheet.png"
contact.save(contact_path)

print(f"Rendered {len(document)} pages to {output_dir}; contact sheet: {contact_path}")
print("PDF page size:", document[0].rect)