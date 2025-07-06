from flask import Flask, request
import telebot

TOKEN = "8044550839:AAGV0EieTKDcoymHZz6ftb-qwLCD02uBKJk"
RENDER_URL = "https://madonna-debochada.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    print("📨 Mensagem recebida:", update)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    expected_url = f"{RENDER_URL}/{TOKEN}"
    info = bot.get_webhook_info()
    if info.url != expected_url:
        bot.remove_webhook()
        bot.set_webhook(url=expected_url)
        print("✅ Webhook configurado")
    else:
        print("ℹ️ Webhook já configurado corretamente")
    return "Bot Madonna está online! 💄"

@bot.message_handler(func=lambda m: True)
def responder(message):
    print(f"👀 Mensagem de {message.chat.id}: {message.text}")
    bot.send_message(message.chat.id, "Madonna te ouviu, amor 💋")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
