import os
import subprocess
import sys
import time
import requests


API_URL = "http://127.0.0.1:8000"


def wait_for_api(timeout_seconds=180):
    url = f"{API_URL}/scenarios/"
    print("⏳ Чекам API-то да биде подготвено...")

    deadline = time.time() + timeout_seconds
    attempt = 0

    while time.time() < deadline:
        attempt += 1
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print("✅ API-то е подготвено!")
                return True
        except requests.RequestException:
            pass

        print(f"   API сè уште не е подготвено... ({attempt})")
        time.sleep(2)

    print(
        f"❌ API-то не успеа да се подготви во рок од {timeout_seconds} секунди."
    )
    return False



def seed_api():
    print("🌱 Го полнам Docker API-то со сценарија...")
    response = requests.post(f"{API_URL}/seed/", timeout=60)
    response.raise_for_status()
    print("✅ API-то е наполнето со сценарија!")


def main():
    print("🚀 Ги стартувам Docker контејнерите (База и API)...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    env= os.environ.copy()
    if wait_for_api():
        seed_api()
        env["GAME_MODE"]="online"
        print("🎮 Ја пуштам играта во онлајн режим...")
    else:
        env["GAME_MODE"]="offline"
        print("🎮 Ги стартувам играта во офлајн режим...")

    print("Затвори го прозорецот од играта кога ќе завршиш!")

    try:
        subprocess.run([sys.executable, "main_adventure.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Грешка при извршување на играта: {e}")
    finally:
        print("🛑 Играта е затворена.")
        print("🐳 Docker will stay running so you can inspect the DB.")
        print("When you're done, stop it manually with: docker compose down")


if __name__ == "__main__":
    main()