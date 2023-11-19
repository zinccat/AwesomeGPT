# parse pdf into txt

import pypdf

import re
from typing import List

import os
import concurrent.futures
from tqdm import tqdm

def clean_article(text):
    # Splitting at 'Abstract' to remove title, author, and affiliation details
    sections = re.split(r'(?i)Abstract\n', text)
    if len(sections) > 1:
        cleaned_text = sections[1]
    else:
        cleaned_text = text  # If no "Abstract" section is found, return the original text
    
    
    # Removing "Preprint. Under review." and "arXiv:..." lines
    cleaned_text = cleaned_text.replace("Preprint. Under review.", "")
    cleaned_text = re.sub(r"arXiv:\d+\.\d+v\d+\s+\[.*?\]\s+\d+ \w+ \d+", "", cleaned_text)
    
    # Removing figure references
    # cleaned_text = re.sub(r"Figure \d+:.*?\n", "", cleaned_text)
    
    # Removing URLs
    # cleaned_text = re.sub(r"https?://[^\s]+", "", cleaned_text)
    
    # Splitting page numbers and section numbers
    # cleaned_text = re.sub(r"(\d)(\.\d+)", r"\1\n\2", cleaned_text)
    
    # Removing any double newlines for cleaner formatting
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    
    return cleaned_text

def merge_text_by_headings(text: str, list_headings: List[str]) -> str:
    # Create a pattern to match the headings (case insensitive)
    # pattern = '|'.join([r'\d+(\.\d+)?\s+' + re.escape(heading) for heading in list_headings])
    pattern = '|'.join([r'\d+\s+' + re.sub(r' ', r'\\s*', heading) for heading in list_headings])
    lines = text.split('\n')

    merged_sections = []
    current_section = ''
    flag = False
    for line in lines:
        # Check if the line matches any heading pattern
        if re.match(pattern, line, re.IGNORECASE):
            flag = True
            # If there's content in the current section, add it to the merged sections
            if current_section:
                merged_sections.append(current_section.strip())
                current_section = ''
        # Add the line to the current section
        current_section += line
        current_section += '\n' if flag else ' '
        flag = False

    # Add the last section if it exists
    if current_section:
        merged_sections.append(current_section.strip())

    return '\n\n'.join(merged_sections)

# def remove_post_acknowledgments(text: str) -> str:
#     # Use regular expressions to find the sections "Acknowledgments" or "References"
#     # and trim the text to only include content before these sections.
#     ack_ref_pattern = re.compile(r"(CONTRIBUTIONS|ACKNOWLEDGEMENTS|Acknowledgments|References)", re.IGNORECASE)
#     match = ack_ref_pattern.search(text)
#     if match:
#         return text[:match.start()].strip()
#     return text

def remove_post_acknowledgments(text: str) -> str:
    # Adjust the regex pattern to make the preceding digit optional and allow for an optional space between the digit and the heading
    # CONTRIBUTIONS|
    ack_ref_pattern = re.compile(r"^\d*\s*?(References|ACKNOWLEDGEMENTS|Acknowledgments|Disclosure of Funding)", re.IGNORECASE | re.MULTILINE)
    # References
    match = ack_ref_pattern.search(text)
    if match:
        return text[:match.start()].strip()
    return text

def extract_text_by_outline(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        outlines = [o['/Title'] for o in reader.outline if not isinstance(o, list)]
        text = ''
        for j in range(len(reader.pages)):
            text += reader.pages[j].extract_text()
        return text, outlines

def remove_page_numbers(text: str) -> str:
    # Use regular expressions to identify lines that likely contain only a page number
    # and remove them. The pattern looks for lines that contain only digits (with optional whitespace).
    return re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE).strip()

def merge_hyphenated_words(text: str) -> str:
    # Use regular expressions to replace patterns like "ma- chine" with "machine"
    return re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)

def standardize_quotes(text: str) -> str:
    # Replace curly single and double quotes with straight quotes
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('“', '"').replace('”', '"')
    return text

def transform_spaced_out_headings(text: str) -> str:
    # This function detects section headings with spaced-out characters 
    # and then merges them into a single word.
    
    # Pattern to detect titles like "6 E XPERIMENTS"
    pattern = r'(\d+\s+)([A-Z]\s+)+[A-Z]'
    
    def repl(match):
        # Remove spaces from the matched heading
        return match.group(1) + ''.join(match.group(0).split()[1:])
    
    return re.sub(pattern, repl, text)

def replace_common_ligatures(text: str) -> str:
    # Dictionary of common ligatures and their replacements
    ligature_dict = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "æ": "ae",
        "œ": "oe",
        "Æ": "AE",
        "Œ": "OE"
    }
    
    for ligature, replacement in ligature_dict.items():
        text = text.replace(ligature, replacement)
    
    return text

def remove_conference_lines(text: str) -> str:
    # Use regular expressions to remove lines that match the pattern 
    # of "X Published as a conference paper at Y"
    text = re.sub(r'^\d+Published as a conference paper at .+\n', '', text, flags=re.MULTILINE|re.IGNORECASE)
    # text = re.sub(r'^\d+Published in .+\n', '', text, flags=re.MULTILINE|re.IGNORECASE)
    return text


def process(text, outlines):
    text = transform_spaced_out_headings(text)
    text = remove_post_acknowledgments(text)
    text = clean_article(text)
    text = remove_conference_lines(text)
    text = replace_common_ligatures(text)
    text = merge_text_by_headings(text, outlines)
    text = merge_hyphenated_words(text)
    text = standardize_quotes(text)
    text = "Abstract\n" + text
    return text

def parse_pdf(pdf_path, output_dir, cache):
    data, outlines = extract_text_by_outline(pdf_path)
    data = process(data, outlines)
    if cache:
        with open(os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', '.txt')), 'w') as f:
            f.write(data)
    return data

def process_pdfs(username, repo, cache=True):
    input_dir = f'data/pdf/{username}/{repo}'
    output_dir = f'data/txt/{username}/{repo}'
    os.makedirs(output_dir, exist_ok=True)

    pdf_paths = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    papers_text = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_pdf = {executor.submit(parse_pdf, pdf_path, output_dir, cache): pdf_path for pdf_path in pdf_paths}
        
        # Initialize tqdm progress bar
        with tqdm(total=len(pdf_paths), desc="Processing PDFs") as progress_bar:
            for future in concurrent.futures.as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    data = future.result()
                    papers_text[os.path.basename(pdf_path)] = data
                except Exception as e:
                    print(f"Exception occurred while processing file {pdf_path}: {e}")
                finally:
                    progress_bar.update(1)  # Update the progress bar for each completed future

    return papers_text



if __name__ == "__main__":
    pdf_path = "data/pdf/AmadeusChan/Awesome-LLM-System-Papers/Blockwise Parallel Transformer for Large Context Models.pdf"
    data = parse_pdf(pdf_path)
    with open("data.txt", "w") as f:
        f.write(data)