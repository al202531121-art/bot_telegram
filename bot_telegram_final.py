import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

# ------------------- TOKEN -------------------
TOKEN = "7522585575:AAGLemnCLfk7tirJPeVO_5UU9W8omVpeySQ"
WEBHOOK_URL = "https://bot-telegram-13.onrender.com/webhook"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ------------------- ESTADOS -------------------
estado = {}
sexo = {}
edad = {}
objetivo = {}
peso = {}
altura = {}

# ------------------- MENÚ PRINCIPAL -------------------
def menu_principal(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Mejorar mi salud", callback_data="menu_1"))
    markup.add(InlineKeyboardButton("Calcular mi IMC", callback_data="menu_2"))
    markup.add(InlineKeyboardButton("Obtener una dieta recomendada", callback_data="menu_3"))
    markup.add(InlineKeyboardButton("Ver ejercicios sugeridos", callback_data="menu_4"))
    markup.add(InlineKeyboardButton("Salir", callback_data="menu_5"))

    bot.send_message(chat_id, "Bienvenido al chat de salud 🩺\nSelecciona una opción:", reply_markup=markup)
    estado[chat_id] = "MENU"

# ------------------- COMANDO START -------------------
@bot.message_handler(commands=["start"])
def start(message):
    menu_principal(message.chat.id)

# ------------------- CALLBACK DEL MENÚ -------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def callback_menu(call):
    chat_id = call.message.chat.id
    opcion = call.data.split("_")[1]
    bot.answer_callback_query(call.id)

    if opcion == "1":
        bot.send_message(chat_id, "✔️ Mantente hidratado\n✔️ Camina 30 min al día\n✔️ Duerme 7-8 horas\n✔️ Come más frutas y verduras")
        menu_principal(chat_id)

    elif opcion == "2":
        estado[chat_id] = "PEDIR_PESO"
        bot.send_message(chat_id, "Escribe tu peso en kg:")

    elif opcion == "3":
        estado[chat_id] = "PEDIR_SEXO"
        bot.send_message(chat_id, "Para tu dieta, dime tu sexo:\nM = Hombre\nF = Mujer")

    elif opcion == "4":
        mostrar_ejercicios(chat_id)

    elif opcion == "5":
        bot.send_message(chat_id, "¡Gracias por usar el bot! ❤️")

# ------------------- MANEJO DE MENSAJES -------------------
@bot.message_handler(func=lambda m: True)
def mensajes(message):
    chat_id = message.chat.id
    texto = message.text.lower()

    if chat_id not in estado:
        menu_principal(chat_id)
        return

    # ---------- SEXO ----------
    if estado[chat_id] == "PEDIR_SEXO":
        if texto not in ["m", "f"]:
            bot.send_message(chat_id, "Por favor escribe M o F.")
            return
        sexo[chat_id] = texto
        estado[chat_id] = "PEDIR_EDAD"
        bot.send_message(chat_id, "Perfecto. Ahora dime tu edad:")
        return

    # ---------- EDAD ----------
    if estado[chat_id] == "PEDIR_EDAD":
        if not texto.isdigit():
            bot.send_message(chat_id, "Escribe solo números.")
            return
        edad[chat_id] = int(texto)

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Subir de peso", callback_data="obj_1"))
        markup.add(InlineKeyboardButton("Ganar masa muscular", callback_data="obj_2"))
        markup.add(InlineKeyboardButton("Bajar grasa", callback_data="obj_3"))
        markup.add(InlineKeyboardButton("Volver", callback_data="obj_volver"))

        estado[chat_id] = "OBJETIVO"
        bot.send_message(chat_id, "¿Cuál es tu objetivo?", reply_markup=markup)
        return

    # ---------- PESO ----------
    if estado[chat_id] == "PEDIR_PESO":
        try:
            peso[chat_id] = float(texto.replace(",", "."))
        except:
            bot.send_message(chat_id, "Ingresa un número válido.")
            return
        estado[chat_id] = "PEDIR_ALTURA"
        bot.send_message(chat_id, "Ahora escribe tu altura en metros (ej: 1.70):")
        return

    # ---------- ALTURA ----------
    if estado[chat_id] == "PEDIR_ALTURA":
        try:
            altura[chat_id] = float(texto.replace(",", "."))
        except:
            bot.send_message(chat_id, "Ingresa un número válido para altura.")
            return

        imc_val = peso[chat_id] / (altura[chat_id] ** 2)
        interpretacion = interpretar_imc(imc_val)

        bot.send_message(chat_id, f"Tu IMC es {imc_val:.2f} → {interpretacion}")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Sí, mostrar dieta", callback_data="imc_dieta"))
        markup.add(InlineKeyboardButton("Volver al menú", callback_data="imc_volver"))
        bot.send_message(chat_id, "¿Deseas recomendación de dieta?", reply_markup=markup)
        return

# ------------------- CALL BACK OBJETIVOS -------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("obj_") or call.data.startswith("imc_"))
def callback_obj(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data in ["obj_volver", "imc_volver"]:
        menu_principal(chat_id)
        return

    if data in ["obj_1", "obj_2", "obj_3"]:
        objetivo[chat_id] = {
            "obj_1": "subir peso",
            "obj_2": "ganar masa muscular",
            "obj_3": "bajar grasa"
        }[data]
        mostrar_dieta(chat_id)
        return

    if data == "imc_dieta":
        estado[chat_id] = "PEDIR_SEXO"
        bot.send_message(chat_id, "Para dieta correcta dime tu sexo (M/F):")

# ------------------- FUNCIONES -------------------
def interpretar_imc(imc):
    if imc < 18.5: return "Bajo peso"
    if imc < 25: return "Peso normal"
    if imc < 30: return "Sobrepeso"
    return "Obesidad"

def mostrar_dieta(chat_id):
    obj = objetivo.get(chat_id, "general")

    if obj == "subir peso":
        texto = "🍽️ *Dieta para Subir Peso*\n- Avena + plátano\n- Pasta + pollo\n- Huevos + tortilla"
    elif obj == "ganar masa muscular":
        texto = "💪 *Dieta Masa Muscular*\n- Huevos + avena\n- Carne o pollo + arroz\n- Pescado + verduras"
    else:
        texto = "🔥 *Dieta Bajar Grasa*\n- Yogurt + frutas\n- Pollo + verduras\n- Ensalada + atún"

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)

def mostrar_ejercicios(chat_id):
    texto = "🏋️ Ejercicios recomendados:\n- Sentadillas\n- Peso muerto\n- Cardio\n- Dominadas"
    bot.send_message(chat_id, texto)
    menu_principal(chat_id)

# ------------------- WEBHOOK -------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot salud activo con Webhook!"

# ------------------- INICIO -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    info = bot.get_webhook_info()
    if info.url != WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        print("Webhook configurado:", WEBHOOK_URL)
    else:
        print("Webhook ya estaba configurado.")

    app.run(host="0.0.0.0", port=port)


