
import re

file_path = '/home/serjaii/serjaii/content/post/practica-cooperativa-instalaciones/index.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

content_lines = []
skip_mode = False
# We want to keep frontmatter (lines 0-8 approx)
# We want to keep the Intro text (lines 10-13)
# We want to SKIP the "ABD Práctica..." down to the first real header "## Instalación de Oracle 21c..."

# Let's find the start of real content.
# The TOC usually has "............"
found_toc_start = False
real_content_started = False

frontmatter_count = 0 
for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Always keep frontmatter (between --- and ---)
    if stripped == '---':
        frontmatter_count += 1
        content_lines.append(line)
        continue
    if frontmatter_count < 2:
        content_lines.append(line)
        continue

    # After frontmatter
    # Keep the Title Header line "# Guía Cooperativa..." and the intro paragraph
    if stripped.startswith("# Guía Cooperativa") or "Este documento recoge" in line:
        content_lines.append(line)
        continue
    
    # Detect TOC start
    if "Índice" in line or "ABD Práctica Cooperativa" in line or "Hecho por" in line:
        continue # Skip these lines
        
    # Detect TOC lines (dashes or dots with numbers at end)
    if re.search(r'\.{5,}\s*\d+', line):
        continue
    
    # Also headers in TOC might look like headers but have dots
    # But usually real headers don't have dots at the end
    if stripped.startswith("## ") and re.search(r'\.{5,}', line):
         continue

    # Strange characters replacement
    line = line.replace('', '-')
    line = line.replace('', '  -')
    line = line.replace('', '') # Remove form feeds

    # Fix broken commands inside code blocks
    # This is a bit risky but standard pattern seen:
    # "sudo\n" "nano\n" "/path/to/file"
    # We can try to join them if they are short?
    # Better to just clean the obvious artifacts.
    
    content_lines.append(line)

# Post-processing to join broken lines in code blocks if possible, or at least common patterns
# And remove multiple empty lines
final_lines = []
for line in content_lines:
    if line.strip() == "" and final_lines and final_lines[-1].strip() == "":
        continue # skip double empty lines
        
    final_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)
