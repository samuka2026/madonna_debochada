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

# As frases e respostas automáticas foram organizadas num arquivo externo para clareza.
# Como são muitas, você já tem a versão mais atualizada no seu histórico (e foram mantidas).

from frases_madonna import boas_maneiras, respostas_automaticas, respostas

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
    usuario = message.from_user
    mencao = f"[{usuario.first_name}](tg://user?id={usuario.id})"

    if not ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto or any(s in texto for s in boas_maneiras)):
        return

    time.sleep(random.uniform(14, 16))

    # Resposta para saudações com histórico
    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            usadas = []
            for dia in historico_saudacoes.get(saudacao, {}):
                usadas.extend(historico_saudacoes[saudacao][dia])
            candidatas = [f for f in frases if f not in usadas]
            frase = random.choice(candidatas or frases)
            atualizar_historico(saudacao, frase)
            bot.send_message(message.chat.id, f"{mencao}, {frase}", parse_mode="Markdown")
            return

    # Resposta automática com gatilhos parciais
    for chave, lista_respostas in respostas_automaticas.items():
        palavras_chave = chave.lower().split()
        if all(p in texto for p in palavras_chave):
            resposta = random.choice(lista_respostas)
            bot.send_message(message.chat.id, f"{mencao}, {resposta}", parse_mode="Markdown")
            return

    # Reações por emoji
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
        if emoji in texto or emoji.replace("❤️", "❤") in texto or emoji in texto:
            bot.send_message(message.chat.id, f"{mencao}, {resposta}", parse_mode="Markdown")
            return

    # Comportamento ciumenta
    if any(p in texto for p in ["linda", "inteligente", "gata", "maravilhosa"]):
        if "@samuel_gpm" not in texto and "madonna" not in texto:
            bot.send_message(message.chat.id, f"{mencao}, elogiar as outras na minha frente? Coragem tua, viu? 😏", parse_mode="Markdown")
            return

    # Estilo por horário
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
    bot.send_message(message.chat.id, f"{mencao}, {resposta_final}", parse_mode="Markdown")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
