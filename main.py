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
DONO_ID = 8338739275
TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ Funções de Persistência
def carregar_json(nome_arquivo, default):
    try:
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return default
    except Exception as e:
        print(f"Erro ao carregar {nome_arquivo}: {e}")
        return default

def salvar_json(nome_arquivo, dados):
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar {nome_arquivo}: {e}")

# ✅ Carregamento de Listas Fixas e Dinâmicas
bom_dia_mulher = carregar_json("bom_dia_mulher.json", [])
bom_dia_homem = carregar_json("bom_dia_homem.json", [])
boa_tarde_mulher = carregar_json("boa_tarde_mulher.json", [])
boa_tarde_homem = carregar_json("boa_tarde_homem.json", [])
boa_noite_entrada_mulher = carregar_json("boa_noite_entrada_mulher.json", [])
boa_noite_entrada_homem = carregar_json("boa_noite_entrada_homem.json", [])
boa_noite_dormir_mulher = carregar_json("boa_noite_dormir_mulher.json", [])
boa_noite_dormir_homem = carregar_json("boa_noite_dormir_homem.json", [])
elogios_mulher = carregar_json("elogios_mulher.json", [])
elogios_homem = carregar_json("elogios_homem.json", [])
desejos_apollo = carregar_json("desejos_apollo.json", [])
men_m = carregar_json("menções_mulher.json", [])
men_h = carregar_json("menções_homem.json", [])
frases_dono = carregar_json("frases_dono.json", [])
defesa_apollo = carregar_json("defesa_apollo.json", [])
usuarios_mulheres = carregar_json("usuarios_mulheres.json", [])
usuarios_homens = carregar_json("usuarios_homens.json", [])

# Dados que precisam persistir após reinício
frases_guardadas = carregar_json("backup_frases.json", [])
usuarios_registrados = carregar_json("backup_usuarios.json", {}) # ID: Nome
frases_usadas = carregar_json("backup_frases_usadas.json", [])
ranking_acertos = carregar_json("backup_ranking.json", {})

temas = {
    "cafe": {"keywords": ["café", "cafezinho", "expresso", "capuccino"], "respostas": carregar_json("temas/cafe.json", [])},
    "comida": {"keywords": ["pizza", "hamburguer", "lanche", "almoço", "janta", "fome"], "respostas": carregar_json("temas/comida.json", [])},
    "namoro": {"keywords": ["namoro", "ficar", "beijo", "crush", "coração partido"], "respostas": carregar_json("temas/namoro.json", [])},
    "preguiça": {"keywords": ["preguiça", "sono", "dormir", "descansar", "cansado"], "respostas": carregar_json("temas/preguica.json", [])},
    "fofoca": {"keywords": ["mentira", "fofoca", "treta", "confusão", "barraco"], "respostas": carregar_json("temas/fofoca.json", [])},
    "motivacao": {"keywords": ["triste", "desanimado", "cansada", "sem forças", "fracasso"], "respostas": carregar_json("temas/motivacao.json", [])},
    "uno": {"keywords": ["uno", "comprar carta", "+4", "baralho uno"], "respostas": carregar_json("temas/uno.json", [])},
    "quiz": {"keywords": ["kiss", "beijo", "beijar", "beijinho"], "respostas": carregar_json("temas/kiss.json", [])},
    "jogo_velha": {"keywords": ["jogo da velha", "velha", "tabuleiro", "x ganha", "o ganha"], "respostas": carregar_json("temas/jogo_velha.json", [])},
    "desenho": {"keywords": ["desenho", "pintar", "desenhei", "arte", "pintura"], "respostas": carregar_json("temas/desenho.json", [])},
    "deuses": {"keywords": ["zeus", "hades", "poseidon", "afrodite", "ares", "hera", "deus", "deusa", "olimpico", "olimpíadas", "mitologia"], "respostas": carregar_json("temas/deuses.json", [])},
    "provocacao": {"keywords": ["ganhei", "venci", "campeão", "vou ganhar", "ninguém me vence"], "respostas": carregar_json("temas/provocacao.json", [])}
}

# ✅ Controles globais (voláteis)
ultimos_envios_geral = {}
enquetes_ativas = {}
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

@bot.message_handler(func=lambda msg: True)
def responder(msg):
    texto = msg.text.lower() if msg.text else ""
    user_id = str(msg.from_user.id) # JSON salva keys como string
    nome = msg.from_user.first_name or "Amor"
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 1. Coleta e Persistência
    if len(texto.split()) >= 3 and not texto.startswith("/"):
        if user_id not in usuarios_registrados or (msg.text, user_id) not in frases_guardadas:
            usuarios_registrados[user_id] = nome
            frases_guardadas.append([msg.text, user_id])
            salvar_json("backup_usuarios.json", usuarios_registrados)
            salvar_json("backup_frases.json", frases_guardadas)

    # 2. Comando Manual
    if int(user_id) == DONO_ID and texto == "/enquete":
        disparar_enquete_periodica(manual=True)
        return

    # 3. Gatilhos de Texto (Madonna/Apollo/Temas)
    # [Mantido o resto da sua lógica de respostas aqui por brevidade...]
    if "apollo" in texto and any(p in texto for p in ["chato", "feio", "bobo", "lixo", "odeio", "ruim"]):
        frase = random.choice(defesa_apollo) if defesa_apollo else "Não fale assim do meu Apollo!"
        enviar_com_delay(2, msg.chat.id, frase, msg.message_id)
        return

    if "madonna" in texto or f"@{bot.get_me().username.lower()}" in texto:
        frase = random.choice(men_m if mulher else men_h)
        enviar_com_delay(2, msg.chat.id, frase, msg.message_id)

@bot.poll_answer_handler()
def receber_voto(poll_answer):
    poll_id = poll_answer.poll_id
    user_id = str(poll_answer.user.id)
    if poll_id in enquetes_ativas:
        if poll_answer.option_ids[0] == enquetes_ativas[poll_id]["resposta"]:
            ranking_acertos[user_id] = ranking_acertos.get(user_id, 0) + 1
            ultima_enquete["acertaram"].append(poll_answer.user.first_name)
            salvar_json("backup_ranking.json", ranking_acertos)

def disparar_enquete_periodica(manual=False):
    global ultima_enquete
    chat_id = GRUPO_ID
    
    # Validação
    if len(frases_guardadas) < 1:
        print("DEBUG: Sem frases no banco para enquete.")
        return
    if len(usuarios_registrados) < 4:
        print(f"DEBUG: Usuários insuficientes ({len(usuarios_registrados)}/4).")
        return

    # Posta resultado da anterior
    if ultima_enquete["frase"] and not manual:
        res = f"✅ **Resultado da última enquete**\n\n🗣️ **Frase:** \"{ultima_enquete['frase']}\"\n→ **Autor:** {ultima_enquete['autor']}\n"
        if ultima_enquete["acertaram"]:
            res += f"\n🎯 **Acertaram:** " + ", ".join(ultima_enquete["acertaram"])
        bot.send_message(chat_id, res, parse_mode="Markdown")

    # Filtra frases não usadas
    candidatas = [f for f in frases_guardadas if f not in frases_usadas]
    if not candidatas: 
        frases_usadas.clear() # Reseta se todas foram usadas
        candidatas = frases_guardadas

    frase_escolhida = random.choice(candidatas)
    texto_frase, autor_id = frase_escolhida
    frases_usadas.append(frase_escolhida)
    salvar_json("backup_frases_usadas.json", frases_usadas)
    
    autor_nome = usuarios_registrados.get(str(autor_id), "Desconhecido")
    outros = [n for uid, n in usuarios_registrados.items() if str(uid) != str(autor_id)]
    
    opcoes = random.sample(outros, min(3, len(outros))) + [autor_nome]
    random.shuffle(opcoes)
    
    try:
        poll = bot.send_poll(chat_id, f"📝 Quem disse:\n\n\"{texto_frase}\"", opcoes, type="quiz", 
                             correct_option_id=opcoes.index(autor_nome), is_anonymous=False)
        
        ultima_enquete = {"frase": texto_frase, "autor": autor_nome, "acertaram": []}
        enquetes_ativas[poll.poll.id] = {"resposta": poll.poll.correct_option_id}
    except Exception as e:
        print(f"Erro ao enviar enquete: {e}")

def loop_enquetes():
    while True:
        agora = datetime.now()
        # Tenta enviar a cada 1 hora entre 08h e 23h
        if 8 <= agora.hour < 23:
            disparar_enquete_periodica()
        time.sleep(3600) 

def postar_ranking_final():
    while True:
        agora = datetime.now()
        if agora.hour == 0 and agora.minute == 0:
            if ranking_acertos:
                txt = "🏆 **Ranking Final do Dia**\n"
                # Ordenar ranking
                sorted_rank = sorted(ranking_acertos.items(), key=lambda x: x[1], reverse=True)
                for uid, pts in sorted_rank:
                    nome = usuarios_registrados.get(uid, "Usuário")
                    txt += f"- {nome}: {pts} pts\n"
                bot.send_message(GRUPO_ID, txt, parse_mode="Markdown")
                ranking_acertos.clear()
                salvar_json("backup_ranking.json", ranking_acertos)
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
