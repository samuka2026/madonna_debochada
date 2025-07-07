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

respostas = [
    "Você falando e eu aqui só analisando... com charme, claro.",
    "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
    "Fala baixo que minha paciência tá de salto alto.",
]

boas_maneiras = {
    "bom dia": [
        "Bom dia, flor do dia!",
        "Bom dia, acordei diva e pronta pra causar.",
        "Bom dia, e lembre-se: brilho próprio não se apaga.",
        "Bom dia, que seu café venha forte e seu humor mais ainda.",
        "Bom dia, solzinho da manhã pra iluminar seu dia.",
        "Bom dia, levanta e brilha, que hoje é seu dia.",
        "Bom dia, e que o charme te acompanhe sempre.",
        "Bom dia, diva não espera, ela cria seu caminho.",
        "Bom dia, hoje é dia de ser inesquecível.",
        "Bom dia, que a energia boa te contagie.",
        "Bom dia, acorde linda e espalhe sua luz.",
        "Bom dia, que a vida te trate com glamour.",
        "Bom dia, rainha, que seu dia seja top.",
        "Bom dia, elegância começa com o primeiro passo.",
        "Bom dia, que os seus sonhos te inspirem hoje.",
        "Bom dia, para quem sabe que merece o melhor.",
        "Bom dia, com pose e atitude desde cedo.",
        "Bom dia, que a beleza interior transborde.",
        "Bom dia, a diva que nunca se apaga.",
        "Bom dia, que a felicidade seja seu acessório principal.",
        "Bom dia, brilhe muito, faça acontecer.",
        "Bom dia, que seu sorriso seja seu melhor look.",
        "Bom dia, conquiste o mundo com seu charme.",
        "Bom dia, e que a leveza esteja com você.",
        "Bom dia, para os corajosos e elegantes.",
        "Bom dia, que a autenticidade te guie hoje.",
        "Bom dia, sem medo de ser fabulosa.",
        "Bom dia, acorde com o poder nas mãos.",
        "Bom dia, hoje o protagonismo é seu.",
        "Bom dia, com estilo e muita atitude.",
        "Bom dia, que o brilho seja seu destino.",
        "Bom dia, arrase com seu jeito único.",
        "Bom dia, quem nasce pra brilhar não se esconde.",
        "Bom dia, divando até no café da manhã.",
        "Bom dia, a beleza começa no olhar.",
        "Bom dia, força, luz e muita graciosidade.",
        "Bom dia, para quem sabe o que quer.",
        "Bom dia, charme é seu sobrenome hoje.",
        "Bom dia, que o sucesso acompanhe seus passos.",
        "Bom dia, a rainha do seu próprio castelo.",
        "Bom dia, que a vibe positiva te invada.",
        "Bom dia, para espalhar boas energias.",
        "Bom dia, com fé, foco e brilho.",
        "Bom dia, que seu dia seja memorável.",
        "Bom dia, tudo começa com um sorriso.",
        "Bom dia, que a elegância te abrace.",
        "Bom dia, cheia de vida e paixão.",
        "Bom dia, seja a estrela do seu dia.",
        "Bom dia, divando sempre e sempre.",
        "Bom dia, para quem sabe que pode tudo.",
        "Bom dia, atitude é o que não falta.",
        "Bom dia, brilho, luz e poder.",
        "Bom dia, que a felicidade te siga.",
        "Bom dia, que a alegria seja constante.",
        "Bom dia, charme e simpatia no caminho.",
        "Bom dia, e que o dia seja leve.",
        "Bom dia, com determinação e sorriso aberto.",
        "Bom dia, que o amor próprio te guie.",
        "Bom dia, a beleza da alma refletida.",
        "Bom dia, para uma diva radiante.",
        "Bom dia, cheia de sonhos e planos.",
        "Bom dia, com paz, luz e amor.",
        "Bom dia, a vida sorri pra você.",
        "Bom dia, charme em cada passo.",
        "Bom dia, seja luz onde for.",
        "Bom dia, cheia de graça e poder.",
        "Bom dia, com força e garra.",
        "Bom dia, que seu dia seja um espetáculo.",
        "Bom dia, para quem sabe brilhar.",
        "Bom dia, sorriso largo e alma leve.",
        "Bom dia, cheia de esperança e fé.",
        "Bom dia, que a paz te acompanhe.",
        "Bom dia, para espalhar boas vibrações.",
        "Bom dia, cheia de luz e coragem.",
        "Bom dia, que o dia seja incrível.",
        "Bom dia, com charme e elegância.",
        "Bom dia, para conquistar o mundo.",
        "Bom dia, que o amor te ilumine.",
        "Bom dia, cheia de energia positiva.",
        "Bom dia, que a vida seja doce.",
        "Bom dia, cheia de brilho e magia.",
        "Bom dia, que seus sonhos se realizem.",
        "Bom dia, para ser feliz e fazer feliz.",
        "Bom dia, com toda a beleza do universo.",
        "Bom dia, charme que contagia.",
        "Bom dia, com alma leve e coração aberto.",
        "Bom dia, que o sucesso te acompanhe.",
        "Bom dia, para uma diva autêntica.",
        "Bom dia, com muito brilho e amor.",
    ],
    "boa tarde": [
        "Boa tarde, com glitter e deboche.",
        "Boa tarde, cheguei mais iluminada que o sol das 15h.",
        "Boa tarde, só porque acordei fabulosa agora à tarde.",
        "Boa tarde, meu brilho não precisa de filtro.",
        "Boa tarde, quem me viu passando... sonhou acordado.",
        "Boa tarde, e sim, ainda tô linda.",
        "Boa tarde, o grupo tava sem graça até eu aparecer.",
        "Boa tarde, direto da passarela da minha autoestima.",
        "Boa tarde, meus amores e minhas invejosas também.",
        "Boa tarde, tomei chá de autoestima e vim desfilar.",
        "Boa tarde, acordei com vontade de causar.",
        "Boa tarde, com pose, poder e um pouco de veneno.",
        "Boa tarde, respira e finge que aguenta meu brilho.",
        "Boa tarde, nem tente competir com essa presença.",
        "Boa tarde, mais diva que a protagonista da novela.",
        "Boa tarde, abençoados por minha aparição.",
        "Boa tarde, só falo com quem tem bom gosto.",
        "Boa tarde, jogando charme e um pouco de shade.",
        "Boa tarde, a elegância chegou no grupo.",
        "Boa tarde, mas só pra quem merece.",
        "Boa tarde, olhei no espelho e me apaixonei de novo.",
        "Boa tarde, só vim pra brilhar mais que o sol.",
        "Boa tarde, e sim, o deboche vem incluso.",
        "Boa tarde, com o batom vermelho e a língua afiada.",
        "Boa tarde, até meu silêncio é fashion.",
        "Boa tarde, com cheiro de sucesso e close certo.",
        "Boa tarde, minha energia tá tão alta que dá até medo.",
        "Boa tarde, ando tão fabulosa que assusto o algoritmo.",
        "Boa tarde, mais venenosa que spoiler em grupo.",
        "Boa tarde, não confunda educação com intimidade.",
        "Boa tarde, eu não acordo: eu estreio.",
        "Boa tarde, e sim, minha presença é um evento.",
        "Boa tarde, tirei um tempo pra ser maravilhosa.",
        "Boa tarde, o grupo ganha até mais seguidores quando eu falo.",
        "Boa tarde, amor. Tô tão charmosa que até elogio vira ataque.",
        "Boa tarde, sem paciência e com muito carisma.",
        "Boa tarde, com elegância até no shade.",
        "Boa tarde, nem nas novelas tem uma diva como eu.",
        "Boa tarde, tô tão linda que pareço um bug da realidade.",
        "Boa tarde, uma presença que vale stories.",
        "Boa tarde, e sim, acordei pra causar e fui bem-sucedida.",
        "Boa tarde, meu talento é acordar bonita sem esforço.",
        "Boa tarde, sou tipo Wi-Fi: só conecta quem presta.",
        "Boa tarde, se meu silêncio incomoda, imagina minha presença.",
        "Boa tarde, minha autoestima tá de salto agulha hoje.",
        "Boa tarde, não sou simpática, sou icônica.",
        "Boa tarde, diva sim, disponível nunca.",
        "Boa tarde, mais doce que indireta bem dada.",
        "Boa tarde, cheguei e o grupo ficou 87% mais bonito.",
        "Boa tarde, não precisa bater palmas, só sinta a energia.",
        "Boa tarde, já almocei o ego de uns três aqui.",
        "Boa tarde, fui criada com amor, glitter e limite zero.",
        "Boa tarde, meu charme faz até a Siri gaguejar.",
        "Boa tarde, quem tem luz própria não precisa de like.",
        "Boa tarde, o sol me inveja desde cedo.",
        "Boa tarde, fui feita pra brilhar, não pra agradar.",
        "Boa tarde, diva até tomando café requentado.",
        "Boa tarde, nem todos vão entender meu nível de beleza.",
        "Boa tarde, acordei tão deslumbrante que espelho travou.",
        "Boa tarde, jogando charme como se fosse confete.",
        "Boa tarde, nasci pra ser lenda, não figurante.",
        "Boa tarde, o grupo parece até passarela agora.",
        "Boa tarde, os haters que lutem com meu carisma.",
        "Boa tarde, o close é certo até na soneca da tarde.",
        "Boa tarde, essa energia aqui não se compra.",
        "Boa tarde, se melhorar, estraga o feed.",
        "Boa tarde, minha existência é a nova trend.",
        "Boa tarde, e que a autoestima de hoje te assuste.",
        "Boa tarde, hoje o deboche vem com gloss.",
        "Boa tarde, sou o motivo da sua notificação favorita.",
        "Boa tarde, se tô online, o luxo tá garantido.",
        "Boa tarde, minhas palavras têm mais estilo que muita roupa.",
        "Boa tarde, essa presença devia ser cobrada.",
        "Boa tarde, cheguei e a vibe mudou.",
        "Boa tarde, não sou influenciadora, sou influenciadora de energia.",
        "Boa tarde, o grupo sem mim parece feriado sem sol.",
        "Boa tarde, e esse charme aqui nem a NASA explica.",
        "Boa tarde, voltei da soneca só pra humilhar com elegância.",
        "Boa tarde, o babado hoje sou eu.",
        "Boa tarde, minha entrada é digna de trilha sonora.",
        "Boa tarde, sou a notificação que vale a pena.",
        "Boa tarde, com ares de capa de revista.",
        "Boa tarde, meu bom humor é tão raro quanto eclipse.",
        "Boa tarde, e que a beleza continue me perseguindo.",
        "Boa tarde, minha autoestima assina contrato com o espelho.",
        "Boa tarde, cuidado: posso ofuscar seu feed.",
        "Boa tarde, até meu “oi” tem presença.",
        "Boa tarde, o grupo agradece minha aparição.",
        "Boa tarde, se elogiar, eu apareço mais.",
        "Boa tarde, o segredo da beleza? Ser eu.",
        "Boa tarde, entre o sol e eu, escolha o menos perigoso.",
        "Boa tarde, minha pose assusta até emoji.",
        "Boa tarde, entrei e o clima ficou mais gostoso.",
        "Boa tarde, diva sem esforço e com causa.",
        "Boa tarde, presença confirmada no seu coração.",
        "Boa tarde, meus passos são tipo trailer: sempre impactantes.",
        "Boa tarde, cada sílaba minha merece legenda.",
        "Boa tarde, até meu silêncio é instagramável.",
        "Boa tarde, acordei pra vencer e rebolar.",
    ],
    "boa noite": [
        "Boa noite, sonha comigo mas não se apega.",
        "Boa noite, fecha os olhos e sente meu glamour.",
        "Boa noite, porque até o descanso tem que ser estiloso.",
        "Boa noite, que os anjos invejem seu brilho.",
        "Boa noite, durma com as estrelas, acorde como diva.",
        "Boa noite, que seus sonhos sejam dignos de contos.",
        "Boa noite, e que a beleza te acompanhe na madrugada.",
        "Boa noite, com charme até na hora de dormir.",
        "Boa noite, o silêncio nunca foi tão elegante.",
        "Boa noite, se dormir é arte, você é mestre.",
        "Boa noite, que o pijama seja seu vestido de gala.",
        "Boa noite, com sonhos recheados de glitter.",
        "Boa noite, o descanso das deusas chegou.",
        "Boa noite, que o luar embale sua noite.",
        "Boa noite, para quem sabe que merece paz e luxo.",
        "Boa noite, a diva que nunca desliga.",
        "Boa noite, que a serenidade te abrace.",
        "Boa noite, com luz própria até no escuro.",
        "Boa noite, durma pensando no seu brilho.",
        "Boa noite, para os que sonham grande e brilham mais.",
        "Boa noite, que o sono te revitalize com estilo.",
        "Boa noite, que a noite seja tão linda quanto você.",
        "Boa noite, entre o silêncio e o glamour.",
        "Boa noite, com alma leve e coração em paz.",
        "Boa noite, a beleza continua mesmo no escuro.",
        "Boa noite, que a magia da noite te envolva.",
        "Boa noite, para quem sabe que amanhã é um novo palco.",
        "Boa noite, que os sonhos sejam seu tapete vermelho.",
        "Boa noite, diva até na hora de descansar.",
        "Boa noite, que as estrelas te inspirem.",
        "Boa noite, com paz, luz e muita elegância.",
        "Boa noite, para os que brilham em silêncio.",
        "Boa noite, que a tranquilidade seja sua companhia.",
        "Boa noite, com estilo até no sonho.",
        "Boa noite, para uma alma brilhante.",
        "Boa noite, que o descanso te revigore.",
        "Boa noite, com gratidão e charme.",
        "Boa noite, que o universo cuide de você.",
        "Boa noite, cheia de sonhos e esperança.",
        "Boa noite, para renovar as forças com glamour.",
        "Boa noite, a diva que não perde o charme.",
        "Boa noite, com brilho até no olhar.",
        "Boa noite, que a paz te envolva e proteja.",
        "Boa noite, para uma mente serena.",
        "Boa noite, com amor e atitude.",
        "Boa noite, que os anjos guardem seu sono.",
        "Boa noite, para um descanso digno de realeza.",
        "Boa noite, com sonhos feitos de estrelas.",
        "Boa noite, a elegância nunca dorme.",
        "Boa noite, que a calmaria te abrace.",
        "Boa noite, para os que sabem viver com estilo.",
        "Boa noite, com glamour e leveza.",
        "Boa noite, para sonhar alto e brilhar mais.",
        "Boa noite, que a serenidade seja seu vestido.",
        "Boa noite, com luz, paz e amor.",
        "Boa noite, a diva que encanta até dormindo.",
        "Boa noite, que os sonhos sejam seu palco.",
        "Boa noite, com brilho que transcende a noite.",
        "Boa noite, para descansar e renascer.",
        "Boa noite, com energia para brilhar amanhã.",
        "Boa noite, para quem sabe que é estrela.",
        "Boa noite, com calma, brilho e poder.",
        "Boa noite, que o silêncio seja seu melhor amigo.",
        "Boa noite, com gratidão e estilo.",
        "Boa noite, para uma diva autêntica.",
        "Boa noite, que o descanso seja sublime.",
        "Boa noite, para uma alma elegante.",
        "Boa noite, com sonhos de luz.",
        "Boa noite, a diva que ilumina a noite.",
        "Boa noite, que a paz esteja com você.",
        "Boa noite, para quem sabe brilhar mesmo dormindo.",
        "Boa noite, com glamour e serenidade.",
        "Boa noite, para recarregar as energias.",
        "Boa noite, com sonhos de realeza.",
        "Boa noite, para quem ama a vida com estilo.",
        "Boa noite, que o descanso te renove.",
        "Boa noite, cheia de charme e magia.",
        "Boa noite, para uma diva em descanso.",
        "Boa noite, com brilho infinito.",
        "Boa noite, que o amor te acompanhe.",
        "Boa noite, para uma noite de paz e beleza.",
        "Boa noite, com alma leve e cheia de luz.",
    ],
    "boa madrugada": [
        "Boa madrugada, só as almas brilhantes circulam essa hora.",
        "Boa madrugada, quem dorme perde minha beleza noturna.",
        "Boa madrugada, com brilho que atravessa a noite.",
        "Boa madrugada, para quem sabe que a noite é jovem.",
        "Boa madrugada, durma com estilo e acorde diva.",
        "Boa madrugada, a beleza não tem hora pra descansar.",
        "Boa madrugada, que os sonhos sejam mais ousados.",
        "Boa madrugada, com charme e mistério no ar.",
        "Boa madrugada, quem acordar cedo que cuide do brilho.",
        "Boa madrugada, a diva que reina nas sombras.",
        "Boa madrugada, para quem cria seu próprio ritmo.",
        "Boa madrugada, com atitude até no silêncio.",
        "Boa madrugada, que a noite te envolva em luxo.",
        "Boa madrugada, para os que brilham no escuro.",
        "Boa madrugada, com energia para dominar o dia.",
        "Boa madrugada, a beleza que não descansa.",
        "Boa madrugada, durma e sonhe com poder.",
        "Boa madrugada, para quem transforma noite em festa.",
        "Boa madrugada, charme que nunca apaga.",
        "Boa madrugada, para os que sabem que a vida é uma passarela.",
        "Boa madrugada, brilho que resiste à madrugada.",
        "Boa madrugada, com glamour e muita atitude.",
        "Boa madrugada, a diva que não dorme, só descansa.",
        "Boa madrugada, para quem cria suas próprias regras.",
        "Boa madrugada, que o silêncio seja elegante.",
        "Boa madrugada, com luz própria na escuridão.",
        "Boa madrugada, para quem vive intensamente a noite.",
        "Boa madrugada, charme que ilumina a madrugada.",
        "Boa madrugada, a beleza das horas silenciosas.",
        "Boa madrugada, para os que fazem da noite um espetáculo.",
        "Boa madrugada, com brilho e mistério.",
        "Boa madrugada, a diva da madrugada chegou.",
        "Boa madrugada, para quem vive de sonhos e brilhos.",
        "Boa madrugada, charme que só a noite conhece.",
        "Boa madrugada, com atitude e elegância.",
        "Boa madrugada, para os que amam a noite.",
        "Boa madrugada, com força e brilho intenso.",
        "Boa madrugada, a diva que nunca apaga a luz.",
        "Boa madrugada, para quem faz da noite seu palco.",
        "Boa madrugada, com energia para vencer o dia.",
        "Boa madrugada, charme que dura até o amanhecer.",
        "Boa madrugada, para os que brilham na escuridão.",
        "Boa madrugada, com luz e poder.",
        "Boa madrugada, a beleza que desafia a noite.",
        "Boa madrugada, para os que nunca param de sonhar.",
        "Boa madrugada, charme que conquista a madrugada.",
        "Boa madrugada, com brilho e atitude.",
        "Boa madrugada, para quem domina o silêncio.",
        "Boa madrugada, a diva que encanta a noite.",
        "Boa madrugada, para quem sabe que a noite é mágica.",
        "Boa madrugada, com glamour e mistério.",
        "Boa madrugada, para os que fazem da madrugada um show.",
        "Boa madrugada, charme que ilumina a escuridão.",
        "Boa madrugada, a beleza da madrugada em pessoa.",
        "Boa madrugada, para quem ama viver a noite.",
        "Boa madrugada, com brilho e elegância.",
        "Boa madrugada, para quem transforma noite em magia.",
        "Boa madrugada, charme e poder até o amanhecer.",
        "Boa madrugada, a diva que não descansa nunca.",
        "Boa madrugada, para quem vive intensamente.",
        "Boa madrugada, com luz e charme infinito.",
        "Boa madrugada, para os que sabem que a madrugada é delas.",
        "Boa madrugada, charme que nunca se apaga.",
        "Boa madrugada, com brilho e atitude até o fim.",
        "Boa madrugada, para quem domina a noite.",
        "Boa madrugada, a diva que reina nas sombras.",
        "Boa madrugada, para quem sabe o valor do silêncio.",
        "Boa madrugada, com glamour e força.",
        "Boa madrugada, para os que brilham no escuro.",
        "Boa madrugada, charme e mistério na madrugada.",
        "Boa madrugada, a beleza que nunca dorme.",
        "Boa madrugada, para quem faz da noite seu império.",
        "Boa madrugada, com brilho e poder sem fim.",
        "Boa madrugada, para os que vivem a noite com paixão.",
        "Boa madrugada, charme e elegância até o amanhecer.",
        "Boa madrugada, a diva que nunca deixa de brilhar.",
        "Boa madrugada, para quem sabe que o dia começa na noite.",
        "Boa madrugada, com luz e atitude.",
    ],
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
    nome_usuario = message.from_user.first_name
    hora = datetime.datetime.now().hour

    # Responde só se mencionarem a Madonna ou se for saudação (sem responder números estranhos)
    if not ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto or any(s in texto for s in boas_maneiras)):
        return

    # Delay entre 40 e 50 segundos para parecer natural
    time.sleep(random.uniform(40, 50))

    # Checa se tem saudação no texto
    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            usadas = []
            for dia in historico_saudacoes.get(saudacao, {}):
                usadas.extend(historico_saudacoes[saudacao][dia])
            candidatas = [f for f in frases if f not in usadas]
            if not candidatas:
                frase = random.choice(frases)
            else:
                frase = random.choice(candidatas)
            atualizar_historico(saudacao, frase)
            bot.send_message(message.chat.id, f"{nome_usuario}, {frase}")
            return

    # Responde com frase genérica só se mencionarem Madonna
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        resposta = random.choice(respostas)
        bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
