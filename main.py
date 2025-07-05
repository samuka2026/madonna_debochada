from flask import Flask, request
import telebot
import openai
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Madonna responde tudo
@bot.message_handler(func=lambda message: True)
def responder_tudo(message):
    resposta = responder_com_madonna(message.text)
    bot.send_message(message.chat.id, resposta)

# Estilo debochado e romântico
def responder_com_madonna(texto):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resposta = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Responda com um estilo debochado e romântico, como se fosse a Madonna. Nunca fale que é um robô."},
            {"role": "user", "content": texto}
        ]
    )
    return resposta.choices[0].message.content.strip()

# Webhook (aqui a mágica acontece)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

# Inicializa o webhook ao iniciar o servidor
@app.route("/", methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    return "Madonna tá online, amor 💋"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
