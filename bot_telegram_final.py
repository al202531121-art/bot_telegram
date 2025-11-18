import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# TOKEN del bot
TOKEN = "7522585575:AAGLemnCLfk7tirJPeVO_5UU9W8omVpeySQ"
bot = telebot.TeleBot(TOKEN)

# Estados y datos del usuario
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

# ------------------- CALLBACK DE BOTONES DEL MENÚ -------------------
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

    # ------------------- PEDIR SEXO -------------------
    if estado[chat_id] == "PEDIR_SEXO":
        if texto not in ["m", "f"]:
            bot.send_message(chat_id, "Por favor escribe M o F.")
            return
        sexo[chat_id] = texto
        estado[chat_id] = "PEDIR_EDAD"
        bot.send_message(chat_id, "Perfecto. Ahora dime tu edad:")
        return

    # ------------------- PEDIR EDAD -------------------
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

    # ------------------- PEDIR PESO (IMC) -------------------
    if estado[chat_id] == "PEDIR_PESO":
        try:
            peso[chat_id] = float(texto.replace(",", "."))
        except ValueError:
            bot.send_message(chat_id, "Ingresa solo números para tu peso.")
            return
        estado[chat_id] = "PEDIR_ALTURA"
        bot.send_message(chat_id, "Escribe tu altura en metros (ej. 1.70):")
        return

    # ------------------- PEDIR ALTURA (IMC) -------------------
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

    # ------------------- Volver al menú -------------------
    if data in ["obj_volver", "imc_volver"]:
        menu_principal(chat_id)
        return

    # ------------------- Dieta desde objetivo -------------------
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

    # ------------------- Dieta desde IMC -------------------
    if data == "imc_dieta":
        estado[chat_id] = "PEDIR_SEXO"
        bot.send_message(chat_id, "Para darte una dieta correcta, dime tu sexo:\nM = Hombre\nF = Mujer")

# ------------------- FUNCIONES DE IMC -------------------
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
    user_sexo = sexo.get(chat_id, "m")

    if obj == "subir peso":
        if user_edad < 30:
            texto = "🍽️ *Dieta joven para Subir de Peso*\n- Desayuno: Avena + plátano + crema de cacahuate\n- Comida: Pasta + pollo + aguacate\n- Cena: Tortilla + huevo + queso\n- Snacks: Nueces, yogurt, batido"
        else:
            texto = "🍽️ *Dieta adulta para Subir de Peso*\n- Desayuno: Avena + fruta\n- Comida: Pollo + arroz + verduras\n- Cena: Huevos + ensalada\n- Snacks: Yogurt, nueces"

    elif obj == "ganar masa muscular":
        if user_edad < 30:
            texto = "💪 *Dieta joven para Masa Muscular*\n- Desayuno: Huevos + avena\n- Comida: Carne magra + pasta\n- Cena: Atún + verduras\n- Snacks: Almendras, batido de proteína"
        else:
            texto = "💪 *Dieta adulta para Masa Muscular*\n- Desayuno: Huevos + avena\n- Comida: Pollo + arroz + verduras\n- Cena: Pescado + verduras\n- Snacks: Yogurt, frutos secos"

    else:  # bajar grasa
        if user_edad < 30:
            texto = "🔥 *Dieta joven para Bajar Grasa*\n- Desayuno: Yogurt + frutas\n- Comida: Pollo + verduras\n- Cena: Ensalada + atún\n- Snacks: Manzana, pepino, té verde"
        else:
            texto = "🔥 *Dieta adulta para Bajar Grasa*\n- Desayuno: Yogurt + avena\n- Comida: Pollo + verduras\n- Cena: Ensalada + huevo\n- Snacks: Frutas, té verde"

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)

# ------------------- MEJORAR SALUD -------------------
def mejorar_salud(chat_id):
    texto = "🌿 *Consejos para mejorar tu salud:*\n- Duerme 7-8 horas diarias\n- Mantente hidratado\n- Realiza caminatas o ejercicio ligero\n- Come frutas y verduras\n- Evita exceso de azúcar y grasa"
    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)

# ------------------- EJERCICIOS SUGERIDOS -------------------
def mostrar_ejercicios(chat_id):
    obj = objetivo.get(chat_id, "general")
    if obj == "subir peso":
        texto = "🏋️ *Ejercicios sugeridos para subir de peso:*\n- Sentadillas 3x12\n- Peso muerto 3x10\n- Press de banca 3x10\n- Remo con barra 3x12"
    elif obj == "ganar masa muscular":
        texto = "💪 *Ejercicios para ganar masa muscular:*\n- Press de banca 3x10\n- Dominadas 3x8\n- Curl de bíceps 3x12\n- Sentadillas 3x12"
    elif obj == "bajar grasa":
        texto = "🔥 *Ejercicios para bajar grasa:*\n- Cardio 30 min\n- Burpees 3x15\n- Saltos de tijera 3x20\n- Plancha 3x1 min"
    else:
        texto = "🤸 *Ejercicios generales:* Caminar, estiramientos, yoga, saltar la cuerda"
    bot.send_message(chat_id, texto, parse_mode="Markdown")
    menu_principal(chat_id)


# ==========================
#  WEBHOOK PARA RENDER
# ==========================

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "BOT DE TELEGRAM FUNCIONANDO"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

bot.remove_webhook()
bot.set_webhook(url=f"https://bot-telegram-7-mgsu.onrender.com/{TOKEN}")

print("BOT ENCENDIDO")
