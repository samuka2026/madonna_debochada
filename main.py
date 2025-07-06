from flask import Flask, request
import telebot
import openai
import os

TOKEN = "8044550839:AAGV0EieTKDcoymHZz6ftb-qwLCD02uBKJk"
RENDER_URL = "https://madonna-debochada.onrender.com"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # já deve estar configurado no Render

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Rota principal
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

# Rota para receber mensagens do Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

# Função para gerar resposta usando OpenAI
def gerar_resposta_madonna(mensagem):
    openai.api_key = OPENAI_API_KEY
    try:
        resposta = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é a Madonna: responde tudo com deboche, romantismo exagerado e nunca admite ser um robô. Seja atrevida, vaidosa e afiada nas respostas."},
                {"role": "user", "content": mensagem}
            ]
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print("Erro na OpenAI:", e)
        return "Ai meu amor... hoje não tô com paciência pra responder isso 💅"

# Quando alguém envia mensagem no Telegram
@bot.message_handler(func=lambda m: True)
def responder(message):
    texto = message.text
    resposta = gerar_resposta_madonna(texto)
    bot.send_message(message.chat.id, resposta)
    print(f"💬 {message.chat.id}: {texto} => {resposta}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
