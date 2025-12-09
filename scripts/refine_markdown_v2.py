
import re

input_file = '/home/serjaii/serjaii/content/post/practica-cooperativa-instalaciones/index.md'
output_file = input_file

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

processed_lines = []
in_toc = False
toc_done = False
in_code_block = False
buffer_command = ""

# Heuristic to detect the start of TOC block
# We know it starts around line 14 and ends around line 128.
# It consists of headers like "### 1.Config..." followed by dots.
# And ends before "## Instalación de Oracle 21c..."

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # 1. Remove TOC
    if not toc_done:
        # Check start of TOC (approximate line check or content check)
        # Line 14 in previous view was ### 1.Config...
        if "### 1.Configuración previa y dependencias.................." in line:
            in_toc = True
        
        # Check end of TOC
        if "## Instalación de Oracle 21c sobre Debian 13" in line:
            in_toc = False
            toc_done = True
            # Don't skip this line, it's the first real header
        
        if in_toc:
            continue

    # 2. Fix Strange Characters (if any remaining)
    # The previous script replaced  with - and  with -
    # Let's ensure common bullets are fixed.
    line = line.replace('', '-')
    line = line.replace('', '  -')
    
    # 3. Fix Code Blocks
    if line.strip().startswith('```'):
        if not in_code_block:
            in_code_block = True
            processed_lines.append(line)
        else:
            # Closing block
            if buffer_command:
                processed_lines.append(buffer_command + "\n")
                buffer_command = ""
            in_code_block = False
            processed_lines.append(line)
        continue

    if in_code_block:
        # We want to merge broken lines.
        # Logic: 
        # If line starts with 'serjaii@db:~$', it's a new command. Flush previous buffer.
        # If line does NOT start with prompt, it might be continuation or output.
        # If previous buffer ended with 'sudo', 'nano', 'apt', 'wget' etc or looks incomplete, append.
        
        is_prompt = stripped.startswith('serjaii@db:~$')
        
        if is_prompt:
            if buffer_command:
                processed_lines.append(buffer_command + "\n")
            buffer_command = stripped
        else:
            if buffer_command:
                # Heuristic: Append to buffer if it's likely a split command
                # Split commands often occur after 'sudo', 'nano', 'apt', 'wget', or paths
                # Or if the current text looks like a path or argument
                prev_text = buffer_command.strip()
                curr_text = stripped
                
                # Check for bad splits like "li" "stener.ora"
                # If we just merge with space, we might break paths? 
                # "network/admin/li" + "stener.ora" -> "network/admin/li stener.ora" (Wrong)
                # It should be ".../listener.ora"
                # If the split happened in original PDF, it might be weird.
                # However, most splits are like "sudo" \n "command".
                
                # Let's merge with space usually, unless previous char was / or -?
                # Actually, simply joining lines with space is safer than no space, 
                # but "listener.ora" split as "li" "stener.ora" implies NO space was intended.
                # But detecting that is hard.
                # Let's assume space is required for now, except for obvious mid-word breaks?
                
                buffer_command += " " + curr_text
            else:
                # No buffer, just an output line?
                processed_lines.append(line)
    else:
        processed_lines.append(line)

# Flush last buffer if any (unlikely to end with open code block but good practice)
if buffer_command:
    processed_lines.append(buffer_command + "\n")

# Write back
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(processed_lines)
