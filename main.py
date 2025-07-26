# ✅ BOT MADONNA REFORMULADA - main.py
# Versão especial com listas .json na raiz, saudacões por gênero e horário, elogios, desejos para Apollo,
# defesa automática do Apollo, submissão ao dono quando mencionada, e estrutura organizada e leve. 💅💖

from flask import Flask, request
import telebot
import os
import random
import time
import json
import threading
from datetime import datetime, timedelta

# ✅ CONFIGURAÇÕES DO GRUPO
GRUPO_ID = -1002363575666              # Substitua pelo ID do seu grupo
DONO_ID = 1481389775                   # ID do dono da Madonna (submissão)
TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ Função para carregar arquivos .json da raiz do projeto

def carregar_lista(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# ✅ Listas .json da raiz do projeto
bom_dia_mulher = carregar_lista("bom_dia_mulher.json")
bom_dia_homem = carregar_lista("bom_dia_homem.json")
boa_tarde_mulher = carregar_lista("boa_tarde_mulher.json")
boa_tarde_homem = carregar_lista("boa_tarde_homem.json")
boa_noite_entrada_mulher = carregar_lista("boa_noite_entrada_mulher.json")
boa_noite_entrada_homem = carregar_lista("boa_noite_entrada_homem.json")
boa_noite_dormir_mulher = carregar_lista("boa_noite_dormir_mulher.json")
boa_noite_dormir_homem = carregar_lista("boa_noite_dormir_homem.json")
elogios_mulher = carregar_lista("elogios_mulher.json")
elogios_homem = carregar_lista("elogios_homem.json")
desejos_apollo = carregar_lista("desejos_apollo.json")
men_m = carregar_lista("menções_mulher.json")
men_h = carregar_lista("menções_homem.json")
frases_dono = carregar_lista("frases_dono.json")
defesa_apollo = carregar_lista("defesa_apollo.json")
usuarios_mulheres = carregar_lista("usuarios_mulheres.json")
usuarios_homens = carregar_lista("usuarios_homens.json")

# ✅ Detecta se é mulher com base no @ ou nome

def e_mulher(user):
    username = (user.username or "").lower()
    if username in [u.lower() for u in usuarios_mulheres]:
        return True
    elif username in [u.lower() for u in usuarios_homens]:
        return False
    nome = (user.first_name or "").lower()
    return nome[-1] in ["a", "e"]

# ✅ Controle de envio 1x por hora para cada usuário
ultimos_envios = {}

# ✅ Handler principal
@bot.message_handler(func=lambda msg: True)
def responder(msg):
    if msg.chat.id != GRUPO_ID:
        return

    texto = msg.text.lower()
    user_id = msg.from_user.id
    nome = msg.from_user.first_name or msg.from_user.username or "Amor"
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 👑 Submissão ao dono (apenas se mencionarem "madonna" ou @)
    if user_id == DONO_ID and frases_dono and ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto):
        bot.send_message(GRUPO_ID, random.choice(frases_dono), reply_to_message_id=msg.message_id)
        return

    # 💘 Madonna em defesa do Apollo
    if "apollo" in texto or "@apolo_8bp_bot" in texto:
        if defesa_apollo:
            bot.send_message(GRUPO_ID, random.choice(defesa_apollo), reply_to_message_id=msg.message_id)
        return

    # 💬 Mencionaram a Madonna
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        if mulher and men_m:
            bot.send_message(GRUPO_ID, random.choice(men_m), reply_to_message_id=msg.message_id)
        elif not mulher and men_h:
            bot.send_message(GRUPO_ID, random.choice(men_h), reply_to_message_id=msg.message_id)
        return

    # 🌞 Bom dia
    if "bom dia" in texto:
        frase = random.choice(bom_dia_mulher if mulher else bom_dia_homem)
        bot.send_message(GRUPO_ID, frase, reply_to_message_id=msg.message_id)
        return

    # ☀️ Boa tarde
    if "boa tarde" in texto:
        frase = random.choice(boa_tarde_mulher if mulher else boa_tarde_homem)
        bot.send_message(GRUPO_ID, frase, reply_to_message_id=msg.message_id)
        return

    # 🌙 Boa noite ou boa madrugada
    if "boa noite" in texto or "boa madrugada" in texto:
        if agora.hour < 21:
            frase = random.choice(boa_noite_entrada_mulher if mulher else boa_noite_entrada_homem)
        else:
            frase = random.choice(boa_noite_dormir_mulher if mulher else boa_noite_dormir_homem)
        bot.send_message(GRUPO_ID, frase, reply_to_message_id=msg.message_id)
        return

    # 💖 Elogios ou desejos automáticos (1 por hora)
    chave = f"{user_id}_{'mulher' if mulher else 'homem'}"
    if chave not in ultimos_envios or (agora - ultimos_envios[chave]) > timedelta(hours=1):
        ultimos_envios[chave] = agora
        if mulher and elogios_mulher:
            bot.send_message(GRUPO_ID, random.choice(elogios_mulher), reply_to_message_id=msg.message_id)
        elif not mulher and elogios_homem:
            bot.send_message(GRUPO_ID, random.choice(elogios_homem), reply_to_message_id=msg.message_id)
        elif desejos_apollo:
            bot.send_message(GRUPO_ID, random.choice(desejos_apollo), reply_to_message_id=msg.message_id)

# 🔁 ROTA FLASK PARA WEBHOOK (Render)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def home():
    url = f"{RENDER_URL}/{TOKEN}"
    if bot.get_webhook_info().url != url:
        bot.remove_webhook()
        bot.set_webhook(url=url)
    return "Madonna online! ✨", 200

# 🔄 Mantém o bot vivo no Render

def manter_vivo():
    import requests
    while True:
        try:
            requests.get(RENDER_URL)
        except:
            pass
        time.sleep(600)

# 🚀 INICIAR
if __name__ == "__main__":
    threading.Thread(target=manter_vivo).start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
