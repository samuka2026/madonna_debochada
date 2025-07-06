import telebot
import random
import os

# Pegue o token do ambiente ou cole diretamente aqui
TOKEN = os.getenv("TELEGRAM_TOKEN") or "COLE_SEU_TOKEN_AQUI"
bot = telebot.TeleBot(TOKEN)

# Lista de respostas debochadas e românticas
respostas_madonna = [
    "Ai meu bem, tenta de novo que dessa vez eu tô zen 💅",
    "Amor, você fala e eu só suspiro... 😘",
    "Hoje tô igual diamante: linda, cara e difícil 💎",
    "Te ouvi, mas não sei se merecia minha resposta 💋",
    "Tô aqui, mas só respondo se for com drama 🎭",
    "Você fala... e eu ignoro com classe 💅",
    "Madonna te ouviu, amor. Mas se vai te responder? Talvez... 💖",
    "Só respondo porque sou um ícone, tá? 💃",
    "Fala direito, que hoje acordei exigente 💋",
    "A Madonna não responde qualquer um... mas vou abrir uma exceção 💌"
]

# Toda mensagem recebida gera uma resposta aleatória
@bot.message_handler(func=lambda message: True)
def responder(message):
    resposta = random.choice(respostas_madonna)
    bot.send_message(message.chat.id, resposta)

# Inicia o bot com polling (escutando 24h)
if __name__ == "__main__":
    print("Madonna tá online, meu amor 💄")
    bot.infinity_polling()
