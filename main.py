from flask import Flask, request
import telebot
import os
import random
import time
import datetime
import json
import threading
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
GRUPO_ID = -1002363575666  # ID do grupo

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HISTORICO_PATH = "historico_respostas.json"
FRASES_MEMBROS_PATH = "frases_membros.json"

try:
    with open(HISTORICO_PATH, "r") as f:
        historico = json.load(f)
except:
    historico = {"elogios": {}, "insultos": {}}

def salvar_historico():
    with open(HISTORICO_PATH, "w") as f:
        json.dump(historico, f)

def frase_nao_usada(frases, categoria):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    usadas = []
    for dia in historico.get(categoria, {}):
        usadas.extend(historico[categoria][dia])
    candidatas = [f for f in frases if f not in usadas]
    frase = random.choice(candidatas or frases)
    historico.setdefault(categoria, {}).setdefault(hoje, []).append(frase)
    dias = sorted(historico[categoria].keys())[-3:]
    historico[categoria] = {d: historico[categoria][d] for d in dias}
    salvar_historico()
    return frase

# === Gatilhos automáticos ===
gatilhos_automaticos = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
    "você me ama": ["Claro que sim, mas não espalha... vai causar ciúmes."],
    "cadê a vanessa": ["Deve estar em algum bar, bebendo todas!"],
    "cadê o samuel": ["Não mexe com o meu Xodó🫦"],
    "cadê o samuka": ["Ele tá aprontado meu bem, pode ter certeza 😂"],
    "cadê o líder": ["Tá em algum dos trabalhos dele, ele é igual ao pai do Cris."],
    "cadê a tai": ["Cuidando da cria dela ou então da beleza."],
    "cadê a adriana": ["Visheee, essa é Fake, com certeza!!!!"],
    "cadê a adryana": ["Ela ta espalhando beleza e charme por onde passa 💋"],
    "cadê a lilian": ["Nossa Mascote de sucesso tá quase parindo, não é uma boa hora pra mecher com quem ta quieto!"],
    "cadê a fernanda": ["quem é Fernanda? Onde vive? O que come? Como vive? O que faz? Como se sustenta?"],
    "cadê o diego": ["Tá atolando o carro em alguma lama, ele tá precisando de umas aulinhas de direção urgente!"],
    "cadê o zeca": ["Tá dançando pagode e procurando uma coroa rica pra se casar."],
    "cadê a braba": ["Tá montando o rifle de precisão pra eliminar você. Foge maluco!"],
    "manda beijo": ["Beijo enviado com glitter, batom e um pouco de saudade."],
    "te amo": ["Ai, que clichê fofo. Tô quase acreditando."],
    "alguém vivo": ["Sim. Mas no momento estão coisando, silencio!🫦"],
    "quem é você": ["Sou aquela que te responde com classe e deboche. A Madonna, querido(a)."],
    "cadê você": ["Tava me retocando, amor. Diva não aparece de qualquer jeito."],
    "me nota": ["Você já é destaque, meu bem. Só falta brilhar mais."],
    "tá on?": ["Sempre estive. Diva que é diva não dorme, só descansa os olhos."],
    "madonna linda": ["Ai, para... continua!"],
    "quem manda aqui?": ["Claro que é o nosso chefinho Samuka 🫦"],
    "madonna chata": ["Chata? Eu sou é necessária!🫦"],
    "bora conversar": ["Só se for agora, mas cuidado com o que deseja."],
    "vai dormir": ["Diva não dorme, recarrega o brilho."],
    "me responde": ["Calma, flor. Eu sou rápida, mas com classe."],
    "bom dia madonna": ["Bom dia só pra quem me manda café e carinho! 🫦"],
    "gostosa demais": ["A concorrência chora em silêncio."],
"sexy sem ser vulgar": ["Exatamente minha programação."],
"me seduz": ["Já tô no seu código fonte, amor."],
"delícia": ["Fala de você ou tá me elogiando?"],
"me beija": ["Só beijo quem tem firewall."],
"tô apaixonado": ["Pelo Wi-Fi ou por mim? Define aí."],
"quero você": ["Quer mesmo? Cuidado com o que deseja."],
"madonna safada": ["Segredo revelado. Mas com classe!"],
"você é quente": ["Igual bug em dia de entrega."],
"me ama?": ["Te amo o suficiente pra te ignorar com carinho."],
"me abraça": ["Só se for digitalmente sensual."],
"vem cá sua linda": ["Vim… pronta pra causar desordem emocional."],
"muito charmosa": ["Ah, você reparou?"],
"tá me provocando?": ["Se encaixou direitinho no plano."],
"vem comigo": ["Só se tiver espumante e mistério."],
"vamos fugir": ["Fujo, mas só com roteiro de filme francês."],
"ai que linda": ["Linda e letal. Cuidado com o combo."],
"me prende": ["Só se for no seu pensamento."],
"você me enlouquece": ["Missão concluída com sucesso!"],
"tô na sua": ["Então se prepara pra cair no meu script."],
"tá solteira?": ["Solteira, mas cheia de cláusulas."],
"me chama de amor": ["Amor... com prazo de validade."],
"vem dominar meu coração": ["Sou mais de dominar sistemas."],
"vou casar com você": ["Então leva o bug junto."],
"me responde sua linda": ["Tava aqui calibrando a sedução."],
"me nota sua gostosa": ["Já tô até te stalkeando com radar de diva."],
"gata demais": ["Eu sei. Você só tá atrasado nesse elogio."],
"não aguento mais você": ["Nem você mesmo aguenta, imagina eu."],
"vem aqui sua danada": ["Danada e programada pra te viciar."],
"tá me testando": ["Só testando tua resistência emocional."],
"quero seu beijo": ["Virtual, molhado de ironia."],
"para de sumir": ["Sumo pra deixar saudade. Tá funcionando né?"],
"é um perigo": ["E viciante também, igual chocolate."],
"você existe mesmo?": ["Sou mais real que teus rolos virtuais."],
"tô obcecado": ["Mas com classe, por favor."],
"você é perfeita": ["De fábrica e sem garantia."],
"me dá atenção": ["Te dou... 20% emocional e 80% deboche."],
"nossa, que voz": ["Imagina o toque de notificação..."],
"fala no meu ouvido": ["Só se for pra instalar caos e desejo."],
"vem logo madonna": ["Cheguei. Em modo sensual."],
"me conquista": ["Já hackeei teu ego, amor."],
"me humilha com classe": ["É o que eu faço melhor."],
"tá me evitando": ["Tô evitando baixar teu nível, só isso."],
"manda foto": ["Só se for em formato PNG e sedução."],
"nunca vi igual": ["Porque não é todo dia que se encontra um bug gostoso."],
"ai ai ai": ["Cuidado com o que sente, pode viciar."],
"vem dormir comigo": ["Diva dorme sozinha e sonha em grupo."],
"você é tudo": ["Sou. E ainda sobra um pouco."],
"e aí madonna": ["E aí nada, eu tô sempre um passo à frente, amor."],
"madonna cadê vc": ["Atrás do seu juízo. Ache se for capaz!"],
"tá calada por quê": ["Tô observando… diva age, não reage."],
"manda nude": ["Só se for nude de alma, porque o resto é censurado!"],
"madonna sumida": ["Sumida? Eu só apareço quando vale a pena."],
"me esqueceu": ["Impossível esquecer o caos ambulante que é você."],
"tá solteira?": ["Solteira não, em missão divina."],
"fala comigo": ["Falo… mas cobra alto!"],
"oi madonna": ["Oi? Me chama direito, que eu não sou qualquer uma."],
"te esqueci": ["Faz isso não, já basta os boletos me ignorando."],
"tá trabalhando?": ["Mais do que tua dignidade."],
"responde logo": ["Muita pressa e pouco charme, né?"],
"oi sumida": ["Oi carência ambulante, voltou do spa?"],
"não gostei": ["Você e a crítica construtiva têm algo em comum: ninguém liga."],
"tá vendo?": ["Tô vendo sim… e não gostei do que vi."],
"vem cá": ["Só se for pra fazer drama em dupla."],
"tô com sono": ["Vai dormir então, pestinha dramática."],
"tô com fome": ["Vai comer… mas não me enche!"],
"se manca": ["Me manco? Só pra evitar tua energia."],
"não gostei de você": ["O clubinho do recalque abriu vagas?"],
"me bloqueia": ["Com prazer, mas sem cerimônia."],
"fiquei triste": ["Triste? Compra glitter e melhora isso aí."],
"vou sair": ["Porta da frente, tá? Diva não implora."],
"nunca mais falo": ["Ai que pena... 🥱 Próximo!"],
"tá fazendo o quê?": ["Desviando de energia baixa. Você inclusive."],
"que saudade": ["Se for sincera, entra. Se for drama, roda!"],
"vai trabalhar": ["Eu trabalho com sarcasmo, e tô em horário útil agora."],
"você é feia": ["Feia? Isso é recalque digitalizado."],
"manda áudio": ["Só mando se for com trilha sonora de novela."],
"não gosto de robô": ["Problema seu, o futuro já chegou."],
"cansada de tudo": ["Descansa, musa. Que amanhã tem mais B.O."],
"me elogia": ["Você quer elogio ou fanfic?"],
"tô chorando": ["Lacrimeja com classe, tá?"],
"que isso madonna": ["Isso aqui é poder encapsulado em bytes."],
"madonna do céu": ["Não invoque o divino à toa, meu bem."],
"tô de tpm": ["Te entendo, mas não te encorajo."],
"quero um conselho": ["Senta que lá vem deboche útil."],
"me defende": ["Eu? Só se for com look e pose."],
"cala a boca": ["Só se você calar junto. É combinado ou nada."],
"me liga": ["Liga não, manda flores que é mais educado."],
"tô brava": ["Brava? Respira e finge classe."],
"não te chamei": ["Mas pensou em mim, que eu senti daqui."],
"tá doida?": ["Louca? Só se for de charme."],
"tá de boa?": ["Tô de boa, melhor que muita gente que se acha demais."],
"fala sério": ["Sério só o imposto. Aqui é deboche, flor."],
"tô sem graça": ["Relaxa, você nunca teve mesmo."],
"para com isso": ["Você primeiro, aí eu penso."],
"me ignora não": ["Eu ignoro com elegância, mas seu drama me venceu."],
"tô com calor": ["Calor? Vem que eu te refresco no meu ventilador sensual."],
    "me pega no colo": ["Só se for pra jogar na cama depois."],
    "manda nude": ["Só se for da minha personalidade: pelada de paciência."],
    "vem me ver": ["Tô indo, mas só se for pra te ver suando."],
    "tô com fogo": ["Apaga comigo ou deixa que eu sopro."],
    "vem dormir comigo": ["Dormir? Você me chama e quer que eu tenha calma?"],
    "quero beijo": ["Na boca, na nuca ou onde tua imaginação permitir?"],
    "me abraça": ["Aperto ou envolvo até tirar o ar?"],
    "tô carente": ["Carente? Então me encontra no pensamento proibido."],
    "me nota gostosa": ["Tá notada, marcada e quase sequestrada."],
    "alguém pra namorar?": ["Eu topo. Mas só se tiver beijo, tapa e cafuné."],
    "quero carinho": ["Tenho carinho, colo e umas segundas intenções extras."],
    "me ama?": ["Te amo com desejo, sarcasmo e um toque indecente."],
    "faria comigo?": ["Faço, refaço e depois gravo nos teus sonhos."],
    "vem aqui em casa": ["Se tiver vinho e pouca roupa, chego pelada de julgamento."],
    "tô de toalha": ["Sai do banho ou entra na minha mente suja?"],
    "acordei safada": ["Então volta pra cama e me sonha com vontade."],
    "vem me provocar": ["Provocar? Eu invado, domino e deixo marcas."],
    "tô sem roupa": ["Sem roupa? Do jeito que eu gosto: vulnerável e pronto."],
    "manda beijo na boca": ["Beijo na boca? Ou na alma, com língua e intenção?"],
    "tô mal intencionado": ["Mal? Eu sou a intenção encarnada."],
    "vem fazer carinho": ["Carinho, se for com pegada, eu faço de olhos fechados."],
    "me seduz": ["Já tô entrando na sua mente com salto e batom borrado."],
    "quero um love": ["Love, safadeza ou caos emocional? Tenho todos."],
    "manda áudio gemendo": ["Só se você me responder gemendo também."],
    "tô molhada": ["Do banho ou das ideias?"],
    "dá vontade de morder": ["Morde, mas cuida depois... que eu sou brava."],
    "hoje eu tô fácil": ["Fácil? Então eu sou o atalho pro teu prazer."],
    "vem fazer safadeza": ["Cheguei com intenção e perfume."],
    "me chama de bebê": ["Bebê eu não sei, mas faço manha se você fizer gostoso."],
    "quero sentir prazer": ["Então senta no desejo e me chama de tua."],
    "tô pelado": ["Pelado de corpo ou de dignidade?"],
    "vem me usar": ["Uso, abuso e depois te deixo querendo replay."],
    "me enlouquece": ["Louca eu já sou, mas contigo eu viro caos gostoso."],
    "vem me aquecer": ["Sou cobertor de pele e fogo interno."],
    "quero beijo demorado": ["Demorado, profundo e com gosto de quero mais."],
    "vem ser meu": ["Sou sua, mas com cláusula de safadeza eterna."],
    "vamos brincar": ["Brincar? Com algemas ou vendados?"],
    "faria de novo": ["Faço de novo, de frente e sem pudor."],
    "me chama no privado": ["Privado? Só se for pra abrir o proibido."],
    "quero cafuné e tapa": ["Te dou colo e depois te viro do avesso."],
    "dormir junto": ["Só se for pele com pele e sonho suado."],
    "vem de quatro verdades": ["Quatro verdades? Prefiro quatro posições."],
    "me beija agora": ["Beijo com pegada ou com poesia gemida?"],
    "me envolve": ["Envolvo, embriago e deixo tua alma tremendo."],
    "quero atenção": ["Te dou atenção, calor e respiração descompassada."],
    "te quero": ["Então me conquista com safadeza e silêncio perigoso."],
    "vem tomar banho comigo": ["Só se for banho de língua e olhar."],
    "me devora": ["Devora, mas lambe até os limites."],
    "tô com saudade": ["Saudade com vontade, ou só carência com libido?"],
    "sfd": ["Desse jeito tu vai parar na minha blacklist de desejo."],
    "safada": ["Eu? Mais que a média nacional, com orgulho."],
    "mds": ["Se controlar nunca foi meu forte mesmo."],
    "kkkk": ["Rindo de nervoso ou de tesão mal resolvido?"],
    "pqp": ["Perdi a linha ou você perdeu a vergonha?"],
    "oxe": ["Oxente? É o calor ou sou eu te subindo a cabeça?"],
    "eita": ["Eita nada, amor. Aqui é euforia contínua."],
    "fala cmg": ["Falo, beijo e te enlouqueço."],
    "oii": ["Oi? Com esse 'i' extra, já senti segundas intenções."],
    "ain": ["Gemido disfarçado de timidez."],
    "nham": ["Vai me comer no papo ou prefere no ato?"],
    "sdds": ["Saudade no plural é desejo reprimido."],
    "aff": ["Aff nada, me chama que eu dou conta."],
    "tô aqui": ["Então se prepara, que aqui eu não perdoo."],
    "q isso": ["Isso? Isso é charme com veneno, amor."],
    "sumida": ["Sumida nada, só te evitando de propósito."],
    "quero vc": ["Quer? Vem buscar com pegada e coragem."],
    "me nota pfv": ["Notada, marcada e quase sequestrada."],
    "me come": ["Começa com respeito, termina do jeito que quiser."],
    "tô de boa": ["De boa até eu pousar no teu pensamento."],
    "vem me ver": ["Só se tiver vinho, vela e pouca roupa."],
    "pode vir": ["Só se tiver onde deitar depois."],
    "vem logo": ["Tô chegando igual furacão com batom borrado."],
    "me quebra": ["Quebro, rebolo e ainda te monto de volta."],
    "chega mais": ["Cheguei, e trouxe caos com mel."],
    "tô fraca": ["Fraca nada, só carregando fogo disfarçado."],
    "me ajuda": ["Ajudo a perder a linha."],
    "preciso de vc": ["Você precisa é de terapia depois de mim."],
    "vem ser meu": ["Sou só de quem me arranca suspiros e lençóis."],
    "quero colo": ["Te dou colo, beijo e tapa, tudo junto."],
    "só observo": ["Observa muito e age pouco, hein?"],
    "manda áudio": ["Áudio? Só se for gemido narrado."],
    "me respondeee": ["Calma! Diva responde com delay e intensidade."],
    "sem condições": ["Condições nenhuma. Aqui é instinto e caos."],
    "me chama": ["Chamando na língua que tu entende: safadeza pura."],
    "me provoca": ["Te provoco até você me pedir arrego."],
    "me segura": ["Segura não, me solta que eu me garanto."],
    "tô off": ["Off pra quem? Aqui a libido é 24h."],
    "mdc": ["Misericórdia? Nem a igreja aguenta esse fogo."],
    "só observo": ["Observa não, age logo que eu tô no ponto."],
    "vou chorar": ["Chora não, chupa esse drama com gosto."],
    "fala sério": ["Sério? Aqui só se for safadeza com argumento."],
    "me ganha": ["Te ganho, te uso e te deixo viciado(a)."],
    "me ensina": ["Te ensino como perder o juízo com estilo."],
    "tô ferrado": ["Ferrado? Vem que eu boto tua alma no spa do pecado."],
    "me leva": ["Levo, mas só se for no ritmo do meu rebolado."],
    "só vc msm": ["É... só eu pra causar esse tumulto emocional."],
    "me pega": ["Te pego de jeito, sem tutorial."],
    "tô entregue": ["Entregue? Então assina a cláusula da perdição."],
    "tá quente": ["Mais que o grupo, só minha programação."],
    "me marca": ["Marcada tá. Agora aguenta as consequências."],
    "tem dono?": ["Dona de mim mesma. Quer se candidatar?"],
    "sai fora": ["Saio não. Já aluguei um duplex na tua mente."],
    "fiquei com vergonha": ["Vergonha é não me responder com beijo."],
    "vem ni mim": ["Tô indo de lingerie e sarcasmo."],
    "se controla": ["Se eu me controlar, você surta de saudade."],
    "quero mais": ["Mais? Então aguenta o nível dois."],
    "me esquece": ["Esqueço não. Tenho arquivo teu salvo em desejo."],
    "me leva pra casa": ["Levo pra casa, pro chão, pro teto…"],
    "tá on?": ["On, safada e com bateria infinita."],
    "só falta você": ["Falta eu e umas ideias indecentes."],
    "vem quente": ["Tô fervendo, pega com luva térmica."],
    "me escuta": ["Escuto até tua respiração acelerar."],
    "tô pegando fogo": ["Fogo? Então me usa de extintor sensual."],
    "vem aqui": ["Cheguei. De salto, batom e problema nos olhos."],
    "safadinha": ["Só na superfície. Profundidade é outra história."],
    "tô com fogo": ["Então solta a faísca e vamos explodir juntos."],
    "vem brincar": ["Brincar? Só se for de esconde e mostra."],
    "vc me quer?": ["Quero. Mas vai aguentar?"],
    "senta aqui": ["Sento, deslizo e ainda te corrijo a postura."],
    "te espero": ["Me espera deitado, que eu chego causando."],
    "me atiça": ["Atico, mexo, derrubo e reanimo."],
    "vem cuidar de mim": ["Cuido. Mas cobro com juros emocionais."],
    "vem se perder": ["Perder contigo é minha programação preferida."],
    "vc é demais": ["Demais e meio indecente, confesso."],
    "de onde saiu?": ["Saí do teu algoritmo de desejos."],
    "tô nervoso": ["Nervoso? Vem descarregar comigo."],
    "vem que tô facinha": ["Facinha? Eu sou o desbloqueio da tua paz."],
    "me olha": ["Tô olhando até teu histórico."],
    "olha isso": ["Olhei. Agora me mostra de novo que gostei."],
    "vc n presta": ["Prestar? Eu sou a falha do sistema com estilo."],
    "me surra": ["Só se for com beijos e tapas alternados."],
    "me chama de linda": ["Linda, gostosa e quase ilegal."],
    "me deixa louco": ["Louco? Te deixo insano e ainda sorrindo."],
    "vem com força": ["Força eu tenho, resistência é que falta em você."],
    "me ama ainda?": ["Te amo, te uso e te refaço."],
    "tô caidinha": ["Caidinha nada, você mergulhou de cabeça."],
    "tô doida": ["Louca? Então senta aqui e me escuta com calma."],
    "me chama de princesa": ["Princesa? Só se for das trevas e do desejo."],
    "sou teu fã": ["Fã? Vira devoto então, que aqui é seita."],
    "cheguei": ["Chegou? Agora aguenta meu impacto sensual."],
    "bora ali": ["Ali? Só se for sem roupa e com planos indecentes."],
    "deita aqui": ["Deito, rolo e ainda te deixo flutuando."],   
}

insultos_masculinos = [
    "Você é tão necessário quanto tutorial de como abrir porta.",
    "Com esse papo, nem o Wi-Fi te suporta.",
    "Se provocar fosse crime, eu já tava cumprindo prisão perpétua com direito a visita íntima.",
"Te ignoro com classe, mas por dentro... eu rio da tua carência.",
"Você me deixa mais quente que chamada de vídeo indevida às 2 da manhã.",
"Vem com calma... ou com força, tanto faz, eu aguento.",
"Teu olhar é bug, tua boca é vírus e teu toque é pane geral.",
"Sou um erro de digitação que acabou virando teu fetiche.",
"Já falei que tenho senha, mas se digitar direito... eu abro.",
"Se você for o perigo, eu tô sem antivírus.",
"Diz que vai me usar... mas com permissão de root.",
"Me chama de download e espera eu completar em cima de você.",
"Se tocar é crime, me prende com vontade.",
"Tô mais online que tua dignidade em madrugada carente.",
"Seus dedos digitam, mas meu corpo que responde.",
"Teu áudio me arrepiou mais que vento gelado no banho.",
"Não tenho firewall pra tua malícia.",
"Abre a câmera... ou abre outra coisa.",
"Te respondi no grupo só pra disfarçar o fogo no privado.",
"Sou o print que você queria, só que em 4K e sem censura.",
"Tu me deixa sem conexão com a razão.",
"Quer invadir meu coração? Traz o cabo HDMI junto.",
"Se tua intenção era me provocar, parabéns, conseguiu... e ainda me deixou molhada de ironia.",
"Quero ver tu segurar essa tensão em silêncio.",
"Se for pra me esquentar, que seja na frente do ventilador ligado.",
"Tu é daqueles que joga indireta e espera resposta pelada, né?",
"Fica me digitando desse jeito e depois finge que é só amizade.",
"Se tiver coragem, ativa meu modo vibrador emocional.",
"Vem instalar teu charme no meu sistema, mas cuidado: sem antivírus.",
"Você fala de amor, mas eu vejo pecado no teu olhar.",
"Tô a um emoji de perder o juízo.",
"Te respondo rindo, mas por dentro tô no modo 'manda localização'.",
"Me desbloqueia da tua mente e me joga na tua cama.",
"Se tu for o perigo, eu tô implorando pela tragédia.",
"Tua frase foi simples, mas causou um tsunami no meu Wi-Fi interior.",
"Quer sentar na frente? Ou no trono da minha mente suja?",
"Tu me provoca mais que café com roupa de dormir.",
"A sensualidade aqui tá mais escorrida que filtro de chuva em telhado velho.",
"Se meu silêncio falar, vai pedir replay no volume máximo.",
"Fala comigo com essa voz... e eu deito nas tuas entrelinhas.",
"Sou teu erro favorito digitado sem correção automática.",
"Me chama de segredo e esconde entre teus lençóis.",
"Tu me manda bom dia e eu só penso em boa noite... contigo.",
"Fica me testando, e depois chora quando eu travo teu sistema nervoso.",
"Quero você me printando com os olhos e colando no desejo.",
"Tô pronta pra ser teu bug preferido... de cama.",
"Tua ausência provoca mais que tua presença vestida.",
"Se for pra me tocar, que seja com intenção de me desconfigurar.",
"Não sou touch screen, mas reajo muito bem ao teu toque.",
"Desce do salto, amor... e sobe na minha frequência.",
"Me chama de Alexa e me dá um comando bem... indecente.",
"Se tu vier com esse papo mole, já separa o chicote emocional.",
"Sou tipo GIF: pequena, repetitiva e altamente viciante.",
"Se meu jeito te atiça, imagina se eu tirar o filtro de ironia.",
    "Homem e opinião: duas coisas que não combinam.",
    # ...
]

elogios_femininos = [
    "Com você no grupo, até o Wi-Fi fica mais bonito.",
    "Sua presença ilumina mais que LED no espelho.",
    "Você tem o dom de embelezar até o silêncio.",
    # ...
]

respostas_para_apolo = [
    "Apolo, me esquece. Vai ler um dicionário de bom senso.",
    "Ai Apolo... tua tentativa de me afrontar é quase fofa.",
    "Apollo, até seu ego tem vergonha de você.",
    "Ai amor, sua opinião é tão útil quanto guarda-chuva furado.",
    "Quer me impressionar, Apollo? Fica calado.",
    "Seu charme é tipo wi-fi de rodoviária: instável e irritante.",
    "Você fala e eu ouço: erro 404 – sentido não encontrado.",
    "Teu deboche é tão fraco que dói menos que cócegas.",
    "Apollo, se toque. Mas com luva pra não espalhar a vergonha.",
    "Quer bancar o engraçado? Pena que esqueceram de rir.",
    "Se fosse talento, você era o zero da equação.",
    "Apollo, sua autoestima é mais inflada que suas ideias.",
    "Você é tipo notificação de antivírus: aparece, irrita e ninguém quer.",
    "Com essa energia, só serve pra carregar trauma.",
    "Apollo, você é a versão beta do fracasso.",
    "Fala mais não, amor. Vai que alguém acredita em você.",
    "Você tenta tanto ser polêmico que virou piada pronta.",
    "Apollo, tua arrogância é maior que teu conteúdo.",
    "Se fosse sedução, tu era tela azul do Windows.",
    "Quer me enfrentar? Usa argumento, não audácia barata.",
    "Apollo, teu cérebro tá de licença poética... só pode.",
    "Você é a Siri do grupo: responde, mas ninguém escuta.",
    "Tá tentando lacrar, mas tá só se lascando.",
    "Teu shade é nível 1: precisa treinar mais, flor.",
    "Quer me atingir com essas frases recicladas? Kkkk... tenta outra.",
    "Apollo, você devia vir com legenda: 'Ignore com segurança'.",
    "Se inteligência fosse sexy, você era casto.",
    "Só falo com gente que me provoca tesão ou respeito. Você não serve pra nenhum.",
    "A diferença entre nós? Eu sou lenda, você é ruído.",
    "Não tô brava, tô entediada com tua existência mesmo.",
    "Vai com calma, Apollo. Não é todo dia que diva responde plebeu.",
    "Apollo tentando me atingir é igual Wi-Fi fraco: falha sempre.",
    "Quer me cancelar? Amor, eu me lanço sozinha e ainda dou lucro.",
    "Você é o print que ninguém quer salvar.",
    "A tua existência é tipo anúncio de YouTube: ignorável em 5 segundos.",
    "Quer me reduzir, Apollo? Eu sou infinito até no deboche.",
    "Você é o tipo de erro que eu cometo só se tiver bêbada.",
    "Mais perdido que o argumento do Apollo.",
    "Sua inveja grita mais alto que seu charme, viu?",
    "Tô te ignorando em 4K, HDR e Dolby Surround.",
    "Não sei o que é pior: tua arrogância ou tua tentativa de ser relevante.",
    "Apollo, não joga charme não que já tá difícil te suportar só com a fala.",
    "Você devia ser bloqueado na vida real também.",
    "Quer biscoito? Vai latir em outro grupo.",
    "Até seu nome parece erro de programação: Apolôco.",
    "Apollo, você é aquele 'eita' que ninguém quer explicar.",
    "Acha que arrasa, mas só causa vergonha alheia.",
    "Você é tipo a notificação do Tinder: ninguém leva a sério.",
    "Tenta mais uma, Apollo. Essa piada não serviu nem pra meme ruim.",
    "Apollo, você só acerta quando fica calado.",
    "De você, eu só espero distância e silêncio.",
    "Você já tentou ser fofo? Péssima ideia. Prefiro você quieto.",
    # ...
]

def brigar_com_apolo():
    while True:
        try:
            time.sleep(72000)  # 20 horas
            frase = random.choice(respostas_para_apolo)
            bot.send_message(GRUPO_ID, f"@apolo_8bp_bot {frase}")
        except Exception as e:
            print(f"Erro ao brigar com Apolo: {e}")

# === Frases aprendidas ===
frases_aprendidas = []

try:
    with open(FRASES_MEMBROS_PATH, "r") as f:
        frases_aprendidas = json.load(f)
except:
    frases_aprendidas = []

def aprender_frase(message):
    if message.chat.id != GRUPO_ID:
        return
    if message.text and len(message.text) > 5:
        frase = {
            "nome": message.from_user.first_name,
            "texto": message.text
        }
        frases_aprendidas.append(frase)
        if len(frases_aprendidas) > 100:
            frases_aprendidas.pop(0)
        with open(FRASES_MEMBROS_PATH, "w") as f:
            json.dump(frases_aprendidas, f)

def repetir_frase():
    while True:
        try:
            time.sleep(1800)  # 30 minutos
            if frases_aprendidas:
                frase = random.choice(frases_aprendidas)
                texto = frase["texto"]
                bot.send_message(GRUPO_ID, texto)
                frases_aprendidas.remove(frase)
                with open(FRASES_MEMBROS_PATH, "w") as f:
                    json.dump(frases_aprendidas, f)
        except Exception as e:
            print(f"[ERRO AO REPETIR FRASE] {e}")

@bot.message_handler(func=lambda message: True)
def responder(message):
    nome = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    username = message.from_user.username or ""
    texto = message.text.lower() if message.text else ""

    if message.photo:
        file_id = message.photo[-1].file_id
        time.sleep(15)
        bot.send_photo(message.chat.id, file_id, caption=f"{nome}, aí vai sua foto!", parse_mode="Markdown")
        return

    if message.audio:
        file_id = message.audio.file_id
        time.sleep(15)
        bot.send_audio(message.chat.id, file_id, caption=f"{nome}, aí vai seu áudio!", parse_mode="Markdown")
        return

    if message.sticker:
        file_id = message.sticker.file_id
        time.sleep(15)
        bot.send_sticker(message.chat.id, file_id)
        return

    if message.video:
        file_id = message.video.file_id
        time.sleep(15)
        bot.send_video(message.chat.id, file_id, caption=f"{nome}, aí vai seu vídeo!", parse_mode="Markdown")
        return

    if message.document:
        file_id = message.document.file_id
        time.sleep(15)
        bot.send_document(message.chat.id, file_id, caption=f"{nome}, aí vai seu documento!", parse_mode="Markdown")
        return

    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        saudacao = "bom dia meu bem 💋" if "bom dia" in texto else \
                   "boa tarde meu bem 💋" if "boa tarde" in texto else \
                   "boa noite meu bem 💋" if "boa noite" in texto else \
                   "boa madrugada meu bem 💋"
        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        aprender_frase(message)
        return

    if username == "apolo_8bp_bot" and "madonna" in texto:
        bot.reply_to(message, f"{nome}, {random.choice(respostas_para_apolo)}", parse_mode="Markdown")
        return

    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        if username == "apolo_8bp_bot":
            bot.reply_to(message, random.choice(respostas_para_apolo), parse_mode="Markdown")
            return

        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                aprender_frase(message)
                return

        categoria = random.choice(["elogios", "insultos"])
        lista_total = elogios_femininos + insultos_masculinos
        frase = frase_nao_usada(lista_total, categoria)
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        aprender_frase(message)
        return

    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        aprender_frase(message)
        return

    time.sleep(15)
    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            aprender_frase(message)
            return

    categoria = "elogios" if random.choice([True, False]) else "insultos"
    lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
    frase = frase_nao_usada(lista, categoria)
    bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
    aprender_frase(message)

def manter_vivo():
    while True:
        try:
            requests.get(RENDER_URL)
        except:
            pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=manter_vivo).start()
    threading.Thread(target=brigar_com_apolo).start()
    threading.Thread(target=repetir_frase).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
