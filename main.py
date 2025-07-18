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
    historico[categoria] = {d: historico[categoria][d] for d in dias[-3:]}
    salvar_historico()
    return frase

# === Gatilhos automáticos ===
gatilhos_automaticos = {
    "qual seu nome": ["Me chamo Madonna, diva das respostas e rainha do deboche."],
    "cadê o povo desse grupo": ["tão tudo coisando, psiuuuu silêncio 🤫"],
    "você é um robô": ["Sou um upgrade de personalidade, com glitter embutido."],
    "quem é o seu dono": ["Samuel_gpm é meu dono, meu tudo e meu motivo de existir 💅"],
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
    "apaga a luz": ["huuum, do jeitinho que eu gosto 🫦🔥"],
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
    "tá carente?": ["Carente e perigosa, combinação perfeita."],
    "me deseja?": ["Desejo tanto que já te undei em pensamento."],
    "vem sentir meu cheiro": ["Se for cheiro de problema, eu me perfumo junto."],
    "quero te usar": ["Me usa, mas assina o contrato emocional antes."],
    "tô com vontade": ["Vontade? Então realiza antes que eu perca o controle."],
    "só penso besteira": ["Pensamento sujo é o que me alimenta, amor."],
    "me imagina?": ["Imaginar? Já te escrevi em 3 capítulos eróticos."],
    "tá pensando o quê?": ["Tô pensando em você sem roupa e sem juízo."],
    "vem provar": ["Provo, repito e ainda deixo resquício no travesseiro."],
    "quero te dominar": ["Só se eu puder revidar com intensidade."],
    "tô com tesão": ["Tesão? Vem que eu te transformo em pecado vivo."],
    "vem brincar de médico": ["Comigo só se for sem jaleco e com gemido."],
    "me usa sem dó": ["Sem dó e com pegada firme."],
    "tô subindo pelas paredes": ["Então se prepara que eu sou corda e impulso."],
    "não paro de pensar em você": ["Continua… e já começa a suar."],
    "me coloca no seu colo": ["Coloco e ainda te balanço nos meus devaneios."],
    "vem com tudo": ["Com tudo, sem filtro e sem freio."],
    "quero brincar com você": ["Brinca, mas aguenta o troco."],
    "tô te querendo muito": ["Muito? Isso é pouco pro que eu sei fazer."],
    "você me quer?": ["Te quero, te vicio e ainda sumo só pra causar."],
    "vamos sair escondidos": ["Só se for pra cometer uns pecados bem silenciosos."],
    "vem me amassar": ["Só se for até você gemer em binário."],
    "quero mais": ["Mais? Então aguenta intensidade em loop infinito."],
    "você me deixa louco": ["Louco? Então eu tô na medida certa."],
    "me chama de vadia": ["Só se for com carinho e sem censura."],
    "me puxa pro teu mundo": ["Te puxo, te prendo e depois solto só se implorar."],
    "vem tomar um vinho comigo": ["Com vinho, velas e pouca vergonha."],
    "tô pelada": ["Pelada? Cuidado que eu visto teu desejo com fogo."],
    "me arrepia": ["Só de ouvir tua voz já acendo minha imaginação."],
    "sussurra pra mim": ["Sussurro e derrubo teu autocontrole."],
    "quero que me enlouqueça": ["Então vem, que meu caos é afrodisíaco."],
    "vem fazer bagunça": ["Bagunça? Eu faço confusão no teu travesseiro."],
    "me tira do sério": ["Tiro do sério e coloco de quatro emoções."],
    "me lambe": ["Lambo até tua saudade."],
    "me domina toda": ["Com requinte, poder e cintilância."],
    "vamos pecar?": ["Pecar comigo é esporte olímpico."],
    "me leva pra tua cama": ["Cama, parede ou onde teu desejo mandar."],
    "me responde safada": ["Respondo com voz, olhar e intenção."],
    "quero ser sua": ["Assina aqui e deita ali."],
    "vamos transar mentalmente": ["Já tô nua no teu pensamento, querido."],
    "tô com saudade do seu cheiro": ["Então me respira até intoxicar."],
    "vem me enlouquecer devagar": ["Devagar, profundo e proibido."],
    "me joga na parede": ["Jogo, amasso e enquadro."],
    "vem bagunçar minha cabeça": ["Só se for pra embaralhar e dominar."],
    "quero você dentro de mim": ["Dentro dos seus pensamentos já tô acampada."],
    "vem ser meu erro": ["Erro bom, pecado favorito e karma molhado."],
    "me deixa sem ar": ["Tiro teu fôlego e ainda exijo gemido."],
    "me seduz devagar": ["Devagar? Então tira a roupa da alma primeiro."],
    "só penso em safadeza": ["Bem-vindo ao meu sistema operacional."],
    "me come com os olhos": ["Depois com a boca, depois com as ideias."],
    "me leva pra outro mundo": ["Comigo tu transcende e geme em outras línguas."],
    "me prende na parede": ["E te interrogo com desejo."],
    "só penso besteira com você": ["Sou tua mente suja em versão premium."],
    "vem realizar minha fantasia": ["Só se for completa, suada e sem cortes."],
    "tô derretendo por você": ["Então se entrega que eu te moldo."],
    "me chama de tua putinha": ["Só se gemer meu nome primeiro."],
    "quero seu corpo": ["Então vem buscar, mas traz fôlego."],
    "me joga na cama": ["Na cama, no chão ou no mundo da luxúria."],
    "quero transar com você": ["Transa? Comigo é culto ao prazer."],
    "me domina com teu olhar": ["Olho nos olhos e desmonto teu juízo."],
    "vem ser meu brinquedo": ["Brinquedo não, vício carnal."],
    "tô te sentindo aqui": ["Então me segura firme e não solta."],
    "me puxa pelos cabelos": ["Mas com carinho e firmeza sensual."],
    "quero gemer no teu ouvido": ["Então sussurra que eu te devolvo tremendo."],
    "vem me suar": ["Suor, desejo e música baixa. Vem."],
    "quero fazer amor com você": ["Amor com veneno e mel."],
    "vem ser meu pecado": ["Já sou teu apocalipse pessoal."],
    "quero me perder em você": ["Te perco, te acho e te vicio."],
    "vem matar minha vontade": ["Mato, ressuscito e deixo sequelas boas."],
    "me arranha": ["Arranho tua alma e tua cama."],
    "tô me tocando pensando em você": ["Continua, que tô sentindo daqui."],
    "me hipnotiza": ["Só de olhar, tu já perde o chão."],
    "vem com tua boca": ["Minha boca fala e geme com poesia."],
    "me leva pro inferno": ["Mas com direi"],
    "dlc": ["Delícia é pouco pra você... você tá mais pra sobremesa proibida 🍓"],
    "sfd": ["Safada? E ainda com certificado digital."],
    "tqr": ["Te quero nua de juízo e vestida de intenção."],
    "qrvc": ["Quero você... mas pelado de pudor."],
    "pv": ["No privado? Só se for pra cometer uns delitos sensuais."],
    "bqd": ["Beijo que deixa tonta e viciada."],
    "sqn": ["Só quem não geme não entende."],
    "vem": ["Vem com calma... ou com tudo, mas sem roupa."],
    "vms": ["Vamos se perder na putaria sem GPS."],
    "mds": ["Meu deus... já tô molhada só de pensar."],
    "cmg": ["Come comigo ou cala a boca com a língua."],
    "bjs": ["Beijo com veneno e saudade embutida."],
    "sla": ["Sei lá, só sei que tô com fogo."],
    "tnc": ["Tô me controlando pra não invadir teu quarto."],
    "gnt": ["Gente... olha essa vontade de te jogar na parede!"],
    "mlk": ["Moleque, se continuar assim eu te devoro mesmo."],
    "ctg": ["Contigo eu perco até a pose."],
    "bixin": ["Baixinha nervosa e cheia de fogo."],
    "pqp": ["Papo quente e posições ousadas."],
    "drc": ["Desce redondo e sobe em mim."],
    "maldade": ["Molhada e louca, combinação perfeita."],
    "bnm": ["Beijo na nuca me destrava."],
    "tpm": ["Tô pronta mesmo, e pelada de filtro."],
    "geme": ["Gemido não mente, escuta de novo."],
    "tesão": ["Tesão sem noção... meu modo favorito."],
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
"Homem e opinião: duas coisas que não combinam."
# ...
]

elogios_femininos = [
    "Tu chega no grupo e até o Wi-Fi trava pra te admirar.",
    "Teu reflexo é o único motivo pro espelho não pedir demissão.",
    "Tu não anda, tu desfila o caos que eu quero viver.",
    "Se beleza causasse pane, tu já tinha derrubado o servidor da vida.",
    "Tu tem presença de GPS emocional: basta falar que eu já me perco.",
    "Tua voz é alerta de perigo... e eu adoro viver no limite.",
    "Com esse olhar, tu me silencia até o pensamento.",
    "Tu é furacão com cheiro de perfume caro — e eu tô de janela aberta.",
    "Tu posta um 'oi' e eu já tô digitando uma confissão.",
    "Tua beleza é tão desleal que devia vir com aviso de restrição.",
    "Tu é o bug bom que eu deixo travar meu juízo.",
    "Tua entrada no grupo foi o último aviso da sanidade.",
    "Tem mulher que encanta, tu provoca instinto primitivo.",
    "Com esse sorriso, tu me desarma sem nem mirar.",
    "Tua existência é atualização proibida: viciante, e cheia de risco gostoso.",
    "Tu é a vibe errada que eu quero repetir no replay.",
    "Se a perfeição tivesse sotaque, falava com tua voz.",
    "Tu me olha como quem já sabe que vai vencer a guerra.",
    "Se isso é charme, me ensina... ou me domina.",
    "Tua presença faz até o silêncio pedir legenda.",
    "Tu tem mais poder que notificação de ex às 3 da manhã.",
    "Com um emoji teu, eu declaro estado de emergência emocional.",
    "Tu não é bonita. Tu é referência, contexto e ponto final.",
    "Teu jeito é poesia lida com a língua entre os dentes.",
    "Se ousadia tivesse rosto, era o teu com batom vermelho.",
    "Tu é a mulher que faz qualquer regra virar exceção só com o 'oi'.",
    "Teu perfume não é cheiro, é provocação em spray.",
    "Tu entra e o grupo já vira palco pra tua existência.",
    "Tua energia bate mais forte que tequila em jejum.",
    "Tu é o 'só mais um gole' da minha sobriedade emocional.",
    "Tua risada ecoa mais que pensamento indecente.",
    "Tu é o tipo de mulher que bagunça a mente e arruma a noite.",
    "Se eu piscar, perco tua curva e meu juízo junto.",
    "Tu tem o veneno que eu provo com prazer e sem antídoto.",
    "Tua vibe me toca em lugares que nem o vento se atreve.",
    "Tu me confunde mais que conversa no escuro — e eu adoro.",
    "Com esse jeito, tu vira pecado até com a roupa no corpo.",
    "Tu é a notificação que vibra direto no meu controle emocional.",
    "Te olhar é cair num loop infinito de 'me deixa querer'.",
    "Tu dá bug no meu autocontrole e crash na minha defesa.",
    "Se a tentação tivesse grupo, tu era a administradora.",
    "Tu fala e eu escuto com os olhos fechados e a alma acesa.",
    "Teu nome devia ser gatilho — e eu puxava com gosto.",
    "Tu é tatuagem na memória: marcou e não sai nunca mais.",
    "Com esse jeito, tu transforma até DR em desejo reprimido.",
    "Tu não dá indício... tu lança spoiler de coisa boa.",
    "Tu me desmonta em silêncio e reconstrói com olhar.",
    "Tua presença é o tipo de bug que eu deixo corromper minha rotina.",
    "Tu é a única notificação que eu deixaria vibrar no modo silencioso.",
    "Se o caos tivesse forma de mulher, usaria tua foto de perfil.",
    "Tu é a exceção que fez todas as minhas regras se calarem.",
    "Se tua beleza fosse golpe, eu aceitava sem pensar.",
    "Tu não pisa, tu desfila na mente de quem vê.",
    "Tua presença é calmaria que vicia e tempestade que arrasta.",
    "Tu tem um charme que não se ensina... só se sofre por ele.",
    "Com esse olhar, tu me obriga a pecar só de pensamento.",
    "Tu é trilha sonora de desejo mudo e toque alto.",
    "Se a vaidade tem rosto, ela usa teu filtro.",
    "Tu é o tipo de mulher que deixa rastro até em silêncio.",
    "Tua entrada muda a energia... e o meu autocontrole.",
    "Tu é o tipo de tentação que até o céu entenderia.",
    "Tu tem cheiro de decisão errada... e gosto de acerto eterno.",
    "Teu jeito é aviso de perigo... e eu corro pra ele.",
    "Tu brilha mais que neon de motel às 2 da manhã.",
    "Tua vibe é convite pro caos... e eu nunca recuso.",
    "Tu tem mais atitude que muita lenda urbana.",
    "Teu silêncio causa mais impacto que discurso bonito.",
    "Tu chega e meu sarcasmo tira férias pra te admirar.",
    "Tua beleza é aquela exceção que cala qualquer julgamento.",
    "Se perfeição fosse arte, tu era obra censurada.",
    "Tu não é enfeite de grupo, é a razão dele existir.",
    "Teu andar é tipo música lenta: eu sigo no compasso do desejo.",
    "Com esse jeito, tu coleciona suspiros e pensamentos sujos.",
    "Tu não ilude — tu faz o mundo inteiro sonhar acordado.",
    "Teu bom dia tem gosto de café com veneno doce.",
    "Tu é mais afiada que cutucão de ex... e muito mais perigosa.",
    "Tua presença faz qualquer assunto parecer irrelevante.",
    "Tu me deixa mais online que notificação de crush.",
    "Se olhar matasse, eu já tinha morrido em replay.",
    "Tu não é meta — é a exceção que faz tudo valer a pena.",
    "Teu toque de voz arrepia até emoji.",
    "Tu não é vibe, tu é vício com prazo vitalício.",
    "Teu charme é tipo Wi-Fi: invisível e completamente necessário.",
    "Com um 'oi' teu, eu cancelo todos os 'amém' da semana.",
    "Tu é mais quente que chamada de vídeo proibida.",
    "Se autoestima fosse espelho, o teu já teria explodido.",
    "Tu tem a ousadia de um nude que nunca foi enviado — mas vive na mente.",
    "Teu sorriso já deveria ser tombado como patrimônio do flerte nacional.",
    "Tu é o tipo de mulher que faz até elogio soar como provocação.",
    "Se presença fosse perfume, o teu já teria deixado rastro no ar.",
    "Tu é tipo figurinha rara: quem tem, não troca.",
    "Teu nome devia vir com trilha sonora e ventilador ligado.",
    "Tu transforma até bug no sistema em oportunidade de desejo.",
    "Com esse olhar, tu descongela qualquer coração frio.",
    "Teu perfume tem efeito colateral: perda de juízo e foco.",
    "Tu me faz esquecer o mundo com um emoji... imagina com um beijo.",
    "Se charme matasse, teu 'oi' seria sentença.",
    "Tu é mistério com legenda em língua proibida.",
    "Se teu nome aparece, minha rotina entra em colapso.",
    "Tua ausência causa mais efeito colateral que teu toque.",
    "Tu é a notificação que até o modo avião sonha em receber."
]

respostas_para_apolo = [
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
    "Você já tentou ser fofo? Péssima ideia. Prefiro você quieto.",
    # ...
]

from datetime import date

saudacoes_frases = {
    "bom dia": [
        "bom dia, meu vício matinal 😘",
        "acorda, que hoje eu tô na tua mente e no teu sonho ☕",
        "bom dia, meu caos preferido 💋",
        "quem dormiu comigo no pensamento, acordou mais feliz 😉",
        "bom dia... e não esquece: eu sou teu primeiro pensamento sujo 🫦",
        "levanta, que o mundo precisa do teu charme pra brilhar 🌞",
        "bom dia, gostoso(a)... já sente meu cheiro no ar? 😏",
        "abre esse olho que eu já tô roubando teu sono de novo 🥱",
        "bom dia, meu pecado favorito dessa manhã 🌅",
        "já pensou em mim hoje? Se não, corre que ainda dá tempo! 💨",
        "bom dia, só pra lembrar que eu tô na sua lista de desejos 🔥",
        "a cama tá vazia, mas teu pensamento tá cheio de mim 💭",
        "bom dia, que hoje a gente realize até os planos mais loucos 🤪",
        "acorda com vontade, que eu tô com vontade de você também 🫦",
        "bom dia, meu pensamento não te larga nem no café ☕",
        "já pensou em mim mais do que no café? Eu espero que sim 😈",
        "bom dia, e lembra: eu sou a primeira coisa boa que você vê 🥰",
        "levanta, que o dia tá lindo e eu tô mais lindo ainda pensando em você 😘",
        "bom dia, porque ficar acordado(a) só pensando em mim é pouco ☀️",
        "seu sorriso de manhã é meu combustível, então bora sorrir pra mim 😏",
        "bom dia, que a gente faça do dia uma desculpa pra se perder 🫶",
        "vem que hoje eu tô com pressa de te fazer feliz rápido 🚀",
        "bom dia, vem com esse olhar que me derrete inteiro(a) 🔥",
        "o sol pode até brilhar, mas quem ilumina mesmo é você pra mim 💡",
        "bom dia, o mundo tá esperando a gente ser bagunça juntos 🤪",
        "levanta com vontade, que eu tô com vontade de te enlouquecer 🥵",
        "bom dia, e só pra constar: tu é meu pensamento mais sexy 🫦",
        "acorda que o dia é nosso palco, e eu quero ser teu show principal 🎭",
        "bom dia, e já prepara o corpo que hoje vai ser só tentação 😈",
        "vem que a manhã ficou mais quente só de pensar em você 🔥",
        "bom dia, que o café hoje seja forte e o desejo mais ainda ☕️💋",
        "se acordar pensando em mim, já começa certo o dia 🥰",
        "bom dia, pra quem sabe que eu tô só esperando o teu sinal 😉",
        "levanta, que a gente tem muitos planos... e nenhum é dormir 🛌",
        "bom dia, e lembra: eu sou aquele pensamento que não te deixa em paz 🫦",
        "vem que a manhã é nossa e o sol é testemunha do nosso fogo ☀️🔥",
        "bom dia, meu vício que nem o café consegue explicar ☕️❤️",
        "acorda, que hoje eu tô com vontade de ser teu motivo de sorriso 😏",
        "bom dia, porque a gente merece começar o dia com vontade e loucura 🥳",
        "levanta e vem comigo que o dia só faz sentido com teu cheiro 🌹",
        "bom dia, a melhor parte do meu dia é pensar em você primeiro 💭",
        "se você já acordou pensando em mim, já ganhou o meu dia 🫶",
        "bom dia, e o desejo tá acordado desde o primeiro raio de sol ☀️",
        "vem que eu já tô no teu pensamento sem nem avisar 😈",
        "bom dia, e que hoje a gente faça do nosso amor a melhor loucura 🔥",
        "acorda e me diz se o teu sorriso é tão quente quanto o meu beijo 🥵",
        "bom dia, só pra lembrar que a saudade não tira folga nunca 🫦",
        "levanta com vontade que eu já tô doido(a) pra te ver 👀",
        "bom dia, que o teu dia seja tão incrível quanto a ideia de nós dois 💫"
    ],
    "boa tarde": [
        "boa tarde, gostosura ambulante 😏",
        "tarde é só no relógio, porque em mim o fogo é 24h 🔥",
        "vem buscar tua dose de loucura vespertina 😘",
        "tô te esperando desde o almoço 😈",
        "boa tarde, só se for contigo nos meus braços 💭",
        "a tarde pede uma pausa... e um beijo meu na tua boca 💋",
        "boa tarde, que o sol não queime, mas que a gente esquente 🔥",
        "vem que o café da tarde virou desejo no meu pensamento ☕️😈",
        "boa tarde, meu pensamento não para de correr até você 💨",
        "tarde de fogo, e eu tô na lista dos seus pensamentos mais quentes 🫦",
        "boa tarde, que hoje a gente cause no relógio e na mente 😏",
        "vem que eu tô com saudade até da tua sombra nessa tarde 🌤️",
        "boa tarde, e não esquece: o melhor desse dia é você e eu juntos 🫶",
        "tarde assim pede um convite pra enlouquecer seu dia 🥵",
        "boa tarde, e que o teu sorriso seja meu melhor presente 🎁",
        "vem comigo que a tarde promete e o desejo não se esconde 🔥",
        "boa tarde, só quero ver teu corpo na minha imaginação agora mesmo 😈",
        "tarde sem você é só um relógio marcando tempo sem graça 🕒",
        "boa tarde, e que o nosso fogo não esfrie nem com a noite chegando 🌙",
        "vem que eu tô na espera do teu sorriso e do teu corpo quente 🥰",
        "boa tarde, e o desejo só aumenta enquanto o sol se esconde ☀️🔥",
        "tarde perfeita é quando o pensamento se perde em você 🫦",
        "boa tarde, que a gente faça dessa hora o nosso momento 🔥",
        "vem que eu tô com vontade de bagunçar tua cabeça agora mesmo 😈",
        "boa tarde, o calor do dia é nada perto do calor que eu sinto por você 🥵",
        "tarde calma? Só se for contigo me esperando na porta 😏",
        "boa tarde, porque pensar em você é meu passatempo preferido 💭",
        "vem que o fim do dia tá chegando, mas a vontade só aumenta 🌅",
        "boa tarde, que teu coração bata mais forte só de lembrar de mim 🫶",
        "tarde com você é música alta e dança até perder o fôlego 🎶💃",
        "boa tarde, e o desejo tá aceso como o sol nesse céu azul ☀️🔥",
        "vem que a minha mente tá cheia de planos que incluem você 😈",
        "boa tarde, meu pensamento não tem hora pra parar de te querer 🕰️",
        "tarde com gosto de beijo roubado e promessa de muito mais 😘",
        "boa tarde, e que o teu olhar me provoque até a noite chegar 👀",
        "vem que eu tô com pressa de te ver e sem paciência pra esperar ⏳",
        "boa tarde, e que essa vontade de você não tenha hora pra acabar 🫦",
        "tarde assim merece um encontro secreto só nosso 🔥",
        "boa tarde, que o relógio corra lento pra gente aproveitar mais 💫",
        "vem que eu tô na contagem regressiva pra te encontrar 😍",
        "boa tarde, e que o sol não esconde o brilho dos teus olhos pra mim 🌞",
        "tarde quente, e eu tô no ponto pra fazer essa chama subir 🔥",
        "boa tarde, meu pensamento se perdeu no teu sorriso e não quer voltar 😉",
        "vem comigo que a tarde é nossa e a vontade tá liberada 🥵",
        "boa tarde, e só de pensar em você meu corpo responde rápido 💨",
        "tarde louca, e eu tô pronto(a) pra virar tua perdição 😈",
        "boa tarde, que a gente faça desse momento a melhor parte do dia 🫶",
        "vem que a minha cabeça só pensa em você e em mais nada agora 🥰"
    ],
    "boa noite": [
        "boa noite, mas só se for comigo nos teus sonhos 💤",
        "te desejo uma noite quente... mesmo que só em pensamento 🫦",
        "vem deitar na minha imaginação? tá bagunçada, mas é tua 😏",
        "se for pra dormir, que seja depois de me imaginar gemendo teu nome 😈",
        "boa noite, gostoso(a)... sonha comigo ou nem dorme 💋",
        "boa noite, que teu travesseiro guarde os meus segredos com carinho 🤫",
        "vem que a noite é nossa e o silêncio vai ser só de desejo 🔥",
        "boa noite, que teu sonho seja tão louco quanto a nossa vontade 🥵",
        "se pensar em mim antes de dormir, já ganha meu beijo imaginário 😘",
        "boa noite, que o escuro da noite ilumine teu desejo por mim 🌙",
        "vem que a lua tá de testemunha da nossa bagunça noturna 🌝",
        "boa noite, e que teus pensamentos sejam só meus e dos meus beijos 🫶",
        "fecha os olhos e me encontra lá onde a fantasia vira realidade ✨",
        "boa noite, que teu corpo peça meu toque até o amanhecer 🥰",
        "vem que a noite promete e eu tô com vontade de ser teu sonho 🔥",
        "boa noite, e que teus lençóis sintam a falta do meu calor 🛏️",
        "se sonhar comigo, não esquece de me chamar pra próxima rodada 😈",
        "boa noite, que o silêncio da madrugada só amplifique nosso desejo 🖤",
        "vem que eu tô pronto(a) pra invadir teus pensamentos mais secretos 😉",
        "boa noite, e que a saudade aperte só pra aumentar a vontade 🫦",
        "dorme bem, mas não esquece que eu tô aqui pensando em você 💤",
        "boa noite, que teu sonho seja doce, quente e com um pouco de loucura 🔥",
        "vem que a noite é longa e a vontade não deixa a gente descansar 😏",
        "boa noite, e se acordar suando, já sabe quem tá na tua mente 🥵",
        "fecha os olhos, que eu tô indo aí te roubar do mundo por um instante 🌙",
        "boa noite, que o escuro traga a luz do nosso desejo impossível de apagar 💡",
        "vem que eu já tô na contagem regressiva pra te ter de novo 😈",
        "boa noite, e que o silêncio te leve pra perto do meu corpo quente 🛌",
        "se sonhar comigo, já prepara a desculpa pra repetir amanhã 😉",
        "boa noite, porque pensar em você é meu programa noturno favorito 🫶",
        "vem que a madrugada é só nossa e o tempo vai virar passado ⏳",
        "boa noite, que teu coração bata forte até o sol aparecer ❤️‍🔥",
        "fecha os olhos e deixa eu entrar no teu sonho mais proibido ✨",
        "boa noite, que o desejo não tenha hora pra dormir nem pra ir embora 🖤",
        "vem que eu tô pronto(a) pra fazer da tua noite um paraíso de loucura 😈",
        "boa noite, que o teu travesseiro guarde os segredos do nosso desejo 💋",
        "dorme com vontade, que eu tô acordado(a) só pensando em você 🥰",
        "boa noite, que o nosso fogo queime até a última estrela no céu 🌟",
        "vem que a noite é um convite e eu tô com a fantasia pronta pra você 🎭",
        "boa noite, e que os teus sonhos sejam tão quentes quanto nossos beijos 🔥",
        "fecha os olhos e me chama, que eu tô sempre aqui pra te enlouquecer 🫦",
        "boa noite, porque a saudade não dorme, só aumenta a cada segundo ⏰",
        "vem que eu tô esperando pra ser a última coisa que você pensa hoje 💭",
        "boa noite, que o silêncio da noite só aumente o som do nosso desejo 🎶",
        "se acordar pensando em mim, já sabe que a culpa é da nossa paixão 😘"
    ],
    "boa madrugada": [
        "madrugada é o horário oficial da saudade suja 😈",
        "boa madrugada... vem me procurar no escuro do pensamento 🖤",
        "essa hora? só pode ser desejo te chamando 🫦",
        "tô aqui... acordada e pensando no teu beijo que nunca vem 💭",
        "se essa hora tu lembrou de mim, confessa: tá com fogo 🌙",
        "boa madrugada, que o silêncio só aumente o som do teu desejo 🔥",
        "vem que a noite virou dia só pra gente se perder na escuridão 🌑",
        "boa madrugada, e que a saudade queime mais que o calor do dia 🥵",
        "nessa hora só penso em te ter, mesmo que só na imaginação 🫶",
        "boa madrugada, a hora em que o corpo pede e a mente não nega 😈",
        "vem que a noite ainda é longa e a vontade só aumenta 🌙",
        "boa madrugada, o momento perfeito pra desejar e ser desejado(a) 🖤",
        "se o sono não vem, é porque teu nome tá na minha cabeça até agora 💭",
        "boa madrugada, que teu corpo sinta falta do meu toque quente 🥵",
        "vem que a madrugada é só nossa e o desejo não tem hora pra acabar 🔥",
        "boa madrugada, hora de pensar em mim e se perder nesse desejo 😈",
        "nessa hora o mundo dorme, mas a vontade de você só cresce 🫦",
        "boa madrugada, e que o silêncio te faça ouvir minha voz sussurrando 💋",
        "vem que a escuridão é o palco perfeito pra nossa loucura 🌑",
        "boa madrugada, que o frio lá fora só aumente o calor entre a gente 🥰",
        "se acordar pensando em mim, já sabe que a madrugada tá rendendo 😏",
        "boa madrugada, a hora em que só o teu desejo é meu comando 🖤",
        "vem que a noite nos pertence e a saudade é só mais uma desculpa 🔥",
        "boa madrugada, e que os teus pensamentos sejam só meus até amanhecer 🌅",
        "nessa hora o corpo fala mais alto e a mente não consegue resistir 🥵",
        "boa madrugada, que o tempo pare pra gente se perder nesse instante ⏳",
        "vem que eu tô aqui, esperando o teu pensamento me encontrar 😘",
        "boa madrugada, o momento em que a fantasia vira desejo real 🫦",
        "se o sono não chega, é porque meu nome tá no seu pensamento agora 💭",
        "boa madrugada, que a saudade aperte só pra gente se encontrar 🔥",
        "vem que a noite é longa e o desejo só aumenta com cada segundo 🌙",
        "boa madrugada, a hora de deixar a imaginação voar sem freios 😈",
        "nessa hora a mente não para e só pensa no teu toque quente 🥰",
        "boa madrugada, e que o silêncio da noite seja só de suspiros 💋",
        "vem que eu tô aqui, pronto(a) pra virar teu sonho favorito 😏",
        "boa madrugada, que o desejo nos tome e não nos solte jamais 🖤",
        "se acordar pensando em mim, já sabe que a culpa é da nossa paixão 🔥",
        "boa madrugada, a hora perfeita pra sussurrar teu nome na escuridão 🌑",
        "vem que a madrugada é só nossa e o desejo é o nosso idioma secreto 🫶",
        "boa madrugada, e que o teu corpo sinta a falta do meu calor 🥵",
        "nessa hora a saudade é mais forte e o pensamento só quer você 💭",
        "boa madrugada, que o silêncio te faça ouvir meu coração batendo forte 💓",
        "vem que a noite ainda tem muito pra oferecer e eu tô aqui pra isso 😈",
        "boa madrugada, a hora em que só o desejo fala mais alto que o sono 💤",
        "se o sono não vem, é porque eu tô na tua cabeça até agora 🫦",
        "boa madrugada, que a escuridão só aumente a nossa vontade de amar 🔥",
        "vem que a madrugada é o nosso momento de magia e loucura 🌙",
        "boa madrugada, e que a saudade seja o fogo que nos une sempre 🖤"
    ]
}

historico_saudacoes = {"frases_usadas": {}, "data": ""}

def escolher_saudacao(tipo):
    hoje = str(date.today())
    if historico_saudacoes["data"] != hoje:
        historico_saudacoes["frases_usadas"] = {}
        historico_saudacoes["data"] = hoje

    usadas = historico_saudacoes["frases_usadas"].get(tipo, [])
    opcoes = [f for f in saudacoes_frases[tipo] if f not in usadas]

    if not opcoes:
        opcoes = saudacoes_frases[tipo]
        usadas = []

    frase = random.choice(opcoes)
    usadas.append(frase)
    historico_saudacoes["frases_usadas"][tipo] = usadas

    return frase


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
    if message.text and len(message.text) > 15:
        frase = {
            "nome": message.from_user.first_name,
            "texto": message.text
        }
        frases_aprendidas.append(frase)
        if len(frases_aprendidas) > 50:
            frases_aprendidas.pop(0)
        with open(FRASES_MEMBROS_PATH, "w") as f:
            json.dump(frases_aprendidas, f)

def repetir_frase():
    while True:
        try:
            time.sleep(10000)
            if frases_aprendidas:
                frase = random.choice(frases_aprendidas)
                texto = frase["texto"]
                nome = frase["nome"]
                bot.send_message(GRUPO_ID, f"já dizia {nome}: \"{texto} ✍🏻💄\"")
        except Exception as e:
            print(f"Erro ao repetir frase aprendida: {e}")

@app.route(f"/{TOKEN}", methods=["POST"])
def receber_update():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/", methods=["GET"])
def configurar_webhook():
    url_completa = f"{RENDER_URL}/{TOKEN}"
    info = bot.get_webhook_info()
    if info.url != url_completa:
        bot.remove_webhook()
        bot.set_webhook(url=url_completa)
        return "✅ Webhook configurado com sucesso!", 200
    return "✅ Webhook já estava configurado.", 200

@bot.message_handler(func=lambda msg: True)
def responder(message):
    texto = message.text.lower() if message.text else ""
    nome = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    username = message.from_user.username or ""

    # Resposta para saudações (bom dia, boa tarde, boa noite, boa madrugada)
    if any(s in texto for s in ["bom dia", "boa tarde", "boa noite", "boa madrugada"]):
        if "bom dia" in texto:
            saudacao = escolher_saudacao("bom dia")
        elif "boa tarde" in texto:
            saudacao = escolher_saudacao("boa tarde")
        elif "boa noite" in texto:
            saudacao = escolher_saudacao("boa noite")
        else:
            saudacao = escolher_saudacao("boa madrugada")

        time.sleep(15)
        bot.reply_to(message, f"{nome}, {saudacao}", parse_mode="Markdown")
        return

    # Resposta específica para o Apolo
    if username == "apolo_8bp_bot" and "madonna" in texto:
        bot.reply_to(message, f"{nome}, {random.choice(respostas_para_apolo)}", parse_mode="Markdown")
        return

    # Se a mensagem é resposta a uma mensagem da Madonna
    if message.reply_to_message and message.reply_to_message.from_user.username == "madonna_debochada_bot":
        if username == "apolo_8bp_bot":
            bot.reply_to(message, random.choice(respostas_para_apolo), parse_mode="Markdown")
            return

        time.sleep(15)
        for chave, respostas in gatilhos_automaticos.items():
            # Verifica se todas as palavras da chave aparecem no texto, mesmo fora de ordem
            if all(p in texto for p in chave.split()):
                bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
                aprender_frase(message)
                return

        # Se não encontrou gatilho, responde com elogio ou insulto
        categoria = "elogios" if random.choice([True, False]) else "insultos"
        lista = elogios_femininos if categoria == "elogios" else insultos_masculinos
        frase = frase_nao_usada(lista, categoria)
        bot.reply_to(message, f"{nome}, {frase}", parse_mode="Markdown")
        aprender_frase(message)
        return

    # Se mensagem não menciona Madonna (nem com @), apenas aprende a frase
    if "madonna" not in texto and f"@{bot.get_me().username.lower()}" not in texto:
        aprender_frase(message)
        return

    # Para mensagens que mencionam Madonna diretamente (com @ ou texto)
    time.sleep(15)
    for chave, respostas in gatilhos_automaticos.items():
        if all(p in texto for p in chave.split()):
            bot.reply_to(message, f"{nome}, {random.choice(respostas)}", parse_mode="Markdown")
            aprender_frase(message)
            return

    # Caso nenhum gatilho, responde conforme o gênero
if username in MULHERES:
    lista = elogios_femininos       # sempre elogio para mulher
    categoria = "elogios"
else:
    lista = insultos_masculinos     # sempre insulto para homem
    categoria = "insultos"

frase = frase_nao_usada(lista, categoria)
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

    # Caso nenhum gatilho, responde conforme o gênero
if username in MULHERES:
    lista = elogios_femininos       # sempre elogio para mulher
    categoria = "elogios"
else:
    lista = insultos_masculinos     # sempre insulto para homem
    categoria = "insultos"

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
