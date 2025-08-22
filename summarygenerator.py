import os
import json
from typing import List, Dict
import pandas as pd
from docling.document_converter import DocumentConverter
from docling_core.types.doc import DoclingDocument
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import nltk
import warnings
from torch.utils.data import dataloader
import time
from collections import defaultdict
import uuid
from dotenv import load_dotenv
from pathlib import Path
from openpyxl.worksheet._reader import UserWarning

load_dotenv()
BASE_PATH = Path(os.getenv("BASE_PATH"))

# Filter the specific warning about Data Validation
warnings.filterwarnings(
    "ignore",
    message="^Data Validation extension is not supported and will be removed$",
    category=UserWarning,
    module="openpyxl.worksheet._reader"
)

# Disable the specific warning
warnings.filterwarnings("ignore", 
    message=".*'pin_memory' argument is set as true but no accelerator is found.*",
    category=UserWarning,
    module=dataloader.__name__
)

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK punkt_tab resource...")
    nltk.download('punkt_tab')

# Check for OCR dependencies
try:
    import easyocr
    ocr_easyocr_available = True
except ImportError:
    ocr_easyocr_available = False
    print("Warning: easyocr not installed. Install with 'pip install docling[easyocr]' for OCR support.")
try:
    import pytesseract
    ocr_pytesseract_available = True
except ImportError:
    ocr_pytesseract_available = False
    print("Warning: pytesseract not installed. Install with 'pip install docling[tesseract]' and Tesseract binary for OCR support.")

# Supported file extensions
supported_extensions = {
    '.pdf', '.docx', '.pptx', '.xlsx', '.html',
    '.png', '.tiff', '.jpeg', '.jpg', '.gif', '.bmp',
    '.adoc', '.md', '.wav', '.mp3'
}

# Base directory to scan
# base_path = r'YourDirectoryToScan' #eg. C:\Users\Goku\Developments
base_path = os.environ.get('BASE_PATH', r'C:\Users\support2\Developments')

# List to hold paths of supported documents
supported_files: List[str] = []

# KPI tracking variables
processing_times: List[float] = []
error_count: int = 0
successful_count: int = 0
ocr_eligible_files: List[str] = []
ocr_processed_files: List[str] = []
file_types_processed: set = set()
summary_lengths: List[int] = []
cosine_similarities: List[float] = []
output_files_success: List[str] = []

# Step 1: Scan directory
print("Scanning for documents supported by Docling...")
for root, _, files in os.walk(base_path):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in supported_extensions:
            file_path = os.path.join(root, file)
            supported_files.append(file_path)
            file_types_processed.add(ext)
            print(f"Found: {file_path}")
            if ext in {'.png', '.tiff', '.jpeg', '.jpg', '.gif', '.bmp', '.pdf'}:
                ocr_eligible_files.append(file_path)
                print(f"  -> OCR may be applied for this file.")

print(f"\nTotal supported documents found: {len(supported_files)}")

if not supported_files:
    print("No supported documents found. Exiting.")
    exit()

# Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize document converter
converter = DocumentConverter()

# Output lists
output_data: List[Dict] = []
llm_input_data: List[Dict] = []

# Function to generate summary
def generate_summary(text: str, doc_embedding: np.ndarray, max_sentences: int = 5, is_table: bool = False) -> str:
    if not text.strip():
        return "No content available for summary."
    try:
        if is_table:
            # For tabular data, create a concise summary of headers and sample rows
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                return "No meaningful text content extracted from table."
            # Take headers and a few rows, focusing on text content
            summary_lines = lines[:max_sentences]
            summary = f"Table summary: {'; '.join(summary_lines)}..."
            summary_lengths.append(len(summary.split()))
            return summary
        else:
            # Sentence-based summary for non-tabular data
            sentences = sent_tokenize(text)
            if not sentences:
                return "No sentences detected for summary."
            sentence_embeddings = embed_model.encode(sentences)
            similarities = cosine_similarity([doc_embedding], sentence_embeddings)[0]
            cosine_similarities.extend(similarities.tolist())
            top_indices = np.argsort(similarities)[-max_sentences:]
            top_sentences = [sentences[i] for i in sorted(top_indices) if similarities[i] > 0.1]
            summary = " ".join(top_sentences)
            summary_lengths.append(len(summary.split()))
            return summary if summary else "Unable to generate summary due to low similarity."
    except Exception as e:
        print(f"  -> Error generating summary: {str(e)}")
        return "Summary generation failed."

# Function to extract text from Excel using pandas
def extract_excel_text(file_path: str) -> str:
    try:
        xl = pd.ExcelFile(file_path)
        all_text = []
        for sheet_name in xl.sheet_names:
            print(f"Processing sheet: {sheet_name} in {file_path}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Convert all cells to strings, handling NaN
            df = df.fillna('').astype(str)
            # Extract headers, ensuring all column names are strings (fixes the float issue)
            headers = ", ".join(str(col) for col in df.columns if str(col).strip())  # Skip empty columns if desired
            all_text.append(f"Sheet: {sheet_name}")
            all_text.append(f"Headers: {headers}")
            # Debug: Print column types to confirm
            # print("Column name types:", [type(col) for col in df.columns])
            # Extract cell values
            for _, row in df.iterrows():
                row_text = ", ".join(str(val) for val in row if val.strip())  # Use str(val) and skip empty
                if row_text:
                    all_text.append(row_text)
        return "\n".join(all_text)
    except Exception as e:
        print(f"  -> Error reading Excel file {file_path} with pandas: {str(e)}")
        return ""

# Process documents
print("\nProcessing supported documents...")
for file_path in supported_files:
    start_time = time.time()
    print(f"Processing: {file_path}")
    try:
        ext = os.path.splitext(file_path)[1].lower()
        doc_dict: Dict = {'file_path': file_path, 'file_type': ext, 'summary': "", 'embedding': []}
        llm_dict: Dict = {'file_path': file_path, 'file_type': ext, 'summary': ""}

        all_text: List[str] = []

        if ext == '.xlsx':
            # Always use pandas for .xlsx files to ensure reliable text extraction
            print(f"  -> Using pandas to extract content from {file_path}")
            excel_text = extract_excel_text(file_path)
            if excel_text:
                all_text.append(excel_text)
        else:
            # Use docling for other formats
            conv_res = converter.convert(file_path)
            if file_path in ocr_eligible_files and (ocr_easyocr_available or ocr_pytesseract_available):
                ocr_processed_files.append(file_path)
            if conv_res.document is not None:
                doc: DoclingDocument = conv_res.document

                # Extract metadata
                metadata = doc.model_dump().get('metadata', {})
                if isinstance(metadata, dict):
                    if 'title' in metadata:
                        doc_dict['title'] = str(metadata['title'])
                        llm_dict['title'] = str(metadata['title'])
                    if 'author' in metadata:
                        doc_dict['author'] = str(metadata['author'])
                        llm_dict['author'] = str(metadata['author'])
                    if 'creation_date' in metadata:
                        doc_dict['creation_date'] = str(metadata['creation_date'])
                        llm_dict['creation_date'] = str(metadata['creation_date'])

                # Extract text items
                all_text.extend(item.text for item in doc.texts if item.text)

                # Extract table content (only text)
                for table in doc.tables:
                    for row in table.data:
                        for cell in row:
                            cell_text = getattr(cell, 'text', str(cell)) if not isinstance(cell, str) else cell
                            if cell_text:
                                all_text.append(cell_text)

        # Join all text
        full_text = "\n".join([t for t in all_text if t]).strip()

        # Generate embedding and summary
        if full_text:
            doc_embedding = embed_model.encode(full_text)
            doc_dict['embedding'] = doc_embedding.tolist()
            summary = generate_summary(full_text, doc_embedding, is_table=(ext == '.xlsx'))
            doc_dict['summary'] = summary
            llm_dict['summary'] = summary
        else:
            doc_dict['summary'] = "No content available for summary."
            llm_dict['summary'] = "No content available for summary."

        output_data.append(doc_dict)
        llm_input_data.append(llm_dict)
        successful_count += 1
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        error_count += 1
    finally:
        processing_times.append(time.time() - start_time)

# Save output
output_file = 'processed_documents.json'
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print(f"\nOutput saved to {output_file}")
    output_files_success.append(output_file)
except Exception as e:
    print(f"Error saving {output_file}: {str(e)}")

llm_output_file = 'llm_input.json'
try:
    with open(llm_output_file, 'w', encoding='utf-8') as f:
        json.dump(llm_input_data, f, ensure_ascii=False, indent=4)
    print(f"Output saved to {llm_output_file}")
    output_files_success.append(llm_output_file)
except Exception as e:
    print(f"Error saving {llm_output_file}: {str(e)}")

# Calculate KPIs
kpi_report = {
    "document_processing_success_rate": (successful_count / len(supported_files) * 100) if supported_files else 0.0,
    "processing_time_per_document_seconds": (sum(processing_times) / len(processing_times)) if processing_times else 0.0,
    "summary_quality_score": (sum(summary_lengths) / len(summary_lengths)) if summary_lengths else 0.0,  # Proxy: avg words in summary
    "embedding_quality_cosine_similarity": (sum(cosine_similarities) / len(cosine_similarities)) if cosine_similarities else 0.0,
    "file_type_coverage": (len(file_types_processed) / len(supported_extensions) * 100) if supported_extensions else 0.0,
    "error_rate": (error_count / len(supported_files) * 100) if supported_files else 0.0,
    "ocr_utilization_rate": (len(ocr_processed_files) / len(ocr_eligible_files) * 100) if ocr_eligible_files else 0.0,
    "output_file_integrity": (len(output_files_success) / 2 * 100)  # Expect 2 output files
}

# Save KPI report
# kpi_output_file = 'summarygeneratorkpi.json'
# try:
#     with open(kpi_output_file, 'w', encoding='utf-8') as f:
#         json.dump(kpi_report, f, ensure_ascii=False, indent=4)
#     print(f"\nKPI report saved to {kpi_output_file}")
# except Exception as e:
#     print(f"Error saving {kpi_output_file}: {str(e)}")

# Print KPI report
print("\n=== KPI Report ===")
print(f"Document Processing Success Rate: {kpi_report['document_processing_success_rate']:.2f}%")
print(f"Average Processing Time per Document: {kpi_report['processing_time_per_document_seconds']:.2f} seconds")
print(f"Summary Quality Score (Avg Words): {kpi_report['summary_quality_score']:.2f}")
#print(f"Embedding Quality (Avg Cosine Similarity): {kpi_report['embedding_quality_cosine_similarity']:.2f}")
#print(f"File Type Coverage: {kpi_report['file_type_coverage']:.2f}%")
print(f"Error Rate: {kpi_report['error_rate']:.2f}%")
print(f"OCR Utilization Rate: {kpi_report['ocr_utilization_rate']:.2f}%")
print(f"Output File Integrity: {kpi_report['output_file_integrity']:.2f}%")
print("=================\n")

print("Processing complete.")









