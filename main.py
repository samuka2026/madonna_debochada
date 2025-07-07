usadas.extend(historico_saudacoes[saudacao][dia])
        candidatas = [f for f in frases if f not in usadas]
        frase = random.choice(candidatas or frases)
        atualizar_historico(saudacao, frase)
        bot.send_message(message.chat.id, f"{nome_usuario}, {frase}")
        return

for chave, lista_respostas in respostas_automaticas.items():
    if chave in texto:
        resposta = random.choice(lista_respostas)
        bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
        return

# Emojis e reações
reacoes = {
    "❤️": "Ui, me apaixonei agora. Brinca assim não!",
    "😍": "Esse emoji é pra mim, né? Porque eu mereço.",
    "😘": "Recebido com batom, blush e boa intenção.",
    "😂": "Rindo de nervoso ou de amor por mim?",
    "kkk": "Tá rindo de mim ou comigo, hein?",
    "😒": "Ih, tá de carinha feia? Vem cá que eu melhoro.",
    "😐": "Essa carinha sua é charme reprimido?"
}
for emoji, resposta in reacoes.items():
    if emoji in texto or emoji.replace("❤️", "❤") in texto or emoji in texto:
        bot.send_message(message.chat.id, f"{nome_usuario}, {resposta}")
        return

# Modo ciumenta
if any(p in texto for p in ["linda", "inteligente", "gata", "maravilhosa"]):
    if "@samuel_gpm" not in texto and "madonna" not in texto:
        bot.send_message(message.chat.id, f"{nome_usuario}, elogiar as outras na minha frente? Coragem tua, viu? 😏")
        return

# Comportamento por horário
hora = datetime.datetime.now().hour
if 5 <= hora <= 11:
    estilo = "manha"
elif 12 <= hora <= 17:
    estilo = "tarde"
elif 18 <= hora <= 22:
    estilo = "noite"
else:
    estilo = "madrugada"

resposta_final = random.choice(respostas.get(estilo, respostas["default"]))
bot.send_message(message.chat.id, f"{nome_usuario}, {resposta_final}")

if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
