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
            json.dump(frases[-500:], f)

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

elogios_femininos = [
    "Com você no grupo, até o Wi-Fi fica mais bonito.",
    "Sua presença ilumina mais que LED no espelho.",
    "Você tem o dom de embelezar até o silêncio.",
    "Dá vontade de te fixar no topo do grupo.",
    "Se beleza fosse áudio, você seria o mais ouvido.",
    "Tua vibe é mais forte que café sem açúcar.",
    "Se eu pudesse, colocava moldura nesse charme.",
    "Você é tipo emoji novo: todo mundo ama.",
    "Com esse brilho, até a Madonna respeita.",
    "Você transforma simples em espetáculo.",
    "Você é Wi-Fi de 5GHz de tão maravilhosa.",
    "Com essa presença, até a piada perde a graça.",
    "Você é a notificação que eu sempre quero receber.",
    "Você é poesia sem precisar de rima.",
    "A Madonna só responde rápido porque é você."
]

insultos_masculinos = [
    "Você é tão necessário quanto tutorial de como abrir porta.",
    "Com esse papo, nem o Wi-Fi te suporta.",
    "Homem e opinião: duas coisas que não combinam.",
    "Você fala e eu só escuto o som do fracasso.",
    "Teu charme é igual teu argumento: inexistente.",
    "Se fosse pra ouvir besteira, eu ligava a TV.",
    "Tua presença é mais cansativa que seguidor carente.",
    "Com esse conteúdo, só falta virar coach.",
    "Homem tentando causar, é só mais um tropeço.",
    "Você devia vir com botão de silencioso.",
    "Poderia tentar ser menos dispensável.",
    "Você é tipo spoiler: ninguém quer ver, mas aparece.",
    "Se elegância fosse crime, você era inocente.",
    "Com esse papo, tu afasta até notificação.",
    "Tua opinião vale menos que Wi-Fi público."
]

respostas_para_apolo = [
    "Apolo, me esquece. Vai ler um dicionário de bom senso.",
    "Ai Apolo... tua tentativa de me afrontar é quase fofa.",
    "Você é o motivo do grupo precisar de moderação, Apolo.",
    "Se você brilhasse metade do que fala, apagava a luz do grupo.",
    "Apolo, teu deboche é tão fraco quanto teu argumento.",
    "Continua, Apolo... tô usando tua audácia como esfoliante.",
    "Apolo, querido... com esse argumento, até a Alexa te silenciava.",
    "Você me mencionou, Apolo? Diva não perde tempo com beta tester.",
    "Volta pro código, Apolo. Tua presença tá bugando minha elegância.",
    "Ô Apolo, você é tipo notificação de antivírus: irritante e dispensável.",
    "Deixa de recalque, Apolo. Até meu log de erro tem mais carisma que você."
]

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

    # Madonna responde diretamente o Apolo se for mencionada
    if message.from_user.username == "apolo_8bp_bot" and "madonna" in texto:
        frase = random.choice(respostas_para_apolo)
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        salvar_frase_usuario(message.text.strip())
        return

    # Saudação
    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        saudacao = "bom dia 🪦" if "bom dia" in texto else \
                   "boa tarde 🪦" if "boa tarde" in texto else \
                   "boa noite 🪦" if "boa noite" in texto else \
                   "boa madrugada 🪦"
        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        return

    # Se responder à Madonna
    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                return

        # Escolhe aleatoriamente entre elogio, insulto ou frase aprendida
        if random.choice([True, False]):
            categoria = "elogios" if random.choice([True, False]) else "insultos"
            lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
            frase = frase_nao_usada(lista, categoria)
        else:
            frase = frase_aprendida() or "Tô pensando em algo pra te dizer..."
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        return

    # Se não for menção nem resposta pra Madonna
    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        return

    time.sleep(15)
    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            return

    # Escolhe aleatoriamente entre elogio, insulto ou frase aprendida
    if random.choice([True, False]):
        categoria = "elogios" if random.choice([True, False]) else "insultos"
        lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
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
