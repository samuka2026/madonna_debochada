import os
import openai
import telebot

# Pega os tokens das variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

def responder_com_madonna(texto):
    resposta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é uma diva debochada e romântica. Responda com charme, ironia e afeto exagerado."},
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
        print(f"Erro: {e}")  # Mostra o erro no log da Render
        bot.send_message(message.chat.id, "A madame travou de salto. 😵‍💫")

bot.infinity_polling()
