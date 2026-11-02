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
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

# ✅ CONFIGURAÇÕES DO GRUPO
GRUPO_ID = [-1002606951329, -1002728824996]     # IDs dos seus grupos permitidos
DONO_ID = 8338739275                   # ID do dono da Madonna (submissão)
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

# ✅ Envia mensagem com atraso
def enviar_com_delay(delay_segundos, chat_id, texto, reply_id=None):
    def tarefa():
        bot.send_message(chat_id, texto, reply_to_message_id=reply_id)
    threading.Timer(delay_segundos, tarefa).start()

# ✅ Função auxiliar para formatar o nome com o @ nas opções da enquete
def formatar_opcao(user_id):
    dados = usuarios_registrados.get(user_id, {"nome": "Membro", "username": ""})
    nome = dados["nome"]
    username = dados["username"]
    if username:
        return f"{nome} (@{username})"
    return nome

# ✅ Handler principal
@bot.message_handler(func=lambda msg: True)
def responder(msg):
    grupos_lista = GRUPO_ID if isinstance(GRUPO_ID, list) else [GRUPO_ID]
    if msg.chat.id not in grupos_lista and msg.chat.type in ["group", "supergroup"]:
        return

    if not msg.text:
        return

    texto = msg.text.lower()
    user_id = msg.from_user.id
    nome = msg.from_user.first_name or "Amor"
    username = msg.from_user.username or ""
    mulher = e_mulher(msg.from_user)
    agora = datetime.now()

    # 🔹 COMANDO DO DONO PARA CRIAR ENQUETE MANUALMENTE
    if user_id == DONO_ID and texto == "/enquete":
        try:
            if not frases_guardadas:
                bot.send_message(msg.chat.id, "Não há frases registradas para criar a enquete 😅")
                return

            candidatas = [f for f in frases_guardadas if f not in frases_usadas]
            if not candidatas:
                bot.send_message(msg.chat.id, "Todas as frases já foram usadas! 🤷‍♀️")
                return

            frase, autor_id = random.choice(candidatas)
            frases_usadas.append((frase, autor_id))

            outros_ids = [uid for uid in usuarios_registrados.keys() if uid != autor_id]
            if len(outros_ids) < 3 or autor_id not in usuarios_registrados:
                bot.send_message(msg.chat.id, "Não há usuários suficientes para criar opções da enquete 😅")
                return

            opcoes_ids = random.sample(outros_ids, 3) + [autor_id]
            random.shuffle(opcoes_ids)

            opcoes_texto = [formatar_opcao(uid) for uid in opcoes_ids]
            corretor_texto = formatar_opcao(autor_id)

            pergunta = f"Quem disse essa frase?\n\n“{frase}”"
            
            for g_id in grupos_lista:
                bot.send_poll(
                    g_id,
                    pergunta,
                    opcoes_texto,
                    type="quiz",
                    correct_option_id=opcoes_texto.index(corretor_texto),
                    is_anonymous=False
                )
            bot.send_message(msg.chat.id, "Enquete manual criada! 🎉")
        except Exception as e:
            bot.send_message(msg.chat.id, f"Erro ao criar enquete: {e}")
        return

    # Registrar o usuário e a frase se for válida
    texto_limpo = msg.text.strip()
    palavras = texto_limpo.split()
    if len(palavras) >= 3 and not all(ch in "kKcC" for ch in texto_limpo):
        if len(texto_limpo) > 5:
            usuarios_registrados[user_id] = {"nome": nome, "username": username}
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

# ✅ Função para disparar enquetes periódicas (Automática, sem ranking e sem poluição)
opt_grupos = GRUPO_ID if isinstance(GRUPO_ID, list) else [GRUPO_ID]

def disparar_enquete_periodica():
    while True:
        agora = datetime.now()
        if 6 <= agora.hour < 24:  # só das 6h até meia-noite
            if len(frases_guardadas) >= 5 and len(usuarios_registrados) >= 4:
                frases_disponiveis = [f for f in frases_guardadas if f not in frases_usadas]
                if frases_disponiveis:
                    frase, autor_id = random.choice(frases_disponiveis)
                    frases_usadas.append((frase, autor_id))

                    outros_ids = [uid for uid in usuarios_registrados.keys() if uid != autor_id]
                    if len(outros_ids) >= 3 and autor_id in usuarios_registrados:
                        opcoes_ids = random.sample(outros_ids, 3) + [autor_id]
                        random.shuffle(opcoes_ids)

                        opcoes_texto = [formatar_opcao(uid) for uid in opcoes_ids]
                        corretor_texto = formatar_opcao(autor_id)

                        pergunta = f"📝 **Enquete:** Quem disse esta frase?\n\n💬 \"{frase}\""
                        
                        for g_id in opt_grupos:
                            try:
                                bot.send_poll(
                                    g_id,
                                    pergunta,
                                    opcoes_texto,
                                    type="quiz",
                                    correct_option_id=opcoes_texto.index(corretor_texto),
                                    is_anonymous=False
                                )
                            except Exception as e:
                                print(f"Erro ao disparar enquete: {e}")

        time.sleep(2000) # A cada 33 minutos

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

# ✅ Função para gerar a "Carteirinha" do novo membro (Versão segura para Render)
def gerar_carteirinha(user, avatar_path_or_image):
    largura, altura = 800, 450
    cartao = Image.new("RGB", (largura, altura), color=(20, 24, 33)) # Fundo escuro elegante
    draw = ImageDraw.Draw(cartao)

    # Borda e cabeçalho temática Resenha & Uno
    draw.rectangle([15, 15, largura - 15, altura - 15], outline=(235, 87, 87), width=3)
    draw.rectangle([15, 15, largura - 15, 85], fill=(30, 36, 48))
    
    # Usando fonte padrão do sistema
    draw.text((35, 33), "🎴 RESENHA & UNO — CREDENCIAL DE MEMBRO", fill=(255, 255, 255))

    # Processar o Avatar do usuário (círculo)
    try:
        response = requests.get(avatar_path_or_image)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")
        avatar = avatar.resize((200, 200))

        mascara = Image.new("L", (200, 200), 0)
        draw_mascara = ImageDraw.Draw(mascara)
        draw_mascara.ellipse((0, 0, 200, 200), fill=255)

        avatar_circular = Image.new("RGBA", (200, 200))
        avatar_circular.paste(avatar, (0, 0), mascara)

        cartao.paste(avatar_circular, (50, 150), avatar_circular)
        
        draw.ellipse([46, 146, 254, 354], outline=(255, 215, 0), width=4)
    except Exception as e:
        print(f"Erro ao processar avatar: {e}")

    # Dados do usuário
    nome = user.first_name or "Membro"
    username = f"@{user.username}" if user.username else "@sem_usuario"
    
    if len(nome) > 18:
        nome = nome[:16] + "..."

    draw.text((280, 160), "NOME:", fill=(150, 160, 180))
    draw.text((280, 185), nome, fill=(255, 255, 255))

    draw.text((280, 240), "USUÁRIO:", fill=(150, 160, 180))
    draw.text((280, 265), username, fill=(0, 229, 255))

    draw.text((280, 330), "STATUS: ✅ AUTORIZADO (Resenha, Quiz, Uno & Jogos)", fill=(100, 255, 100))

    output = BytesIO()
    cartao.save(output, format="PNG")
    output.seek(0)
    return output


# ✅ Handler para novos membros que entram no grupo
@bot.message_handler(content_types=['new_chat_members'])
def boas_vindas_novos_membros(msg):
    for novo_usuario in msg.new_chat_members:
        if novo_usuario.id == bot.get_me().id:
            continue

        user_id = novo_usuario.id
        nome = novo_usuario.first_name or "Amor"
        mention = f"@{novo_usuario.username}" if novo_usuario.username else f"[{nome}](tg://user?id={user_id})"
        mulher = e_mulher(novo_usuario)

        avatar_url = None
        try:
            fotos = bot.get_user_profile_photos(user_id, limit=1)
            if fotos.total_count > 0:
                file_id = fotos.photos[0][-1].file_id
                file_info = bot.get_file(file_id)
                avatar_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        except Exception as e:
            print(f"Erro ao buscar foto de perfil: {e}")

        if not avatar_url:
            avatar_url = "https://www.w3schools.com/howto/img_avatar.png"

        try:
            carteirinha_io = gerar_carteirinha(novo_usuario, avatar_url)
            
            saudacao_f = f"Opa, olha só quem chegou para somar na nossa mesa! Seja muito bem-vindo(a) {mention}! Puxe uma cadeira, prepare seu +4 no Uno e venha tankar nossos quizzes e resenhas. 🃏🔥"
            saudacao_m = f"Salve, {mention}! Chegou reforço de peso no **Resenha & Uno**. Já vai esquentando os dados pro xadrez, damas e claro... preparando o psicológico pro +4! 🚀👑"
            
            frase_final = saudacao_f if mulher else saudacao_m

            bot.send_photo(
                chat_id=msg.chat.id,
                photo=carteirinha_io,
                caption=frase_final,
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.send_message(msg.chat.id, f"Seja bem-vindo(a) ao **Resenha & Uno**, {mention}! 🎉 Divirta-se com a gente!", parse_mode="Markdown")

# 🚀 INICIAR
if __name__ == "__main__":
    threading.Thread(target=manter_vivo).start()
    threading.Thread(target=disparar_enquete_periodica, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
