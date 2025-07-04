import telebot
import openai
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

def responder_com_madonna(pergunta):
    resposta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é Madonna, uma mulher debochada e romântica. Fala como uma diva apaixonada e irônica. Nunca diga que é robô."},
            {"role": "user", "content": pergunta}
        ]
    )
    return resposta.choices[0].message['content'].strip()

@bot.message_handler(commands=['beijo'])
def beijo_handler(message):
    bot.reply_to(message, "Beijo? Só se for na alma, baby 💋")

@bot.message_handler(commands=['conselho'])
def conselho_handler(message):
    bot.reply_to(message, "Se ele não te responde rápido, é porque não merece nem tua dúvida, flor 💅")

@bot.message_handler(commands=['verso'])
def verso_handler(message):
    bot.reply_to(message, "Me chamaram de exagerada... Eu só amei demais quem não valia nem metade 💔✨")

@bot.message_handler(func=lambda m: True)
def responder_tudo(message):
    resposta = responder_com_madonna(message.text)
    bot.reply_to(message, resposta)

print("Madonna está online e plena.")
bot.infinity_polling()
