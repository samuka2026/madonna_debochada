from flask import Flask, request
import telebot
import os

TOKEN = "8044550839:AAGV0EieTKDcoymHZz6ftb-qwLCD02uBKJk"  # já direto no código
RENDER_URL = "https://madonna-debochada.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        json_data = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        print(f"📨 Mensagem recebida: {update}")
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    try:
        url_esperada = f"{RENDER_URL}/{TOKEN}"
        info = bot.get_webhook_info()
        if info.url != url_esperada:
            bot.remove_webhook()
            bot.set_webhook(url=url_esperada)
            print("✅ Webhook atualizado.")
        else:
            print("ℹ️ Webhook já está correto.")
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
    return "Madonna simples tá online 💄"

@bot.message_handler(func=lambda message: True)
def responder_simples(message):
    print(f"👀 Recebido: {message.text} de {message.chat.id}")
    try:
        bot.send_message(message.chat.id, "Madonna te ouviu, bebê 💋")
    except Exception as e:
        print(f"❌ Erro ao responder: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
