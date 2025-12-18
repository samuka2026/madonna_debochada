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
    except Exception:
        return default

def salvar_json(nome_arquivo, dados):
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

# ✅ Carregamento de Listas
frases_guardadas = carregar_json("backup_frases.json", [])
usuarios_registrados = carregar_json("backup_usuarios.json", {}) 
frases_usadas = carregar_json("backup_frases_usadas.json", [])
ranking_acertos = carregar_json("backup_ranking.json", {})

# Carrega os temas (ajuste os caminhos se necessário)
def carregar_tema(caminho):
    return carregar_json(caminho, [])

temas = {
    "cafe": {"keywords": ["café", "cafezinho"], "respostas": carregar_tema("temas/cafe.json")},
    "comida": {"keywords": ["pizza", "fome"], "respostas": carregar_tema("temas/comida.json")},
    "deuses": {"keywords": ["zeus", "hades", "deus"], "respostas": carregar_tema("temas/deuses.json")}
}

# ✅ Controles globais
enquetes_ativas = {}
ultima_enquete = {"frase": "", "autor": "", "acertaram": []}

def enviar_com_delay(delay_segundos, chat_id, texto, reply_id=None):
    def tarefa():
        try: bot.send_message(chat_id, texto, reply_to_message_id=reply_id, parse_mode="Markdown")
        except: pass
    threading.Timer(delay_segundos, tarefa).start()

# ✅ Função Principal de Disparo (Corrigida com Feedback)
def disparar_enquete_periodica(manual=False, msg_origem=None):
    global ultima_enquete
    
    # 1. Verificações de segurança
    if not frases_guardadas:
        erro = "❌ Não posso enviar enquete: O banco de frases está vazio! Alguém precisa conversar no grupo primeiro."
        if manual and msg_origem: bot.reply_to(msg_origem, erro)
        return False

    if len(usuarios_registrados) < 4:
        erro = f"❌ Erro: Preciso de pelo menos 4 usuários diferentes registrados para criar as opções. Atualmente tenho {len(usuarios_registrados)}."
        if manual and msg_origem: bot.reply_to(msg_origem, erro)
        return False

    # 2. Lógica de Seleção
    candidatas = [f for f in frases_guardadas if f not in frases_usadas]
    if not candidatas:
        frases_usadas.clear()
        candidatas = frases_guardadas

    frase_escolhida = random.choice(candidatas)
    texto_frase, autor_id = frase_escolhida
    autor_id_str = str(autor_id)
    
    autor_nome = usuarios_registrados.get(autor_id_str, "Alguém")
    
    # Pegar 3 nomes aleatórios que NÃO sejam o autor
    outros_nomes = [nome for uid, nome in usuarios_registrados.items() if uid != autor_id_str]
    if len(outros_nomes) < 3:
        # Se não tiver outros 3, pega nomes genéricos para completar
        outros_nomes += ["Apolo", "Madonna", "Dono do Grupo", "Membro Misterioso"]
    
    opcoes = random.sample(outros_nomes, 3) + [autor_nome]
    random.shuffle(opcoes)
    
    try:
        # Envia resultado da anterior (se houver)
        if ultima_enquete["frase"] and not manual:
            res = f"✅ **Fim da rodada!**\n\n🗣️ **Frase:** \"{ultima_enquete['frase']}\"\n→ **Autor:** {ultima_enquete['autor']}"
            bot.send_message(GRUPO_ID, res, parse_mode="Markdown")

        # Envia a nova
        poll = bot.send_poll(GRUPO_ID, f"📝 Quem disse:\n\n\"{texto_frase}\"", opcoes, 
                             type="quiz", correct_option_id=opcoes.index(autor_nome), is_anonymous=False)
        
        ultima_enquete = {"frase": texto_frase, "autor": autor_nome, "acertaram": []}
        enquetes_ativas[poll.poll.id] = {"resposta": poll.poll.correct_option_id}
        frases_usadas.append(frase_escolhida)
        salvar_json("backup_frases_usadas.json", frases_usadas)
        return True
    except Exception as e:
        if manual and msg_origem: bot.reply_to(msg_origem, f"❌ Erro técnico: {e}")
        return False

@bot.message_handler(func=lambda msg: True)
def responder(msg):
    texto = msg.text.lower() if msg.text else ""
    user_id = str(msg.from_user.id)
    nome = msg.from_user.first_name or "Membro"

    # 1. Registrar Usuário e Frase (Apenas se não for comando)
    if not texto.startswith("/") and len(texto.split()) >= 3:
        if user_id not in usuarios_registrados:
            usuarios_registrados[user_id] = nome
            salvar_json("backup_usuarios.json", usuarios_registrados)
        
        if [msg.text, user_id] not in frases_guardadas:
            frases_guardadas.append([msg.text, user_id])
            salvar_json("backup_frases.json", frases_guardadas)

    # 2. Comando Manual de Enquete
    if int(user_id) == DONO_ID and texto == "/enquete":
        disparar_enquete_periodica(manual=True, msg_origem=msg)
        return

    # 3. Respostas Automáticas (Simplificado para o exemplo)
    if "madonna" in texto:
        bot.reply_to(msg, "Chamou a rainha? 💅")

@bot.poll_answer_handler()
def receber_voto(poll_answer):
    poll_id = poll_answer.poll_id
    if poll_id in enquetes_ativas:
        if poll_answer.option_ids[0] == enquetes_ativas[poll_id]["resposta"]:
            user_id = str(poll_answer.user.id)
            ranking_acertos[user_id] = ranking_acertos.get(user_id, 0) + 1
            salvar_json("backup_ranking.json", ranking_acertos)

def loop_enquetes():
    while True:
        agora = datetime.now()
        if 8 <= agora.hour < 23:
            disparar_enquete_periodica()
        time.sleep(3600) # Verifica a cada 1 hora

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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
        
