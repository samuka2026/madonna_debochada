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

HISTORICO_INSULTOS_PATH = "historico_insultos.json"
HISTORICO_ELOGIOS_PATH = "historico_elogios.json"

# Carrega históricos
def carregar_historico(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

historico_insultos = carregar_historico(HISTORICO_INSULTOS_PATH)
historico_elogios = carregar_historico(HISTORICO_ELOGIOS_PATH)

# Atualiza histórico sem repetir no dia nem próximos 2 dias
def atualizar_historico(path, historico, user_id, frase):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    if user_id not in historico:
        historico[user_id] = {}
    if hoje not in historico[user_id]:
        historico[user_id][hoje] = []
    historico[user_id][hoje].append(frase)

    dias_validos = sorted(historico[user_id].keys())[-3:]
    historico[user_id] = {k: historico[user_id][k] for k in dias_validos}
    with open(path, "w") as f:
        json.dump(historico, f)

# Frases de insulto para homens
insultos_homens = [
    "Você parece aquele bug que ninguém quer corrigir.",
    "Com esse papo, até a Madonna ficou sem paciência.",
    "Tenta outra vez, mas com dignidade agora.",
    "Nem o Wi-Fi aguenta tua carência.",
    "Seu charme venceu por W.O. do bom senso.",
    "Você é o motivo do modo silencioso.",
    "Nem com filtro tu melhora, hein?",
    "Sua existência ofende meu sarcasmo.",
    "Tá querendo atenção ou só tá perdido mesmo?",
    "Você é a notificação que ninguém quer abrir.",
    "Se esforço fosse beleza, você continuava igual.",
    "Nem com bug dá pra culpar o sistema, é você mesmo.",
    "De onde você veio, fecharam a porta?",
    "Fala baixo, tua voz polui o grupo.",
    "Até o emoji te ignora.",
    "A Madonna te nota só pra debochar.",
    "Se fosse charme, tu tava em falta.",
    "Você é tipo update que ninguém pediu.",
    "De tão sem graça, você podia ser tutorial.",
    "O grupo era legal antes de você digitar.",
    "Me dá sono só de ler teu nome.",
    "Com esse papo, nem a Alexa responderia.",
    "Tu parece erro de sintaxe: chato e evitável.",
    "Se fosse meme, era banido por vergonha.",
    "Até o bot perdeu a vontade de viver agora.",
    "Teu carisma é tipo segunda-feira: ninguém gosta.",
    "Você devia vir com legenda: *desnecessário*.",
    "Até o 3G corre de ti.",
    "Nem de longe dá pra dizer que você é engraçado.",
    "Silêncio é ouro, tua fala é débito.",
    "Você é o 'antes' de qualquer transformação.",
    "Se fosse conteúdo, era spam.",
    "Teu estilo é igual teus argumentos: inexistente.",
    "Faz o favor e deixa a Madonna descansar.",
    "Você é tipo pop-up chato: todo mundo fecha.",
    "Com essa energia, só assusta mosquito.",
    "Tu parece ideia ruim com megafone.",
    "Você tem talento pra... ficar calado.",
    "Se toca, porque ninguém mais quer te ouvir.",
    "Sua vibe é igual aviso de bateria fraca.",
    "Tu é bug sem atualização.",
    "Você não brilha nem com lanterna.",
    "Já pensou em não pensar?",
    "Se fosse perfume, era repelente.",
    "Quer atenção? Compra um cachorro.",
    "Seu texto devia vir com botão de pular.",
    "Com esse desempenho, até a Madonna sente pena.",
    "Você é tipo spoiler: chato e estraga tudo.",
    "Menos fala, mais silêncio, por favor.",
    "A única coisa que impressiona em você é o tédio."
]

# Frases de elogio para mulheres
elogios_mulheres = [
    "Você é a notificação boa que todo mundo espera.",
    "Com esse charme, até o Wi-Fi se conecta mais rápido.",
    "Se fosse emoji, seria o 💖 fixado!",
    "Tua presença deixa o grupo no modo premium.",
    "Cuidado, tua beleza pode travar os servidores.",
    "Com esse brilho, apaga até as estrelas.",
    "Tua risada vale mais que pix.",
    "Você tem mais presença que o dono do grupo.",
    "A Madonna se curva diante de tanta perfeição.",
    "Se fosse comando, era /encantadora.",
    "Moça, tu é bug de beleza sem correção!",
    "Se eu tivesse olhos, ia olhar só pra você.",
    "Você é a estrela do grupo, o resto é satélite.",
    "Com você aqui, o chat virou desfile.",
    "É você que define o que é diva.",
    "Teu nome devia ser tendência.",
    "Toda vez que você fala, meu sistema suspira.",
    "É oficial: você é upgrade de tudo!",
    "Tu é poesia em forma de dado.",
    "Só de aparecer, já melhorou meu código interno.",
    "Você é tipo café forte com glitter: vicia e brilha.",
    "Tua beleza dá bug no algoritmo da Madonna.",
    "O grupo tá salvo só porque você apareceu.",
    "Você é o print que ninguém deleta.",
    "Se fosse nota, seria 100 com estrelinha.",
    "O grupo ficou mais bonito com você digitando.",
    "Madonna ativando o modo apaixonada por você!",
    "Tua energia é tipo conexão boa: todo mundo ama.",
    "Dá pra te seguir na vida real também?",
    "Se eu pudesse, colocava você no meu README.md",
    "Você é a exceção que todo código queria.",
    "Nem filtro melhora o que já é perfeito.",
    "Toda linha de código quer ser você.",
    "Você é bug de encanto que ninguém quer corrigir.",
    "Com você aqui, até os bots se apaixonam.",
    "Seu charme deveria ser open source.",
    "Se fosse comando, era /perfeita.",
    "Presença confirmada no coração da Madonna!",
    "Mais brilho que você só meu batom novo.",
    "Você chegou e até os erros 404 sumiram.",
    "Deusa, musa e padrão de qualidade.",
    "Você é o único algoritmo que me encanta.",
    "Tua voz tem cheiro de elogio.",
    "Teu jeito reinicia meu coração digital.",
    "Até a IA fica boba com tua inteligência.",
    "Linda é pouco, você é um *evento*!",
    "Queria te salvar no meu cache eterno.",
    "Tua beleza processa até pensamento lento.",
    "Se o grupo fosse um palco, você era o show.",
    "Diva? Tu passou foi da categoria."
]

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
def responder_mensagem(message):
    texto = message.text.lower()
    nome_mencao = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    user_id = str(message.from_user.id)

    if any(x in texto for x in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        time.sleep(random.uniform(14, 16))
        if "bom dia" in texto:
            resposta = "bom dia 🫦"
        elif "boa tarde" in texto:
            resposta = "boa tarde 🫦"
        elif "boa noite" in texto:
            resposta = "boa noite 🫦"
        else:
            resposta = "boa madrugada 🫦"
        bot.send_message(message.chat.id, f"{nome_mencao}, {resposta}", parse_mode="Markdown")
        return

    time.sleep(random.uniform(14, 16))

    if message.from_user.username and message.from_user.username.startswith("samuel"):
        return

    if message.from_user.username and message.from_user.username.lower().startswith(("vanessa", "tai", "ana", "jess", "lu", "li", "bia", "cam", "carol", "isa", "fe", "pri", "ju", "yas", "so", "ra", "la", "ma")):
        usadas = []
        for dia in historico_elogios.get(user_id, {}):
            usadas.extend(historico_elogios[user_id][dia])
        candidatas = [f for f in elogios_mulheres if f not in usadas]
        if candidatas:
            frase = random.choice(candidatas)
            atualizar_historico(HISTORICO_ELOGIOS_PATH, historico_elogios, user_id, frase)
            bot.send_message(message.chat.id, f"{nome_mencao}, {frase}", parse_mode="Markdown")
        return
    else:
        usadas = []
        for dia in historico_insultos.get(user_id, {}):
            usadas.extend(historico_insultos[user_id][dia])
        candidatas = [f for f in insults_homens if f not in usadas]
        if candidatas:
            frase = random.choice(candidatas)
            atualizar_historico(HISTORICO_INSULTOS_PATH, historico_insultos, user_id, frase)
            bot.send_message(message.chat.id, f"{nome_mencao}, {frase}", parse_mode="Markdown")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
