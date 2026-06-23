"""Update Learn.vue watermark to match MiMo official style + full width"""
import re

path = r"D:\Dev\demo\frontend\src\views\student\Learn.vue"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Replace watermarkRows with 20 rows of Do It. spans
old_rows = re.search(r"const watermarkRows = \[.*?\]", c, re.DOTALL)
if old_rows:
    rows_lines = []
    for i in range(20):
        rows_lines.append("  'Do It. '.repeat(25).split(' '),")
    new_rows = "const watermarkRows = [\n" + "\n".join(rows_lines) + "\n]"
    c = c[:old_rows.start()] + new_rows + c[old_rows.end():]
    print("Data: 20 rows x 25 Do It. spans")

# 2. Replace template - each span is a phrase
old_tpl_block = re.search(
    r'<div class="watermark-layer">.*?</div>\s*</div>\s*<!--',
    c, re.DOTALL
)
if old_tpl_block:
    new_tpl = '''<div class="watermark-layer">
            <div class="wm-row" v-for="(row, ri) in watermarkRows" :key="ri">
              <span class="wm-phrase" v-for="(ch, ci) in row" :key="ci">{{ ch }}</span>
            </div>
          </div>
          <!--'''
    c = c[:old_tpl_block.start()] + new_tpl + c[old_tpl_block.end():]
    print("Template: MiMo-style spans per row")
else:
    print("Template: watermark-layer block not found")

# 3. Replace CSS block
old_css = re.search(
    r'/\* 水印层.*?(?=\.flip-card \{)',
    c, re.DOTALL
)
if old_css:
    new_css = """/* 水印层 - MiMo官网风格大字铺满 */
.watermark-layer {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  justify-content: space-between;
  pointer-events: none; z-index: 0;
  overflow: hidden; padding: 10px 0;
}
.wm-row {
  display: flex; justify-content: flex-start; gap: 0;
  white-space: nowrap; overflow: hidden;
}
.wm-phrase {
  font-family: 'Noto Sans SC', 'Arial Black', sans-serif;
  font-size: clamp(50px, 9vw, 100px);
  font-weight: 900;
  color: rgba(0, 0, 0, 0.03);
  line-height: 1;
  letter-spacing: 0.15em;
  transition: color 0.6s ease;
  user-select: none;
  flex-shrink: 0;
  margin-right: 0.8em;
}
.wm-row:nth-child(even) {
  padding-left: 3em;
}
.quote-cell:hover .wm-phrase {
  color: rgba(0, 0, 0, 0.06);
}
.flip-card { position: relative; z-index: 1; }

"""
    c = c[:old_css.start()] + new_css + c[old_css.end():]
    print("CSS: MiMo official style applied")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(c)
print("Learn.vue saved!")
