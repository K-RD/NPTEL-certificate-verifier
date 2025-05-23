import os
import logging
from PIL import Image
import pytesseract
from pyzbar.pyzbar import decode

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def all_file_paths(folder="./converted-certificate-image"):
    if not os.path.exists(folder):
        logging.warning(f"Folder not found: {folder}")
        return []

    all_files = sorted(os.listdir(folder))
    return [
        os.path.join(folder, file_name)
        for file_name in all_files
        if file_name.lower().endswith((".jpg", ".jpeg"))
    ]

def read_qr_image(qr_image):
    decoded = decode(qr_image)
    if decoded:
        return decoded[0].data.decode()
    return None

def extract_certificate_data(image_path):
    try:
        image = Image.open(image_path)
    except Exception as e:
        logging.error(f"Failed to open image: {image_path} - {e}")
        return {"filename": os.path.basename(image_path), "error": "Could not open image"}

    width, height = image.size

    # Cropping regions: (left, top, right, bottom)
    regions = {
        "qr_code": (3544, 4664, 3973, 5058),
        "name": (1316, 1319, 5795, 1467),
        "course": (1128, 1779, 5884, 2226),
        "marks": (3850, 2273, 4380, 2516),
        "credit": (6500, 4760, 6800, 4900),
        "roll": (580, 4750, 2050, 4920),
        "duration": (3000, 3550, 4200, 3759),
    }

    extracted_data = {"filename": os.path.basename(image_path)}
    for field, box in regions.items():
        try:
            cropped = image.crop(box)
            if field == "qr_code":
                text = read_qr_image(cropped)
            else:
                text = pytesseract.image_to_string(cropped).strip()
            extracted_data[field] = text
        except Exception as e:
            logging.warning(f"OCR failed for {field} in {image_path}: {e}")
            extracted_data[field] = ""

    return extracted_data
