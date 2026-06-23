path = r'D:\Dev\demo\frontend\src\views\student\Learn.vue'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '<div class="quote-cell">'
idx = c.find(target)
if idx >= 0:
    insert_html = (
        '<div class="watermark-layer">\n'
        '            <div class="wm-cell" v-for="w in watermarks" :key="w">\n'
        '              <span class="wm-text">{{ w }}</span>\n'
        '            </div>\n'
        '          </div>\n'
        '          '
    )
    c = c[:idx + len(target)] + insert_html + c[idx + len(target):]
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(c)
    print('Step 1: watermark HTML added')
else:
    print('quote-cell not found')
