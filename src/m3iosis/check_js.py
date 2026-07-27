import re

with open('/home/mrnob0dy666/imsgct/k3v-with-dialects.html', 'r') as f:
    html = f.read()

# Find the script content between the main <script> and </script> tags
# First <script> after line 1048 and first </script> after that
start = html.find('<script>', html.find('line-height: 1.4;'))
end = html.find('</script>', start)
js = html[start + len('<script>'):end]

# Save it for node to check
with open('/tmp/check.js', 'w') as f:
    f.write(js)

print(f'Script block from char {start} to {end}, {len(js)} chars, {js.count(chr(10))} lines')
print(f'First line: {js[:80]}')
print(f'Last 100 chars: {js[-100:]}')

# Check for template literals containing HTML
# Look for backtick strings that contain <
backtick_regions = []
i = 0
while i < len(js):
    bt = js.find('`', i)
    if bt == -1:
        break
    bt_end = js.find('`', bt + 1)
    if bt_end == -1:
        print(f'UNTERMINATED BACKTICK at char {bt}')
        break
    content = js[bt+1:bt_end]
    if '<' in content:
        backtick_regions.append((bt, bt_end, content[:50]))
    i = bt_end + 1

print(f'Found {len(backtick_regions)} backtick strings containing <')
for bt, be, preview in backtick_regions[:5]:
    line_num = js[:bt].count('\n') + 1
    print(f'  Line ~{line_num}: `{preview}...`')
