import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Update html lang
    content = re.sub(r'<html([^>]*)lang=[\'"]en[\'"]([^>]*)>', r'<html\1lang="ru"\2>', content, flags=re.IGNORECASE)

    # 2. Update Title
    # The title might vary slightly across files, but we can target the common one
    new_title = "Ремонт телефонов, ноутбуков и электроники в Бишкеке | Best Electronics"
    content = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', content, flags=re.IGNORECASE|re.DOTALL)

    # 3. Update Author
    content = re.sub(r'<meta name=[\'"]author[\'"] content=[\'"]ThemeLooks[\'"]>', '<meta name="author" content="Best Electronics">', content, flags=re.IGNORECASE)

    # 4. Update Description
    new_desc = "Профессиональный ремонт смартфонов, планшетов, ноутбуков, ПК и другой электроники в Бишкеке. Быстро, качественно, с гарантией. Best Electronics."
    content = re.sub(r'<meta name=[\'"]description[\'"] content=[\'"][^\'"]*[\'"]>', f'<meta name="description" content="{new_desc}">', content, flags=re.IGNORECASE)

    # 5. Update Keywords
    new_keywords = "ремонт телефонов бишкек, ремонт ноутбуков, сервисный центр бишкек, best electronics, починить iphone бишкек, ремонт электроники, ремонт макбуков"
    content = re.sub(r'<meta name=[\'"]keywords[\'"] content=[\'"][^\'"]*[\'"]>', f'<meta name="keywords" content="{new_keywords}">', content, flags=re.IGNORECASE)

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated SEO tags in: {filepath}")

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
