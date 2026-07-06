import os
import re

WHATSAPP_HTML = """
<!-- WhatsApp Floating Widget -->
<a href="https://wa.me/996501313114?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5%21%20%D0%A5%D0%BE%D1%87%D1%83%20%D0%BF%D1%80%D0%BE%D0%BA%D0%BE%D0%BD%D1%81%D1%83%D0%BB%D1%8C%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C%D1%81%D1%8F." target="_blank" style="position:fixed;bottom:90px;right:30px;background-color:#25D366;color:white;width:60px;height:60px;border-radius:50%;text-align:center;font-size:35px;box-shadow:2px 2px 10px rgba(0,0,0,0.2);z-index:9999;display:flex;align-items:center;justify-content:center;text-decoration:none;transition:transform 0.3s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
    <i class="fa fa-whatsapp"></i>
</a>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Check if already added
    if '<!-- WhatsApp Floating Widget -->' not in content:
        # Insert right before </body>
        content = content.replace('</body>', f'{WHATSAPP_HTML}\n</body>')

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added WhatsApp to: {filepath}")

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
