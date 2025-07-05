import os
import openai
import telebot

# Pega tokens do ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

def responder_com_madonna(texto):
    resposta = client.chat.completions.create(
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
        bot.send_message(message.chat.id, "A Madonna travou o salto... 💅")
        print("Erro:", e)

print("👠 Madonna está online e plena!")
bot.polling()
