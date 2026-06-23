"""Fix switchSubject to update datasets in place for smooth bar transitions"""
import re

path = r"D:\Dev\demo\frontend\src\views\student\Scores.vue"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace switchSubject - update data in place instead of replacing datasets
old_switch = re.compile(
    r'function switchSubject\(key: string\) \{.*?\n\s*mainChart\.update\(\);\s*\n\}',
    re.DOTALL
)

new_switch = """function switchSubject(key: string) {
  currentMainKey.value = key;
  if (!mainChart) return;

  const rankData =
    key === "total"
      ? { classRank: classRank.value, schoolRank: schoolRank.value }
      : {
          classRank: subjectClassRanks.value[key] || [],
          schoolRank: subjectSchoolRanks.value[key] || [],
        };

  mainChart.data.datasets[0].data = getBarData(key);
  mainChart.data.datasets[0].label = key === "total" ? "总分" : subjectNames[key];
  mainChart.data.datasets[1].data = rankData.classRank;
  mainChart.data.datasets[2].data = rankData.schoolRank;
  mainChart.options.scales!.bar!.max = getBarMax(key);
  mainChart.update();
}"""

content, n = old_switch.subn(new_switch, content, count=1)
print(f"switchSubject replaced: {n}")

# 2. Add transitions config to chart options (after animation line)
old_anim = 'animation: { duration: 800, easing: "easeOutQuart" },'
new_anim = """animation: { duration: 800, easing: "easeOutQuart" },
      transitions: {
        active: { animation: { duration: 500, easing: "easeInOutCubic" } }
      },"""
if old_anim in content:
    content = content.replace(old_anim, new_anim, 1)
    print("transitions config added")
else:
    # Try the version we added before
    old_anim2 = 'animation: { duration: 600, easing: "easeOutQuart" },'
    if old_anim2 in content:
        content = content.replace(old_anim2, new_anim, 1)
        print("transitions config added (variant)")
    else:
        print("animation line not found, skipping transitions")

with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content)

print("File saved")
