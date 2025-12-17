from flask import Flask, request
import telebot
import os
import random
import time
import json
import threading
from datetime import datetime, timedelta

# ✅ CONFIGURAÇÕES DO GRUPO
GRUPO_ID = -1002606951329
DONO_ID = 1481389775
TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ Função para carregar arquivos .json
def carregar_lista(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# ✅ Carregamento de Listas
bom_dia_mulher = carregar_lista("bom_dia_mulher.json")
bom_dia_homem = carregar_lista("bom_dia_homem.json")
boa_tarde_mulher = carregar_lista("boa_tarde_mulher.json")
boa_tarde_homem = carregar_lista("boa_tarde_homem.json")
boa_noite_entrada_mulher = carregar_lista("boa_noite_entrada_mulher.json")
boa_noite_entrada_homem = carregar_lista("boa_noite_entrada_homem.json")
boa_noite_dormir_mulher = carregar_lista("boa_noite_dormir_mulher.json")
boa_noite_dormir_homem = carregar_lista("boa_noite_dormir_homem.json")
elogios_mulher = carregar_lista("elogios_mulher.json")
elogios_homem = carregar_lista("elogios_homem.json")
desejos_apollo = carregar_lista("desejos_apollo.json")
men_m = carregar_lista("menções_mulher.json")
men_h = carregar_lista("menções_homem.json")
frases_dono = carregar_lista("frases_dono.json")
defesa_apollo = carregar_lista("defesa_apollo.json")
usuarios_mulheres = carregar_lista("usuarios_mulheres.json")
usuarios_homens = carregar_lista("usuarios_homens.json")

temas = {
    "cafe": {"keywords": ["café", "cafezinho", "expresso", "capuccino"], "respostas": carregar_lista("temas/cafe.json")},
    "comida": {"keywords": ["pizza", "hamburguer", "lanche", "almoço", "janta", "fome"], "respostas": carregar_lista("temas/comida.json")},
    "namoro": {"keywords": ["namoro", "ficar", "beijo", "crush", "coração partido"], "respostas": carregar_lista("temas/namoro.json")},
    "preguiça": {"keywords": ["preguiça", "sono", "dormir", "descansar", "cansado"], "respostas": carregar_lista("temas/preguica.json")},
    "fofoca": {"keywords": ["mentira", "fofoca", "treta", "confusão", "barraco"], "respostas": carregar_lista("temas/fofoca.json")},
    "motivacao": {"keywords": ["triste", "desanimado", "cansada", "sem forças", "fracasso"], "respostas": carregar_lista("temas/motivacao.json")},
    "uno": {"keywords": ["uno", "comprar carta", "+4", "baralho uno"], "respostas": carregar_lista("temas/uno.json")},
    "quiz": {"keywords": ["kiss", "beijo", "beijar", "beijinho"], "respostas": carregar_lista("temas/kiss.json")},
    "jogo_velha": {"keywords": ["jogo da velha", "velha", "tabuleiro", "x ganha", "o ganha"], "respostas": carregar_lista("temas/jogo_velha.json")},
    "desenho": {"keywords": ["desenho", "pintar", "desenhei", "arte", "pintura"], "respostas": carregar_lista("temas/desenho.json")},
    "deuses": {"keywords": ["zeus", "hades", "poseidon", "afrodite", "ares", "hera", "deus", "deusa", "olimpico", "olimpíadas", "mitologia"], "respostas": carregar_lista("temas/deuses.json")},
    "provocacao": {"keywords": ["ganhei", "venci", "campeão", "vou ganhar", "ninguém me vence"], "respostas": carregar_lista("temas/provocacao.json")}
}

# ✅ Controles globais
ultimos_envios_geral = {}
frases_guardadas = []
frases_usadas = []
usuarios_registrados = {}
enquetes_ativas = {}
ranking_acertos = {}
ultima_enquete = {"frase": "", "autor": "", "acertaram": []}

def e_mulher(user):
    username = (user.username or "").lower()
    if username in [u.lower() for u in usuarios_mulheres]: return True
    if username in [u.lower() for u in usuarios_homens]: return False
    nome = (user.first_name or "").lower()
    return nome[-1] in ["a", "e"]

def enviar_com_delay(delay_segundos, chat_id, texto, reply_id=None):
    def tarefa():
        try:
            bot.send_message(chat_id, texto, reply_to_message_id=reply_id, parse_mode="Markdown")
        except: pass
    threading.Timer(delay_segundos, tarefa).start()

# ✅ Handler Principal Corrigido
@bot.message_handler(func=lambda msg: True)
def responder(msg):
    texto = msg.text.lower()
    user_id = msg.from_user.id
    nome = msg.from_user.first_name or "Amor"
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 1. Coleta de frases para enquete (Sempre rodando)
    if len(texto.split()) >= 3 and not texto.startswith("/"):
        usuarios_registrados[user_id] = nome
        frases_guardadas.append((msg.text, user_id))

    # 2. Comando Manual de Enquete
    if user_id == DONO_ID and texto == "/enquete":
        disparar_enquete_periodica(manual=True)
        return

    # 3. Defesa Automática do Apollo
    if "apollo" in texto and any(p in texto for p in ["chato", "feio", "bobo", "lixo", "odeio", "ruim"]):
        frase = random.choice(defesa_apollo) if defesa_apollo else "Não fale assim do meu Apollo! 💅"
        enviar_com_delay(2, msg.chat.id, frase, msg.message_id)
        return

    # 4. Desejos para o Apollo (Quando mencionado com carinho)
    if "apollo" in texto and any(p in texto for p in ["lindo", "querido", "bom", "amo", "perfeito"]):
        frase = random.choice(desejos_apollo) if desejos_apollo else "Ele é um príncipe, não é? ✨"
        enviar_com_delay(3, msg.chat.id, frase, msg.message_id)
        return

    # 5. Mencionaram a Madonna (Saudações e Submissão ao Dono)
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        if user_id == DONO_ID and frases_dono:
            frase = random.choice(frases_dono)
        elif "bom dia" in texto:
            frase = random.choice(bom_dia_mulher if mulher else bom_dia_homem)
        elif "boa tarde" in texto:
            frase = random.choice(boa_tarde_mulher if mulher else boa_tarde_homem)
        elif "boa noite" in texto:
            frase = random.choice(boa_noite_entrada_mulher if mulher else boa_noite_entrada_homem)
        else:
            # Chance de mandar um elogio aleatório ao ser mencionada
            if random.random() < 0.3: # 30% de chance
                frase = random.choice(elogios_mulher if mulher else elogios_homem)
            else:
                frase = random.choice(men_m if mulher else men_h)
        
        enviar_com_delay(3, msg.chat.id, frase, msg.message_id)
        return

    # 6. Gatilhos de Temas (com trava de 10 segundos)
    if user_id in ultimos_envios_geral and (agora - ultimos_envios_geral[user_id]) < timedelta(seconds=10):
        return

    for tema, dados in temas.items():
        if any(palavra in texto for palavra in dados["keywords"]):
            if dados["respostas"]:
                frase = random.choice(dados["respostas"])
                enviar_com_delay(3, msg.chat.id, frase, msg.message_id)
                ultimos_envios_geral[user_id] = agora
                return

@bot.poll_answer_handler()
def receber_voto(poll_answer):
    poll_id = poll_answer.poll_id
    user_id = poll_answer.user.id
    if poll_id in enquetes_ativas:
        if poll_answer.option_ids[0] == enquetes_ativas[poll_id]["resposta"]:
            ranking_acertos[user_id] = ranking_acertos.get(user_id, 0) + 1
            ultima_enquete["acertaram"].append(poll_answer.user.first_name)

def disparar_enquete_periodica(manual=False):
    global ultima_enquete
    chat_id = GRUPO_ID
    
    # Posta resultado da anterior
    if ultima_enquete["frase"] and not manual:
        res = f"✅ **Resultado da última enquete**\n\n🗣️ **Frase:** \"{ultima_enquete['frase']}\"\n→ **Autor:** {ultima_enquete['autor']}\n"
        if ultima_enquete["acertaram"]:
            res += f"\n🎯 **Acertaram:** " + ", ".join(ultima_enquete["acertaram"])
        bot.send_message(chat_id, res, parse_mode="Markdown")

    # Cria nova enquete
    candidatas = [f for f in frases_guardadas if f not in frases_usadas]
    if len(candidatas) > 0 and len(usuarios_registrados) >= 4:
        frase, autor_id = random.choice(candidatas)
        frases_usadas.append((frase, autor_id))
        
        autor_nome = usuarios_registrados[autor_id]
        outros = [n for uid, n in usuarios_registrados.items() if uid != autor_id]
        opcoes = random.sample(outros, min(3, len(outros))) + [autor_nome]
        random.shuffle(opcoes)
        
        poll = bot.send_poll(chat_id, f"📝 Quem disse:\n\n\"{frase}\"", opcoes, type="quiz", 
                             correct_option_id=opcoes.index(autor_nome), is_anonymous=False)
        
        ultima_enquete = {"frase": frase, "autor": autor_nome, "acertaram": []}
        enquetes_ativas[poll.poll.id] = {"resposta": poll.poll.correct_option_id}

def loop_enquetes():
    while True:
        agora = datetime.now()
        if 8 <= agora.hour < 23:
            disparar_enquete_periodica()
        time.sleep(3600) # 1 em 1 hora

def postar_ranking_final():
    while True:
        agora = datetime.now()
        if agora.hour == 0 and agora.minute == 0:
            if ranking_acertos:
                txt = "🏆 **Ranking Final do Dia**\n"
                for uid, pts in sorted(ranking_acertos.items(), key=lambda x: x[1], reverse=True):
                    txt += f"- {usuarios_registrados.get(uid, '??')}: {pts} pts\n"
                bot.send_message(GRUPO_ID, txt, parse_mode="Markdown")
                ranking_acertos.clear()
        time.sleep(60)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def home():
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    return "Madonna Online 💅", 200

if __name__ == "__main__":
    threading.Thread(target=loop_enquetes, daemon=True).start()
    threading.Thread(target=postar_ranking_final, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
