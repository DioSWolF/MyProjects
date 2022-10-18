from pathlib import Path
from googletrans import Translator
import json
translator = Translator()
# "hi": "hindi"

transl_lang = "en"
write_lang = "hi"
path = Path(r"C:\Users\wolkm\Desktop\transl")
new_text = ""
for file in path.iterdir():
    with open(file, "r", encoding='utf-8') as json_file:
        text = json.load(json_file)
        for key, value in text.items():
            value = translator.translate(value, src = transl_lang, dest=write_lang).text
            text[key] = value
            new_text = text
            
    with open(file, "w", encoding='utf-8') as outfile:
            json.dump(new_text, outfile, ensure_ascii=False)

