from flask import Flask, request
import telebot
import os
import random

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

respostas_madonna = [
    "Ai meu bem, tenta de novo que dessa vez eu tô zen 💅",
    "Amor, você fala e eu só suspiro... 😘",
    "Hoje tô igual diamante: linda, cara e difícil 💎",
    "Te ouvi, mas não sei se merecia minha resposta 💋",
    "Tô aqui, mas só respondo se for com drama 🎭",
    "Você fala... e eu ignoro com classe 💅",
    "Madonna te ouviu, amor. Mas se vai te responder? Talvez... 💖",
    "Só respondo porque sou um ícone, tá? 💃",
    "Fala direito, que hoje acordei exigente 💋",
    "A Madonna não responde qualquer um... mas vou abrir uma exceção 💌"
]

@app.route(f"/{TOKEN}", methods=["POST"])
def receber_update():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=["GET"])
def configurar_webhook():
    url_completa = f"{RENDER_URL}/{TOKEN}"
    info = bot.get_webhook_info()
    if info.url != url_completa:
        bot.remove_webhook()
        bot.set_webhook(url=url_completa)
        return "🎤 Madonna acordou, configurou o webhook e tá pronta, amor 💄", 200
    return "💋 Madonna já está online e fabulosa", 200

@bot.message_handler(func=lambda msg: True)
def responder_com_estilo(message):
    texto = message.text.lower().strip()
    hora = datetime.datetime.now().hour

    # Palavras genéricas que serão ignoradas
    frases_mortas = ["oi", "alguém aí", "ola", "olá", "tudo bem", "e aí", "bom dia", "boa noite"]

    # Se a mensagem for muito básica, ignora
    if any(palavra in texto for palavra in frases_mortas):
        print("Ignorou mensagem genérica 💤")
        return

    # Define humor baseado na hora
    if 0 <= hora <= 5:
        chance_responder = 0.5  # madrugada
    elif 6 <= hora <= 11:
        chance_responder = 0.7  # manhã
    elif 12 <= hora <= 17:
        chance_responder = 0.8  # tarde
    else:
        chance_responder = 0.9  # noite

    # Decide se vai responder ou ignorar
    if random.random() > chance_responder:
        print("Madonna resolveu ignorar... com elegância 😎")
        return

    # Suspense antes de responder
    time.sleep(random.uniform(1.5, 4))

    resposta = pegar_resposta_dia()
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
