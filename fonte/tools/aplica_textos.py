"""Textos curtos, em português e inglês, para obras, exposições e coletivas.

Cada obra: texto (pt), en (texto em inglês), e traduções da ficha.
Os argumentos vêm dos textos do artista: o ruído como expressão do mundo, o corpo sonoro,
o campo sonoro, a escuta, a deriva, a cidade como labirinto, o anônimo, a pele do mundo.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "obras.json"

OBRAS = {
 "esquina": dict(
   pt="A esquina é onde os caminhos se cruzam e o som muda de direção. Sensores acionam motores e trânsito: quem caminha compõe a cidade que escuta.",
   en="A corner is where paths cross and sound changes direction. Sensors set off engines and traffic: whoever walks composes the city they hear.",
   materiais_en="Wood, acrylic paint, audio, presence sensors", dimensoes_en="Variable dimensions",
   local_en="Futuros – Arte e Tecnologia, Rio de Janeiro"),
 "esquinas": dict(
   pt="Desenhos em preto e branco feitos de linhas que se cruzam. Nenhum ponto de vista é o único: cada linha que fecha um plano abre outro.",
   en="Black-and-white drawings made of crossing lines. No viewpoint is the only one: every line that closes a plane opens another.",
   materiais_en="Acrylic on canvas", dimensoes_en="10 pieces, 100 × 100 cm each",
   local_en="Futuros – Arte e Tecnologia, Rio de Janeiro"),
 "mascara-sonora": dict(
   pt="Uma máscara de gás que não filtra: respira. O corpo vira alto-falante do ar que a cidade torna irrespirável.",
   en="A gas mask that does not filter: it breathes. The body becomes a loudspeaker for the air the city makes unbreathable.",
   materiais_en="Gas mask altered with loudspeakers; video performance", local_en="Rio de Janeiro"),
 "turbina": dict(
   pt="Uma parede de tubos devolve o mar à praia onde foi gravado. O som traduz a paisagem em outra matéria.",
   en="A wall of tubes returns the sea to the beach where it was recorded. Sound translates landscape into another matter.",
   materiais_en="Wood, acrylic paint, PVC, recording of the sea",
   dimensoes_en="261 × 263 cm (2013); 410 × 285 × 30 cm (2023)",
   local_en="Casa de Cultura Laura Alvim (2013); Futuros – Arte e Tecnologia (2023)"),
 "historias-anonimas": dict(
   pt="E se as ruas tivessem o nome de quem as construiu? Uma coluna de caixas de som dá voz aos anônimos que a grande narrativa esqueceu.",
   en="What if streets bore the names of those who built them? A column of loudspeakers gives voice to the anonymous people the grand narrative forgot.",
   materiais_en="Amplified loudspeakers on a stand, fictional recordings and field recordings",
   dimensoes_en="3 × 2 × 1.80 m; 3 min 45 s. Version as a column of handmade wooden speaker boxes: 160 × 20 cm",
   citacao_en="What if Rua do Ouvidor were called Maria das Dores / What if Rua do Senado were called João da Silva / What if Presidente Vargas were called João Cândido / What if every street belonged to the Silvas and the Santos / What if the city remembered its bodies / What would it say"),
 "espreguicadeiras-sonoras": dict(
   pt="Deitar e ouvir o mar diante de outra paisagem. A escuta vira hábito do corpo em repouso.",
   en="Lie down and hear the sea before another landscape. Listening becomes a habit of the resting body.",
   materiais_en="Wood, recording of the sea",
   local_en="Parque das Ruínas, Rio de Janeiro (2016); Futuros – Arte e Tecnologia (2023)"),
 "muro-de-som": dict(
   pt="Duas paredes de alto-falantes sopram um vento feito da respiração do artista. Nas ruínas, o muro não separa: abre passagem.",
   en="Two walls of loudspeakers blow a wind made of the artist's own breath. In the ruins, the wall does not divide: it opens a way through.",
   materiais_en="Two walls with 32 loudspeakers each, sound of wind", dimensoes_en="2 walls, 330 × 170 cm",
   local_en="Parque das Ruínas, Rio de Janeiro"),
 "binoculos-sonoros": dict(
   pt="Quanto mais nítida a vista, mais próxima a voz. A paisagem é contada por quem a construiu.",
   en="The sharper the view, the closer the voice. The landscape is told by those who built it.",
   materiais_en="Coin-operated panoramic binoculars, adapted; fictional narrative", local_en="Parque das Ruínas, Rio de Janeiro"),
 "errancia": dict(
   pt="Frases ouvidas de passagem nos bares da cidade, gravadas por um corpo à deriva. Sem origem, os fragmentos fazem da fala um ruído comum.",
   en="Phrases overheard in the city's bars, recorded by a drifting body. Without an origin, the fragments turn speech into common noise.",
   materiais_en="Loudspeakers; recordings made with a capture system worn by a passer-by", dimensoes_en="Variable dimensions",
   local_en="Sala A Contemporânea, Centro Cultural Banco do Brasil, Rio de Janeiro — CCBB Contemporary Award"),
 "sonar": dict(
   pt="Pela primeira vez dentro de uma casa: uma exposição inteira feita de ruído, em que cada obra soa quando a outra se cala.",
   en="For the first time inside a house: a whole exhibition made of noise, where each work sounds as another falls silent.",
   local_en="Casa de Cultura Laura Alvim, Rio de Janeiro"),
 "cidades-sonoras": dict(
   pt="Orelhões caídos guardam o som de quinze cidades. Basta se aproximar para estar em outro lugar.",
   en="Fallen public phone booths hold the sound of fifteen cities. Coming closer is enough to be somewhere else.",
   materiais_en="Public phone booths, soundscapes of 15 cities", dimensoes_en="Variable dimensions",
   local_en="Galeria Funarte, Palácio Gustavo Capanema, Rio de Janeiro"),
 "sapatos-sonoros": dict(
   pt="Pandeiros, guizos e conchas nos pés: cada passo é um instrumento. Caminhar passa a ser tocar o chão.",
   en="Tambourines, bells and shells on the feet: every step is an instrument. Walking becomes playing the ground.",
   materiais_en="Tambourine shoes, bell shoes, rattle and shell shoes; mixed materials", dimensoes_en="Variable dimensions",
   local_en="Panorama da Arte Brasileira, MAM São Paulo (2011); performances at exhibition openings (2011, 2013, 2015)"),
 "chuveiros-sonoros": dict(
   pt="O registro abre a voz, não a água. Quem sobe no chuveiro empresta o corpo a um cantor anônimo.",
   en="The tap opens a voice, not water. Whoever steps in lends their body to an anonymous singer.",
   materiais_en="Stainless steel showers, amplifier, loudspeaker and home recordings",
   local_en="7th Mercosul Biennial, Mostra Absurdo, Porto Alegre (2009); Casa de Cultura Laura Alvim (2013)",
   colecao_en="Museu de Arte Contemporânea de Niterói — acquired through the Marcantonio Vilaça Award, Funarte, 2012"),
 "chapeu-panoramico": dict(
   pt="Câmeras no chapéu dos mestres de capoeira: o jogo visto de dentro da roda. O artista deixa o centro para que o outro entre.",
   en="Cameras on the capoeira masters' hats: the game seen from inside the circle. The artist leaves the centre so that the other may enter.",
   materiais_en="Hats with surveillance cameras, multichannel video", local_en="Beach, Rio de Janeiro; MAC Niterói (2009)"),
 "falante": dict(
   pt="Um alto-falante nas costas repete: não preste atenção. Quem se vira para ouvir já desobedeceu.",
   en="A loudspeaker on the back keeps saying: do not pay attention. Whoever turns to listen has already disobeyed.",
   materiais_en="Backpack with loudspeaker, sound poem “Não preste atenção” [Do not pay attention]",
   local_en="Fortaleza (58th Salão de Abril, honourable mention) and São Paulo (Futuro do Presente, Itaú Cultural), 2007",
   colecao_en="Museo de Artes Visuales, Santiago, Chile"),
 "cruz": dict(
   pt="Um micro-rádio desenha uma cruz sobre o cruzamento. Fora do seu alcance, a transmissão desaparece.",
   en="A micro-radio draws a cross over the crossroads. Beyond its reach, the broadcast disappears.",
   materiais_en="Micro-radio transmitter, soundtrack; documented in aerial photograph and video",
   dimensoes_en="Crossing of Rua Imperatriz Leopoldina and Rua Luís de Camões", local_en="Downtown Rio de Janeiro"),
 "o-inusitado": dict(
   pt="Um programa semanal numa rádio comunitária da Lapa, aberto a quem tivesse algo a dizer. Entre 2002 e 2004, a cena sonora carioca se encontrou no ar.",
   en="A weekly programme on a community radio station in Lapa, open to anyone with something to say. From 2002 to 2004, Rio's sound scene met on air.",
   materiais_en="Weekly radio programme", local_en="Rádio Madame Satã, Lapa, Rio de Janeiro"),
 "radionovelas": dict(
   pt="Rádios antigos contam pequenas ficções sobre sonhos e sobre o próprio ato de ouvir.",
   en="Old radios tell short fictions about dreams and about the act of listening itself.",
   materiais_en="Vintage radios and fictional recordings", local_en="Casa de Cultura Laura Alvim, in the exhibition Sonar"),
 "desenhos": dict(
   pt="Fita isolante sobre papel: trajetos, cruzamentos, encontros possíveis. É daqui que nascem as Esquinas.",
   en="Electrical tape on paper: routes, crossings, possible encounters. This is where the Esquinas began.",
   materiais_en="Electrical tape on paper", dimensoes_en="Various sizes (20 × 30, 50 × 40, 40 × 20 cm)",
   local_en="Casa de Cultura Laura Alvim, in the exhibition Sonar (2013)"),
 "cidade-labirinto": dict(
   pt="A cidade é um labirinto a ser decifrado pela escuta. Em Tablado número 30, o corpo do artista entra no som das ruas e o atravessa.",
   en="The city is a labyrinth to be deciphered by listening. In Tablado número 30 [Stage 30], the artist's body enters the sound of the streets and moves through it.",
   materiais_en="Tablado número 30: painted wooden platform, loudspeakers, street recordings, gas mask with loudspeaker; digital exhibition and podcast",
   local_en="Centro Municipal de Arte Hélio Oiticica, Rio de Janeiro (May 2021); cidadelabirinto.art (August 2021)"),
 "cidade-sensivel": dict(
   pt="Três caminhadas pelo centro vazio durante a pandemia: Cinelândia, Pedra do Sal, Praça Mauá. Escutar a cidade é lembrar quem a fez.",
   en="Three walks through the empty city centre during the pandemic: Cinelândia, Pedra do Sal, Praça Mauá. To listen to the city is to remember who made it.",
   materiais_en="Sound work in three parts: Cinelândia, Pedra do Sal and Praça Mauá; podcast",
   local_en="Rio de Janeiro; recorded on 20 February 2021"),
 "espacos-do-ainda": dict(
   materiais_en="Installation and sound object, sound poem",
   local_en="Paço Imperial, Rio de Janeiro (2022); Centro Cultural São Paulo (2023)"),
 "poema-tornado": dict(
   pt="Um poema que gira e se espalha pela galeria: escrita, som e sentido se desfazem em turbilhão. Respira, olha, siga.",
   en="A poem that spins and spreads through the gallery: writing, sound and meaning dissolve into a whirl. Breathe, look, follow.",
   materiais_en="Poem-installation: writing, sounds and visual sources spread through the gallery",
   local_en="Galeria Reserva Cultural, Niterói. Curated by Marisa Flórido; coordinated by Vilmar Madruga, EIXO Arte Contemporânea"),
 "o-rio-dos-navegantes": dict(
   pt="Instalação sonora comissionada pelo Museu de Arte do Rio para a exposição O Rio dos Navegantes. Hoje no acervo do museu.",
   en="Sound installation commissioned by the Museu de Arte do Rio for the exhibition O Rio dos Navegantes. Now in the museum's collection.",
   materiais_en="Commissioned sound installation",
   local_en="Museu de Arte do Rio — exhibition O Rio dos Navegantes, curated by Evandro Salles, 2019–2020",
   colecao_en="Museu de Arte do Rio"),
 "nuvem": dict(
   pt="Guarda-chuvas que chovem som. Sob cada um, um abrigo e uma escuta.",
   en="Umbrellas that rain sound. Under each one, a shelter and a way of listening.",
   materiais_en="Sound installation with umbrellas", local_en="Centro Cultural Furnas, Rio de Janeiro"),
 "microradio": dict(
   pt="Transmissores feitos em casa e um guia para quem quiser ocupar o ar: o rádio como território comum.",
   en="Homemade transmitters and a guide for anyone who wants to occupy the air: radio as common ground.",
   materiais_en="Video; homemade transmitters"),
 "radio-lugar": dict(
   pt="Sapatos com alto-falantes na travessia da barca. Bailarinos fazem do percurso uma apresentação, e do passageiro, público.",
   en="Shoes with loudspeakers on the ferry crossing. Dancers turn the journey into a performance, and passengers into an audience.",
   materiais_en="MP3 players and loudspeakers sewn onto ordinary shoes", dimensoes_en="Variable dimensions",
   local_en="Rio–Niterói ferry and Praça XV, Rio de Janeiro — Projeto EME>> Conexão Artes Visuais, Funarte"),
 "o-estrangeiro": dict(
   pt="Um móvel de vinte gavetas guarda sons de viagem. Abrir uma gaveta é ouvir um lugar distante.",
   en="A cabinet of twenty drawers holds sounds from journeys. Opening a drawer means hearing a faraway place.",
   materiais_en="Furniture, loudspeakers, home recordings", local_en="Casa de Cultura Laura Alvim, Rio de Janeiro"),
 "intrasom": dict(
   pt="Quatro ações sonoras no vão livre do MAM Rio.",
   en="Four sound actions in the open ground floor of MAM Rio.",
   materiais_en="Four sound actions in the museum's open ground floor",
   local_en="Museu de Arte Moderna do Rio de Janeiro — supported by the Rio de Janeiro State Secretariat of Culture"),
}

EXPOS = {
 "a-pele-do-mundo": dict(
   pt="O instante em que o corpo mergulha e se sente no mundo. Embaixo, máquinas e trânsito; em cima, o mar e a voz.",
   en="The moment the body dives in and feels itself in the world. Downstairs, machines and traffic; upstairs, the sea and the voice.",
   local_en="Futuros – Arte e Tecnologia, Rio de Janeiro",
   catalogo_en="Bilingual catalogue, Refresco / Futuros, 2023, ISBN 978-65982255-0-6"),
 "cidade-labirinto": dict(
   pt="Uma cidade imaginária construída pela escuta, entre a instalação e a exposição digital.",
   en="An imaginary city built by listening, between installation and digital exhibition.",
   local_en="Centro Municipal de Arte Hélio Oiticica, Rio de Janeiro; digital exhibition cidadelabirinto.art"),
 "poema-tornado": dict(
   pt="Exposição sonora: o poema expandido em labirinto.",
   en="A sound exhibition: the poem expanded into a labyrinth.",
   local_en="Galeria Reserva Cultural, Niterói", curadoria="Marisa Flórido"),
 "nuvem": dict(pt="Abrigos que soam.", en="Shelters that sound.", local_en="Centro Cultural Furnas, Rio de Janeiro"),
 "muro-de-som": dict(
   pt="Nas ruínas de uma casa, o som ocupa o que a parede perdeu. Quem percorre o parque segue uma história que só existe enquanto se anda.",
   en="In the ruins of a house, sound occupies what the walls have lost. Whoever walks through the park follows a story that exists only while walking.",
   local_en="Parque das Ruínas, Rio de Janeiro"),
 "errancia": dict(
   pt="A noite da cidade entra no cubo branco. Ao sair, o mundo lá fora soa como silêncio.",
   en="The city's night enters the white cube. On leaving, the world outside sounds like silence.",
   local_en="Centro Cultural Banco do Brasil, Rio de Janeiro — CCBB Contemporary Award"),
 "sonar": dict(
   pt="Som e ar. De frente para o mar de Ipanema, muitas obras se tornam um único ruído na memória de quem ouve.",
   en="Sound and air. Facing the sea at Ipanema, many works become a single noise in the listener's memory.",
   local_en="Casa de Cultura Laura Alvim, Rio de Janeiro"),
 "a-cidade-sonora": dict(
   pt="Quinze cidades caídas no chão de um palácio moderno.",
   en="Fifteen cities fallen on the floor of a modernist palace.",
   local_en="Galeria Funarte, Palácio Gustavo Capanema, Rio de Janeiro"),
}

COLETIVAS = {
 "virada-sonica": dict(titulo_en="Virada Sônica: the rise of sound in contemporary art — Espreguiçadeiras Sonoras",
                       local_en="Farol Santander, São Paulo. Curated by Chico Dub"),
 "o-rio-dos-navegantes": dict(
   pt="A história do Rio como cidade portuária, contada por quem chegou pelo mar.",
   en="The history of Rio as a port city, told through those who arrived by sea.",
   local_en="Museu de Arte do Rio, May 2019 to May 2020. Conceived and curated by Evandro Salles"),
 "arte-pra-sentir": dict(
   pt="Obras que convocam outros sentidos além da visão.", en="Works that call on senses beyond sight.",
   local_en="Caixa Cultural Brasília (16 October to 23 December 2018) and Caixa Cultural São Paulo. Curated by Isabel Portella"),
 "corpo-de-som": dict(
   titulo_en="Corpo de Som [Body of Sound], with Helen Cole and Alex Bradley — Panorama Festival",
   pt="O corpo ausente e os rastros que ele deixa no som.", en="The absent body and the traces it leaves in sound.",
   local_en="Centro Municipal de Arte Hélio Oiticica, Rio de Janeiro — Panorama Festival, 3–24 November 2018"),
 "paqueta-experimenta": dict(
   pt="Obras feitas a partir de uma imersão na ilha: natureza, cidade, ruído e silêncio.",
   en="Works made from an immersion on the island: nature, city, noise and silence.",
   local_en="Casa de Artes de Paquetá, Paquetá Island, Rio de Janeiro — 21 May to 25 June 2016. Curated by Ivair Reinaldim"),
 "permanencias-e-destruicoes": dict(
   pt="As camadas de tempo de um antigo hotel de 1922.", en="The layers of time in a former hotel built in 1922.",
   local_en="Former Hotel Balneário Sete de Setembro, now Colégio Brasileiro de Altos Estudos, UFRJ, Rio de Janeiro — 17–30 January 2015. Curated by João Paulo Quintella"),
 "trio-bienal": dict(
   titulo_en="TRIO Biennial — Forma e Matéria: the limits of the three-dimensional in expanded fields",
   pt="A primeira bienal do Rio dedicada ao tridimensional.", en="Rio's first biennial devoted to three-dimensional work.",
   local_en="Centro Cultural Banco do Brasil, Rio de Janeiro. Curated by Marcus de Lontra"),
 "aparicao": dict(
   pt="Dezessete artistas repensam a escultura.", en="Seventeen artists rethink sculpture.",
   local_en="Caixa Cultural Rio de Janeiro. Curated by Fernanda Lopes. Performance with Sapatos Sonoros at the opening"),
}

# títulos descritivos das coletivas simples
TITULOS_EN = {
 "Falante, performance": "Falante, performance",
 "SomaRumor, Seminário Internacional de Arte Sonora": "SomaRumor, International Sound Art Seminar",
 "Happenings, performance com Máscara Sonora": "Happenings, performance with Máscara Sonora",
 "Panorama da Arte Brasileira, Sapatos Sonoros": "Panorama of Brazilian Art, Sapatos Sonoros",
 "Intrasom, quatro ações sonoras": "Intrasom, four sound actions",
 "Esculturas Sonoras Urbanas, Circuito Interações Estéticas": "Urban Sound Sculptures, Interações Estéticas circuit",
 "7ª Bienal do Mercosul — Chuveiros Sonoros (Mostra Absurdo) e Radiovisual": "7th Mercosul Biennial — Chuveiros Sonoros (Mostra Absurdo) and Radiovisual",
 "58º Salão de Abril, Falante — menção honrosa": "58th Salão de Abril, Falante — honourable mention",
 "Paradoxos, Rumos Itaú Cultural": "Paradoxos, Rumos Itaú Cultural",
 "Contraponto, Coleção Sérgio Carvalho": "Contraponto, Sérgio Carvalho Collection",
}
LOCAL_EN = [("Santiago do Chile", "Santiago, Chile"), ("Noruega", "Norway"), ("Londres", "London"),
            ("Romênia", "Romania"), ("Liubliana", "Ljubljana"), ("Eslovênia", "Slovenia"),
            ("Museu Nacional de Brasília", "Museu Nacional, Brasília"),
            ("Paço Imperial, Rio de Janeiro, e São Paulo", "Paço Imperial, Rio de Janeiro, and São Paulo"),
            ("São Paulo, Recife e Belo Horizonte", "São Paulo, Recife and Belo Horizonte"),
            ("Museu de Arte Moderna de São Paulo", "Museu de Arte Moderna de São Paulo")]


def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    for o in d["obras"]:
        t = OBRAS.get(o["id"])
        if not t:
            continue
        if "pt" in t:
            o["texto"] = [t["pt"]]
        if "en" in t:
            o["texto_en"] = [t["en"]]
        for k in ("materiais_en", "dimensoes_en", "local_en", "colecao_en", "citacao_en"):
            if k in t:
                o[k] = t[k]
        o.pop("autoria_texto", None)
    for x in d["exposicoes"]:
        t = EXPOS.get(x["id"])
        if t:
            x["texto"] = t["pt"]; x["texto_en"] = t["en"]
            for k in ("local_en", "catalogo_en", "curadoria"):
                if k in t:
                    x[k] = t[k]
    for c in d["coletivas"]:
        t = COLETIVAS.get(c.get("id", ""))
        if t:
            if "pt" in t:
                c["texto"] = t["pt"]; c["texto_en"] = t["en"]
            for k in ("local_en", "titulo_en"):
                if k in t:
                    c[k] = t[k]
        if "titulo_en" not in c and c["titulo"] in TITULOS_EN:
            c["titulo_en"] = TITULOS_EN[c["titulo"]]
        if "local_en" not in c:
            le = c["local"]
            for a, b in LOCAL_EN:
                le = le.replace(a, b)
            c["local_en"] = le
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("textos aplicados:", len(OBRAS), "obras,", len(EXPOS), "exposições,", len(COLETIVAS), "coletivas")


if __name__ == "__main__":
    main()
