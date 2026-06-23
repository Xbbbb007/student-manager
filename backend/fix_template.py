"""Fix template to use individual spans like MiMo official"""
import re

path = r"D:\Dev\demo\frontend\src\views\student\Learn.vue"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Find and replace the current template
old = '<span class="wm-phrase">{{ row.join(\'\') }}</span>'
new = '<span class="wm-phrase" v-for="(ch, ci) in row" :key="ci">{{ ch }}</span>'
if old in c:
    c = c.replace(old, new, 1)
    print("Template fixed: individual spans")
else:
    print("Pattern not found, checking current state...")
    idx = c.find('wm-phrase')
    if idx >= 0:
        print(repr(c[idx-20:idx+100]))

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(c)
print("Done!")
