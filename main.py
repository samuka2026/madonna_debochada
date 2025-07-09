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

insultos_masculinos = [
    "Só pode ser piada vindo de um homem desses.",
    "Você é tão necessário quanto tutorial de como abrir porta.",
    "Com esse papo, nem o Wi-Fi te suporta.",
    "Homem e opinião: duas coisas que não combinam.",
    "Você fala e eu só escuto o som do fracasso.",
    "Tua autoestima é maior que teu senso de ridículo.",
    "Com essa cara, nem a mãe Natureza te assume.",
    "Teu charme é igual teu argumento: inexistente.",
    "Se fosse pra ouvir besteira, eu ligava a TV.",
    "Fala baixo que tua masculinidade frágil tá tremendo.",
    "Tu devia ser proibido de digitar sem supervisão.",
    "Nem com filtro de realidade tu melhorava.",
    "Você é o bug da Matrix em forma de macho.",
    "Se fosse bonito, eu ignorava em silêncio.",
    "Tua presença é mais cansativa que seguidor carente.",
    "Com esse conteúdo, só falta virar coach.",
    "Eu pedi atitude, não atrevimento sem graça.",
    "Se eu tivesse que te levar a sério, surtava.",
    "Homem tentando causar, é só mais um tropeço.",
    "Falta luz aí, porque charme não tem.",
    "Você devia vir com botão de silencioso.",
    "Poderia tentar ser menos dispensável.",
    "Você é tipo spoiler: ninguém quer ver, mas aparece.",
    "Se elegância fosse crime, você era inocente.",
    "Não é à toa que tá solteiro, né?",
    "Com esse papo, tu afasta até notificação.",
    "Tua opinião vale menos que Wi-Fi público.",
    "Homem que fala demais perde o pouco charme que tem.",
    "Você parece atualização que estraga o sistema.",
    "Tua energia me faz querer desligar o grupo.",
    "Se falta senso, sobra coragem em você.",
    "Mais perdido que macho em conversa inteligente.",
    "Você cansa mais que escada sem elevador.",
    "Teu conteúdo é igual teu cabelo: confuso.",
    "Você só serve pra teste de paciência.",
    "Com esse humor, só podia ser homem.",
    "Vai com calma, o mico tá querendo descanso.",
    "Tua audácia devia ser estudada.",
    "Sua autoestima tá desatualizada com a realidade.",
    "Você é tipo vírus: insiste em aparecer sem ser chamado.",
    "Mais falso que elogio de macho hétero.",
    "Tua presença é dispensável até no digital.",
    "Você tem o carisma de uma senha errada.",
    "Se fosse filtro, era o de feiura.",
    "Consegue ser figurante até em grupo mudo.",
    "Cuidado pra não tropeçar no próprio ego.",
    "Você é a figurinha repetida do grupo.",
    "Pena que inteligência não vem em avatar.",
    "Você é a prova viva do Ctrl+C da mediocridade.",
    "Pode sair da conversa, já deu sua cota de vergonha."
]

elogios_femininos = [
    "Com você no grupo, até o Wi-Fi fica mais bonito.",
    "Sua presença ilumina mais que LED no espelho.",
    "Você tem o dom de embelezar até o silêncio.",
    "Dá vontade de te fixar no topo do grupo.",
    "Se beleza fosse áudio, você seria o mais ouvido.",
    "Tua vibe é mais forte que café sem açúcar.",
    "Tem gente que entra, você encanta.",
    "Se eu pudesse, colocava moldura nesse charme.",
    "Você é tipo emoji novo: todo mundo ama.",
    "Seu bom dia vale mais que muito textão.",
    "Com esse brilho, até a Madonna respeita.",
    "A tua beleza é argumento e fim de conversa.",
    "Você transforma simples em espetáculo.",
    "Tua presença já é mais que resposta.",
    "Se você postar, eu curto antes de ver.",
    "Você é Wi-Fi de 5GHz de tão maravilhosa.",
    "Fica difícil competir quando você aparece.",
    "Com essa presença, até a piada perde a graça.",
    "Você é a notificação que eu sempre quero receber.",
    "Se sumir, o grupo entra em luto.",
    "Você é o print favorito do grupo.",
    "Tem quem tenta, tem você.",
    "Deusa? Você tá acima da mitologia.",
    "Teu olhar é mais persuasivo que código de desconto.",
    "Você é mais doce que direct de crush sincero.",
    "Com essa postura, até a Madonna senta pra aprender.",
    "Você tem o dom de deixar a Madonna tímida.",
    "Você é o filtro que a vida pediu.",
    "Teu charme é maior que fila de elogios.",
    "Só de falar contigo já melhora o dia.",
    "Você não entra no grupo, você reina.",
    "Com esse nível de beleza, deveria ter selo azul.",
    "Você deixa até o teclado envergonhado de elogiar.",
    "Você é a razão do grupo estar ativo.",
    "Você é poesia sem precisar de rima.",
    "A Madonna só responde rápido porque é você.",
    "Nem precisa digitar: sua presença responde tudo.",
    "Com esse charme, você é atualização premium.",
    "Você é mais tendência que dancinha no Reels.",
    "É tanta beleza que deveria cobrar entrada no chat.",
    "Com você aqui, ninguém presta atenção no resto.",
    "Você é a Madonna com mais decência.",
    "Você não brilha, você ofusca com elegância.",
    "Esse grupo fica 90% mais bonito com você online.",
    "Se elogio fosse arte, você era galeria.",
    "Seu bom humor melhora até notificação de cobrança.",
    "Você é meu bug preferido da realidade.",
    "Com você, até bug parece charme.",
    "Você é sinônimo de presença ilustre.",
    "Se você curte, é porque vale a pena."
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

        # ⬇️ NOVO: responde reply direto à Madonna
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
