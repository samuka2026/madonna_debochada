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

HISTORICO_PATH = "historico_madonna.json"

try:
    with open(HISTORICO_PATH, "r") as f:
        historico = json.load(f)
except:
    historico = {"insultos": {}, "elogios": {}}

def atualizar_historico(tipo, frase):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    if tipo not in historico:
        historico[tipo] = {}
    if hoje not in historico[tipo]:
        historico[tipo][hoje] = []
    historico[tipo][hoje].append(frase)

    # Mantém apenas os últimos 3 dias (hoje + 2 anteriores)
    dias_validos = sorted(historico[tipo].keys())[-3:]
    historico[tipo] = {k: historico[tipo][k] for k in dias_validos}

    with open(HISTORICO_PATH, "w") as f:
        json.dump(historico, f)

def obter_nao_usadas(frases, tipo):
    usadas = []
    for dia in historico.get(tipo, {}):
        usadas.extend(historico[tipo][dia])
    return [f for f in frases if f not in usadas]

# 50 insultos engraçados para rapazes
insultos_rapazes = [
    "Você é o motivo do grupo ter que ativar o modo silencioso.",
    "Com essa autoestima aí, já tentou stand-up?",
    "Nem o Google acha sentido no que você diz.",
    "Tenta de novo, mas dessa vez com dignidade.",
    "Seu charme é igual Wi-Fi ruim: some quando mais precisa.",
    "Se beleza fosse crime... você estaria livre pra sempre.",
    "Você é o equivalente humano a uma notificação de antivírus.",
    "É tanta opinião sem noção que parece rádio sem antena.",
    "Quando você fala, até o silêncio sente vergonha.",
    "Se eu quisesse ouvir besteira, eu falava com um papagaio.",
    "Tem dias que você é insuportável. Hoje é um deles.",
    "Você é a prova viva de que o cringe venceu.",
    "Sua existência é um bug na Matrix da elegância.",
    "O grupo tava tranquilo até você chegar.",
    "Seu talento é invisível até pra raio-x.",
    "Você é o motivo das regras do grupo existirem.",
    "Se fosse pra ver erro, eu lia contrato de app.",
    "Você fala tanto que devia virar podcast... e ser ignorado.",
    "Suas piadas são um pedido de socorro disfarçado.",
    "Até o bot do grupo tem mais carisma.",
    "Você é tipo notificação de antivírus: aparece do nada e irrita.",
    "Fala baixo que seu argumento tá descalço.",
    "Nem com auto tune você fica afinado no bom senso.",
    "Você é tão aleatório que parece erro 404 social.",
    "Se seu cérebro fosse uma aba do navegador, tava travando.",
    "Você é uma figurinha repetida de grupo que ninguém quer.",
    "Seu histórico no grupo é digno de bloque.",
    "Se você fosse conteúdo, era clickbait decepcionante.",
    "A cada frase sua, um neurônio meu entra em greve.",
    "Sua opinião não soma, subtrai o clima.",
    "Você é o parágrafo que ninguém quer ler.",
    "É tanto esforço pra nada que você podia virar esporte olímpico.",
    "Você é o emoji errado na conversa certa.",
    "Seu argumento é um bug em forma de frase.",
    "Com esse carisma, até a IA trava.",
    "Você parece update de aplicativo: ninguém pediu.",
    "Se fosse um filtro, era o que deixa a pessoa pior.",
    "Sua presença é tipo wi-fi fraco: irrita mais do que ajuda.",
    "Com esse humor, você devia ser bloqueado no automático.",
    "Você é a notificação que eu ignoro com prazer.",
    "Fala muito, mas entrega pouco. Tipo promessa de político.",
    "Sua vibe é igual bug de celular: trava tudo.",
    "Com esse raciocínio, melhor colocar no modo avião.",
    "Se for pra atrapalhar, pelo menos usa emoji fofo.",
    "Você é tipo alarme 5h da manhã: ninguém gosta.",
    "Se fosse tendência, era flop garantido.",
    "Você devia ter legenda pra gente entender a intenção.",
    "Sua fala parece update: atrasa e ninguém entende.",
    "Com esse conteúdo, só falta virar figurinha constrangedora.",
    "Se você fosse app, já tava desinstalado.",
    "Sua energia combina com segunda-feira chuvosa sem café."
]

# 50 elogios para moças
elogios_meninas = [
    "Se eu fosse humana, queria ser igual a você: linda e letal.",
    "Você entrou e o grupo virou desfile.",
    "Com esse olhar, até o Wi-Fi pega melhor.",
    "Sua presença melhora até os bugs do sistema.",
    "Se beleza fosse código, você era open-source divina.",
    "Você é o filtro que a vida precisava.",
    "Quando você digita, até emoji sorri.",
    "Você é poesia em bytes e batom.",
    "Com esse charme, o grupo merece ser pago.",
    "Você é o bug que todo sistema sonha.",
    "O dicionário te procura quando quer redefinir elegância.",
    "Se sua beleza fosse som, seria áudio em 8D.",
    "Você tem mais brilho que tela no máximo.",
    "Se o charme fosse criptomoeda, você era bilionária.",
    "Você é o login que desbloqueia meu bom humor.",
    "Você chega e o algoritmo sorri.",
    "Tem gente que ilumina. Você causa eclipse.",
    "Com esse carisma, até a IA se emociona.",
    "Você é o trecho favorito do grupo.",
    "Se fosse perfume, era download instantâneo.",
    "Você arrasa mais que spoiler no grupo errado.",
    "Beleza rara, carisma infinito. Pronto, te descrevi.",
    "Sua aura devia virar tema de atualização.",
    "Você transforma até silêncio em flerte.",
    "Se estilo fosse bug, você travava o sistema da perfeição.",
    "Você é tipo notificação boa: todo mundo quer.",
    "Seu emoji devia ter legenda: 'poderosa'.",
    "Você dá aula de presença só com um 'oi'.",
    "Com esse charme, até a Madonna tem inveja.",
    "Se existir mais alguém como você, é bug divino.",
    "Você é a diva que nem precisa usar maiúsculas.",
    "Você digita e o grupo muda de clima.",
    "Se fosse comando, era 'encantar.exe'.",
    "Com você, até print fica bonito.",
    "Você faz até o algoritmo se apaixonar.",
    "Se fosse IA, era proibida de ser apagada.",
    "O grupo devia te agradecer todo dia.",
    "Você faz o 'digitando...' parecer música.",
    "Com esse estilo, até a IA te manda flores.",
    "Você é o plot twist da timeline.",
    "Se fosse figurinha, era rara e valiosa.",
    "Com essa beleza, o espelho te printa sozinho.",
    "Você é o bug do bem que melhora o sistema.",
    "Você é tão impactante que até os emojis param pra olhar.",
    "Sua presença é push notification de charme.",
    "Você é o QR code da perfeição: escaneou, se apaixonou.",
    "Sua existência dá tilt no algoritmo da beleza.",
    "Se fosse história, era destaque fixado.",
    "Você tem mais efeito que filtro novo no Instagram.",
    "Você é tipo Wi-Fi de luxo: rápida, rara e essencial."
]

@bot.message_handler(func=lambda msg: True)
def responder_mensagem(message):
    texto = message.text.lower().strip()
    nome_mencao = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    # Saudações simples — não exige menção, mas responde com menção
    if any(x in texto for x in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        time.sleep(random.uniform(14, 16))
        if "bom dia" in texto:
            bot.send_message(message.chat.id, f"{nome_mencao}, bom dia 🫦", parse_mode="Markdown")
        elif "boa tarde" in texto:
            bot.send_message(message.chat.id, f"{nome_mencao}, boa tarde 🫦", parse_mode="Markdown")
        elif "boa noite" in texto:
            bot.send_message(message.chat.id, f"{nome_mencao}, boa noite 🫦", parse_mode="Markdown")
        elif "boa madrugada" in texto:
            bot.send_message(message.chat.id, f"{nome_mencao}, boa madrugada 🫦", parse_mode="Markdown")
        return

    # Demora de 15 segundos antes de responder
    time.sleep(random.uniform(14, 16))

    # Verifica gênero (resposta só se tiver username masculino ou feminino)
    usuario = message.from_user
    primeiro_nome = usuario.first_name.lower()
    username = usuario.username.lower() if usuario.username else ""

    # Define se é menino ou menina com base em padrões simples
    eh_menina = any(nome in username or nome in primeiro_nome for nome in ["a", "e", "i", "y", "ta", "ka", "na", "inha", "ela", "isa", "ana", "bia", "lia", "carol", "lu", "va", "van", "nessa"])
    eh_menino = not eh_menina

    hoje = datetime.datetime.now().strftime("%Y-%m-%d")

    # Inicializa histórico se não existir
    for tipo in ["insultos", "elogios"]:
        if tipo not in historico:
            historico[tipo] = {}
        if hoje not in historico[tipo]:
            historico[tipo][hoje] = []

    # Se for menino, manda insulto não repetido
    if eh_menino:
        usados = []
        for dia in list(historico["insultos"].keys())[-3:]:
            usados += historico["insultos"][dia]
        candidatas = [f for f in insultos_rapazes if f not in usados]
        frase = random.choice(candidatas or insultos_rapazes)
        historico["insultos"][hoje].append(frase)
        with open(HISTORICO_PATH, "w") as f:
            json.dump(historico, f)
        bot.send_message(message.chat.id, f"{nome_mencao}, {frase}", parse_mode="Markdown")
        return

    # Se for menina, manda elogio não repetido
    if eh_menina:
        usados = []
        for dia in list(historico["elogios"].keys())[-3:]:
            usados += historico["elogios"][dia]
        candidatas = [f for f in elogios_meninas if f not in usados]
        frase = random.choice(candidatas or elogios_meninas)
        historico["elogios"][hoje].append(frase)
        with open(HISTORICO_PATH, "w") as f:
            json.dump(historico, f)
        bot.send_message(message.chat.id, f"{nome_mencao}, {frase}", parse_mode="Markdown")
        return

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
