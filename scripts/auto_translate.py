#!/usr/bin/env python3
import os
import re
import urllib.request
import urllib.parse
import json
import time

# Google Translate destekli başlıca diller
LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
    'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian',
    'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
    'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German',
    'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian',
    'iw': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic',
    'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
    'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian',
    'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
    'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'ps': 'Pashto', 'fa': 'Persian',
    'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
    'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
    'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
    'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik',
    'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian',
    'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa',
    'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

POT_FILE = 'po/pardus-desktop-shortcut.pot'

def translate_text(text, target_lang):
    if not text: return ""
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={}&dt=t&q={}'.format(
            target_lang, urllib.parse.quote(text)
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        translated = "".join([i[0] for i in data[0] if i[0]])
        # Format stringlerini korumaya çalış ({} kısımları bozulursa diye basit bir kontrol)
        if "{}" in text and "{}" not in translated:
            translated = translated.replace("{}", "{}").replace("{ }", "{}") 
        return translated
    except Exception as e:
        print(f"Hata ({target_lang}): {e}")
        return text

def main():
    if not os.path.exists(POT_FILE):
        print(f"{POT_FILE} bulunamadı!")
        return

    with open(POT_FILE, 'r', encoding='utf-8') as f:
        pot_content = f.read()

    # msgid'leri bul
    msgids = re.findall(r'^msgid "(.*?)"', pot_content, re.MULTILINE)
    msgids = [m for m in msgids if m != ""] # Boş olan başlık msgid'sini atla

    print(f"Toplam {len(msgids)} çevrilecek metin bulundu.")

    # Hedef klasör
    os.makedirs('po', exist_ok=True)

    for lang_code, lang_name in LANGUAGES.items():
        po_path = f"po/{lang_code}.po"
        
        # Eğer zaten varsa (bizim yazdıklarımız) atla (TR hariç hepsini ezebiliriz ama güvenli gidelim)
        if os.path.exists(po_path) and lang_code in ['tr', 'de', 'es', 'fr', 'ru']:
            print(f"{lang_name} ({lang_code}) zaten mevcut, atlanıyor...")
            continue

        print(f"{lang_name} ({lang_code}) diline çevriliyor...")
        
        # Header oluştur
        po_content = f"""msgid ""
msgstr ""
"Project-Id-Version: pardus-desktop-shortcut\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-05-16 23:00+0300\\n"
"PO-Revision-Date: 2026-05-16 23:00+0300\\n"
"Last-Translator: Auto-Translator Script\\n"
"Language-Team: {lang_name}\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""
        for msgid in msgids:
            translated = translate_text(msgid, lang_code)
            # Kaçış karakterlerini düzenle
            translated = translated.replace('"', '\\"')
            
            po_content += f'msgid "{msgid}"\n'
            po_content += f'msgstr "{translated}"\n\n'
            time.sleep(0.1) # Rate limit'e takılmamak için hafif bekleme

        with open(po_path, 'w', encoding='utf-8') as f:
            f.write(po_content)

    print("Tüm çeviriler başarıyla tamamlandı!")

if __name__ == '__main__':
    main()
