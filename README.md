# DocumentOrganizer 📁🤖

An AI-powered tool that scans, summarizes, and organizes documents such as PDFs, DOCX, images, and more. Leveraging Google's Gemini AI and advanced NLP techniques, it extracts metadata, generates concise summaries, and creates logical folder structures to save time for researchers, professionals, and students. Easy to set up, highly configurable, and designed for educational and research purposes. 🚀

## 📑 Overview

`DocumentOrganizer` is a two-part Python-based pipeline:

- `summarygenerator.py` 📜: Scans a directory for supported file types, extracts text and metadata, generates summaries using SentenceTransformers, and produces embeddings for AI analysis.
- `fileorganizer.py` 🗂️: Uses Google's Gemini AI to analyze document summaries, proposes an optimized folder structure, and moves files after user confirmation.

The tool supports a wide range of file formats, including documents (PDF, DOCX, PPTX, XLSX), images (PNG, JPEG, etc.), and audio (WAV, MP3), with optional OCR for scanned documents.

## ✨ Features

- **Multi-Format Support** 📄: Processes PDFs, DOCX, PPTX, XLSX, HTML, Markdown, images (PNG, TIFF, JPEG, JPG, GIF, BMP), and audio (WAV, MP3).
- **AI-Powered Summarization** ✍️: Generates concise summaries using the `all-MiniLM-L6-v2` SentenceTransformer model with cosine similarity for relevance.
- **Smart File Organization** 🧠: Uses Gemini AI (`gemini-2.5-flash`) to propose logical folder structures based on document content, with JSON plans and ASCII file trees.
- **Metadata Extraction** 🔍: Captures titles, authors, and creation dates where available.
- **OCR Capabilities** 🖼️: Extracts text from images and scanned PDFs using EasyOCR or Tesseract (optional).
- **Performance Tracking** 📊: Generates KPI reports for processing success, error rates, processing times, and API usage.
- **User Confirmation** ✅: Ensures safe file reorganization with user approval at critical steps.

## 📁 Repository Structure

```
.
├── .env.example               # Template for environment variables 🔑
├── .gitignore                 # Excludes .env from version control 🚫
├── fileorganizer.py           # AI-driven file organization with JSON plans and ASCII file trees 🗂️
├── requirements.txt            # Python dependencies 📋
├── summarygenerator.py        # Scans directories, extracts metadata, and generates summaries 📜
├── llm_input.json             # Metadata and summaries for AI analysis 📤
├── processed_documents.json   # Full processing results with embeddings 📄
└── README.md                  # Project documentation 📘
```

## 🛠️ Installation

### Prerequisites
- **Python** 🐍: 3.8 or higher
- **Tesseract OCR** 🔍: Required for OCR with `pytesseract` (optional)
  - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`
- **Google API Key** 🔐: Obtain from [Google AI Studio](https://aistudio.google.com/)

### Install Dependencies
1. Clone the repository:
   ```bash
   git clone https://github.com/preetam077/DocumentOrganizer.git
   cd DocumentOrganizer
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Optional OCR support:
   ```bash
   pip install docling[easyocr]   # For EasyOCR
   pip install docling[tesseract] # For Tesseract
   ```
4. Configure environment variables:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` to include:
   - `GOOGLE_API_KEY`: Your Gemini AI API key 🔑
   - `BASE_PATH`: Directory to scan for documents 📍
   - `DESTINATION_ROOT`: Directory for organized files 🏁

   Example `.env`:
   ```
   GOOGLE_API_KEY=your_api_key
   BASE_PATH=/path/to/source/directory
   DESTINATION_ROOT=/path/to/output/directory
   ```

## 🚀 Quick Start

### Step 1: Process Documents
Run the summarization script to scan and summarize documents:
```bash
python summarygenerator.py
```
**What it does**:
- Scans `BASE_PATH` for supported files 📂.
- Extracts text and metadata using `docling` (most formats) or `pandas` (XLSX) 📄.
- Applies OCR to images and scanned PDFs if enabled 🖼️.
- Generates embeddings and summaries using SentenceTransformers ✍️.
- Saves results to:
  - `processed_documents.json`: Full metadata, embeddings, and summaries 📄.
  - `llm_input.json`: Summaries for `fileorganizer.py` 📤.
- Displays a KPI report (e.g., processing success, error rates) 📊.

### Step 2: Organize Files
Run the organization script to create an optimized folder structure:
```bash
python fileorganizer.py
```
**What it does**:
- Loads `llm_input.json` and uses Gemini AI to analyze document summaries 🧠.
- Proposes a JSON organization plan and ASCII file tree 🌳.
- Displays the current structure analysis, proposed plan, and reasoning 📑.
- Prompts for user confirmation before moving files to `DESTINATION_ROOT` ✅.
- Displays a KPI report (e.g., file movement success, API response times) 📊.

⚠️ **Warning**: Back up files before running `fileorganizer.py`, as it moves files to new locations 💾.

## 📊 Supported File Types
| Category  | Formats                              |
|-----------|--------------------------------------|
| Documents | PDF, DOCX, PPTX, XLSX, HTML, ADOC, MD |
| Images    | PNG, TIFF, JPEG, JPG, GIF, BMP       |
| Audio     | WAV, MP3                             |

## 🔧 How It Works
1. **Directory Scanning** 📂: Recursively scans `BASE_PATH` for supported file types.
2. **Content Extraction** 📜: Uses `docling` for most formats, `pandas` for Excel, and OCR for images/PDFs.
3. **Summarization** ✍️: Generates embeddings with SentenceTransformers and selects top sentences based on cosine similarity.
4. **AI Organization** 🧠: Gemini AI analyzes summaries to propose a folder structure (e.g., by project or year).
5. **File Movement** 🚚: Moves files to `DESTINATION_ROOT` after user approval.
6. **KPI Reporting** 📈: Tracks metrics like success rates, processing times, and API usage.

## 📋 Output Files
- `llm_input.json` 📤: Metadata and summaries for AI organization.
- `processed_documents.json` 📄: Full processing results, including embeddings.

## 📊 KPI Reports
Both scripts output KPI reports to the console:

**`summarygenerator.py`**:
- Document Processing Success Rate ✅
- Average Processing Time per Document ⏱️
- Summary Quality Score (average words) 📝
- Error Rate 🚫
- OCR Utilization Rate 🔍
- Output File Integrity 💾

**`fileorganizer.py`**:
- File Organization Success Rate ✅
- Processing Time ⏱️
- AI Plan Validity Rate 🧠
- Directory Creation Success Rate 📂
- File Path Mapping Accuracy 📍
- Error Rate 🚫
- Input File Load Success Rate 📄
- API Response Time 🌐
- Tokens Used 🔢

## 🐛 Troubleshooting
- **Missing API Key** 🔑: Ensure `GOOGLE_API_KEY` is set correctly in `.env`.
- **OCR Issues** 🔍: Verify Tesseract or EasyOCR installation and PATH configuration.
- **Permission Errors** 🚫: Check read/write access to `BASE_PATH` and `DESTINATION_ROOT`.
- **JSON Errors** 📄: Validate `llm_input.json` for correct formatting.
- **Large Files** 📂: Allow extra processing time for large documents.
- **Dependencies** 📋: Run `pip install -r requirements.txt` to ensure all packages are installed.

For detailed logs, review the console output or KPI reports.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. Note: Usage of Google's Gemini AI must comply with Google's API terms.

## 🤝 Contributing
We welcome contributions! To contribute:
- Report bugs or request features via [GitHub Issues](https://github.com/preetam077/DocumentOrganizer/issues).
- Submit pull requests with improvements or fixes.
- Suggest documentation enhancements.

Please ensure code follows PEP 8 style guidelines and includes appropriate tests.

## 📬 Contact
For questions or support, contact the maintainer via [GitHub Issues](https://github.com/preetam077/DocumentOrganizer/issues) or email at [your-email@example.com].
