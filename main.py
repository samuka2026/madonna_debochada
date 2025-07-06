from flask import Flask, request
import telebot
import openai
import os

# Tokens de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

# Inicializa bot e Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Estilo debochado e romântico
def responder_com_madonna(texto):
    openai.api_key = OPENAI_KEY
    resposta = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Responda com um estilo debochado e romântico, como se fosse a Madonna. Nunca fale que é um robô."
            },
            {"role": "user", "content": texto}
        ]
    )
    return resposta.choices[0].message.content.strip()

# Madonna responde tudo
@bot.message_handler(func=lambda message: True)
def responder_tudo(message):
    try:
        resposta = responder_com_madonna(message.text)
        bot.send_message(message.chat.id, resposta)
    except Exception as e:
        print(f"Erro ao responder mensagem: {e}")

# Webhook que recebe mensagens do Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Erro ao processar update: {e}")
    return "ok", 200

# Endpoint que configura o webhook (sem sobrecarregar o Telegram)
@app.route("/", methods=["GET"])
def index():
    try:
        info = bot.get_webhook_info()
        url_esperada = f"{RENDER_URL}/{TOKEN}"
        if info.url != url_esperada:
            bot.remove_webhook()
            bot.set_webhook(url=url_esperada)
            print("✅ Webhook atualizado com sucesso.")
        else:
            print("ℹ Webhook já está correto.")
    except Exception as e:
        print(f"Erro ao configurar webhook: {e}")
    return "Madonna tá online, amor 💋"

# Inicia servidor Flask
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
