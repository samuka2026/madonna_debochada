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
def responder_com_deboche(message):
    resposta = random.choice(respostas_madonna)
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
