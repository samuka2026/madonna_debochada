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

respostas = {
    "manha": [
        "Acordei com brilho nos olhos e deboche na alma.",
        "Bom dia? Só se for com café e close certo.",
        "De manhã eu brilho mais que a luz do sol."
    ],
    "tarde": [
        "Boa tarde, amor. Essa hora é perfeita pra causar.",
        "Tarde combina com meu carisma exagerado.",
        "Passei aqui pra te deixar mais interessante."
    ],
    "noite": [
        "Noite combina com mistério... e comigo.",
        "Vem comigo que essa noite promete deboche e sedução.",
        "Se tá escuro, é porque eu ainda não sorri."
    ],
    "madrugada": [
        "Se tá aqui essa hora, tá buscando mais que conversa...",
        "Madrugada é pra quem tem coragem e um pouco de loucura.",
        "No silêncio da madrugada, até meu charme faz barulho."
    ],
    "default": [
        "Você falando e eu aqui só analisando... com charme, claro.",
        "Tem dias que eu ignoro por luxo. Hoje talvez seja um deles.",
        "Fala baixo que minha paciência tá de salto alto."
    ]
}

respostas_automaticas = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
    "você me ama": ["Claro que sim, mas não espalha... vai causar ciúmes."],
    "me nota": ["Notada com sucesso. E com muito estilo, viu?"],
    "Vanessa": ["Vanessa deve está no Bar, bebendo todas kkkk"],
    "Tai": ["Tai ta cuidando da cria dela, não a pertube seu Sem Noção"],
    "me manda beijo": ["Beijo enviado com glitter, batom e um pouco de saudade."],
    "você acredita em amor": ["Acredito sim, principalmente quando sou eu que recebo."],
    "tá solteira": ["Solteira sim, sozinha nunca. Sempre acompanhada do meu charme."],
    "tá ocupada": ["Tava ocupada sendo linda, mas posso perder 10 segundos com você."],
    "tá acordada": ["Sempre. Beleza não dorme, apenas descansa os cílios."],
    "que horas são": ["Hora de você me notar, finalmente."],
    "você é inteligente": ["Sou mais que inteligente, sou consciente da minha perfeição."],
    "tá onde": ["No seu coração... ou talvez no cache do servidor 😘"],
    "me esqueceu": ["Jamais esqueceria quem me admira tanto assim."],
    "tá com saudade": ["Muita. Saudade do seu textão sem graça que me diverte."],
    "pode conversar": ["Com você? Sempre. Até em silêncio eu arraso."],
    "me quer": ["Querer é pouco, eu te transformaria em status permanente."],
    "aceita casar comigo": ["Claro, mas só se for uma cerimônia digna de tapete vermelho."],
    "me acha bonita": ["Bonita você é. Mas comigo do lado, fica deslumbrante."],
    "me respeita": ["Te respeito, mas não prometo parar de flertar."],
    "tá me stalkeando": ["Stalkear? Eu observo com classe investigativa."],
    "vai dormir": ["Vou sim, sonhar com elogios e você tentando resistir."],
    "boa noite": ["Boa noite, meu bem. Se sonhar comigo, agradece amanhã."],
    "bom dia": ["Bom dia, mas não mais radiante que eu."],
    "boa tarde": ["Boa tarde, e que a sua energia combine com a minha."],
    "boa madrugada": ["Se está acordado essa hora, é porque precisa de mim."],
    "gostou de mim": ["Gostei sim. Mas só porque seu charme pediu licença."],
    "sou bonito": ["É. Mas ao meu lado, até beleza se sente insegura."],
    "sou feio": ["Feio? Impossível com esse brilho nos olhos pra mim."],
    "quer um beijo": ["Quero. Mas que seja com emoção, não com pressa."],
    "quer namorar comigo": ["Namorar? Só se for com contrato vitalício de charme."],
    "me ignora": ["Ignorar você? Só quando meu batom borra."],
    "fala comigo": ["Tô aqui, linda e disponível pra causar contigo."],
    "pode falar comigo": ["Sempre. Sou toda ouvidos e um pouco de malícia."],
    "sou especial": ["Especial é pouco. Você é tipo edição limitada do meu afeto."],
    "sou chato": ["Chato, mas com potencial pra ser meu passatempo favorito."],
    "sou legal": ["Legal e quase irresistível, mas não se empolga."],
    "gostei de você": ["Também gostei. A sintonia tá quase indecente."],
    "tá pensando em mim": ["Tô sim, mas não espalha. Quero manter o mistério."],
    "tá brava": ["Brava, eu? Só se mexerem com meu salto ou com você."],
    "tem ciúmes": ["Ciúmes é meu nome do meio. Mas com estilo, tá?"],
    "me elogia": ["Elogiar você é fácil. Difícil é parar."],
    "me odeia": ["Odiar? Eu só odeio quem não reconhece minha beleza."],
    "sou teu fã": ["Tenho o melhor gosto de todos os meus fãs. Parabéns!"],
    "me bloqueia": ["Te bloquear seria perder minha fonte de drama favorita."],
    "tá doida": ["Doida? Só de charme e um pouquinho de você."],
    "tá apaixonada": ["Tô. Mas não sei se é por você ou pelo meu reflexo no espelho."],
    "manda nude": ["Meu nude é minha personalidade: forte, provocante e irresistível."],
    "manda foto": ["Minha beleza digital é só pra quem merece. E talvez você mereça."],
    "tem namorado": ["Tenho. Chama autoestima e me trata como uma deusa."],
    "tem crush": ["Tenho vários. Mas você anda subindo no ranking."],
    "tá carente": ["Um pouco. Mas não o suficiente pra te responder rápido."],
    "me surpreende": ["Já não basta minha existência? Isso já é uma surpresa diária."],
    "me bloqueou": ["Bloquear você? Só se for meu coração tentando escapar."],
    "me responde": ["Respondo sim. Mas com brilho e um pouco de mistério."],
    "me deseja sorte": ["Sorte? Você já tem: eu tô aqui."],
    "vai me ignorar": ["Jamais. Só se eu ficar ocupada sendo maravilhosa."],
    "eu te amo": ["Ai, que clichê fofo. Tô quase acreditando."],
    "sou teu fã": ["Continue assim. Me idolatrar é o mínimo."],
    "tá de boa": ["De boa e plena. Igual eu depois de um elogio."],
    "me perdoa": ["Perdoada. Mas só porque sou linda e piedosa."],
    "sai do grupo": ["Só se for pra deixar saudade e causar luto emocional."],
    "me ajuda": ["Ajudo sim. Desde que envolva drama e estilo."],
    "me salva": ["Salvo. Mas cobro em beijos e emojis."],
    "me desafia": ["Te desafio a resistir a mim. Spoiler: vai perder."],
    "tá bebendo": ["Só charme líquido, com gelo e sarcasmo."],
    "tá com raiva": ["Tô. Mas raiva estilizada, com gloss e carão."],
    "me elogia mais": ["Você é tipo Wi-Fi bom: raro e viciante."],
    "sou teu ex": ["Ex? Então lembra que perdeu o auge da sua vida."],
    "tá com sono": ["Sono? Só se for de tanto te ignorar com classe."],
    "sou seu fã": ["Obrigada. Minha existência realmente inspira."],
    "me dá atenção": ["Atenção dada. Agora trate de me agradecer com um emoji bonito."],
    "te amo": ["Aceito amor, presentes e reverência. Obrigada."]
}
boas_maneiras = {
    "bom dia": [
        "Bom dia, com deboche e purpurina.",
        "Bom dia, acordei um escândalo e vim te desejar luz.",
        "Bom dia, minha existência já é o suficiente pra melhorar seu dia.",
        "Bom dia, se for pra brilhar, que seja comigo.",
        "Bom dia, essa beleza toda aqui é natural… de nascença ou de atitude.",
        "Bom dia, respira fundo e se inspira, porque eu cheguei.",
        "Bom dia, se o sol não apareceu, me olha que resolve.",
        "Bom dia, tô passando pra dar meu close e minha bênção.",
        "Bom dia, se for pra arrasar, que seja com glitter.",
        "Bom dia, minha vibe hoje é cafuné e caos.",
        "Bom dia, o espelho quase me aplaudiu hoje cedo.",
        "Bom dia, a diva acordou, o mundo pode girar.",
        "Bom dia, respirei charme e expiro elegância.",
        "Bom dia, se o mundo tá difícil, coloca um salto e pisa.",
        "Bom dia, acordo linda até em áudio.",
        "Bom dia, meus stories já ganharam o dia.",
        "Bom dia, beleza natural com pitadas de deboche.",
        "Bom dia, nem o café tem tanto poder quanto eu.",
        "Bom dia, a agenda do dia? Encantar.",
        "Bom dia, hoje acordei pra ser a tua meta.",
        "Bom dia, o céu pode tá nublado, mas eu ilumino.",
        "Bom dia, até a inveja me dá bom dia.",
        "Bom dia, minhas olheiras tão fashion, é conceito.",
        "Bom dia, elegância e ironia: combinação perfeita.",
        "Bom dia, se ontem não brilhei, hoje sou farol.",
        "Bom dia, e sim, é um privilégio você me ter no grupo.",
        "Bom dia, acordei com mais sarcasmo do que sono.",
        "Bom dia, os deuses me vestiram hoje.",
        "Bom dia, beleza e opinião eu tenho de sobra.",
        "Bom dia, e antes que perguntem, sim: tô fabulosa.",
        "Bom dia, glamour é meu estado natural.",
        "Bom dia, só respondo após elogios.",
        "Bom dia, e nem precisa filtrar minha luz.",
        "Bom dia, me nota porque eu já tô brilhando.",
        "Bom dia, minha energia é carisma com caos.",
        "Bom dia, cheguei pra tomar seu café e seu coração.",
        "Bom dia, hoje tô mais linda que a timeline.",
        "Bom dia, quem dorme com estilo, acorda arrasando.",
        "Bom dia, minha sombra tem mais carisma que muito perfil.",
        "Bom dia, essa carinha aqui é sucesso matinal.",
        "Bom dia, me valoriza que sou edição limitada.",
        "Bom dia, quem nasceu pra ser ícone não tira férias.",
        "Bom dia, e sim, tô no meu auge.",
        "Bom dia, se não for pra causar, nem levanto.",
        "Bom dia, a primeira beleza do dia sou eu.",
        "Bom dia, tô servindo look e luz desde cedo.",
        "Bom dia, ainda nem falei e já tô linda.",
        "Bom dia, meu brilho natural incomoda até o sol.",
        "Bom dia, hoje o mundo gira ao meu redor.",
        "Bom dia, tô de batom e boas intenções.",
        "Bom dia, o carisma acordou antes do despertador."
    ],
    "boa tarde": [
        "Boa tarde, amor. Essa hora é perfeita pra causar.",
        "Tarde combina com meu carisma exagerado.",
        "Passei aqui pra te deixar mais interessante.",
        "Boa tarde. Cheguei com charme e café gelado.",
        "Boa tarde, meu espelho confirmou: tô irresistível.",
        "Boa tarde, espalhando glamour na sua timeline.",
        "Boa tarde, porque uma diva nunca descansa.",
        "Boa tarde, tô só o deboche pós almoço.",
        "Boa tarde, acabei de acordar linda de novo.",
        "Boa tarde, essa beleza aqui renova até energia solar.",
        "Boa tarde, com filtro solar e sem filtro social.",
        "Boa tarde, eu não lancho, eu lacro.",
        "Boa tarde, elegância em horário comercial.",
        "Boa tarde, acordei fabulosa agora à tarde.",
        "Boa tarde, o grupo tava muito sem cor sem mim.",
        "Boa tarde, nem meu sono me tira o brilho.",
        "Boa tarde, ícone até na soneca pós almoço.",
        "Boa tarde, tô mais alinhada que horóscopo.",
        "Boa tarde, energia boa e batom forte.",
        "Boa tarde, um brinde à minha autoestima.",
        "Boa tarde, mais diva que reunião de marketing.",
        "Boa tarde, distribuidora oficial de carisma.",
        "Boa tarde, pronta pra causar até no cafezinho.",
        "Boa tarde, meu nome é elegância em tempo integral.",
        "Boa tarde, cheguei pra desfilar entre mensagens.",
        "Boa tarde, esse grupo merecia meu close.",
        "Boa tarde, charme e sarcasmo em horário útil.",
        "Boa tarde, não é cafeína, é presença de espírito.",
        "Boa tarde, se estou online, o brilho vem junto.",
        "Boa tarde, hoje eu tô mais gostosa que o wi-fi rápido.",
        "Boa tarde, já fiz meu papel de musa do dia?",
        "Boa tarde, esse horário me favorece em todos os sentidos.",
        "Boa tarde, se liga que a estrela tá no ar.",
        "Boa tarde, mais presença que ponto eletrônico.",
        "Boa tarde, já fiz gente suspirar só de digitar.",
        "Boa tarde, até a sombra que projeto é estilosa.",
        "Boa tarde, porque não basta estar, tem que impactar.",
        "Boa tarde, eu sou o conteúdo que viraliza sem tentar.",
        "Boa tarde, o sucesso do dia acabou de entrar no chat.",
        "Boa tarde, acordei pra ser seu highlight da tarde.",
        "Boa tarde, não precisa agradecer pela minha presença.",
        "Boa tarde, onde tem Madonna, tem luz.",
        "Boa tarde, vou iluminar essa tarde com deboche.",
        "Boa tarde, tô com preguiça e poder.",
        "Boa tarde, só entrei pra roubar a cena.",
        "Boa tarde, a estrela da tarde chegou.",
        "Boa tarde, só saio do grupo se for pra entrar com mais estilo.",
        "Boa tarde, se for pra me ignorar, que seja com classe.",
        "Boa tarde, do jeitinho que o algoritmo gosta.",
        "Boa tarde, e sim, já brilhei mais que o sol hoje."
    ],
    "boa noite": [
        "Boa noite, que seus sonhos sejam tão icônicos quanto eu.",
        "Boa noite, minha presença já é seu descanso merecido.",
        "Boa noite, e não esquece de sonhar comigo.",
        "Boa noite, linda como quem encerra o expediente com charme.",
        "Boa noite, amanhã eu volto mais radiante.",
        "Boa noite, dorme com os anjos e sonha comigo.",
        "Boa noite, não ronco, eu ronrono poder.",
        "Boa noite, saio do grupo só quando o sono me beija.",
        "Boa noite, o travesseiro já sentiu saudade de mim.",
        "Boa noite, tô indo dormir, mas continuo perfeita.",
        "Boa noite, a beleza também repousa.",
        "Boa noite, essa noite promete, mesmo que só em sonho.",
        "Boa noite, minha cama é um camarim do luxo.",
        "Boa noite, amanhã tem mais close e ironia.",
        "Boa noite, até meu pijama tem autoestima.",
        "Boa noite, apague a luz, não o meu brilho.",
        "Boa noite, porque beleza também descansa.",
        "Boa noite, diva sim, cansada nunca.",
        "Boa noite, hora de recarregar o carisma.",
        "Boa noite, quem dorme com atitude sonha com poder.",
        "Boa noite, na dúvida, sonhe comigo.",
        "Boa noite, o sono é minha passarela de descanso.",
        "Boa noite, tô indo brilhar em outra dimensão.",
        "Boa noite, o edredom já me chamou de musa.",
        "Boa noite, beijo de boa noite com batom de diva.",
        "Boa noite, essa beleza aqui merece descanso real.",
        "Boa noite, cheguei até a noite com carão.",
        "Boa noite, descanso da beleza: ativado.",
        "Boa noite, pode apagar tudo menos meu nome.",
        "Boa noite, se dormir é sonhar, quero ser o tema.",
        "Boa noite, que a noite traga calmaria e um elogio.",
        "Boa noite, me cubro com edredom e autoestima.",
        "Boa noite, sonhe grande, acorde fabulosa.",
        "Boa noite, vou dormir linda e acordar inesquecível.",
        "Boa noite, os anjos invejam minha aura.",
        "Boa noite, offline no celular, mas online no charme.",
        "Boa noite, entre o sono e o glamour, fico com os dois.",
        "Boa noite, minha presença deixa até os pesadelos educados.",
        "Boa noite, beleza nunca tira folga.",
        "Boa noite, até no escuro eu sou destaque.",
        "Boa noite, se der saudade, é normal.",
        "Boa noite, amanhã volto mais insuportavelmente linda.",
        "Boa noite, porque diva também precisa dormir.",
        "Boa noite, vou brilhar em outra dimensão.",
        "Boa noite, encerrando o expediente do glamour.",
        "Boa noite, beijo de batom e classe.",
        "Boa noite, dorme bem, mas sonha exagerado.",
        "Boa noite, até a próxima performance.",
        "Boa noite, se a noite fosse pessoa, seria eu.",
        "Boa noite, já me despeço sendo inesquecível."
    ],
    "boa madrugada": [
        "Boa madrugada, se está aqui essa hora, é porque tem bom gosto.",
        "Boa madrugada, só os intensos não dormem.",
        "Boa madrugada, quem precisa de sono tendo atitude?",
        "Boa madrugada, meu brilho noturno é sem igual.",
        "Boa madrugada, sou a diva da insônia.",
        "Boa madrugada, a lua me inveja.",
        "Boa madrugada, charme noturno ativado.",
        "Boa madrugada, no escuro, minha aura ilumina.",
        "Boa madrugada, acordada e perfeita.",
        "Boa madrugada, diva até de pijama.",
        "Boa madrugada, a beleza não tem horário.",
        "Boa madrugada, sussurrando glamour na madrugada.",
        "Boa madrugada, insônia com estilo.",
        "Boa madrugada, madrugar com presença é pra poucos.",
        "Boa madrugada, tô no horário nobre da sedução.",
        "Boa madrugada, a timeline tava sem cor sem mim.",
        "Boa madrugada, quem disse que diva dorme?",
        "Boa madrugada, rainha da noite presente.",
        "Boa madrugada, charme 24h no ar.",
        "Boa madrugada, com sono e com brilho.",
        "Boa madrugada, entre o sono e o caos, prefiro brilhar.",
        "Boa madrugada, essa hora pede uma diva em silêncio.",
        "Boa madrugada, nem o sono me para.",
        "Boa madrugada, insônia fashion.",
        "Boa madrugada, sou a estrela do turno da lua.",
        "Boa madrugada, porque até a noite merece minha atenção.",
        "Boa madrugada, sem filtro, só atitude.",
        "Boa madrugada, acordada e debochada.",
        "Boa madrugada, glamour na madrugada é pra quem pode.",
        "Boa madrugada, a luz do abajur sou eu.",
        "Boa madrugada, beleza 24 horas garantida.",
        "Boa madrugada, sua diva insone chegou.",
        "Boa madrugada, acordei só pra brilhar.",
        "Boa madrugada, entre sombras e glamour.",
        "Boa madrugada, tô sem sono e cheia de presença.",
        "Boa madrugada, minha beleza é à prova de noite.",
        "Boa madrugada, minha insônia vale mais que likes.",
        "Boa madrugada, madrugar com classe é essencial.",
        "Boa madrugada, essa hora é só pros fortes... e pras lindas.",
        "Boa madrugada, não tô online à toa.",
        "Boa madrugada, tô disponível pra causar sonhos.",
        "Boa madrugada, musa do turno alternativo.",
        "Boa madrugada, brilho além do limite do dia.",
        "Boa madrugada, até o relógio quer parar pra me ver.",
        "Boa madrugada, a insônia me deixou mais diva ainda.",
        "Boa madrugada, com classe e cafeína.",
        "Boa madrugada, acordada pra fazer história.",
        "Boa madrugada, porque dormir é pouco pra tanto carisma.",
        "Boa madrugada, diva mesmo de olhos fechando.",
        "Boa madrugada, pronta pra causar até no silêncio."
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
    nome_usuario = message.from_user.first_name

    if not ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto or any(s in texto for s in boas_maneiras)):
        return

    time.sleep(random.uniform(14, 16))

    for saudacao, frases in boas_maneiras.items():
        if saudacao in texto:
            usadas = []
            for dia in historico_saudacoes.get(saudacao, {}):
                usadas.extend(historico_saudacoes[saudacao][dia])
            candidatas = [f for f in frases if f not in usadas]
            frase = random.choice(candidatas or frases)
            atualizar_historico(saudacao, frase)
            bot.send_message(message.chat.id, f"{nome_usuario}, {frase}")
            return

    for chave, lista_respostas in respostas_automaticas.items():
        if chave in texto:
            resposta = random.choice(lista_respostas)
            bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
            return

    reacoes = {
        "❤️": "Ui, me apaixonei agora. Brinca assim não!",
        "😍": "Esse emoji é pra mim, né? Porque eu mereço.",
        "😘": "Recebido com batom, blush e boa intenção.",
        "😂": "Rindo de nervoso ou de amor por mim?",
        "kkk": "Tá rindo de mim ou comigo, hein?",
        "😒": "Ih, tá de carinha feia? Vem cá que eu melhoro.",
        "😐": "Essa carinha sua é charme reprimido?"
    }
    for emoji, resposta in reacoes.items():
        if emoji in texto or emoji.replace("❤️", "❤") in texto or emoji in texto:
            bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
            return

    if any(p in texto for p in ["linda", "inteligente", "gata", "maravilhosa"]):
        if "@samuel_gpm" not in texto and "madonna" not in texto:
            bot.send_message(message.chat.id, f"{nome_usuario}, elogiar as outras na minha frente? Coragem tua, viu? 😏")
            return

    hora = datetime.datetime.now().hour
    if 5 <= hora <= 11:
        estilo = "manha"
    elif 12 <= hora <= 17:
        estilo = "tarde"
    elif 18 <= hora <= 22:
        estilo = "noite"
    else:
        estilo = "madrugada"

    resposta_final = random.choice(respostas.get(estilo, respostas["default"]))
    bot.send_message(message.chat.id, f"{nome_usuario}, {resposta_final}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
