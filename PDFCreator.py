from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from PIL import Image
import requests
from io import BytesIO
import os
def create_pdf(image_urls, grade, name):
    page_width, page_height = landscape(letter)
    if not os.path.exists(f'pdf/{grade}/{name}.pdf'):
        if not os.path.exists(f'pdf/{grade}'):
            os.makedirs(f'pdf/{grade}')
        c = canvas.Canvas(f'pdf/{grade}/{name}.pdf', pagesize=(page_width, page_height))
        for index, url in enumerate(image_urls):
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            with open(f"images/temp_{index}.jpg", "wb") as f:
                f.write(response.content)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            if aspect > 1:
                # If the image is taller than it is wide, scale by height
                img_width = page_height / aspect
                img_height = page_height
            else:
                # If the image is wider than it is tall, scale by width
                img_width = page_width
                img_height = page_width * aspect
            x = (page_width - img_width) / 2
            y = (page_height - img_height) / 2
            c.drawImage(f"images/temp_{index}.jpg", x, y, img_width, img_height)
            c.showPage()
        c.save()

