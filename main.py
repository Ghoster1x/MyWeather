from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from pyowm.commons.exceptions import NotFoundError
import telebot

# ──────────────────────
# 1. Настройка OWM
# ──────────────────────
CONFIG = get_default_config()
CONFIG["language"] = "ru"

OWM_API_KEY    = "e7fd4e77137bd38ebe40b9587a1a2759"
TELEGRAM_TOKEN = "8079059458:AAEinhJPzhn0U-AqqrmpqfAzfsue87064fg"

owm = OWM(OWM_API_KEY, CONFIG)
mgr = owm.weather_manager()

# ──────────────────────
# 2. Телеграм-бот
# ──────────────────────
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_city(chat_id):
    """Отправляет вопрос и регистрирует обработчик следующего ответа."""
    msg = bot.send_message(chat_id, "В каком городе вы хотите узнать погоду?")
    bot.register_next_step_handler(msg, send_weather)

@bot.message_handler(commands=["start"])
def start(message):
    ask_city(message.chat.id)

def send_weather(message):
    place = message.text.strip()

    try:
        observation = mgr.weather_at_place(place)
        w = observation.weather
        temp = w.temperature("celsius")["temp"]

        reply = (
            f"Сейчас в городе {place} — {w.detailed_status}.\n"
            f"Температура: {temp:.1f} °C.\n"
        )
        if temp < 10:
            reply += "На улице холодно, одевайтесь теплее!"
        elif temp < 20:
            reply += "Свежо, куртка не помешает."
        else:
            reply += "Тепло — можно одеться полегче."

        bot.send_message(message.chat.id, reply)

    except NotFoundError:
        bot.send_message(message.chat.id, f"Не удалось найти город «{place}».")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

    # снова спрашиваем город (даже после ошибки)
    ask_city(message.chat.id)

# ──────────────────────
# 3. Запуск
# ──────────────────────
if __name__ == "__main__":
    bot.infinity_polling()
