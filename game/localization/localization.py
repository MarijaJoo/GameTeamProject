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

OFFLINE_TRANSLATIONS = {
    "en": EN_TRANSLATIONS,
    "tr": TR_TRANSLATIONS,
    "sq": SQ_TRANSLATIONS,
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

        lang_dict = self.translations
        if (
            isinstance(self.translations, dict)
            and self.current_language in self.translations
            and isinstance(self.translations[self.current_language], dict)
        ):
            lang_dict = self.translations[self.current_language]

        translated = None
        if isinstance(lang_dict, dict):
            translated = lang_dict.get(text)
            if translated is None:
                translated = lang_dict.get(clean_text)

        if translated is None:
            fallback_dict = OFFLINE_TRANSLATIONS.get(
                self.current_language,
                {},
            )
            translated = fallback_dict.get(text)
            if translated is None:
                translated = fallback_dict.get(clean_text, text)

        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, IndexError, AttributeError):
                pass

        return translated


localization = Localization()


def t(text, **kwargs):
    return localization.translate(text, **kwargs)