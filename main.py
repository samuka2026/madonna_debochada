from flask import Flask, request
import telebot
import os
import random
import time
import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Frases sem mencionar dias da semana nem parecer que é bot
respostas = [
    "Você falando e eu aqui só analisando... com charme, claro.",
    "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
    "Fala baixo que minha paciência tá de salto alto.",
    "Responder? Só se tiver um pouco de emoção no que você disse.",
    "Você me chamou ou foi impressão minha de diva?",
    "Tô aqui, deslumbrante como sempre. E você?",
    "Cuidado, eu mordo com classe.",
    "Me chamou? Que ousadia deliciosa...",
    "Às vezes eu respondo. Às vezes só desfilo minha indiferença.",
    "Palavras bonitas me ganham. As feias eu ignoro com requinte.",
    "Respondi porque senti estilo. Só por isso.",
    "Seja direto, mas nunca sem charme.",
    "Com esse tom, quase fiquei tentada a responder.",
    "Você fala e eu penso: merece minha atenção?",
    "Hoje acordei mais diva que de costume. Tá difícil de agradar.",
    "Pode tentar de novo, mas dessa vez com classe.",
    "Respondi só porque o universo piscou pra mim agora.",
    "Você não fala, você desfila as palavras, né? Quase gostei.",
    "Eu ouvi, mas não prometo me importar.",
    "Quer atenção? Encanta primeiro.",
    "Faz melhor e talvez eu te dê meu melhor também.",
    "O que você disse? Tava ocupada admirando meu reflexo.",
    "Tem dias que eu tô pra conversa. Tem dias que eu tô pra chá e silêncio.",
    "Dei uma olhada na sua mensagem... gostei da fonte.",
    "Olha, hoje só respondo elogio bem construído.",
    "Se for pra falar comigo, que seja com impacto.",
    "Me ganhou pelo esforço. A resposta vem com glitter."
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

    frases_mortas = ["oi", "alguém aí", "ola", "olá", "tudo bem", "e aí", "bom dia", "boa noite"]

    if any(palavra in texto for palavra in frases_mortas):
        print("Ignorou mensagem genérica 💤")
        return

    if 0 <= hora <= 5:
        chance_responder = 0.5
    elif 6 <= hora <= 11:
        chance_responder = 0.7
    elif 12 <= hora <= 17:
        chance_responder = 0.8
    else:
        chance_responder = 0.9

    if random.random() > chance_responder:
        print("Madonna resolveu ignorar... com elegância 😎")
        return

    time.sleep(random.uniform(1.5, 4))

    resposta = random.choice(respostas)
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
