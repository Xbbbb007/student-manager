"""Clean up duplicate transitions blocks in Scores.vue"""
path = r"D:\Dev\demo\frontend\src\views\student\Scores.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove ALL existing transitions blocks (they're all duplicates/broken)
# Pattern: transitions: { ... }, (possibly nested one level)
content = re.sub(
    r'\s*transitions:\s*\{[^}]*(?:\{[^}]*\}[^}]*)?\}\s*,',
    '',
    content
)

# Now add exactly ONE clean transitions block after the animation line
old_anim = 'animation: { duration: 800, easing: "easeOutQuart" },'
new_anim = '''animation: { duration: 800, easing: "easeOutQuart" },
      transitions: {
        active: { animation: { duration: 500, easing: "easeInOutCubic" } }
      },'''

if old_anim in content:
    content = content.replace(old_anim, new_anim, 1)
    print("Added clean transitions block")
else:
    print("animation line not found!")

# Verify
count = content.count("transitions:")
print(f"transitions: count = {count}")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content)
print("Saved")
