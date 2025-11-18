import telebot
from flask import Flask, request
import os

TOKEN = "7522585575:AAGLemnCLfk7tirJPeVO_5UU9W8omVpeySQ"
WEBHOOK_URL = "https://bot-telegram-9.onrender.com/webhook"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ------------------------
# Manejadores del bot
# ------------------------

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "¡BOT ENCENDIDO Y FUNCIONANDO EN RENDER! 🚀")

@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "Soy un bot funcionando con webhook en Render.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"Recibí tu mensaje:\n\n{message.text}")

# ------------------------
# RUTA DEL WEBHOOK
# ------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# ------------------------
# INICIO – SETEO DEL WEBHOOK
# ------------------------

@app.route("/", methods=["GET"])
def index():
    return "Bot funcionando correctamente!"

if __name__ == "__main__":

    # Render exige usar el puerto dinámico
    port = int(os.environ.get("PORT", 10000))

    # Eliminar webhook anterior
    bot.remove_webhook()

    # Configurar nuevamente el webhook
    bot.set_webhook(url=WEBHOOK_URL)

    print("WEBHOOK CONFIGURADO:", WEBHOOK_URL)
    print("BOT INICIADO EN RENDER")

    # Iniciar servidor Flask
    app.run(host="0.0.0.0", port=port)
