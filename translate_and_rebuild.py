import os
import re
import urllib.request
import urllib.parse
import json
import time
from html.parser import HTMLParser

workspace = "/Users/morfi/be-demo"
en_dir = os.path.join(workspace, "en")
kg_dir = os.path.join(workspace, "kg")

cache_file = os.path.join(workspace, "translation_cache.json")
translation_cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            translation_cache = json.load(f)
    except Exception as e:
        print(f"Failed to load cache: {e}")

def save_cache():
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(translation_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save cache: {e}")

def translate_text(text, target_lang):
    text = text.strip()
    # Check if empty, numbers, or tags
    if not text or text.isdigit() or re.match(r'^[0-9\W]+$', text):
        return text
    
    # Check cache
    cache_key = f"{text}||{target_lang}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    # Call free Google Translate API
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q=" + urllib.parse.quote(text)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            translated_text = "".join([part[0] for part in data[0] if part[0]])
            translation_cache[cache_key] = translated_text
            print(f"Translated: '{text[:20]}...' -> '{translated_text[:20]}...' [{target_lang}]")
            time.sleep(0.05) # Be gentle to Google API
            return translated_text
    except Exception as e:
        print(f"Error translating '{text[:30]}': {e}")
        return text

class TranslateHTMLParser(HTMLParser):
    def __init__(self, target_lang):
        super().__init__()
        self.target_lang = target_lang
        self.result = []
        self.in_script_or_style = False
        
    def handle_decl(self, decl):
        self.result.append(f"<!{decl}>")
        
    def handle_pi(self, data):
        self.result.append(f"<?{data}>")
        
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.in_script_or_style = True
        
        # Translate placeholder/value attributes if they exist
        new_attrs = []
        for name, value in attrs:
            if name in ('placeholder', 'value') and value and not value.isdigit() and tag in ('input', 'button', 'textarea'):
                value = translate_text(value, self.target_lang)
            new_attrs.append((name, value))
            
        attr_str = "".join([f' {k}="{v}"' if v is not None else f' {k}' for k, v in new_attrs])
        self.result.append(f"<{tag}{attr_str}>")
        
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.in_script_or_style = False
        self.result.append(f"</{tag}>")
        
    def handle_data(self, data):
        if self.in_script_or_style:
            self.result.append(data)
        else:
            stripped = data.strip()
            # Don't translate links, emails, numbers
            if stripped and not stripped.isdigit() and len(stripped) > 1 and not re.match(r'^\+?[0-9\s\-]+$', stripped):
                # Preserve whitespace
                leading = data[:len(data)-len(data.lstrip())]
                trailing = data[len(data.rstrip()):]
                translated = translate_text(stripped, self.target_lang)
                self.result.append(f"{leading}{translated}{trailing}")
            else:
                self.result.append(data)
                
    def handle_comment(self, data):
        self.result.append(f"<!--{data}-->")
        
    def handle_entityref(self, name):
        self.result.append(f"&{name};")
        
    def handle_charref(self, name):
        self.result.append(f"&#{name};")
        
    def get_html(self):
        return "".join(self.result)

# Rebuild files and add topbar language switcher
def inject_topbar_switcher(content, page, current_lang):
    # Remove old navbar dropdown if it was added
    content = re.sub(r'<div class="header--nav-lang dropdown float--right">.*?</div>', '', content, flags=re.DOTALL)
    
    # Find the social list float--right in the topbar
    social_tag = '<ul class="nav social float--right">'
    if social_tag not in content:
        return content
        
    # Build URLs
    if current_lang == "ru":
        ru_url = page
        kg_url = f"kg/{page}"
        en_url = f"en/{page}"
    elif current_lang == "en":
        ru_url = f"../{page}"
        kg_url = f"../kg/{page}"
        en_url = page
    elif current_lang == "kg":
        ru_url = f"../{page}"
        kg_url = page
        en_url = f"../en/{page}"
        
    ru_active = 'class="active" ' if current_lang == "ru" else ""
    kg_active = 'class="active" ' if current_lang == "kg" else ""
    en_active = 'class="active" ' if current_lang == "en" else ""
    
    switcher_html = f'''<ul class="nav links float--right lang-switcher" style="margin-right: 25px;">
    <li {ru_active}style="display: inline-block;"><a href="{ru_url}" style="padding: 13px 0;">RU</a></li>
    <li {kg_active}style="display: inline-block; margin-left: 10px; padding-left: 12px; position: relative;"><a href="{kg_url}" style="padding: 13px 0;">KG</a></li>
    <li {en_active}style="display: inline-block; margin-left: 10px; padding-left: 12px; position: relative;"><a href="{en_url}" style="padding: 13px 0;">EN</a></li>
</ul>
'''
    # In template topbar, links list items have vertical line via CSS: .header--topbar .links li+li:before { content: "|"; ... }
    # So we give them the links class and inline styling to display inline-block.
    
    return content.replace(social_tag, switcher_html + social_tag)

def restore_root_paths(content):
    content = content.replace('href="../css/', 'href="css/')
    content = content.replace('href="../style.css', 'href="style.css')
    content = content.replace('src="../js/', 'src="js/')
    content = content.replace('src="../img/', 'src="img/')
    content = content.replace('href="../favicon.png', 'href="favicon.png')
    content = content.replace('data-bg-img="../img/', 'data-bg-img="img/')
    return content

# List of files to process
html_files = [f for f in os.listdir(en_dir) if f.endswith(".html")]

print(f"Found {len(html_files)} source files in /en/. Starting translation and rebuild...")

for file in html_files:
    source_path = os.path.join(en_dir, file)
    with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
        en_source = f.read()
        
    print(f"\n--- Processing: {file} ---")
    
    # 1. Generate EN version (English text, Topbar Switcher)
    en_final = inject_topbar_switcher(en_source, file, "en")
    with open(os.path.join(en_dir, file), "w", encoding="utf-8") as f:
        f.write(en_final)
    print(f"Rebuilt EN: {file}")
    
    # 2. Generate RU version (Russian text, Root Paths, Topbar Switcher)
    print("Translating to Russian...")
    ru_parser = TranslateHTMLParser("ru")
    ru_parser.feed(en_source)
    ru_translated = ru_parser.get_html()
    ru_translated = restore_root_paths(ru_translated)
    ru_final = inject_topbar_switcher(ru_translated, file, "ru")
    with open(os.path.join(workspace, file), "w", encoding="utf-8") as f:
        f.write(ru_final)
    print(f"Rebuilt RU (root): {file}")
    save_cache()
    
    # 3. Generate KG version (Kyrgyz text, Relative Paths, Topbar Switcher)
    print("Translating to Kyrgyz...")
    kg_parser = TranslateHTMLParser("ky")
    kg_parser.feed(en_source)
    kg_translated = kg_parser.get_html()
    kg_final = inject_topbar_switcher(kg_translated, file, "kg")
    with open(os.path.join(kg_dir, file), "w", encoding="utf-8") as f:
        f.write(kg_final)
    print(f"Rebuilt KG: {file}")
    save_cache()

# Clean up translation cache file from workspace to keep it clean, or keep it for future runs
save_cache()
print("\nTranslation and rebuild complete!")
