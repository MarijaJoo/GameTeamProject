import subprocess
import time
import sys

def main():
    print("🚀 Ги стартувам Docker контејнерите (База и API)...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    
    print("⏳ Чекам 5 секунди за API-то да биде подготвено...")
    time.sleep(5)
    
    print("🎮 Ја пуштам играта... (Затвори го прозорецот од играта кога ќе завршиш)")
    try:
        # Ја пушта играта преку тековниот Python и чека додека корисникот не ја затвори
        subprocess.run([sys.executable, "main_adventure.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Грешка при извршување на играта: {e}")
    finally:
        print("🛑 Играта е затворена. Го гасам Docker...")
        subprocess.run(["docker", "compose", "down"], check=True)
        print("✅ Се е успешно изгасено!")

if __name__ == "__main__":
    main()