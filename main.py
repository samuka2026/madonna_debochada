# ✅ BOT MADONNA REFORMULADA - main.py
# Versão especial com listas .json na raiz, saudacões por gênero e horário, elogios, desejos para Apollo,
# defesa automática do Apollo, submissão ao dono quando mencionada, e estrutura organizada e leve. 💅💖

from flask import Flask, request
import telebot
import os
import random
import time
import json
import threading
from datetime import datetime, timedelta

# ✅ CONFIGURAÇÕES DO GRUPO
GRUPO_ID = -1002606951329              # Substitua pelo ID do seu grupo
DONO_ID = 1481389775                   # ID do dono da Madonna (submissão)
TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ Função para carregar arquivos .json da raiz do projeto
def carregar_lista(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# ✅ Listas .json da raiz do projeto
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

# ✅ Listas temáticas para respostas inteligentes
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

# ✅ Detecta se é mulher com base no @ ou nome
def e_mulher(user):
    username = (user.username or "").lower()
    if username in [u.lower() for u in usuarios_mulheres]:
        return True
    elif username in [u.lower() for u in usuarios_homens]:
        return False
    nome = (user.first_name or "").lower()
    return nome[-1] in ["a", "e"]

# ✅ Controles globais
ultimos_envios = {}
ultimos_envios_saudacoes = {}
ultimos_envios_geral = {}
frases_guardadas = []
frases_usadas = []
usuarios_registrados = {}
enquetes_ativas = {}
ranking_acertos = {}
ultima_enquete = {"frase": "", "autor": "", "acertaram": []}

# ✅ Envia mensagem com atraso
def enviar_com_delay(delay_segundos, chat_id, texto, reply_id=None):
    def tarefa():
        bot.send_message(chat_id, texto, reply_to_message_id=reply_id)
    threading.Timer(delay_segundos, tarefa).start()

# ✅ Handler principal
@bot.message_handler(func=lambda msg: True)
def responder(msg):
    texto = msg.text.lower()
    user_id = msg.from_user.id
    nome = msg.from_user.first_name or msg.from_user.username or "Amor"
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 🔹 COMANDO DO DONO PARA CRIAR ENQUETE MANUALMENTE
    if user_id == DONO_ID and texto == "/enquete":
        try:
            if not frases_guardadas:
                bot.send_message(GRUPO_ID, "Não há frases registradas para criar a enquete 😅")
                return

            candidatas = [f for f in frases_guardadas if f not in frases_usadas]
            if not candidatas:
                bot.send_message(GRUPO_ID, "Todas as frases já foram usadas! 🤷‍♀️")
                return

            frase, autor_id = random.choice(candidatas)
            frases_usadas.append((frase, autor_id))

            if len(usuarios_registrados) < 4:
                bot.send_message(GRUPO_ID, "Não há usuários suficientes para criar a enquete 😅")
                return

            autor_nome = usuarios_registrados.get(autor_id, "???")
            outros = [nome for uid, nome in usuarios_registrados.items() if uid != autor_id]
            if len(outros) < 3:
                bot.send_message(GRUPO_ID, "Não há usuários suficientes para criar opções da enquete 😅")
                return

            opcoes = random.sample(outros, 3) + [autor_nome]
            random.shuffle(opcoes)

            pergunta = f"Quem disse essa frase?\n\n“{frase}”"
            bot.send_poll(GRUPO_ID, pergunta, opcoes, is_anonymous=False, type="regular")
            bot.send_message(GRUPO_ID, "Enquete manual criada! 🎉")
        except Exception as e:
            bot.send_message(GRUPO_ID, f"Erro ao criar enquete: {e}")
        return

    # Registrar o usuário e a frase se for válida
    if msg.text:
        texto_limpo = msg.text.strip()
        palavras = texto_limpo.split()
        if len(palavras) >= 3 and not all(ch in "kKcC" for ch in texto_limpo):
            if len(texto_limpo) > 5:
                usuarios_registrados[user_id] = nome
                frases_guardadas.append((texto_limpo, user_id))

    # 👑 Submissão ao dono
    if user_id == DONO_ID and frases_dono and ("madonna" in texto or f"@{bot.get_me().username.lower()}" in texto):
        frase = random.choice(frases_dono)
        enviar_com_delay(40, msg.chat.id, frase, msg.message_id)
        return

    # 💬 Mencionaram a Madonna
    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        if "bom dia" in texto:
            frase = random.choice(bom_dia_mulher if mulher else bom_dia_homem)
        elif "boa tarde" in texto:
            frase = random.choice(boa_tarde_mulher if mulher else boa_tarde_homem)
        elif "boa noite" in texto or "boa madrugada" in texto:
            if agora.hour < 21:
                frase = random.choice(boa_noite_entrada_mulher if mulher else boa_noite_entrada_homem)
            else:
                frase = random.choice(boa_noite_dormir_mulher if mulher else boa_noite_dormir_homem)
        else:
            frase = random.choice(men_m if mulher else men_h)
        enviar_com_delay(60, msg.chat.id, frase, msg.message_id)
        return

    # 🎯 Resposta inteligente por tema
    if user_id in ultimos_envios_geral and (agora - ultimos_envios_geral[user_id]) < timedelta(minutes=1):
        return
    for tema, dados in temas.items():
        if any(palavra in texto for palavra in dados["keywords"]):
            if dados["respostas"]:
                frase = random.choice(dados["respostas"])
                enviar_com_delay(random.randint(10, 30), msg.chat.id, frase, msg.message_id)
                ultimos_envios_geral[user_id] = agora
            return

# ✅ Handler de respostas de enquetes
@bot.poll_answer_handler()
def receber_voto(poll_answer):
    poll_id = poll_answer.poll_id
    user_id = poll_answer.user.id
    first_name = poll_answer.user.first_name

    if poll_id not in enquetes_ativas:
        return

    resposta_certa = enquetes_ativas[poll_id]["resposta"]
    if poll_answer.option_ids and resposta_certa == poll_answer.option_ids[0]:
        ranking_acertos[user_id] = ranking_acertos.get(user_id, 0) + 1
        if ultima_enquete:
            ultima_enquete["acertaram"].append(first_name)

# ✅ Função para disparar enquetes periódicas
def disparar_enquete_periodica():
    global ultima_enquete
    while True:
        agora = datetime.now()
        if 6 <= agora.hour < 24:  # só das 6h até meia-noite
            chat_id = GRUPO_ID

            # postar resultado da última enquete
            if ultima_enquete and ultima_enquete["frase"]:
                frase = ultima_enquete["frase"]
                autor = ultima_enquete["autor"]
                acertaram = ultima_enquete["acertaram"]

                texto = f"✅ **Resultado da última enquete**\n\n"
                texto += f"🗣️ **Quem falou a frase:**\n\"{frase}\"\n→ **{autor}**\n\n"

                if acertaram:
                    texto += f"🎯 **Acertaram:**\n" + "\n".join([f"- {nome}" for nome in acertaram]) + "\n\n"
                else:
                    texto += "😅 **Ninguém acertou.**\n\n"

                if ranking_acertos:
                    texto += "🏆 **Ranking parcial do dia:**\n"
                    for uid, pontos in sorted(ranking_acertos.items(), key=lambda x: x[1], reverse=True):
                        nome = usuarios_registrados.get(uid, "??")
                        texto += f"{pontos} pts - {nome}\n"

                bot.send_message(chat_id, texto)

            # pegar nova frase sem repetir
            frases_disponiveis = [f for f in frases_guardadas if f not in frases_usadas]
            if frases_disponiveis:
                frase, autor_id = random.choice(frases_disponiveis)
                frases_usadas.append((frase, autor_id))

                usuarios = list(usuarios_registrados.keys())
                random.shuffle(usuarios)
                corretor = autor_id
                # Pega 3 usuários aleatórios que não sejam o autor
                opcoes = [usuarios_registrados[u] for u in usuarios if u != corretor]
                opcoes = random.sample(opcoes, min(3, len(opcoes)))  # garante 3 opções
                opcoes.append(usuarios_registrados[corretor])  # adiciona o autor
                random.shuffle(opcoes)

                pergunta = f"📝 **Enquete:** Quem disse esta frase?\n\n💬 \"{frase}\""
                msg = bot.send_poll(
                    chat_id,
                    pergunta,
                    opcoes,
                    type="quiz",
                    correct_option_id=opcoes.index(usuarios_registrados[corretor]),
                    is_anonymous=False
                )


                ultima_enquete = {
                    "frase": frase,
                    "autor": usuarios_registrados[corretor],
                    "acertaram": []
                }
                enquetes_ativas[msg.poll.id] = {"resposta": msg.poll.correct_option_id, "frase": frase}

        time.sleep(3600)

# ✅ Função para postar ranking final à meia-noite
def postar_ranking_final():
    global ranking_acertos
    while True:
        agora = datetime.now()
        if agora.hour == 0 and agora.minute == 0:
            if ranking_acertos:
                texto = "🏆 Ranking final do dia:\n"
                ordenado = sorted(ranking_acertos.items(), key=lambda x: x[1], reverse=True)
                for uid, pontos in ordenado:
                    nome = usuarios_registrados.get(uid, "??")
                    texto += f"- {nome}: {pontos} pontos\n"
                bot.send_message(GRUPO_ID, texto)
                ranking_acertos = {}
        time.sleep(60)

# inicia a thread do ranking final
threading.Thread(target=postar_ranking_final, daemon=True).start()

# 🔁 ROTA FLASK PARA WEBHOOK
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/")
def home():
    url = f"{RENDER_URL}/{TOKEN}"
    if bot.get_webhook_info().url != url:
        bot.remove_webhook()
        bot.set_webhook(url=url)
    return "Madonna online! ✨", 200

# 🔄 Mantém o bot vivo no Render
def manter_vivo():
    import requests
    while True:
        try:
            requests.get(RENDER_URL)
        except:
            pass
        time.sleep(600)

# 🚀 INICIAR
if __name__ == "__main__":
    threading.Thread(target=manter_vivo).start()
    threading.Thread(target=disparar_enquete_periodica, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
