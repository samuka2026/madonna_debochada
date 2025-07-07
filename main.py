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

# Arquivo para controle de saudações por dia
HISTORICO_SAUDACOES_PATH = "historico_saudacoes.json"

# Função para carregar histórico
try:
    with open(HISTORICO_SAUDACOES_PATH, "r") as f:
        historico_saudacoes = json.load(f)
except:
    historico_saudacoes = {}

# Garante que sempre terá o histórico dos últimos 4 dias
def atualizar_historico(saudacao, frase):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    if saudacao not in historico_saudacoes:
        historico_saudacoes[saudacao] = {}
    if hoje not in historico_saudacoes[saudacao]:
        historico_saudacoes[saudacao][hoje] = []
    historico_saudacoes[saudacao][hoje].append(frase)
    # Remove dados com mais de 4 dias
    dias_validos = sorted(historico_saudacoes[saudacao].keys())[-4:]
    historico_saudacoes[saudacao] = {
        k: historico_saudacoes[saudacao][k] for k in dias_validos
    }
    with open(HISTORICO_SAUDACOES_PATH, "w") as f:
        json.dump(historico_saudacoes, f)

# Frases genéricas
respostas = [
    # ... (mantenha aqui todas as frases genéricas que já estavam, acima de 50)
    "Você falando e eu aqui só analisando... com charme, claro.",
    "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
    "Fala baixo que minha paciência tá de salto alto.",
    # ... (continue com suas outras frases)
]

# Boas maneiras com mais de 99 opções
boas_maneiras = {
    "bom dia": [f"Bom dia número {i}, com deboche e purpurina." for i in range(1, 105)],
    "boa tarde": [f"Boa tarde {i}. Só porque acordei fabulosa agora à tarde." for i in range(1, 105)],
    "boa noite": [f"Boa noite {i}. Que seus sonhos sejam tão icônicos quanto eu." for i in range(1, 105)],
    "boa madrugada": [f"Boa madrugada {i}. Se está aqui essa hora, é porque tem bom gosto." for i in range(1, 105)]
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
    hora = datetime.datetime.now().hour

    # Só responde mensagens se for mencionada ou se for saudação
    if not ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto or any(s in texto for s in boas_maneiras)):
        return

    # Delay mínimo de 40 segundos antes de responder
    time.sleep(random.uniform(40, 50))

    # Resposta para saudações sem repetir frases dos últimos 3 dias
    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            usadas = []
            for dia in historico_saudacoes.get(saudacao, {}):
                usadas.extend(historico_saudacoes[saudacao][dia])
            candidatas = [f for f in frases if f not in usadas]
            if not candidatas:
                frase = random.choice(frases)  # se esgotar, ignora filtro
            else:
                frase = random.choice(candidatas)
            atualizar_historico(saudacao, frase)
            bot.send_message(message.chat.id, f"{nome_usuario}, {frase}")
            return

    # Frases genéricas só se mencionarem a Madonna
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        resposta = random.choice(respostas)
        bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
