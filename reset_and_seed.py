import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Вчитување на конекцијата од .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/game_db")

engine = create_engine(DATABASE_URL)


def run_seed():
    seed_file_path = os.path.join(os.path.dirname(__file__), "seed_data.sql")

    if not os.path.exists(seed_file_path):
        print("❌ Грешка: Не го гледам 'seed_data.sql' во овој фолдер!")
        return

    print("🔄 1. Ги чистиме претходните табели од базата...")

    # engine.begin() автоматски прави commit на крајот
    with engine.begin() as conn:
        # Ги празниме табелите за да нема стари конфликти
        conn.execute(text("TRUNCATE TABLE player_progress CASCADE;"))
        conn.execute(text("TRUNCATE TABLE actions CASCADE;"))
        conn.execute(text("TRUNCATE TABLE scenarios CASCADE;"))
        print("🧹 Базата е исчистена.")

        print("🌱 2. Ги вчитуваме новите прашања и поени од seed_data.sql...")
        with open(seed_file_path, "r", encoding="utf-8") as file:
            # Го делиме SQL фајлот на поединечни наредби за да не заглави Postgres
            sql_commands = file.read().split(";")

            for command in sql_commands:
                command = command.strip()
                if command:  # Скокаме празни линии и коментари
                    try:
                        conn.execute(text(command))
                    except Exception as e:
                        print(f"⚠️ Проблем со оваа наредба: {command[:50]}...")
                        print(f"Грешка: {e}")
                        return

    print("\n🎉 УСПЕШНО! Базата е ресетирана и во неа се запишани новите поени (+10 и -5)!")


if __name__ == "__main__":
    run_seed()