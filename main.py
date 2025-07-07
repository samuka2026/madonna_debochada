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

# Frases por dia da semana + padrao
respostas = {
    "segunda": [
        "Segunda? Só com muito glitter e paciência... 💅",
        "Tô aqui mas ainda de ressaca emocional da semana passada 🚪",
        "Nem café me anima numa segunda, imagina você ☕",
        "Hoje só respondo se me chamar de deusa 💄",
        "Segunda é dia de ghosting com classe 🕯️"
    ],
    "terca": [
        "Terça é dia de brilhar sem pressa, amor ✨",
        "Hoje tô romântica com veneno... cuidado 💋",
        "Respondi só pra mostrar que consigo ser educada 😘",
        "Terça? Só se for com filtro rosa 💗",
        "Te notei, mas finjo que não pra manter o mistério 😌"
    ],
    "quarta": [
        "Quarta-feira sensual com um toque de deboche 🌹",
        "Hoje tô dividida: ignoro ou respondo com classe? 💄",
        "Me chamou? Espero que seja pra elogiar 💅",
        "Quarta é o novo sábado, se eu quiser 💃",
        "Respondi só porque sou caridosa 💖"
    ],
    "quinta": [
        "Quinta com cara de diva de novela das 8 💃",
        "Tô mais perigosa que spoiler de série hoje 👀",
        "Quer resposta? Me convence primeiro 💖",
        "A quinta me deixa misteriosa... ou só cansada mesmo 😴",
        "Hoje só respondo quem brilha mais que eu (difícil) ✨"
    ],
    "sexta": [
        "Sexta é meu dia oficial de causar 💃💥",
        "Hoje só respondo com champanhe e indiretas 🍾",
        "Fala comigo como quem manda nudes 💌",
        "Sexta é pra lacrar, não pra discutir 💅",
        "Se é sexta, eu tô pronta pra responder com veneno 🐍"
    ],
    "sabado": [
        "Sábado eu sou pura sedução... ou preguiça 💅",
        "Cheguei pra abalar esse grupo, bebê 💋",
        "Hoje minha resposta tem glitter e recalque 🎉",
        "Sábado é dia de diva ocupada e misteriosa 🌙",
        "Tô em clima de sábado: distraída e maravilhosa 💃"
    ],
    "domingo": [
        "Domingo é dia de descanso… mas abro exceção pra ti 😘",
        "Hoje respondo como quem manda um áudio cantando 🎤",
        "Se for amor, eu respondo. Se for tédio, ignoro 🛌",
        "Domingo combina com silêncio e sombra rosa 💄",
        "Acordei num domingo existencial: responder ou não? 🤔"
    ],
    "padrao": [
        "Ai meu bem, tenta de novo que dessa vez eu tô zen 💅",
        "Amor, você fala e eu só suspiro... 😘",
        "Hoje tô igual diamante: linda, cara e difícil 💎",
        "Te ouvi, mas não sei se merecia minha resposta 💋",
        "Tô aqui, mas só respondo se for com drama 🎭",
        "Você fala... e eu ignoro com classe 💅",
        "Madonna te ouviu, amor. Mas se vai te responder? Talvez... 💖",
        "Só respondo porque sou um ícone, tá? 💃",
        "Fala direito, que hoje acordei exigente 💋",
        "A Madonna não responde qualquer um... mas vou abrir uma exceção 💌",
        "Se for pra me chamar, que seja com emoção 💄",
        "Cuidado, amor. Uma diva responde, mas também esnoba 💅",
        "Tô muito ocupada sendo maravilhosa pra isso 💃",
        "Você não aguenta 5 minutos no meu salto 💅",
        "Fala comigo direito ou vai pro castigo, bebê 💋",
        "Tô aqui, mas cheia de atitude 💥",
        "Manda flores, depois a mensagem 🌹",
        "Com essa vibe? Só um deboche serve 🌪️",
        "Quer resposta? Traz café e um elogio ☕",
        "Ai que preguiça de responder básico 😴",
        "Chama a Madonna direito, meu bem 💄",
        "Hoje tô me sentindo a própria resposta 💅",
        "Você falando e eu pensando no glitter 💫",
        "Te respondo, mas só porque sou generosa 💖",
        "Olha, por menos eu já ignorei fã-clube 😌",
        "Sua mensagem foi quase um convite pra bocejar 😴",
        "Cheguei, meu bem. Agora segura o close 💃",
        "Madonna responde, mas só se o tom for chique 💎",
        "Se for pra chamar, que seja com luxo e intenção ✨",
        "Sua dúvida foi quase um elogio… mas não foi 🤬"
    ]
}

def pegar_resposta_dia():
    dia_semana = datetime.datetime.now().strftime('%A').lower()
    mapa_dias = {
        "monday": "segunda",
        "tuesday": "terca",
        "wednesday": "quarta",
        "thursday": "quinta",
        "friday": "sexta",
        "saturday": "sabado",
        "sunday": "domingo"
    }
    chave = mapa_dias.get(dia_semana, "padrao")
    return random.choice(respostas.get(chave, respostas["padrao"]))

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

    # Palavras genéricas que serão ignoradas
    frases_mortas = ["oi", "alguém aí", "ola", "olá", "tudo bem", "e aí", "bom dia", "boa noite"]

    if any(palavra in texto for palavra in frases_mortas):
        print("Ignorou mensagem genérica 🛌")
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

    resposta = pegar_resposta_dia()
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
