# 📁 Interactive Document Organizer 🤖

Welcome to **InteractiveDocumentOrganizer**! This AI-powered tool does more than just organize your files – it analyzes your current file distribution, lets you ask questions about it, proposes a smarter folder structure using Google's Gemini AI, and moves files only after your approval. Perfect for researchers, professionals, and students looking to declutter with intelligence and control! 🚀

## 📑 Overview

This Python-based pipeline offers a powerful, interactive workflow:
- **summarygenerator.py** 📜: Scans your directory, extracts text/metadata, and generates summaries for AI analysis.
- **organizerqa.py** 🗂️: Analyzes your current file structure, answers your questions, proposes an optimized organization plan, and moves files to new folders with your permission.

It supports a wide range of file formats, includes optional OCR, and is designed for educational/research use. Always back up your files before organizing! 💾

## ✨ Features

- **Current Structure Analysis** 🔍: Examines your file distribution and highlights inefficiencies (e.g., scattered files or unclear groupings).
- **Interactive Q&A** ❓: Ask questions about your files or the analysis to understand your setup better.
- **AI-Driven Organization Plans** 🧠: Gemini AI suggests logical folder structures (e.g., by topic/project/year) with JSON plans and ASCII trees.
- **User-Controlled File Moving** ✅: Files are moved to `DESTINATION_ROOT` only after you approve the AI's plan.
- **Multi-Format Support** 📄: Handles PDFs, DOCX, PPTX, XLSX, HTML, Markdown, images (PNG, JPEG, etc.), and audio (WAV, MP3).
- **Smart Summaries** ✍️: Uses SentenceTransformers to create concise, relevant summaries via cosine similarity.
- **Metadata Extraction** 📋: Captures titles, authors, and creation dates when available.
- **OCR Capabilities** 🖼️: Extracts text from images/scanned PDFs using EasyOCR or Tesseract (optional).
- **Performance Tracking** 📊: KPI reports on success rates, processing times, and API usage.

## 📁 Repository Structure

```
.
├── .env.example               # 🔑 Template for environment variables
├── .gitignore                 # 🚫 Excludes sensitive files (like .env)
├── organizerqa.py             # 🗂️ Analyzes, answers questions, and organizes files
├── requirements.txt           # 📋 Python dependencies
├── summarygenerator.py        # 📜 Scans, summarizes, and extracts metadata
├── llm_input.json             # 📤 AI-ready summaries (generated)
├── processed_documents.json   # 📄 Full results with embeddings (generated)
└── README.md                  # 📘 You're reading it!
```

## 🛠️ Installation

### Prerequisites
- **Python** 🐍: 3.8 or higher.
- **Tesseract OCR** 🔍 (optional for image/PDF text extraction):
  - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
  - Linux: `sudo apt install tesseract-ocr`.
  - macOS: `brew install tesseract`.
- **Google API Key** 🔐: Get one from [Google AI Studio](https://aistudio.google.com/) for Gemini AI.

### Steps (Run in Command Prompt/Terminal)
1. Clone the repository:
   ```
   git clone https://github.com/preetam077/InteractiveDocumentOrganizer.git
   cd InteractiveDocumentOrganizer
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   For optional OCR support:
   ```
   pip install docling[easyocr]    # EasyOCR
   pip install docling[tesseract]  # Tesseract
   ```

4. Configure environment variables:
   ```
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/macOS
   ```
   Edit `.env` with a text editor (e.g., Notepad) and add:
   - `GOOGLE_API_KEY=your_api_key_here` 🔑 (from Google AI Studio)
   - `BASE_PATH=/path/to/source/folder` 📂 (where your files are)
   - `DESTINATION_ROOT=/path/to/output/folder` 🏁 (where files will be organized)

   **Tip**: Use forward slashes `/` for paths, or double backslashes `\\` on Windows (e.g., `C:\\Users\\You\\Docs`).

## 🚀 Quick Start (Run via CMD/Terminal)

### Step 1: Scan & Summarize 📜
```
python summarygenerator.py
```
- Scans `BASE_PATH` for supported files.
- Extracts text/metadata (using Docling for most formats, Pandas for XLSX, OCR for images/PDFs).
- Generates summaries and embeddings.
- Saves:
  - `processed_documents.json`: Full metadata and embeddings.
  - `llm_input.json`: Summaries for the organizer.
- Shows a KPI report (success rates, times, errors) 📊.

### Step 2: Analyze, Ask, and Organize 🗂️
```
python organizerqa.py
```
- **Analyzes Current Structure**: Loads `llm_input.json` and uses Gemini AI to evaluate your file distribution, explaining why it may not be optimal.
- **Interactive Q&A**: Ask questions about the analysis (e.g., "Why are these files grouped together?") to clarify your setup.
- **Proposes a Plan**: Suggests a new folder structure (JSON + ASCII tree) with reasoning (e.g., grouping by project or year).
- **Requires Approval**: Asks for confirmation before moving files to `DESTINATION_ROOT`.
- Outputs a KPI report (file moves, API times, etc.).

⚠️ **Backup Warning**: Back up `BASE_PATH` before running `organizerqa.py` – it moves files!

## 📊 Supported File Types

| Category   | Formats                          |
|------------|----------------------------------|
| Documents | PDF, DOCX, PPTX, XLSX, HTML, ADOC, MD |
| Images    | PNG, TIFF, JPEG, JPG, GIF, BMP  |
| Audio     | WAV, MP3                        |

## 🔧 How It Works

1. **Scan & Summarize** 📂: `summarygenerator.py` scans `BASE_PATH`, extracts content (Docling/Pandas/OCR), and creates summaries/embeddings.
2. **Analyze Structure** 🔍: `organizerqa.py` uses Gemini AI to analyze your current file distribution and identify inefficiencies.
3. **Ask Questions** ❓: Engage in Q&A to understand the analysis and your files better.
4. **Propose New Plan** 🌳: AI suggests a logical folder structure (e.g., `/Projects/2025`) with a JSON plan and ASCII tree.
5. **Move Files** 🚚: After your approval, files are moved to `DESTINATION_ROOT`.
6. **Track Performance** 📈: Both scripts provide KPI reports on success, errors, and more.

## 📋 Output Files

- `llm_input.json` 📤: Summaries and metadata for AI analysis.
- `processed_documents.json` 📄: Detailed results with embeddings.

## 📊 KPI Reports

Both scripts print KPI reports to the console:
- **summarygenerator.py** 📜:
  - Document Processing Success Rate ✅
  - Processing Time per Document ⏱️
  - Summary Quality (avg. words) 📝
  - Error Rate 🚫
  - OCR Utilization 🔍
  - Output File Integrity 💾
- **organizerqa.py** 🗂️:
  - File Organization Success Rate ✅
  - Total Processing Time ⏱️
  - AI Plan Validity 🧠
  - Directory Creation Success 📂
  - File Path Mapping Accuracy 📍
  - Error Rate 🚫
  - Input File Load Success 📄
  - API Response Time 🌐
  - Tokens Used 🔢

## 🐛 Troubleshooting

- **API Key Issue** 🔑: Verify `GOOGLE_API_KEY` in `.env` works in Google AI Studio.
- **OCR Problems** 🔍: Check Tesseract/EasyOCR installation and PATH setup.
- **Permission Errors** 🚫: Run CMD as admin or ensure folder access.
- **JSON Errors** 📄: If `llm_input.json` fails, re-run `summarygenerator.py`.
- **Slow Processing** ⏳: Large files take longer – be patient.
- **Missing Dependencies** 📋: Re-run `pip install -r requirements.txt`.

Check console logs for details. Need help? File a [GitHub Issue](https://github.com/preetam077/InteractiveDocumentOrganizer/issues)! ❗

## 📄 License

MIT License – use, modify, and share freely! See [LICENSE](LICENSE) for details. Follow Google's API terms for Gemini AI. 📜

## 🤝 Contributing

Want to make this tool even better? Awesome! 🌟
- Report bugs or suggest features via [GitHub Issues](https://github.com/preetam077/InteractiveDocumentOrganizer/issues).
- Submit Pull Requests with code/docs (follow PEP 8).
- Add tests or improve documentation.

## 📬 Contact

Questions? Reach out via [GitHub Issues](https://github.com/preetam077/InteractiveDocumentOrganizer/issues) or email preetam077@example.com (replace with your actual email). Let's make organizing fun! 💬
