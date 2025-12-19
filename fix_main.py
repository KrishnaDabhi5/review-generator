
path = 'api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The pattern is 4 spaces + return """ + newline + 4 spaces + return """
bad_pattern = '    return """\n    return """'
good_pattern = '    return """'

if bad_pattern in content:
    new_content = content.replace(bad_pattern, good_pattern)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed file.")
else:
    print("Pattern not found.")
    # Debug: print what we see around root
    idx = content.find('root():')
    if idx != -1:
        print("Around root:", repr(content[idx:idx+200]))
