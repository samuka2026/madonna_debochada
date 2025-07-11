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
FRASES_MEMBROS_PATH = "frases_membros.json"

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

# === Gatilhos automáticos ===
gatilhos_automaticos = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
    "você me ama": ["Claro que sim, mas não espalha... vai causar ciúmes."],
    "cadê a vanessa": ["Deve estar em algum bar, bebendo todas!"],
    "cadê o samuel": ["Não mexe com o meu Xodó!"],
    "cadê o líder": ["Tá em algum dos trabalhos dele, ele é igual ao pai do Cris."],
    "cadê a tai": ["Cuidando da cria dela ou então da beleza."],
    "cadê a adriana": ["Visheee, essa é Fake, com certeza!!!!"],
    "cadê a lilian": ["Nossa Mascote de sucesso tá quase parindo, não é uma boa hora pra mecher com quem ta quieto!"],
    "cadê a fernanda": ["quem é Fernanda? Onde vive? O que come? Como vive? O que faz? Como se sustenta?"],
    "cadê o diego": ["Tá atolando o carro em alguma lama, ele tá precisando de umas aulinhas de direção urgente!"],
    "cadê o zeca": ["Tá dançando pagode e procurando uma coroa rica pra se casar."],
    "cadê a braba": ["Tá montando o rifle de precisão pra eliminar você. Foge maluco!"],
    "manda beijo": ["Beijo enviado com glitter, batom e um pouco de saudade."],
    "te amo": ["Ai, que clichê fofo. Tô quase acreditando."],
    "alguém vivo": ["Sim. Mas no momento estão coisando, silencio!🪦"],
    "quem é você": ["Sou aquela que te responde com classe e deboche. A Madonna, querido(a)."],
    "cadê você": ["Tava me retocando, amor. Diva não aparece de qualquer jeito."],
    "me nota": ["Você já é destaque, meu bem. Só falta brilhar mais."],
    "tá on?": ["Sempre estive. Diva que é diva não dorme, só descansa os olhos."],
    "madonna linda": ["Ai, para... continua!"],
    "quem manda aqui?": ["Claro que é o nosso chefinho Samuka 🪦"],
    "madonna chata": ["Chata? Eu sou é necessária!"],
    "bora conversar": ["Só se for agora, mas cuidado com o que deseja."],
    "vai dormir": ["Diva não dorme, recarrega o brilho."],
    "me responde": ["Calma, flor. Eu sou rápida, mas com classe."],
    "bom dia madonna": ["Bom dia só pra quem me manda café e carinho! 🪦"]
}

insultos_masculinos = [
    "Você é tão necessário quanto tutorial de como abrir porta.",
    "Com esse papo, nem o Wi-Fi te suporta.",
    "Homem e opinião: duas coisas que não combinam.",
    # ...
]

elogios_femininos = [
    "Com você no grupo, até o Wi-Fi fica mais bonito.",
    "Sua presença ilumina mais que LED no espelho.",
    "Você tem o dom de embelezar até o silêncio.",
    # ...
]

respostas_para_apolo = [
    "Apolo, me esquece. Vai ler um dicionário de bom senso.",
    "Ai Apolo... tua tentativa de me afrontar é quase fofa.",
    # ...
]

def brigar_com_apolo():
    while True:
        try:
            time.sleep(72000)  # 20 horas
            frase = random.choice(respostas_para_apolo)
            bot.send_message(GRUPO_ID, f"@apolo_8bp_bot {frase}")
        except Exception as e:
            print(f"Erro ao brigar com Apolo: {e}")

# === Frases aprendidas ===
frases_aprendidas = []

try:
    with open(FRASES_MEMBROS_PATH, "r") as f:
        frases_aprendidas = json.load(f)
except:
    frases_aprendidas = []

def aprender_frase(message):
    if message.chat.id != GRUPO_ID:
        return
    if message.text and len(message.text) > 10:
        frase = {
            "nome": message.from_user.first_name,
            "texto": message.text
        }
        frases_aprendidas.append(frase)
        if len(frases_aprendidas) > 50:
            frases_aprendidas.pop(0)
        with open(FRASES_MEMBROS_PATH, "w") as f:
            json.dump(frases_aprendidas, f)

def repetir_frase():
    while True:
        try:
            time.sleep(1800)
            if frases_aprendidas:
                frase = random.choice(frases_aprendidas)
                texto = frase["texto"]
                nome = frase["nome"]
                bot.send_message(GRUPO_ID, f"ja dizia {nome}: \"{texto} ✍🏻💋💄\"")
        except Exception as e:
            print(f"Erro ao repetir frase aprendida: {e}")

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
    texto = message.text.lower() if message.text else ""
    nome = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    username = message.from_user.username or ""

    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        saudacao = "bom dia 🪦" if "bom dia" in texto else \
                   "boa tarde 🪦" if "boa tarde" in texto else \
                   "boa noite 🪦" if "boa noite" in texto else \
                   "boa madrugada 🪦"
        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        aprender_frase(message)
        return

    if username == "apolo_8bp_bot" and "madonna" in texto:
        bot.reply_to(message, f"{nome}, {random.choice(respostas_para_apolo)}", parse_mode="Markdown")
        return

    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        if username == "apolo_8bp_bot":
            bot.reply_to(message, random.choice(respostas_para_apolo), parse_mode="Markdown")
            return

        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                aprender_frase(message)
                return

        categoria = "elogios" if random.choice([True, False]) else "insultos"
        lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
        frase = frase_nao_usada(lista, categoria)
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        aprender_frase(message)
        return

    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        aprender_frase(message)
        return

    time.sleep(15)
    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            aprender_frase(message)
            return

    categoria = "elogios" if random.choice([True, False]) else "insultos"
    lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
    frase = frase_nao_usada(lista, categoria)
    bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
    aprender_frase(message)

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
    threading.Thread(target=repetir_frase).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
