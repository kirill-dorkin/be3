import os
import glob

workspace = "/Users/morfi/be-demo"
html_files = glob.glob(f"{workspace}/**/*.html", recursive=True)

broken_str = 'data-owl-responsive="{"0":{"items": "1"}, "551":{"items": "2"}, "992":{"items": "3"}, "1200":{"items": "4"}}"'
fixed_str = "data-owl-responsive='{\"0\":{\"items\": \"1\"}, \"551\":{\"items\": \"2\"}, \"992\":{\"items\": \"3\"}, \"1200\":{\"items\": \"4\"}}'"

count = 0
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if broken_str in content:
        new_content = content.replace(broken_str, fixed_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
        count += 1

print(f"Total files fixed: {count}")
