import json
import os
import shutil
import google.generativeai as genai # Correct import
import time
from collections import defaultdict
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DESTINATION_ROOT = Path(os.getenv("DESTINATION_ROOT"))

# --- Configuration ---
# Configure the GenAI library with the API key from the environment variable.
# This is the standard way to set it up.
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Error configuring Google GenAI. Ensure GOOGLE_API_KEY is set correctly. Error: {e}")
    exit()

# KPI tracking variables
start_time = time.time()
files_moved = 0
total_files_in_plan = 0
dirs_created = 0
total_dirs_in_plan = 0
valid_path_mappings = 0
total_filenames_in_plan = 0
errors_encountered = 0
json_load_success = False
ai_plan_valid = False
api_response_time = 0.0
tokens_used = 0

# --- Main Functions ---

def load_document_data(filepath='llm_input.json'):
    """Loads the document metadata from the specified JSON file."""
    global json_load_success, errors_encountered
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_load_success = True
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{filepath}' not found.")
        errors_encountered += 1
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        errors_encountered += 1
        return None

def create_file_path_map(document_data):
    """Creates a simple mapping from filename to its full original path."""
    path_map = {}
    for doc in document_data:
        filename = os.path.basename(doc['file_path'])
        path_map[filename] = doc['file_path']
    return path_map

def get_current_structure_analysis_from_ai(document_data):
    """Sends document info to the AI and requests an analysis of the current file structure."""
    global errors_encountered, api_response_time, tokens_used
    documents_str = "\n".join([
        f"- File Path: {doc['file_path']}\n  Type: {doc.get('type', 'N/A')}\n  Summary: {doc['summary']}\n"
        for doc in document_data
    ])

    prompt = f"""
    You are an expert file organization assistant. Your task is to analyze the current file structure based on the provided file paths, types, and summaries, explain why the existing placement and structure may not be the best optimized, and convince the user that a new organization would be beneficial.

    **File Information:**
    {documents_str}

    **Instructions:**
    Respond ONLY with a concise analysis (200-400 words) that includes:
    - A description of the current structure (e.g., how files are grouped, any patterns in directories).
    - Why it may not be optimal (e.g., scattered files, lack of logical grouping by project/year/topic, redundancy, difficulty in navigation).
    - Suggestions for improvement (high-level, without providing the full plan yet).
    - A convincing argument on the benefits of reorganizing (e.g., easier access, better scalability, reduced search time).

    Do not provide a JSON plan, file tree, or any reorganization details yet. Focus on analysis and persuasion.
    """

    print("Asking the AI to analyze the current file structure... (This may take a moment)")
    try:
        # ** FIX: Instantiate the model first, then call generate_content **
        model = genai.GenerativeModel('gemini-1.5-flash')
        start_api_time = time.time()
        response = model.generate_content(prompt)
        api_response_time += time.time() - start_api_time
        response_text = response.text.strip()

        # Estimate tokens
        input_tokens = len(prompt) // 4
        output_tokens = len(response_text) // 4
        tokens_used += input_tokens + output_tokens
        return response_text
    except Exception as e:
        print(f"\n--- Error ---")
        print(f"Failed to get a valid response from the AI. Error: {e}")
        errors_encountered += 1
        return None

def handle_user_questions(document_data, current_analysis):
    """Handles an interactive Q&A session with the user about the file analysis."""
    global errors_encountered, api_response_time, tokens_used
    print("\n--- Q&A Session ---")
    print("You can now ask questions about the file analysis or potential organization.")

    documents_str = "\n".join([
        f"- File: {os.path.basename(doc['file_path'])}\n  Summary: {doc['summary']}\n"
        for doc in document_data
    ])

    while True:
        user_question = input("Ask a question (or type 'quit' to proceed): ").strip()
        if user_question.lower() in ['quit', 'exit', 'q', '']:
            print("Exiting Q&A session.")
            break

        prompt = f"""
        You are a file organization assistant. You have already provided the user with an initial analysis of their files. Now, your task is to answer the user's follow-up questions.

        **Original File Information:**
        {documents_str}

        **Your Previous Analysis:**
        {current_analysis}

        **User's Question:**
        "{user_question}"

        **Instructions:**
        Based on all the context above, provide a clear and concise answer to the user's question. If the question is about why certain files might be grouped together, explain the logical connection based on their summaries. If it's about a specific file, refer to its summary to provide an answer.
        """

        print("...Thinking...")
        try:
            # ** FIX: Instantiate the model first, then call generate_content **
            model = genai.GenerativeModel('gemini-1.5-flash')
            start_api_time = time.time()
            response = model.generate_content(prompt)
            api_response_time += time.time() - start_api_time
            response_text = response.text.strip()

            print(f"\nAI Response: {response_text}\n")

            # Estimate tokens
            input_tokens = len(prompt) // 4
            output_tokens = len(response_text) // 4
            tokens_used += input_tokens + output_tokens

        except Exception as e:
            print(f"\n--- Error ---")
            print(f"Failed to get a valid response from the AI. Error: {e}")
            errors_encountered += 1


def get_organization_plan_from_ai(document_data, current_analysis):
    """Sends document info and previous analysis to the AI and requests a file organization plan with a file tree."""
    global ai_plan_valid, errors_encountered, api_response_time, tokens_used
    documents_str = "\n".join([
        f"- File: {os.path.basename(doc['file_path'])}\n  Summary: {doc['summary']}\n"
        for doc in document_data
    ])

    prompt = f"""
    You are an expert file organization assistant. Based on the following analysis of the current file structure, your task is to organize the files listed below into a logical folder structure and provide a JSON plan, an ASCII file tree representation, and a reasoning section explaining the organization.

    **Previous Analysis of Current Structure:**
    {current_analysis}

    **File Information:**
    {documents_str}

    **Instructions:**
    Respond ONLY with a single output containing three sections, separated clearly. Do not include any additional text, explanations, or markdown formatting outside the specified structure. DO NOT CHANGE THE NAME OF FILES; KEEP THEM AS THEY ARE.

    1. **JSON Plan**:
       - A JSON object where each key is the proposed new directory path (e.g., "Case_Studies/2020_Grimmen_Vegetation").
       - Each value is a list of filenames (e.g., ["Case Study_Cutting Vegetation_2020.docx", "Fassade nach Cutting.png"]) to be moved into that directory.
       - Use forward slashes (/) for directory paths.

    2. **ASCII File Tree**:
       - After the JSON, include a line with exactly "-----" to separate sections.
       - Provide an ASCII file tree representation of the same structure.

    3. **Reasoning**:
       - After the file tree, include another line with exactly "-----" to separate sections.
       - Provide a concise explanation (100-200 words) of why this organization plan was chosen.

    **Output Format**:
    ```json
    {{
      "Case_Studies/2018_Cadolzburg": [
        "Case Study_Cadolzburg_v1.docx",
        "ZAE_Modulliste.pdf"
      ]
    }}
    -----
    Case_Studies/
    └── 2018_Cadolzburg/
        ├── Case Study_Cadolzburg_v1.docx
        └── ZAE_Modulliste.pdf
    -----
    The files are organized by project and year...
    ```

    Ensure all files from the input are included in both the JSON and the file tree.
    """

    print("Asking the AI to generate an organization plan, file tree, and reasoning... (This may take a moment)")
    try:
        # ** FIX: Instantiate the model first, then call generate_content **
        model = genai.GenerativeModel('gemini-1.5-flash')
        start_api_time = time.time()
        response = model.generate_content(prompt)
        api_response_time += time.time() - start_api_time
        response_text = response.text.strip().replace('```json', '').replace('```', '')

        parts = response_text.split('-----', 2)
        if len(parts) != 3:
            raise ValueError("Invalid response format: Expected three sections separated by '-----'.")
        json_part, file_tree, reasoning = [part.strip() for part in parts]

        plan = json.loads(json_part)
        ai_plan_valid = True
        
        input_tokens = len(prompt) // 4
        output_tokens = len(response_text) // 4
        tokens_used += input_tokens + output_tokens
        return plan, file_tree, reasoning
    except (json.JSONDecodeError, Exception) as e:
        print(f"\n--- Error ---")
        print(f"Failed to get a valid response from the AI. Error: {e}")
        print("AI's raw response was:")
        print(response.text if 'response' in locals() and hasattr(response, 'text') else "No response object.")
        errors_encountered += 1
        return None, None, None

def execute_file_organization(plan, path_map, destination_root):
    """Creates directories and moves files based on the provided plan."""
    global files_moved, total_files_in_plan, dirs_created, total_dirs_in_plan
    global valid_path_mappings, total_filenames_in_plan, errors_encountered
    print("\nStarting file organization process...")
    
    if not plan:
        print("Cannot proceed with an empty or invalid plan.")
        errors_encountered += 1
        return

    total_dirs_in_plan = len(plan)
    total_filenames_in_plan = sum(len(files) for files in plan.values())
    total_files_in_plan = total_filenames_in_plan

    for directory, filenames in plan.items():
        new_dir_path = destination_root / Path(directory)
        
        try:
            os.makedirs(new_dir_path, exist_ok=True)
            print(f"\n[OK] Ensured directory exists: '{new_dir_path}'")
            dirs_created += 1
        except OSError as e:
            print(f"[ERROR] Could not create directory '{new_dir_path}'. Skipping. Error: {e}")
            errors_encountered += 1
            continue

        for filename in filenames:
            original_path = path_map.get(filename)
            
            if not original_path:
                print(f"  [WARN] Could not find original path for '{filename}'. Skipping.")
                errors_encountered += 1
                continue

            if not os.path.exists(original_path):
                print(f"  [WARN] Source file does not exist at '{original_path}'. Skipping.")
                errors_encountered += 1
                continue

            valid_path_mappings += 1
            destination_path = new_dir_path / filename

            try:
                shutil.move(original_path, destination_path)
                print(f"  -> Moved '{filename}' to '{new_dir_path}'")
                files_moved += 1
            except Exception as e:
                print(f"  [ERROR] Failed to move '{filename}'. Error: {e}")
                errors_encountered += 1


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load data from llm_input.json
    all_docs = load_document_data()

    if all_docs:
        # 2. Get the analysis of the current structure from the AI
        current_analysis = get_current_structure_analysis_from_ai(all_docs)

        if current_analysis:
            # 3. Display the analysis
            print("\n--- Analysis of Current File Structure ---")
            print(current_analysis)
            print("------------------------------------------")

            # 4. Start the interactive Q&A session
            handle_user_questions(all_docs, current_analysis)

            # 5. Ask for confirmation to proceed with reorganization plan generation
            confirm_plan_generation = input("Would you like me to generate a new organization plan now? (yes/no): ").lower().strip()

            if confirm_plan_generation == 'yes':
                # 6. Get the organization plan, file tree, and reasoning from the AI
                organization_plan, file_tree, reasoning = get_organization_plan_from_ai(all_docs, current_analysis)

                if organization_plan and file_tree and reasoning:
                    # 7. Create a map of filenames to their original paths
                    file_path_map = create_file_path_map(all_docs)

                    # 8. Display the plan and file move information
                    print("\n--- Proposed Organization Plan ---")
                    for directory, files in organization_plan.items():
                        print(f"\nFolder: {directory}")
                        for f in files:
                            original_path = file_path_map.get(f, "Not found")
                            destination_path = DESTINATION_ROOT / Path(directory) / f
                            print(f"  File: {f}")
                            print(f"    From: {original_path}")
                            print(f"    To:   {destination_path}")
                    print("\n------------------------------------")

                    # 9. Display the LLM-generated file tree and reasoning
                    print("\nVisible File Tree:")
                    print(file_tree)
                    print("\nReasoning for Organization Plan:")
                    print(reasoning)
                    print("\n------------------------------------")

                    # 10. Ask for final confirmation to apply the plan
                    confirm_apply = input("Do you want to apply this organization? This will move files. (yes/no): ").lower().strip()

                    if confirm_apply == 'yes':
                        # 11. Execute the plan
                        execute_file_organization(organization_plan, file_path_map, DESTINATION_ROOT)
                    else:
                        print("Organization application cancelled by user.")
            else:
                print("Reorganization cancelled by user.")

    # Calculate and Print KPIs
    end_time = time.time()
    total_processing_time = end_time - start_time
    
    kpi_report = {
        "file_organization_success_rate": (files_moved / total_files_in_plan * 100) if total_files_in_plan > 0 else 0.0,
        "processing_time_seconds": total_processing_time,
        "ai_plan_validity_rate": 100.0 if ai_plan_valid else 0.0,
        "directory_creation_success_rate": (dirs_created / total_dirs_in_plan * 100) if total_dirs_in_plan > 0 else 0.0,
        "file_path_mapping_accuracy": (valid_path_mappings / total_filenames_in_plan * 100) if total_filenames_in_plan > 0 else 0.0,
        "error_rate": (errors_encountered / (total_filenames_in_plan + total_dirs_in_plan) * 100) if (total_filenames_in_plan + total_dirs_in_plan) > 0 else 0.0,
        "input_file_load_success_rate": 100.0 if json_load_success else 0.0,
        "api_response_time_seconds": api_response_time,
        "tokens_used": tokens_used
    }

    print("\n=== KPI Report ===")
    print(f"File Organization Success Rate: {kpi_report['file_organization_success_rate']:.2f}% ({files_moved}/{total_files_in_plan} files)")
    print(f"Processing Time: {kpi_report['processing_time_seconds']:.2f} seconds")
    print(f"AI Plan Validity Rate: {kpi_report['ai_plan_validity_rate']:.2f}%")
    print(f"Directory Creation Success Rate: {kpi_report['directory_creation_success_rate']:.2f}% ({dirs_created}/{total_dirs_in_plan} dirs)")
    print(f"File Path Mapping Accuracy: {kpi_report['file_path_mapping_accuracy']:.2f}%")
    print(f"Error Rate: {kpi_report['error_rate']:.2f}% ({errors_encountered} errors)")
    print(f"Input File Load Success Rate: {kpi_report['input_file_load_success_rate']:.2f}%")
    print(f"Total API Response Time: {kpi_report['api_response_time_seconds']:.2f} seconds")
    print(f"Total Tokens Used (Estimated): {kpi_report['tokens_used']}")
    print("=================\n")

    print("Processing complete.")