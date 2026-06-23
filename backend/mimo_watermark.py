"""
Replace the watermark in Learn.vue with MiMo-style watermark:
- Large bold sans-serif letters filling the entire card
- Alternating letter positions per row (M I M O pattern)
- Horizontal, not tilted
"""
import re

# ===== Fix Learn.vue =====
path = r"D:\Dev\demo\frontend\src\views\student\Learn.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace template: use rows-based watermark
old_tpl = '''<div class="watermark-layer">
            <div class="wm-cell" v-for="w in watermarks" :key="w">
              <span class="wm-text">{{ w }}</span>
            </div>
          </div>'''

new_tpl = '''<div class="watermark-layer">
            <div class="wm-row" v-for="(row, ri) in watermarkRows" :key="ri">
              <span class="wm-letter" v-for="(ch, ci) in row" :key="ci">{{ ch }}</span>
            </div>
          </div>'''

if old_tpl in content:
    content = content.replace(old_tpl, new_tpl, 1)
    print("Template: rows-based watermark added")
else:
    print("Template: old watermark not found, trying insert...")
    target = '<div class="watermark-layer">'
    if target in content:
        idx = content.find(target)
        end = content.find('</div>', idx) + 6
        content = content[:idx] + new_tpl.strip() + '\n          ' + content[end:]
        print("Template: replaced via insert")

# Replace data: use watermarkRows instead of watermarks
old_data = '''const watermarks = [
  '学而不思则罔', '思而不学则殆', '温故而知新', '可以为师矣',
  '三人行必有我师', '知之为知之', '不知为不知', '是知也',
  '敏而好学', '不耻下问', '学而时习之', '不亦说乎',
]'''

new_data = """const watermarkRows = [
  'M'.repeat(40).split(''),
  'I'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'O'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'I'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'O'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'I'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'O'.repeat(40).split(''),
  'M'.repeat(40).split(''),
  'I'.repeat(40).split(''),
]"""

if 'const watermarks' in content:
    content = content.replace(old_data, new_data, 1)
    print("Data: watermarkRows added")
elif 'const watermarkRows' not in content:
    # Find and replace the old watermarks array
    m = re.search(r"const watermarks = \[.*?\]", content, re.DOTALL)
    if m:
        content = content[:m.start()] + new_data + content[m.end():]
        print("Data: replaced via regex")

# Replace CSS
old_css_match = re.search(r'/\* 水印网格层 \*/.*?(?=\.flip-card \{)', content, re.DOTALL)
if old_css_match:
    new_css = """/* 水印层 - MiMo风格大字铺满 */
.watermark-layer {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  justify-content: space-around;
  pointer-events: none; z-index: 0;
  overflow: hidden;
}
.wm-row {
  display: flex; justify-content: center; gap: 0;
  white-space: nowrap; overflow: hidden;
}
.wm-letter {
  font-family: 'Noto Sans SC', 'Arial Black', sans-serif;
  font-size: clamp(40px, 7vw, 80px);
  font-weight: 900;
  color: rgba(0, 0, 0, 0.035);
  line-height: 1;
  letter-spacing: 0.3em;
  transition: color 0.6s ease;
  user-select: none;
  flex-shrink: 0;
}
.wm-row:nth-child(odd) .wm-letter {
  letter-spacing: 0.3em;
}
.wm-row:nth-child(even) .wm-letter {
  letter-spacing: 0.3em;
  margin-left: 1.5em;
}
/* 鼠标进入整个名言区 → 水印微微浮现 */
.quote-cell:hover .wm-letter {
  color: rgba(0, 0, 0, 0.065);
}
/* 翻牌内容保持在水印上面 */
.flip-card { position: relative; z-index: 1; }

"""
    content = content[:old_css_match.start()] + new_css + content[old_css_match.end():]
    print("CSS: MiMo-style watermark CSS added")
else:
    print("CSS: old watermark CSS not found")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content)
print("Learn.vue saved!")

# ===== Update Preview =====
preview = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MiMo风格水印预览</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700;900&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Noto Sans SC',sans-serif;background:#f0f0f0;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:40px}
.preview-card{width:900px;max-width:100%;background:#fff;overflow:hidden;position:relative}
.quote-body{min-height:420px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 40px;position:relative;overflow:hidden}

/* MiMo风格水印 */
.wm-layer{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:space-around;pointer-events:none;z-index:0;overflow:hidden}
.wm-row{display:flex;justify-content:center;white-space:nowrap;overflow:hidden}
.wm-letter{font-family:'Noto Sans SC','Arial Black',sans-serif;font-size:clamp(40px,7vw,80px);font-weight:900;color:rgba(0,0,0,0.035);line-height:1;letter-spacing:.3em;transition:color .6s;user-select:none;flex-shrink:0}
.wm-row:nth-child(even) .wm-letter{margin-left:1.5em}
.preview-card:hover .wm-letter{color:rgba(0,0,0,0.07)}

.quote-content{position:relative;z-index:1;text-align:center}
.quote-text{font-size:36px;font-weight:700;color:#1a1a2e;line-height:1.8;letter-spacing:3px;margin-bottom:20px}
.quote-author{font-size:14px;color:#9a9ab4;letter-spacing:4px;margin-bottom:8px}
.quote-era{font-size:12px;color:#c0bdb5;letter-spacing:2px}
.flip-hint{position:absolute;bottom:24px;left:50%;transform:translateX(-50%);font-size:11px;color:#bbb;letter-spacing:3px;animation:pulse 2s ease-in-out infinite;z-index:2}
@keyframes pulse{0%,100%{opacity:.3}50%{opacity:.8}}
.module-row{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #000}
.module-cell{padding:32px 12px;text-align:center;cursor:pointer;min-height:80px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;border-right:1px solid #000;transition:all .35s}
.module-cell:last-child{border-right:none}
.module-cell::before{content:'';position:absolute;inset:0;background:#1a1a2e;opacity:0;transition:opacity .35s}
.module-cell:hover::before{opacity:1}
.module-cell:hover .module-label{color:#fff;transform:translateY(-2px);letter-spacing:5px}
.module-label{font-size:15px;font-weight:700;letter-spacing:3px;position:relative;z-index:1;color:#1a1a2e;transition:all .35s}
.hint{text-align:center;margin-top:20px;font-size:13px;color:#999;letter-spacing:1px}
</style>
</head>
<body>
<div>
<div class="preview-card">
<div class="quote-body">
<!-- MiMo风格水印：M I M O 交替排列 -->
<div class="wm-layer">
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span></div>
<div class="wm-row"><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span><span class="wm-letter">I</span><span class="wm-letter">M</span><span class="wm-letter">O</span><span class="wm-letter">M</span></div>
</div>
<!-- 名言内容 -->
<div class="quote-content">
<p class="quote-text">学而不思则罔<br>思而不学则殆</p>
<p class="quote-author">—— 孔子</p>
<p class="quote-era">春秋时期思想家</p>
</div>
<span class="flip-hint">鼠标悬停查看水印变化</span>
</div>
<div class="module-row">
<div class="module-cell"><span class="module-label">成绩</span></div>
<div class="module-cell"><span class="module-label">作业</span></div>
<div class="module-cell"><span class="module-label">考试</span></div>
<div class="module-cell"><span class="module-label">错题本</span></div>
<div class="module-cell"><span class="module-label">课表</span></div>
</div>
</div>
<p class="hint">↑ MiMo风格水印：大号粗体字母交替排列，hover时水印变清晰</p>
</div>
</body>
</html>"""

preview_path = r"D:\Dev\demo\quote_watermark_preview.html"
with open(preview_path, "w", encoding="utf-8") as f:
    f.write(preview)
print("Preview updated!")
