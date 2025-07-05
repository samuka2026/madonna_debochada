import os
import openai
import telebot

# Pega tokens do ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

def responder_com_madonna(texto):
    resposta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é uma diva debochada e romântica. Responda com classe, ironia e charme."},
            {"role": "user", "content": texto}
        ]
    )
    return resposta.choices[0].message.content

@bot.message_handler(func=lambda message: True)
def responder_tudo(message):
    try:
        resposta = responder_com_madonna(message.text)
        bot.send_message(message.chat.id, resposta)
    except Exception as e:
        bot.send_message(message.chat.id, "A madame travou de salto. 😵‍💫")

bot.infinity_polling()
