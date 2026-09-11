import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from game.localization.en import TRANSLATIONS as EN_TRANSLATIONS
from game.localization.tr import TRANSLATIONS as TR_TRANSLATIONS
from game.localization.sq import TRANSLATIONS as SQ_TRANSLATIONS

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/game_db"
)

engine = create_engine(DATABASE_URL)


def seed_translations():
    print("🌍 Seeding translations...")

    # Combine all existing translations.
    translations = {
        "en": EN_TRANSLATIONS,
        "tr": TR_TRANSLATIONS,
        "sq": SQ_TRANSLATIONS,
    }

    # ---------------------------------------------------------
    # Macedonian
    # ---------------------------------------------------------
    #
    # Macedonian is currently the original/source language
    # in your game.
    #
    # Example:
    #
    # "Почни нов ден" -> "Почни нов ден"
    #
    # We create the MK dictionary from all source strings that
    # currently exist in your translation dictionaries.
    #
    # Because the dictionaries use Macedonian as the KEY,
    # we can use those keys as Macedonian translations.
    # ---------------------------------------------------------

    all_macedonian_texts = set()

    for language_dictionary in translations.values():
        all_macedonian_texts.update(language_dictionary.keys())

    translations["mk"] = {
        text: text
        for text in all_macedonian_texts
    }

    with engine.begin() as conn:

        # Make sure the table exists.
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    id SERIAL PRIMARY KEY,
                    language VARCHAR(10) NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    CONSTRAINT uq_translation
                        UNIQUE (language, source_text)
                );
                """
            )
        )

        # Clear old translations before inserting again.
        conn.execute(
            text("TRUNCATE TABLE translations RESTART IDENTITY;")
        )

        inserted = 0

        for language, dictionary in translations.items():

            print(
                f"  → Adding {language}: "
                f"{len(dictionary)} translations"
            )

            for source_text, translated_text in dictionary.items():

                conn.execute(
                    text(
                        """
                        INSERT INTO translations
                            (language, source_text, translated_text)
                        VALUES
                            (:language, :source_text, :translated_text)
                        ON CONFLICT (language, source_text)
                        DO UPDATE SET
                            translated_text = EXCLUDED.translated_text;
                        """
                    ),
                    {
                        "language": language,
                        "source_text": str(source_text),
                        "translated_text": str(translated_text),
                    },
                )

                inserted += 1

    print()
    print("✅ Translation seeding finished!")
    print(f"✅ Inserted/updated: {inserted} translations")


if __name__ == "__main__":
    seed_translations()