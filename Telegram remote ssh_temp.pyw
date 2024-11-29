import telebot
import subprocess
import sys
import re

# Вставте свій токен бота
TOKEN = "token"
bot = telebot.TeleBot(TOKEN)

# Перевірте список користувачів, які можуть користуватися ботом
ALLOWED_USERS = [list of ids]  # Вставте свої ID користувачів


def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS


def log_to_console(user_id, command, output):
    """Логування команд і результатів у консоль."""
    print(f"\n[USER {user_id}] написав: {command}")
    print(f"[CONSOLE OUTPUT]:\n{output}\n")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Привітання та інформація про бота."""
    bot.reply_to(
        message,
        "Привіт! Я бот для виконання віддалених команд у Windows через cmd.exe. "
        "Просто введіть команду, і я її виконаю.\n"
        "Доступні команди:\n"
        "- /suicide: зупиняє роботу бота\n"
        "Щоб запустити якусь команду, просто напишіть мені. Для прикладу, спробуйте: whoami"
    )


@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def execute_plain_command(message):
    """Виконання тексту як команди."""
    user_id = message.from_user.id
    if not is_user_allowed(user_id):
        bot.reply_to(message, "Вам не дозволено використовувати цього бота.")
        return

    command = message.text.strip()
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", command],
            text=True,
            capture_output=True,
            timeout=10
        )
        output = result.stdout or result.stderr
        bot.reply_to(message, f"Результат:\n{output}")
        log_to_console(user_id, command, output)  # Лог у консоль
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "Час виконання команди перевищено.")
        log_to_console(user_id, command, "Час виконання команди перевищено.")  # Лог у консоль
    except Exception as e:
        bot.reply_to(message, f"Помилка виконання команди: {e}")
        log_to_console(user_id, command, f"Помилка: {e}")  # Лог у консоль

@bot.message_handler(commands=['suicide'])
def shutdown_bot(message):
    """Завершення роботи бота."""
    user_id = message.from_user.id
    if not is_user_allowed(user_id):
        bot.reply_to(message, "Вам не дозволено зупиняти цього бота.")
        return

    bot.reply_to(message, "Бот зупиняється... Прощавайте! 👋")
    print(f"[USER {user_id}] Викликав команду /suicide. Бот зупиняється.")
    bot.stop_polling()  # Зупиняє прийом нових повідомлень
    sys.exit(0)  # Завершує програму


@bot.message_handler(func=lambda m: True)
def default_response(message):
    """Відповідь на невідомі команди."""
    bot.reply_to(message, "Команда не розпізнана. Введіть текст без '/' для виконання або використовуйте /help для списку команд.")


if __name__ == "__main__":
    print("Бот запущено...")
    bot.infinity_polling()