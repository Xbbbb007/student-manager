"""Change watermark from M I M O to Do It."""
import re

path = r"D:\Dev\demo\frontend\src\views\student\Learn.vue"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Replace watermarkRows data
old_rows = re.search(r"const watermarkRows = \[.*?\]", c, re.DOTALL)
if old_rows:
    new_rows = """const watermarkRows = [
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
  'Do It. '.repeat(8).split(' '),
]"""
    c = c[:old_rows.start()] + new_rows + c[old_rows.end():]
    print("Data: Do It. watermarkRows added")

# 2. Replace template: wm-letter loop -> wm-phrase single span
old_tpl = """<div class="wm-row" v-for="(row, ri) in watermarkRows" :key="ri">
              <span class="wm-letter" v-for="(ch, ci) in row" :key="ci">{{ ch }}</span>
            </div>"""
new_tpl = """<div class="wm-row" v-for="(row, ri) in watermarkRows" :key="ri">
              <span class="wm-phrase">{{ row.join('') }}</span>
            </div>"""
if old_tpl in c:
    c = c.replace(old_tpl, new_tpl, 1)
    print("Template: wm-phrase added")
else:
    print("Template: old pattern not found")

# 3. Replace CSS: wm-letter -> wm-phrase
old_css = re.search(r"\.wm-row \{.*?\.wm-letter \{.*?\}", c, re.DOTALL)
if old_css:
    new_css = """.wm-row {
  display: flex; justify-content: center; gap: 0;
  white-space: nowrap; overflow: hidden;
}
.wm-phrase {
  font-family: 'Noto Sans SC', 'Arial Black', sans-serif;
  font-size: clamp(48px, 8vw, 90px);
  font-weight: 900;
  color: rgba(0, 0, 0, 0.035);
  line-height: 1.1;
  letter-spacing: 0.08em;
  transition: color 0.6s ease;
  user-select: none;
  text-transform: uppercase;
}"""
    c = c[:old_css.start()] + new_css + c[old_css.end():]
    print("CSS: wm-phrase styles added")

# 4. Fix hover selector
c = c.replace(".quote-cell:hover .wm-letter", ".quote-cell:hover .wm-phrase")
print("CSS: hover updated")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(c)
print("Learn.vue saved!")
