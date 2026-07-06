import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Find all forms
    forms = re.findall(r'<form\b[^>]*>', content, flags=re.IGNORECASE)
    
    for form in forms:
        # Skip forms with method="get" (usually search forms)
        if re.search(r'method=[\'"]get[\'"]', form, flags=re.IGNORECASE):
            continue
            
        # Skip mailchimp forms
        if 'themelooks.us12.list-manage.com' in form:
            continue
            
        # If it's not already pointing to our API
        if '/api/send-message' not in form:
            # We want to replace action="..." with action="/api/send-message"
            # and add method="post" and data-form="ajax"
            
            new_form = form
            
            # Replace or add action
            if re.search(r'action=[\'"][^\'"]*[\'"]', new_form):
                new_form = re.sub(r'action=[\'"][^\'"]*[\'"]', 'action="/api/send-message"', new_form)
            else:
                new_form = new_form.replace('<form', '<form action="/api/send-message"')
                
            # Replace or add method
            if re.search(r'method=[\'"][^\'"]*[\'"]', new_form):
                new_form = re.sub(r'method=[\'"][^\'"]*[\'"]', 'method="post"', new_form)
            else:
                new_form = new_form.replace('<form', '<form method="post"')
                
            # Add data-form="ajax" if not present
            if 'data-form="ajax"' not in new_form:
                new_form = new_form.replace('<form', '<form data-form="ajax"')
                
            content = content.replace(form, new_form)

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

def main():
    root_dir = '/Users/morfi/be-demo'
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.html'):
                process_file(os.path.join(dirpath, filename))
                
if __name__ == '__main__':
    main()
