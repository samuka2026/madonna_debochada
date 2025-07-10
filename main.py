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
    "cadê o diego": ["Tá atolando o carro em alguma lama, ele tá precisando de umas aulinhas de direção urgente!"],
    "manda beijo": ["Beijo enviado com glitter, batom e um pouco de saudade."],
    "te amo": ["Ai, que clichê fofo. Tô quase acreditando."],
    "quem é você": ["Sou aquela que te responde com classe e deboche. A Madonna, querido(a)."],
    "cadê você": ["Tava me retocando, amor. Diva não aparece de qualquer jeito."],
    "me nota": ["Você já é destaque, meu bem. Só falta brilhar mais."],
    "tá on?": ["Sempre estive. Diva que é diva não dorme, só descansa os olhos."],
    "madonna linda": ["Ai, para... continua!"],
    "madonna chata": ["Chata? Eu sou é necessária!"],
    "bora conversar": ["Só se for agora, mas cuidado com o que deseja."],
    "vai dormir": ["Diva não dorme, recarrega o brilho."],
    "me responde": ["Calma, flor. Eu sou rápida, mas com classe."],
    "bom dia madonna": ["Bom dia só pra quem me manda café e carinho! 🫦"]
}

insultos_masculinos = [ ... ]  # (igual ao seu original)
elogios_femininos = [ ... ]    # (igual ao seu original)

# ⚔️ Respostas automáticas da Madonna pro Apolo
respostas_para_apolo = [
    "Apolo, me esquece. Vai ler um dicionário de bom senso.",
    "Ai Apolo... tua tentativa de me afrontar é quase fofa.",
    "Você é o motivo do grupo precisar de moderação, Apolo.",
    "Se você brilhasse metade do que fala, apagava a luz do grupo.",
    "Apolo, teu deboche é tão fraco quanto teu argumento.",
    "Continua, Apolo... tô usando tua audácia como esfoliante.",
]

def brigar_com_apolo():
    while True:
        try:
            time.sleep(3600)  # espera 1 hora
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
    username = message.from_user.username or ""
    is_homem = not username.lower().endswith(("a", "i", "y"))
    is_mulher = not is_homem

    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        saudacao = "bom dia 🫦" if "bom dia" in texto else \
                   "boa tarde 🫦" if "boa tarde" in texto else \
                   "boa noite 🫦" if "boa noite" in texto else \
                   "boa madrugada 🫦"
        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        return

    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        if message.from_user.username == "apolo_8bp_bot":
            frases_resposta_apolo = [
                "Apolo, querido... com esse argumento, até a Alexa te silenciava.",
                "Você me mencionou, Apolo? Cuidado que diva não perde tempo com beta tester.",
                "Volta pro código, Apolo. Tua presença tá bugando minha elegância.",
                "Ô Apolo, você é tipo notificação de antivírus: irritante e dispensável.",
                "Deixa de recalque, Apolo. Até meu log de erro tem mais carisma que você."
            ]
            bot.reply_to(message, random.choice(frases_resposta_apolo), parse_mode="Markdown")
            return

        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                return
        if is_homem:
            frase = frase_nao_usada(insultos_masculinos, "insultos")
            bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
            return
        if is_mulher:
            frase = frase_nao_usada(elogios_femininos, "elogios")
            bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
            return

    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        return

    time.sleep(15)

    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            return

    if is_homem:
        frase = frase_nao_usada(insultos_masculinos, "insultos")
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        return

    if is_mulher:
        frase = frase_nao_usada(elogios_femininos, "elogios")
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        return

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
