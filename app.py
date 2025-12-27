from flask import Flask, render_template, request, send_file
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import json
import os
import uuid
from datetime import datetime
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- FIELD EXTRACTION ----------------
def extract_fields_from_blocks(blocks):
    extracted = {}
    full_text = "\n".join(block["text"] for block in blocks)

    # LABEL-BASED NAME EXTRACTION
    for i in range(len(blocks) - 1):
        label_line = blocks[i]["text"].lower()
        value_line = blocks[i + 1]["text"]
        if "last name" in label_line and "first name" in label_line:
            parts = value_line.split()
            if len(parts) >= 2:
                extracted["last_name"] = parts[0]
                extracted["first_name"] = parts[1]
                extracted["full_name"] = f"{parts[1]} {parts[0]}"
            break

    # NAME WITH "Name:" PATTERN
    name_match = re.search(
        r'(?:name|full name)\s*[:\-]\s*([A-Za-z]+)\s+([A-Za-z]+)',
        full_text,
        re.IGNORECASE
    )
    if name_match and "first_name" not in extracted:
        extracted["first_name"] = name_match.group(1)
        extracted["last_name"] = name_match.group(2)
        extracted["full_name"] = f"{name_match.group(1)} {name_match.group(2)}"

    # EMAIL
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    if email_match:
        extracted["email"] = email_match.group(0)

    # PHONE
    phone_match = re.search(r'(\+?\d{1,3}[\s-]?\d{10})', full_text)
    if phone_match:
        extracted["phone"] = phone_match.group(0)

    return extracted, full_text

# ---------------- PDF UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "pdf_file" not in request.files:
        return render_template("index.html")

    pdf = request.files["pdf_file"]
    if pdf.filename == "":
        return render_template("index.html")

    original_filename = os.path.splitext(pdf.filename)[0]
    document_id = original_filename
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(pdf_path)

    images = convert_from_path(pdf_path)
    pages = []
    all_blocks = []

    for page_num, image in enumerate(images, start=1):
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        blocks = []
        current_words = []
        current_conf = []

        for i in range(len(ocr_data["text"])):
            word = ocr_data["text"][i].strip()
            conf = int(ocr_data["conf"][i])
            if word:
                current_words.append(word)
                current_conf.append(conf)
            else:
                if current_words:
                    block = {
                        "block_id": str(uuid.uuid4()),
                        "type": "line",
                        "text": " ".join(current_words),
                        "confidence": sum(current_conf)//len(current_conf)
                    }
                    blocks.append(block)
                    all_blocks.append(block)
                    current_words, current_conf = [], []
        if current_words:
            block = {
                "block_id": str(uuid.uuid4()),
                "type": "line",
                "text": " ".join(current_words),
                "confidence": sum(current_conf)//len(current_conf)
            }
            blocks.append(block)
            all_blocks.append(block)

        pages.append({"page_number": page_num, "blocks": blocks})

    extracted_data, _ = extract_fields_from_blocks(all_blocks)

    output_json = {
        "document": {"id": document_id, "type": "pdf", "source": "uploaded_pdf"},
        "metadata": {
            "total_pages": len(pages),
            "ocr_engine": "tesseract",
            "language": "eng",
            "created_at": datetime.utcnow().isoformat()
        },
        "extracted_data": extracted_data,
        "pages": pages
    }

    json_filename = f"{document_id}.json"
    json_path = os.path.join(OUTPUT_FOLDER, json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    return render_template("index.html", download_file=json_filename, success=True, upload_type="pdf")

# ---------------- IMAGE UPLOAD ----------------
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "image_file" not in request.files:
        return render_template("index.html")

    image = request.files["image_file"]
    if image.filename == "":
        return render_template("index.html")

    original_filename = os.path.splitext(image.filename)[0]
    document_id = original_filename
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    ocr_data = pytesseract.image_to_data(Image.open(image_path), output_type=pytesseract.Output.DICT)

    blocks = []
    all_blocks = []
    current_words = []
    current_conf = []

    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        conf = int(ocr_data["conf"][i])
        if word:
            current_words.append(word)
            current_conf.append(conf)
        else:
            if current_words:
                block = {
                    "block_id": str(uuid.uuid4()),
                    "type": "line",
                    "text": " ".join(current_words),
                    "confidence": sum(current_conf)//len(current_conf)
                }
                blocks.append(block)
                all_blocks.append(block)
                current_words, current_conf = [], []
    if current_words:
        block = {
            "block_id": str(uuid.uuid4()),
            "type": "line",
            "text": " ".join(current_words),
            "confidence": sum(current_conf)//len(current_conf)
        }
        blocks.append(block)
        all_blocks.append(block)

    extracted_data, full_text = extract_fields_from_blocks(all_blocks)

    # ---------------- SMART SUMMARY ----------------
    # Split at commas and periods, new line for each segment
    clean_text = re.sub(r'\s+', ' ', full_text).strip()

    # Split ONLY on sentence end
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)

    # Each sentence on new line
    summary = "\n".join(sentences)
    # ---------------------------------------------------

    pages = [{"page_number": 1, "blocks": blocks}]

    output_json = {
        "document": {"id": document_id, "type": "image", "source": "uploaded_image"},
        "metadata": {
            "total_pages": 1,
            "ocr_engine": "tesseract",
            "language": "eng",
            "created_at": datetime.utcnow().isoformat()
        },
        "extracted_data": extracted_data,
        "summary": summary,
        "pages": pages
    }

    json_filename = f"{document_id}.json"
    json_path = os.path.join(OUTPUT_FOLDER, json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    return render_template(
        "index.html",
        download_file=json_filename,
        success=True,
        upload_type="image",
        summary=summary
    )

# ---------------- DOWNLOAD ----------------
@app.route("/download/<filename>")
def download_json(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
