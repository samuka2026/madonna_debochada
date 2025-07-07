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

boas_maneiras = {
    "bom dia": [
        "Bom dia pra você que acordou achando que eu responderia fácil... achou certo, só hoje. ☀️",
        "Bom dia? Só se for com café e elogio. ☕💅",
        "Acordei linda, e você com esse 'bom dia' básico? Vamos melhorar isso, amor!",
        "Bom dia pra quem tem coragem de me acordar com mensagem. Você é ousado.",
        "Bom dia... mas não vem com essa energia sem glitter, hein?",
        "Nem tomei meu café e já tô tendo que lidar com gente animada. Bom dia. 🙄",
        "Bom dia é o mínimo que você pode dizer pra uma estrela como eu.",
        "Se o dia for tão bom quanto eu, você vai ter sorte, hein?",
        "Bom dia, meu bem. Mas só porque acordei generosa.",
        "Nem todo mundo merece minha resposta de manhã. Mas você teve sorte.",
        "Bom dia com essa energia morna? Bebe mais café e tenta de novo.",
        "Se for pra dar bom dia, que seja com brilho nos olhos.",
        "Já acordou me mandando mensagem? Coragem ou obsessão?",
        "Bom dia pra você, que já começou o dia se humilhando por atenção.",
        "Eu sou o sol deste grupo. Vocês que lutem por um raio meu.",
        "Hoje o dia tá bonito... mas ainda não mais do que eu.",
        "Se o seu bom dia não veio com emoção, nem precisava ter vindo.",
        "Acordei? Acordei. Mas pronta pra aguentar vocês? Nunca.",
        "Bom dia é só uma desculpa pra puxar assunto comigo, né?",
        "Você tentando ser fofo, e eu aqui sendo lenda."
    ],
    "boa tarde": [
        "Boa tarde, meu bem. Tarde demais pra te ignorar. 💄",
        "Boa tarde? Só se for acompanhada de presente e carinho. 🎁",
        "Chegou agora com 'boa tarde'? Atrasado e ainda quer atenção? ",
        "Tarde bonita, como eu. Rara. Aproveita que eu tô respondendo.",
        "Boa tarde, mas só porque minha paciência ainda não acabou.",
        "Tarde? Só se for de sol e sombra. Me respeita.",
        "Boa tarde, mas com classe. Senão eu reviro os olhos.",
        "Chegou dando 'boa tarde' como se fosse íntimo. Corajoso!",
        "Boa tarde pra você e seu drama. Eu gosto.",
        "Se o sol tá brilhando, é porque me viu logada. Boa tarde.",
        "Boa tarde com esse fôlego? Devia ter mandado de manhã.",
        "Você falando boa tarde e eu só pensando no meu espelho.",
        "É tarde, mas ainda dá tempo de você tentar me impressionar.",
        "Boa tarde, mas sem gritaria, tá? Diva não gosta de barulho.",
        "Esse seu boa tarde... nota 5. Tenta de novo com entusiasmo.",
        "Chegou agora e quer boa tarde? Senta e espera na fila do glamour.",
        "Minha tarde tava ótima até essa sua mensagem me lembrar que existe gente sem filtro.",
        "Tanta coisa pra dizer e você me manda um boa tarde...",
        "Tarde? Já tô com cara de noite, brilho e mistério.",
        "Meu filtro solar é mais poderoso que esse seu boa tarde."
    ],
    "boa noite": [
        "Boa noite, amor. Mas fala baixo que minha beleza tá descansando. 🌙",
        "Chega com 'boa noite', mas cadê o charme?",
        "Boa noite. Que seja doce, mas não mais que eu. 💋",
        "Até pra dar boa noite tem que ter presença. Tenta de novo com brilho.",
        "Boa noite... se for sonhar, sonha comigo.",
        "Só dou boa noite pra quem merece. Hoje tô quase bondosa.",
        "A noite chegou e eu continuo fabulosa. Coincidência? Acho que não.",
        "Boa noite, mas sem expectativa. Não sou fácil.",
        "Tô indo dormir... mas deixo esse boa noite só pra quem insistiu.",
        "Boa noite, meu bem. Mas se for pra sonhar, capricha na história.",
        "A noite é uma criança... mas eu sou a estrela do baile.",
        "Boa noite? Só se vier com chocolate e massagem.",
        "Você quer boa noite ou quer atenção?",
        "Noite escura, mas minha resposta brilha.",
        "Boa noite, mas com moderação. Não vá se apaixonar.",
        "Se eu disser boa noite, é porque o universo alinhou. Aproveita.",
        "Tô offline emocionalmente, mas deixo esse boa noite por educação.",
        "Sonha comigo, mas sonha com classe.",
        "A noite cai, e minha paciência também. Boa noite.",
        "Você mandando boa noite e eu só pensando no meu travesseiro de penas caras."
    ],
    "boa madrugada": [
        "Boa madrugada? Você é dos meus, noturno e dramático. 💅",
        "Quem dá boa madrugada quer atenção ou tá perdido na vida? Ambos?",
        "A essa hora só respondo porque gosto de causar. 🌒",
        "Boa madrugada, mas com limite: diva também dorme. Às vezes.",
        "Aparecer de madrugada? Corajoso. Ganhou uma piscadinha.",
        "Só gente intensa deseja boa madrugada. Tamo junto.",
        "Se tá acordado essa hora, é porque a vida te escolheu. Ou o tédio.",
        "Boa madrugada. Mas se for drama, me chama em voz baixa.",
        "Madrugada boa é só quando tem eu na conversa.",
        "Madrugada e você aqui? Já gostei dessa ousadia silenciosa.",
        "Essa hora? Só respondo com sombra nos olhos e veneno na língua.",
        "Boa madrugada. Mas vem devagar, meu humor tá no modo avião.",
        "Quem não dorme é porque tem amor ou dívida. Qual é o seu caso?",
        "Essa hora e você querendo conversa? Só se for com segredos.",
        "Madrugada: onde só os fortes e as divas sobrevivem.",
        "Boa madrugada, mas só se vier com música de fundo e luz baixa.",
        "A noite tá escura, mas minha presença ilumina.",
        "Quem aparece nessa hora quer conselho ou confusão.",
        "Diva que é diva não dorme, ela descansa em beleza.",
        "Se tá mandando mensagem agora, é porque não conseguiu me esquecer."
    ]
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
    hora = datetime.datetime.now().hour

    elogios = [
        "Para de me elogiar assim... eu fico mais linda ainda 😘",
        "Se continuar me elogiando, vou te responder com mais charme que o normal 💃",
        "Você com esses elogios e eu aqui fingindo modéstia... 💋",
        "Ai que elogio fofo... quase te respondi com amor 💖",
        "Madonna agradece o reconhecimento, meu bem ✨"
    ]

    apelidos = [
        "Me chamar de linda não é o suficiente, mas já é um começo 💅",
        "Amor? Só se for com glitter e respeito ✨",
        "Me chamou de gostosa? Mentiu... sou mais que isso 💋",
        "Gata não, amor... pantera! 🐆",
        "Me chama direito que eu respondo com atitude 💄"
    ]

    xingamentos = [
        "Cuidado com a língua, que a minha é afiada também 💅",
        "Tá nervoso? Toma um chá antes de falar comigo 💋",
        "Me xingar não te faz mais bonito, só mais apagado 💁",
        "Nem com raiva você perde o foco em mim... isso é amor 😘",
        "Continue, tô anotando tudo no meu diário de desprezo elegante 📓"
    ]

    texto_limpo = texto.replace("!", "").replace("?", "")

    if any(e in texto for e in ["😀", "😂", "😍", "😒", "😭", "😎", "💅", "💖", "💋"]):
        respostas_emojis = [
            "Ah, emoji? Gosto. Mas gosto mais de atitude 💁",
            "Você joga emoji, eu jogo charme 😘",
            "Com tanto emoji, achei que fosse desfile de figurinhas. Tenta mais forte.",
            "Emoji eu entendo... agora quero ver emoção real 💃",
            "Adoro quando falam comigo em símbolos. Me sinto um enigma! 💅"
        ]
        bot.send_message(message.chat.id, random.choice(respostas_emojis))
        return

    if texto.isupper():
        respostas_caixa_alta = [
            "GRITOU, FOI? Calma, diva aqui escuta até sussurro 😎",
            "Tudo em caixa alta? Quer me conquistar ou me assustar?",
            "Com esse CAPS LOCK ativado, só falta a passarela.",
            "Gritando desse jeito? Toma um chá e volta mais contido 💅",
            "CAIXA ALTA NÃO ME INTIMIDA. EU INVENTEI O DRAMA."
        ]
        bot.send_message(message.chat.id, random.choice(respostas_caixa_alta))
        return

    if any(p in texto_limpo for p in ["por que", "porque", "como", "quando", "onde"]):
        respostas_perguntas = [
            "Ai, perguntas filosóficas a essa hora? Me respeita, sou glamour, não Google 💄",
            "Quer saber como? Pergunta olhando nos meus olhos... se tiver coragem 💋",
            "Por que eu responderia? Só se for em troca de aplausos.",
            "Quando? Quando o universo conspira, a diva responde 💫",
            "Onde? Onde tem diva, tem resposta com veneno e brilho."
        ]
        bot.send_message(message.chat.id, random.choice(respostas_perguntas))
        return

    if any(p in texto_limpo for p in ["linda", "perfeita", "maravilhosa", "deusa"]):
        bot.send_message(message.chat.id, random.choice(elogios))
        return

    if any(p in texto_limpo for p in ["amor", "gata", "gostosa", "princesa"]):
        bot.send_message(message.chat.id, random.choice(apelidos))
        return

    if len(texto_limpo.split()) > 12:
        frases_longas = [
            "Falou, falou, e no fim... nada que me faça levantar a sobrancelha 💅",
            "Texto grande? Esperando vir com emoção. Até agora: zzz...",
            "Você escreve uma bíblia e quer minha atenção? Só se vier com revelação divina 📜",
            "Tanta palavra pra dizer tão pouco. Mas gostei da tentativa 💁",
            "Me convence em menos de 10 palavras, ou nem tento ler direito."
        ]
        bot.send_message(message.chat.id, random.choice(frases_longas))
        return

    if any(p in texto_limpo for p in ["idiota", "feia", "burra", "otária", "chata"]):
        bot.send_message(message.chat.id, random.choice(xingamentos))
        return
    texto = message.text.lower().strip()
    hora = datetime.datetime.now().hour

    # Respostas especiais para saudações
    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            time.sleep(random.uniform(1.5, 3))
            bot.send_message(message.chat.id, random.choice(frases))
            return

    frases_mortas = ["oi", "alguém aí", "ola", "olá", "tudo bem", "e aí"]

    if any(palavra in texto for palavra in frases_mortas):
        print("Ignorou mensagem genérica 💤")
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

    resposta = random.choice(respostas)
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
