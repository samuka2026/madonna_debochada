from flask import Flask, request
import telebot
import openai
import os

# Carrega variáveis de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

# Inicializa Flask e bot do Telegram
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Função que gera respostas estilo Madonna
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

# Webhook do Telegram que recebe mensagens
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        json_data = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Erro no webhook: {e}")
    return "ok", 200

# Página inicial: ativa o webhook se necessário
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
            print("ℹ️ Webhook já estava correto.")
    except Exception as e:
        print(f"Erro ao configurar webhook: {e}")
    return "Madonna tá online, amor 💋"

# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
