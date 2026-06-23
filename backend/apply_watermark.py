"""Add watermark to Learn.vue + create HTML preview"""
import re

# ===== Part 1: Modify Learn.vue =====
path = r"D:\Dev\demo\frontend\src\views\student\Learn.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Add watermark HTML inside quote-cell, before flip-card
old1 = '<div class="quote-cell">\r\n          <div'
new1 = '''<div class="quote-cell">
          <div class="watermark-layer">
            <div class="wm-cell" v-for="w in watermarks" :key="w">
              <span class="wm-text">{{ w }}</span>
            </div>
          </div>
          <div'''
if old1 in content:
    content = content.replace(old1, new1, 1)
    print("Step 1: watermark HTML added")
else:
    print("Step 1: pattern not found!")

# Step 2: Add watermarks data after quotes array close
old2 = '  { text: "教育不是填满一桶水<br>而是点燃一把火", author: "叶芝", era: "爱尔兰诗人", desc: "威廉\u00b7巴特勒\u00b7叶芝（1865\u20141939），爱尔兰诗人、剧作家，1923年诺贝尔文学奖得主。" },\n]'
new2 = old2 + '\n\nconst watermarks = [\n  \'学而不思则罔\', \'思而不学则殆\', \'温故而知新\', \'可以为师矣\',\n  \'三人行必有我师\', \'知之为知之\', \'不知为不知\', \'是知也\',\n  \'敏而好学\', \'不耻下问\', \'学而时习之\', \'不亦说乎\',\n]'
if "const watermarks" not in content:
    content = content.replace(old2, new2, 1)
    print("Step 2: watermarks data added")
else:
    print("Step 2: already exists")

# Step 3: Add CSS before .flip-card { in style section
wm_css = """/* 水印网格层 */
.watermark-layer {
  position: absolute; inset: 0; pointer-events: none;
  display: grid; grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr); z-index: 0;
}
.wm-cell {
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  pointer-events: auto;
}
.wm-cell .wm-text {
  position: absolute;
  font-family: "Noto Serif SC", serif;
  font-size: 13px; font-weight: 600;
  color: rgba(180, 160, 140, 0.05);
  white-space: nowrap; transform: rotate(-25deg);
  letter-spacing: 6px;
  transition: color 0.5s ease, transform 0.5s ease;
  user-select: none;
}
.wm-cell:hover .wm-text {
  color: rgba(160, 130, 100, 0.22);
  transform: rotate(-25deg) scale(1.05);
}
.quote-cell:hover .wm-text {
  color: rgba(180, 160, 140, 0.09);
}

"""

# Find .flip-card { only inside <style scoped>
style_idx = content.rfind("<style scoped>")
if style_idx > 0:
    style_section = content[style_idx:]
    if ".watermark-layer" not in style_section:
        # Insert before first .flip-card { in style section
        flip_idx = content.find(".flip-card {", style_idx)
        if flip_idx > 0:
            content = content[:flip_idx] + wm_css + content[flip_idx:]
            print("Step 3: watermark CSS added")
        else:
            print("Step 3: .flip-card not found in style")
    else:
        print("Step 3: already exists")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content)
print("Learn.vue saved!")

# ===== Part 2: Create HTML preview =====
preview_html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>名人名言 - 水印效果预览</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Noto Sans SC',sans-serif;background:#f0f0f0;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:40px}
.preview-card{width:900px;max-width:100%;background:#fff;overflow:hidden;position:relative}
.quote-body{min-height:420px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 40px;position:relative;overflow:hidden}
.wm-layer{position:absolute;inset:0;pointer-events:none;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(3,1fr);z-index:0}
.wm-cell{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;pointer-events:auto}
.wm-cell::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(-45deg,transparent,transparent 28px,rgba(180,160,140,0.04) 28px,rgba(180,160,140,0.04) 29px);opacity:0;transition:opacity .5s}
.wm-cell:hover::before{opacity:1}
.wm-text{position:absolute;font-family:'Noto Serif SC',serif;font-size:13px;font-weight:600;color:rgba(180,160,140,0.05);white-space:nowrap;transform:rotate(-25deg);letter-spacing:6px;transition:color .5s,transform .5s;user-select:none}
.wm-cell:hover .wm-text{color:rgba(160,130,100,0.22);transform:rotate(-25deg) scale(1.05)}
.preview-card:hover .wm-text{color:rgba(180,160,140,0.09)}
.quote-content{position:relative;z-index:1;text-align:center}
.quote-text{font-family:'Noto Serif SC',serif;font-size:32px;font-weight:700;color:#1a1a2e;line-height:1.8;letter-spacing:3px;margin-bottom:20px}
.quote-author{font-size:14px;color:#9a9ab4;letter-spacing:4px;margin-bottom:8px}
.quote-era{font-size:12px;color:#c0bdb5;letter-spacing:2px}
.flip-hint{position:absolute;bottom:24px;left:50%;transform:translateX(-50%);font-size:11px;color:#bbb;letter-spacing:3px;cursor:pointer;animation:pulse 2s ease-in-out infinite;z-index:2}
@keyframes pulse{0%,100%{opacity:.3}50%{opacity:.8}}
.module-row{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #000}
.module-cell{padding:32px 12px;text-align:center;cursor:pointer;min-height:80px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;border-right:1px solid #000;transition:all .35s cubic-bezier(.4,0,.2,1)}
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
<div class="wm-layer">
<div class="wm-cell"><span class="wm-text">学而不思则罔</span></div>
<div class="wm-cell"><span class="wm-text">思而不学则殆</span></div>
<div class="wm-cell"><span class="wm-text">温故而知新</span></div>
<div class="wm-cell"><span class="wm-text">可以为师矣</span></div>
<div class="wm-cell"><span class="wm-text">三人行必有我师</span></div>
<div class="wm-cell"><span class="wm-text">知之为知之</span></div>
<div class="wm-cell"><span class="wm-text">不知为不知</span></div>
<div class="wm-cell"><span class="wm-text">是知也</span></div>
<div class="wm-cell"><span class="wm-text">敏而好学</span></div>
<div class="wm-cell"><span class="wm-text">不耻下问</span></div>
<div class="wm-cell"><span class="wm-text">学而时习之</span></div>
<div class="wm-cell"><span class="wm-text">不亦说乎</span></div>
</div>
<div class="quote-content">
<p class="quote-text">学而不思则罔<br>思而不学则殆</p>
<p class="quote-author">—— 孔子</p>
<p class="quote-era">春秋时期思想家</p>
</div>
<span class="flip-hint">悬停水印区域查看效果</span>
</div>
<div class="module-row">
<div class="module-cell"><span class="module-label">成绩</span></div>
<div class="module-cell"><span class="module-label">作业</span></div>
<div class="module-cell"><span class="module-label">考试</span></div>
<div class="module-cell"><span class="module-label">错题本</span></div>
<div class="module-cell"><span class="module-label">课表</span></div>
</div>
</div>
<p class="hint">↑ 将鼠标悬停在名言区域的不同位置，水印会逐格变清晰</p>
</div>
</body>
</html>"""

preview_path = r"D:\Dev\demo\quote_watermark_preview.html"
with open(preview_path, "w", encoding="utf-8") as f:
    f.write(preview_html)
print(f"Preview saved to {preview_path}")
