import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace QuickFix (exact case) -> Best Electronics
    content = content.replace("QuickFix", "Best Electronics")
    # Replace Quickfix -> Best Electronics
    content = content.replace("Quickfix", "Best Electronics")
    # Replace quickfix -> best electronics
    content = content.replace("quickfix", "best electronics")
    # Replace QUICKFIX -> BEST ELECTRONICS
    content = content.replace("QUICKFIX", "BEST ELECTRONICS")

    # Also replace "от Themelooks" which is the template author
    content = content.replace("от Themelooks", "")
    content = content.replace("by Themelooks", "")

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Removed QuickFix from: {filepath}")

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
