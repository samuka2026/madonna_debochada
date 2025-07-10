from flask import Flask, request
import telebot
import os
import random
import time
import datetime
import json
import threading
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
GRUPO_ID = -1002363575666  # ID do grupo

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HISTORICO_PATH = "historico_respostas.json"
FRASES_USUARIOS_PATH = "frases_aprendidas.json"

try:
    with open(HISTORICO_PATH, "r") as f:
        historico = json.load(f)
except:
    historico = {"elogios": {}, "insultos": {}}

def salvar_historico():
    with open(HISTORICO_PATH, "w") as f:
        json.dump(historico, f)

def frase_nao_usada(frases, categoria):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    usadas = []
    for dia in historico.get(categoria, {}):
        usadas.extend(historico[categoria][dia])
    candidatas = [f for f in frases if f not in usadas]
    frase = random.choice(candidatas or frases)
    historico.setdefault(categoria, {}).setdefault(hoje, []).append(frase)
    dias = sorted(historico[categoria].keys())[-3:]
    historico[categoria] = {d: historico[categoria][d] for d in dias}
    salvar_historico()
    return frase

def salvar_frase_usuario(frase):
    try:
        with open(FRASES_USUARIOS_PATH, "r") as f:
            frases = json.load(f)
    except:
        frases = []
    if frase not in frases and 10 < len(frase) < 100:
        frases.append(frase)
        with open(FRASES_USUARIOS_PATH, "w") as f:
            json.dump(frases[-500:], f)  # mantém as últimas 500

def frase_aprendida():
    try:
        with open(FRASES_USUARIOS_PATH, "r") as f:
            frases = json.load(f)
        return random.choice(frases) if frases else None
    except:
        return None

gatilhos_automaticos = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
    "te amo": ["Ai, que clichê fofo. Tô quase acreditando."],
    "quem é você": ["Sou aquela que te responde com classe e deboche. A Madonna, querido(a)."],
    "tá on?": ["Sempre estive. Diva que é diva não dorme, só descansa os olhos."],
    "madonna linda": ["Ai, para... continua!"],
    "madonna chata": ["Chata? Eu sou é necessária!"],
    "bom dia madonna": ["Bom dia só pra quem me manda café e carinho! 🪦"]
}

elogios_femininos = [...]
insultos_masculinos = [...]
respostas_para_apolo = [...]

def brigar_com_apolo():
    while True:
        try:
            time.sleep(3600)
            frase = random.choice(respostas_para_apolo)
            bot.send_message(GRUPO_ID, f"@apolo_8bp_bot {frase}")
        except Exception as e:
            print(f"Erro ao brigar com Apolo: {e}")

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
        return "✅ Webhook configurado com sucesso!", 200
    return "✅ Webhook já estava configurado.", 200

@bot.message_handler(func=lambda msg: True)
def responder(message):
    texto = message.text.lower()
    nome = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    # Se o Apolo mencionar "madonna" em qualquer frase, ela responde
if message.from_user.username == "apolo_8bp_bot" and "madonna" in texto:
    frase = random.choice(respostas_para_apolo)
    bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
    return
    salvar_frase_usuario(message.text.strip())

    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        saudacao = "bom dia 🪦" if "bom dia" in texto else \
                   "boa tarde 🪦" if "boa tarde" in texto else \
                   "boa noite 🪦" if "boa noite" in texto else \
                   "boa madrugada 🪦"
        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        return

    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        if message.from_user.username == "apolo_8bp_bot":
            bot.reply_to(message, random.choice(respostas_para_apolo), parse_mode="Markdown")
            return

        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                return

        # resposta aleatória: elogio, insulto ou frase aprendida
        if random.choice([True, False]):
            categoria = "elogios" if random.choice([True, False]) else "insultos"
            lista = elogios_femininos if categoria == "elogios" else insults_masculinos
            frase = frase_nao_usada(lista, categoria)
        else:
            frase = frase_aprendida() or "Tô pensando em algo pra te dizer..."
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        return

    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        return

    time.sleep(15)
    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            return

    if random.choice([True, False]):
        categoria = "elogios" if random.choice([True, False]) else "insultos"
        lista = elogios_femininos if categoria == "elogios" else insults_masculinos
        frase = frase_nao_usada(lista, categoria)
    else:
        frase = frase_aprendida() or "Fiquei sem palavras agora, mas tô aqui 🪦"

    bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")


def manter_vivo():
    while True:
        try:
            requests.get(RENDER_URL)
        except:
            pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=manter_vivo).start()
    threading.Thread(target=brigar_com_apolo).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
