# ai-ocr-pdf-image-processor


# AI OCR PDF & Image Processor

An AI-powered OCR web application built with **Flask** and **Tesseract** that extracts structured text and key fields from **PDFs and Images**, and exports results as clean **JSON** files.

---

## 🚀 Features

- 📄 Upload **PDF files** (multi-page supported)
- 🖼️ Upload **Images** (PNG, JPG, JPEG)
- 🔍 OCR using **Tesseract**
- 🧠 Intelligent text line grouping
- 📌 Automatic extraction of:
  - Name
  - Email
  - Phone number
- 📝 Smart summary generation
  - New line only after commas or sentence breaks
  - Prevents broken word-by-word lines
- 📦 JSON output with metadata and page-wise blocks
- ⬇️ Download extracted JSON file

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **OCR Engine:** Tesseract OCR  
- **Image Processing:** Pillow  
- **PDF Processing:** pdf2image  
- **Frontend:** HTML (Jinja Templates)

---

## 📁 Project Structure

ai-ocr-pdf-image-processor/
│
├── app.py
├── uploads/
├── outputs/
├── templates/
│ └── index.html
├── README.md
└── requirements.txt


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/ABHINAVPUL08/ai-ocr-pdf-image-processor.git
cd ai-ocr-pdf-image-processor

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

brew install tesseract
sudo apt install tesseract-ocr
python app.py
http://127.0.0.1:5000


📤 How It Works

Upload a PDF or Image

OCR extracts text line-by-line

Text is grouped intelligently

Key fields are detected using regex

A clean summary is generated

Output is saved as structured JSON

"summary": "It was the best of times,
it was the worst of times,
it was the age of wisdom,
it was the age of foolishness"

💼 Use Cases

Resume parsing

Document digitization

Invoice & form processing

OCR-based automation systems

AI document pipelines

📌 Future Improvements

Database storage

REST API endpoints

UI enhancements

Multi-language OCR

AI-based entity recognition

👤 Author

Abhinav Pulyani
GitHub: https://github.com/ABHINAVPUL08


