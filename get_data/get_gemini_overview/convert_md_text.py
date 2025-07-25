"""
将gemini 网页版解读得到的Markdown格式文本转换为单行文本格式
"""

import os
import json

def convert_md_to_text(md_content):
    """
    Convert Markdown content to plain text without line breaks.
    - Normal line breaks: \n
    - Empty lines: \n\n
    
    Args:
        md_content (str): The Markdown content as a string.
        
    Returns:
        str: The converted plain text in single line format.
    """
    lines = md_content.split('\n')
    text_parts = []
    i = 0
    
    while i < len(lines):
        original_line = lines[i]
        line = original_line.strip()
        
        # Check if this is an empty line
        if line == '':
            # Look ahead to see if there are consecutive empty lines
            empty_count = 0
            j = i
            while j < len(lines) and lines[j].strip() == '':
                empty_count += 1
                j += 1
            
            # Add \n\n for empty lines (paragraph breaks)
            if text_parts:  # Only add if there's already content
                text_parts.append('\\n\\n')
            i = j  # Skip all consecutive empty lines
            continue
        
        # Process non-empty lines
        # Skip markdown headers but keep their content
        if line.startswith('#'):
            # Extract header content without # symbols
            line = line.lstrip('#').strip()
        
        # Remove bold syntax but keep content
        if line.startswith('**') and line.endswith('**'):
            line = line[2:-2]
        
        # Remove bullet points but keep content
        if line.startswith('* ') or line.startswith('- '):
            line = line[2:]
        
        # Add the processed line
        if line:  # Only add non-empty content
            # If there's already content, add \n for normal line break
            if text_parts and not text_parts[-1].endswith('\\n\\n'):
                text_parts.append('\\n')
            text_parts.append(line)
        
        i += 1
    
    # Join all parts
    result = ''.join(text_parts)
    
    return result.strip()
if __name__ == "__main__":
    # Example usage
    text_file = "text.txt"
    with open(text_file, "r", encoding="utf-8") as f:
        md_text = f.read()
    plain_text = convert_md_to_text(md_text)
    print("Finished Converted")
    data = {
        "text": plain_text
    }
    with open("converted_text.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)