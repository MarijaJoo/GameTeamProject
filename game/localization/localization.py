from game.localization.en import TRANSLATIONS as EN_TRANSLATIONS
from game.localization.tr import TRANSLATIONS as TR_TRANSLATIONS
from game.localization.sq import TRANSLATIONS as SQ_TRANSLATIONS
from game.localization.scenario_en import TRANSLATIONS as SCENARIO_EN_TRANSLATIONS

LANGUAGES = {
    "mk": "Македонски",
    "en": "English",
    "tr": "Türkçe",
    "sq": "Shqip",
}

class Localization:
    def __init__(self, translations=None):
        self.current_language = "mk"
        self.translations = translations or {}

    def set_translations(self, translations):
        self.translations = translations or {}

    def set_language(self, language):
        if language in LANGUAGES:
            self.current_language = language

    def get_language(self):
        return self.current_language

    def translate(self, text, **kwargs):
        if self.current_language == "mk":
            return text.format(**kwargs) if kwargs else text

        clean_text = str(text).strip()
        translated = self.translations.get(text, self.translations.get(clean_text, text))

        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, IndexError):
                pass

        return translated

localization = Localization()

def t(text, **kwargs):
    return localization.translate(text, **kwargs)