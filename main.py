from flask import Flask, request
import telebot
import os
import random
import time
import datetime
import json

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HISTORICO_SAUDACOES_PATH = "historico_saudacoes.json"

try:
    with open(HISTORICO_SAUDACOES_PATH, "r") as f:
        historico_saudacoes = json.load(f)
except:
    historico_saudacoes = {}

def atualizar_historico(saudacao, frase):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    if saudacao not in historico_saudacoes:
        historico_saudacoes[saudacao] = {}
    if hoje not in historico_saudacoes[saudacao]:
        historico_saudacoes[saudacao][hoje] = []
    historico_saudacoes[saudacao][hoje].append(frase)
    dias_validos = sorted(historico_saudacoes[saudacao].keys())[-4:]
    historico_saudacoes[saudacao] = {
        k: historico_saudacoes[saudacao][k] for k in dias_validos
    }
    with open(HISTORICO_SAUDACOES_PATH, "w") as f:
        json.dump(historico_saudacoes, f)

respostas = {
    "manha": [
        "Acordei com brilho nos olhos e deboche na alma.",
        "Bom dia? Só se for com café e close certo.",
        "De manhã eu brilho mais que a luz do sol."
    ],
    "tarde": [
        "Boa tarde, amor. Essa hora é perfeita pra causar.",
        "Tarde combina com meu carisma exagerado.",
        "Passei aqui pra te deixar mais interessante."
    ],
    "noite": [
        "Noite combina com mistério... e comigo.",
        "Vem comigo que essa noite promete deboche e sedução.",
        "Se tá escuro, é porque eu ainda não sorri."
    ],
    "madrugada": [
        "Se tá aqui essa hora, tá buscando mais que conversa...",
        "Madrugada é pra quem tem coragem e um pouco de loucura.",
        "No silêncio da madrugada, até meu charme faz barulho."
    ],
    "default": [
        "Você falando e eu aqui só analisando... com charme, claro.",
        "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
        "Fala baixo que minha paciência tá de salto alto."
    ]
}

respostas_automaticas = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
    "você me ama": ["Claro que sim, mas não espalha... vai causar ciúmes."],
    "me nota": ["Notada com sucesso. E com muito estilo, viu?"],
    "me manda beijo": ["Beijo enviado com glitter, batom e um pouco de saudade."],
    "você acredita em amor": ["Acredito sim, principalmente quando sou eu que recebo."]
}

boas_maneiras = {
    "bom dia": ["Bom dia, com deboche e purpurina." for _ in range(105)],
    "boa tarde": ["Boa tarde. Só porque acordei fabulosa agora à tarde." for _ in range(105)],
    "boa noite": ["Boa noite. Que seus sonhos sejam tão icônicos quanto eu." for _ in range(105)],
    "boa madrugada": ["Boa madrugada. Se está aqui essa hora, é porque tem bom gosto." for _ in range(105)]
}

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
    nome_usuario = message.from_user.first_name

    if not ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto or any(s in texto for s in boas_maneiras)):
        return

    time.sleep(random.uniform(13, 17))  # Reduzido para 15 segundos aprox.

    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            usadas = []
            for dia in historico_saudacoes.get(saudacao, {}):
                usadas.extend(historico_saudacoes[saudacao][dia])
            candidatas = [f for f in frases if f not in usadas]
            frase = random.choice(candidatas or frases)
            atualizar_historico(saudacao, frase)
            bot.send_message(message.chat.id, f"{nome_usuario}, {frase}")
            return

    for chave, lista_respostas in respostas_automaticas.items():
        if chave in texto:
            resposta = random.choice(lista_respostas)
            bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
            return

    reacoes = {
        "❤️": "Ui, me apaixonei agora. Brinca assim não!",
        "😍": "Esse emoji é pra mim, né? Porque eu mereço.",
        "😘": "Recebido com batom, blush e boa intenção.",
        "😂": "Rindo de nervoso ou de amor por mim?",
        "kkk": "Tá rindo de mim ou comigo, hein?",
        "😒": "Ih, tá de carinha feia? Vem cá que eu melhoro.",
        "😐": "Essa carinha sua é charme reprimido?"
    }
    for emoji, resposta in reacoes.items():
        if emoji in texto or emoji.replace("❤️", "❤") in texto:
            bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
            return

    if any(p in texto for p in ["linda", "inteligente", "gata", "maravilhosa"]):
        if "@samuel_gpm" not in texto and "madonna" not in texto:
            bot.send_message(message.chat.id, f"{nome_usuario}, elogiar as outras na minha frente? Coragem tua, viu? 😏")
            return

    hora = datetime.datetime.now().hour
    if 5 <= hora <= 11:
        estilo = "manha"
    elif 12 <= hora <= 17:
        estilo = "tarde"
    elif 18 <= hora <= 22:
        estilo = "noite"
    else:
        estilo = "madrugada"

    resposta_final = random.choice(respostas.get(estilo, respostas["default"]))
    bot.send_message(message.chat.id, f"{nome_usuario}, {resposta_final}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
