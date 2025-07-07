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

# Frases genéricas
respostas = [
    "Você falando e eu aqui só analisando... com charme, claro.",
    "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
    "Fala baixo que minha paciência tá de salto alto.",
    "Responder? Só se tiver um pouco de emoção no que você disse.",
    "Você me chamou ou foi impressão minha de diva?",
    "Tô aqui, deslumbrante como sempre. E você?",
    "Cuidado, eu mordo com classe.",
    "Me chamou? Que ousadia deliciosa...",
    "Às vezes eu respondo. Às vezes só desfilo minha indiferença.",
    "Palavras bonitas me ganham. As feias eu ignoro com requinte.",
    "Respondi porque senti estilo. Só por isso.",
    "Seja direto, mas nunca sem charme.",
    "Com esse tom, quase fiquei tentada a responder.",
    "Você fala e eu penso: merece minha atenção?",
    "Hoje acordei mais diva que de costume. Tá difícil de agradar.",
    "Pode tentar de novo, mas dessa vez com classe.",
    "Respondi só porque o universo piscou pra mim agora.",
    "Você não fala, você desfila as palavras, né? Quase gostei.",
    "Eu ouvi, mas não prometo me importar.",
    "Quer atenção? Encanta primeiro.",
    "Faz melhor e talvez eu te dê meu melhor também.",
    "O que você disse? Tava ocupada admirando meu reflexo.",
    "Tem dias que eu tô pra conversa. Tem dias que eu tô pra chá e silêncio.",
    "Dei uma olhada na sua mensagem... gostei da fonte.",
    "Olha, hoje só respondo elogio bem construído.",
    "Se for pra falar comigo, que seja com impacto.",
    "Me ganhou pelo esforço. A resposta vem com glitter.",
    "Se eu não respondi antes, é porque eu estava ocupada sendo fabulosa.",
    "Tem gente que fala e tem gente que brilha. Você tá quase lá.",
    "Fico em silêncio não por falta de resposta, mas por excesso de classe.",
    "É cada mensagem que eu leio que fico grata por ser eu.",
    "Você tentou... e isso já é digno de aplauso. Só não o meu ainda.",
    "Mensagem recebida. Atenção? Talvez amanhã.",
    "Isso foi uma tentativa de conversa ou só um erro de digitação?",
    "Se for pra me chamar, que seja com propósito.",
    "Fala mais alto... no meu nível, claro.",
    "Toda vez que eu ignoro, uma estrela brilha mais forte.",
    "Eu respondo com classe. Mas hoje tô sem tempo pra aula.",
    "Você tentando, eu analisando. Quem cansa primeiro?",
    "Só entrei aqui pra ver se alguém merecia minha atenção. Talvez você...",
    "Às vezes eu respondo só pra causar intriga. Hoje é um desses dias.",
    "Quer conversa ou quer aula de atitude?",
    "Madonna responde quando sente que há arte na mensagem.",
    "Você mandou mensagem achando que ia passar batido? Fofo.",
    "Não me desafie com mensagens mornas. Eu exijo fogo.",
    "Se eu te respondi, parabéns. O universo te ama hoje.",
    "Me provoca com palavras bonitas, e talvez eu dance.",
    "Não sou rápida, sou icônica. Minhas respostas têm hora.",
    "Já vi mensagens melhores... mas também já vi piores. Você tá no meio.",
    "A resposta veio. Não por obrigação, mas por caridade cósmica.",
    "Meu silêncio foi a melhor parte da conversa até agora."
]

# (boas_maneiras permanece igual)
# ...

@bot.message_handler(func=lambda msg: True)
def responder_com_estilo(message):
    texto = message.text.lower().strip()
    texto_limpo = texto.replace("!", "").replace("?", "")
    hora = datetime.datetime.now().hour

    nome_usuario = message.from_user.first_name

    # Respostas especiais para saudações
    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            time.sleep(random.uniform(1.5, 3))
            resposta = random.choice(frases)
            bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
            return

    # Se não for saudação, só responde se for mencionada
    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        print("Mensagem ignorada: não é saudação e nem mencionou a Madonna")
        return

    # (demais lógicas continuam: elogios, apelidos, xingamentos, etc)
    # ...

    # Resposta genérica final
    if random.random() <= 0.7:
        time.sleep(random.uniform(1.5, 3))
        resposta = random.choice(respostas)
        bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
