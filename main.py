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

# ✅ Listas temáticas para respostas inteligentes
temas = {
    "cafe": {
        "keywords": ["café", "cafezinho", "expresso", "capuccino"],
        "respostas": carregar_lista("temas/cafe.json")
    },
    "comida": {
        "keywords": ["pizza", "hamburguer", "lanche", "almoço", "janta", "fome"],
        "respostas": carregar_lista("temas/comida.json")
    },
    "namoro": {
        "keywords": ["namoro", "ficar", "beijo", "crush", "coração partido"],
        "respostas": carregar_lista("temas/namoro.json")
    },
    "preguiça": {
        "keywords": ["preguiça", "sono", "dormir", "descansar", "cansado"],
        "respostas": carregar_lista("temas/preguica.json")
    },
    "fofoca": {
        "keywords": ["mentira", "fofoca", "treta", "confusão", "barraco"],
        "respostas": carregar_lista("temas/fofoca.json")
    },
    "motivacao": {
        "keywords": ["triste", "desanimado", "cansada", "sem forças", "fracasso"],
        "respostas": carregar_lista("temas/motivacao.json")
    }
}

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
# ✅ Controle de envio para saudação e respostas automáticas
ultimos_envios_saudacoes = {}
ultimos_envios_geral = {}

# ✅ Envia mensagem com atraso (em segundos)
def enviar_com_delay(delay_segundos, chat_id, texto, reply_id=None):
    def tarefa():
        bot.send_message(chat_id, texto, reply_to_message_id=reply_id)
    threading.Timer(delay_segundos, tarefa).start()

# ✅ Handler principal
@bot.message_handler(func=lambda msg: True)
def responder(msg):
    #if msg.chat.id != GRUPO_ID:
    #    return

    texto = msg.text.lower()
    user_id = msg.from_user.id
    nome = msg.from_user.first_name or msg.from_user.username or "Amor"
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 👑 Submissão ao dono (apenas se mencionarem "madonna" ou @)
    if user_id == DONO_ID and frases_dono and ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto):
        frase = random.choice(frases_dono)
        enviar_com_delay(40, msg.chat.id, frase, msg.message_id)  # 40 segundos de delay
        return

    # 💘 Madonna em defesa do Apollo
    #if "apollo" in texto or "@apolo_8bp_bot" in texto:
    #    if defesa_apollo:
    #        bot.send_message(GRUPO_ID, random.choice(defesa_apollo), reply_to_message_id=msg.message_id)
    #    return

    # 💬 Mencionaram a Madonna (com saudação ou não)
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        if "bom dia" in texto:
            frase = random.choice(bom_dia_mulher if mulher else bom_dia_homem)
        elif "boa tarde" in texto:
            frase = random.choice(boa_tarde_mulher if mulher else boa_tarde_homem)
        elif "boa noite" in texto or "boa madrugada" in texto:
            if agora.hour < 21:
                frase = random.choice(boa_noite_entrada_mulher if mulher else boa_noite_entrada_homem)
            else:
                frase = random.choice(boa_noite_dormir_mulher if mulher else boa_noite_dormir_homem)
        else:
            frase = random.choice(men_m if mulher else men_h)

        enviar_com_delay(60, msg.chat.id, frase, msg.message_id)
        return

    # 🎯 Resposta inteligente por tema detectado
for tema, dados in temas.items():
    if user_id in ultimos_envios_geral and (agora - ultimos_envios_geral[user_id]) < timedelta(minutes=20):
        return
    ultimos_envios_geral[user_id] = agora
    if any(palavra in texto for palavra in dados["keywords"]):
        if dados["respostas"]:
            frase = random.choice(dados["respostas"])
            enviar_com_delay(random.randint(10, 30), msg.chat.id, frase, msg.message_id)
        return

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
