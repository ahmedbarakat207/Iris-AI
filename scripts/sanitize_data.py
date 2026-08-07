import os
import re
import glob

def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # استبدال روابط الخطوط الخاطئة
        content = content.replace("https://fonts.googleapis.com/css2family", "https://fonts.googleapis.com/css2?family")

        # إضافة الوسم المناسب (Static أو Dynamic)
        mode = "[Mode: Dynamic App]\n" if re.search(r'\b(fetch|axios|XMLHttpRequest)\b', content) else "[Mode: Static UI]\n"
        
        # إذا لم يكن الوسم موجوداً مسبقاً، قم بإضافته في البداية
        if not content.startswith("[Mode:"):
            content = mode + content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

if __name__ == "__main__":
    count = 0
    # المرور على كل الملفات النصية
    for root_dir in ["training", "raw_data"]:
        for file in glob.glob(f"{root_dir}/**/*.md", recursive=True):
            if process_file(file):
                count += 1
    print(f"تم تنظيف وتحديث {count} ملف بنجاح!")
