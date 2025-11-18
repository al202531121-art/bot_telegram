import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# ------------------- TOKEN DEL BOT -------------------
TOKEN = "7522585575:AAGLemnCLfk7tirJPeVO_5UU9W8omVpeySQ"
bot = telebot.TeleBot(TOKEN)

# ------------------- SERVIDOR FLASK PARA RENDER -------------------
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot funcionando correctamente", 200

# ------------------- ESTADOS Y DATOS -------------------
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
    bot.answer_callback_query(call.id)
    opcion = call.data.split("_")[1]

    if opcion == "1":
        mejorar_salud(chat_id)
    elif opcion == "2":
        estado[chat_id] = "PEDIR_PESO"
        bot.send_message(chat_id, "Escribe tu peso en kg:")
    elif opcion == "3":
        estado[chat_id] = "PEDIR_SEXO"
        bot.send_message(chat_id, "Para darte una dieta correcta, dime tu sexo:\nM = Hombre\nF = Mujer")
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

    # ---------- PEDIR SEXO ----------
    if estado[chat_id] == "PEDIR_SEXO":
        if texto not in ["m", "f"]:
            bot.send_message(chat_id, "Por favor escribe M o F.")
            return
        sexo[chat_id] = texto
        estado[chat_id] = "PEDIR_EDAD"
        bot.send_message(chat_id, "Perfecto. Ahora dime tu edad:")
        return

    # ---------- PEDIR EDAD ----------
    if estado[chat_id] == "PEDIR_EDAD":
        if not texto.isdigit():
            bot.send_message(chat_id, "Escribe solo números, por favor.")
            return
        edad[chat_id] = int(texto)
        estado[chat_id] = "PEDIR_OBJETIVO"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Subir de peso", callback_data="obj_1"))
        markup.add(InlineKeyboardButton("Ganar masa muscular", callback_data="obj_2"))
        markup.add(InlineKeyboardButton("Bajar grasa", callback_data="obj_3"))
        markup.add(InlineKeyboardButton("Volver", callback_data="obj_volver"))

        bot.send_message(chat_id, "¿Cuál es tu objetivo?", reply_markup=markup)
        return

    # ---------- PEDIR PESO IMC ----------
    if estado[chat_id] == "PEDIR_PESO":
        try:
            peso[chat_id] = float(texto.replace(",", "."))
        except ValueError:
            bot.send_message(chat_id, "Ingresa solo números para tu peso.")
            return
        estado[chat_id] = "PEDIR_ALTURA"
        bot.send_message(chat_id, "Escribe tu altura en metros (ej. 1.70):")
        return

    # ---------- PEDIR ALTURA IMC ----------
    if estado[chat_id] == "PEDIR_ALTURA":
        try:
            altura[chat_id] = float(texto.replace(",", "."))
        except ValueError:
            bot.send_message(chat_id, "Ingresa un número válido para la altura.")
            return

        imc_val = peso[chat_id] / (altura[chat_id] ** 2)
        interpretacion = interpretar_imc(imc_val)

        bot.send_message(chat_id, f"Tu IMC es {imc_val:.2f} → {interpretacion}")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Sí, mostrar dieta", callback_data="imc_dieta"))
        markup.add(InlineKeyboardButton("No, volver al menú", callback_data="imc_volver"))
        bot.send_message(chat_id, "¿Quieres ver una dieta recomendada?", reply_markup=markup)
        return

# ------------------- CALLBACK OBJETIVOS -------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("obj_") or call.data.startswith("imc_"))
def callback_objetivo(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    data = call.data

    # Volver
    if data in ["obj_volver", "imc_volver"]:
        menu_principal(chat_id)
        return

    # Dietas por objetivo
    if data in ["obj_1", "obj_2", "obj_3"]:
        if data == "obj_1":
            objetivo[chat_id] = "subir peso"
        elif data == "obj_2":
            objetivo[chat_id] = "ganar masa muscular"
        elif data == "obj_3":
            objetivo[chat_id] = "bajar grasa"

        estado[chat_id] = "MOSTRAR_DIETA"
        mostrar_dieta(chat_id)
        return

    # Dieta desde IMC
    if data == "imc_dieta":
        estado[chat_id] = "PEDIR_SEXO"
        bot.send_message(chat_id, "Para darte una dieta correcta, dime tu sexo:\nM = Hombre\nF = Mujer")

# ------------------- FUNCIONES INICIALES -------------------
def interpretar_imc(imc):
    if imc < 18.5:
        return "Bajo peso"
    elif 18.5 <= imc < 25:
        return "Peso normal"
    elif 25 <= imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidad"

# ------------------- DIETAS -------------------
def mostrar_dieta(chat_id):
    obj = objetivo[chat_id]
    user_edad = edad.get(chat_id, 25)

    if obj == "subir peso":
        texto = "🍽️ *Dieta para Subir Peso*\n- Desayuno: Avena + plátano\n- Comida: Pasta + pollo\n- Cena: Huevos + tortilla\n- Snacks: Nueces y yogurt"
    elif obj == "ganar masa muscular":
        texto = "💪 *Dieta para Masa Muscular*\n- Desayuno: Huevos + avena\n- Comida: Carne o pollo + arroz\n- Cena: Pescado + verduras\n- Snacks: Almendras y proteína"
    else:
        texto = "🔥 *Dieta para Bajar Grasa*\n- Desayuno: Yogurt + frutas\n- Comida: Pollo + verduras\n- Cena: Ensalada + atún\n- Snacks: Té verde y fruta"

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)

# ------------------- EJERCICIOS -------------------
def mostrar_ejercicios(chat_id):
    obj = objetivo.get(chat_id, "general")

    if obj == "subir peso":
        texto = "🏋️ Ejercicios: Sentadilla, peso muerto, press banca"
    elif obj == "ganar masa muscular":
        texto = "💪 Ejercicios: Banca, dominadas, bíceps, sentadilla"
    elif obj == "bajar grasa":
        texto = "🔥 Ejercicios: Cardio, burpees, plancha, saltos"
    else:
        texto = "🤸 Ejercicios generales: Yoga, caminata, estiramientos"

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)

# ------------------- INICIAR BOT EN HILO -------------------
def iniciar_bot():
    print("BOT ENCENDIDO")
    bot.infinity_polling(skip_pending=True)

# ------------------- INICIO RENDER -------------------
if __name__ == "__main__":
    hilo = threading.Thread(target=iniciar_bot)
    hilo.daemon = True
    hilo.start()

    app.run(host="0.0.0.0", port=10000)
