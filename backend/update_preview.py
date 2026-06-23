"""Update preview HTML to match MiMo official structure"""
rows_html = ""
for i in range(20):
    offset = ' style="padding-left:3em"' if i % 2 == 1 else ""
    spans = "".join(f'<span class="wm-phrase">Do It.</span>' for _ in range(25))
    rows_html += f'<div class="wm-row"{offset}>{spans}</div>\n'

preview = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Do It. Watermark Preview</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700;900&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans SC',sans-serif;background:#f0f0f0;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:0 60px}}
.preview-card{{width:100%;background:#fff;overflow:hidden;position:relative}}
.quote-body{{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 0;position:relative;overflow:hidden}}
.wm-layer{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:space-between;pointer-events:none;z-index:0;overflow:hidden;padding:10px 0}}
.wm-row{{display:flex;justify-content:flex-start;white-space:nowrap;overflow:hidden}}
.wm-phrase{{font-family:'Noto Sans SC','Arial Black',sans-serif;font-size:clamp(50px,9vw,100px);font-weight:900;color:rgba(0,0,0,0.03);line-height:1;letter-spacing:.15em;transition:color .6s;user-select:none;flex-shrink:0;margin-right:.8em}}
.wm-row:nth-child(even){{padding-left:3em}}
.preview-card:hover .wm-phrase{{color:rgba(0,0,0,0.06)}}
.quote-content{{position:relative;z-index:1;text-align:center}}
.quote-text{{font-size:36px;font-weight:700;color:#1a1a2e;line-height:1.8;letter-spacing:3px;margin-bottom:20px}}
.quote-author{{font-size:14px;color:#9a9ab4;letter-spacing:4px;margin-bottom:8px}}
.quote-era{{font-size:12px;color:#c0bdb5;letter-spacing:2px}}
.flip-hint{{position:absolute;bottom:24px;left:50%;transform:translateX(-50%);font-size:11px;color:#bbb;letter-spacing:3px;animation:pulse 2s ease-in-out infinite;z-index:2}}
@keyframes pulse{{0%,100%{{opacity:.3}}50%{{opacity:.8}}}}
.module-row{{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #000}}
.module-cell{{padding:32px 12px;text-align:center;cursor:pointer;min-height:80px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;border-right:1px solid #000;transition:all .35s}}
.module-cell:last-child{{border-right:none}}
.module-cell::before{{content:'';position:absolute;inset:0;background:#1a1a2e;opacity:0;transition:opacity .35s}}
.module-cell:hover::before{{opacity:1}}
.module-cell:hover .module-label{{color:#fff;transform:translateY(-2px);letter-spacing:5px}}
.module-label{{font-size:15px;font-weight:700;letter-spacing:3px;position:relative;z-index:1;color:#1a1a2e;transition:all .35s}}
.hint{{text-align:center;margin-top:20px;font-size:13px;color:#999;letter-spacing:1px}}
</style>
</head>
<body>
<div style="width:100%">
<div class="preview-card">
<div class="quote-body">
<div class="wm-layer">
{rows_html}</div>
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
<p class="hint">Do It. MiMo风格水印 - 全宽铺满 - hover 时变清晰</p>
</div>
</body>
</html>"""

with open(r"D:\Dev\demo\quote_watermark_preview.html", "w", encoding="utf-8") as f:
    f.write(preview)
print("Preview updated!")
