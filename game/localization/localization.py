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
    def __init__(self):
        self.current_language = "mk"

        self.translations = {
            "en": {
                **EN_TRANSLATIONS,
                **SCENARIO_EN_TRANSLATIONS,
            },
            "tr": TR_TRANSLATIONS,
            "sq": SQ_TRANSLATIONS,
        }

    def set_language(self, language):
        if language in LANGUAGES:
            self.current_language = language

    def get_language(self):
        return self.current_language

    def translate(self, text, **kwargs):
        if self.current_language == "mk":
            return text.format(**kwargs) if kwargs else text

        # translated = self.translations.get(
        #     self.current_language,
        #     {},
        # ).get(text, text)
        clean_text = str(text).strip()
        lang_dict = self.translations.get(self.current_language, {})

        translated = lang_dict.get(text, lang_dict.get(clean_text, text))

        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, IndexError):
                pass

        return translated


localization = Localization()


def t(text, **kwargs):
    return localization.translate(text, **kwargs)