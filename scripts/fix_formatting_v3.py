
import re

file_path = '/home/serjaii/serjaii/content/post/practica-cooperativa-instalaciones/index.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

processed_lines = []
in_code = False

# Known dependencies to bulletize
deps = [
    'libaio1t64', 'libaio-dev', 'unixodbc', 'rlwrap', 'bc', 'ksh', 'alien', 'not-tools', 'net-tools', 'unzip', 'curl', 'gnupg'
]

# Regex for SQL splitting
sql_keywords = ['CREATE TABLE', 'INSERT INTO', 'CONSTRAINT', 'REFERENCES', 'VALUES', 'USE hotel;', 'MariaDB \[(.*?)\]>']

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Fix Dependencies List
    # "libaio1t64: dependencia... libaio-dev: contiene..."
    # We want to split this into bullets if it's all in one line or poorly formatted.
    # The grep showed it might be spread across lines but maybe not bulleted.
    # User's request showed them all mashed together.
    # Let's try to detect if a line starts with a dependency name followed by ':' and try to bullet it if not already
    
    # Actually, the user's snippet "libaio1t64: dependencia ... libaio-dev: ..." suggests they might be on the same line.
    # In my view_file output lines 34-45 looked okay (each on new line).
    # BUT line 797 in view_file: "sudo apt install ... - curl: sirve ... gnupg: permite ..."
    # That one IS mashed.
    
    formatted_line = line
    
    # 1. Formatting mashed text into bullets
    # Only do this if line contains multiple "key: value" patterns or is long and contains specific keys
    found_keys = [k for k in deps if k + ':' in formatted_line]
    if len(found_keys) > 1 or (len(found_keys) == 1 and not stripped.startswith('-') and not stripped.startswith('#') and len(formatted_line) > 80):
       # Replace " key:" with "\n- **key**:"
       for key in deps:
           # regex to replace "key:" with "\n- **key**:" matching whole word
           # Avoid replacing if it's already bulleted
           pattern = r'(?<!- )(?<!\*\*)\b' + re.escape(key) + r':'
           formatted_line = re.sub(pattern, r'\n- **' + key + r'**:', formatted_line)
    
    # Formatting single lines that should be bullets (lines 34-45 in view_file were just text)
    # Check if line starts with specific keys
    for key in deps:
        if formatted_line.strip().startswith(key + ':'):
             formatted_line = '- **' + key + '**:' + formatted_line.strip()[len(key)+1:] + '\n'

    # 2. Fix 'lrwxrwxrwx' (Line 60 in view_file)
    if 'lrwxrwxrwx' in formatted_line:
        # Check if previous line was closing code block
        if processed_lines and processed_lines[-1].strip() == '```':
             # Remove the closing block from previous line
             processed_lines.pop()
             # Append current line
             processed_lines.append(formatted_line)
             # Add closing block
             processed_lines.append('```\n')
             continue
             
    # 3. Fix Monster SQL Line (Line 777 in view_file)
    if 'INSERT INTO' in formatted_line and 'CREATE TABLE' in formatted_line and len(formatted_line) > 200:
        # This is the monster line.
        # Strategy: Replace specific patterns with "\n" + pattern
        
        # Replace comment-like text "Creación de..."
        formatted_line = re.sub(r'(Creación de la tabla .*?\.)', r'\n-- \1\n', formatted_line)
        formatted_line = re.sub(r'(Inserción de datos .*?\.)', r'\n-- \1\n', formatted_line)
        formatted_line = re.sub(r'(Datos tabla .*?:)', r'\n-- \1\n', formatted_line)
        
        # Split Commands
        formatted_line = formatted_line.replace('CREATE TABLE', '\nCREATE TABLE')
        formatted_line = formatted_line.replace('INSERT INTO', '\nINSERT INTO')
        formatted_line = formatted_line.replace('USE hotel;', '\nUSE hotel;\n')
        
        # Formatting internal SQL
        formatted_line = formatted_line.replace('CONSTRAINT', '\n  CONSTRAINT')
        formatted_line = formatted_line.replace('PRIMARY KEY', 'PRIMARY KEY') 
        formatted_line = formatted_line.replace(');', ');\n')
        formatted_line = formatted_line.replace('VALUES', 'VALUES') # Keep on same line usually?
        
        # Split MariaDB prompt
        formatted_line = re.sub(r'(MariaDB \[(.*?)\]>)', r'\n\1 ', formatted_line)

    processed_lines.append(formatted_line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(processed_lines)
