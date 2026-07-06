import os
import re

def process_file(filepath):
    # Don't translate the English version
    if '/en/' in filepath:
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # The exact string is split across two lines in some places
    # We use regex to match "(Sunday\s+Closed)"
    content = re.sub(r'\(Sunday\s+Closed\)', r'(Воскресенье - выходной)', content, flags=re.IGNORECASE)

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed schedule translation in: {filepath}")

def main():
    root_dir = '/Users/morfi/be-demo'
    # Walk through the directory
    for dirpath, _, filenames in os.walk(root_dir):
        # Skip hidden directories like .git or .gemini
        if '/.' in dirpath or dirpath.startswith('.'):
            continue
            
        for filename in filenames:
            if filename.endswith('.html'):
                process_file(os.path.join(dirpath, filename))
                
if __name__ == '__main__':
    main()
