"""Prepara as imagens das obras a partir do material da pasta 'site' do Google Drive.

Gera JPGs (lado maior até 1600 px) em media/obras/<id>/ e devolve, em data/imagens.json,
a lista de imagens por obra com legenda e crédito.
"""
import json
from pathlib import Path
from PIL import Image

SRC = Path("/home/claude/drive-material")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media" / "obras"

T, W, G, V, F, C, A, TB = ("Pedro Tressi", "Wilton Montenegro", "Mario Grisolli", "Vicente de Mello",
                           "Edouard Fraipont", "Gisele Camargo", "Arquivo do artista",
                           "Floriano Romano e Tiago Baldissara")
P, M, L, D, CL, S = ("pele_do_mundo_img", "muro_de_som_img", "laura_alvim_img", "dossier_2015_img",
                     "cidade_labirinto_img", "soltas")

PLANO = {
  "esquina": [(P, "i-035-045.jpg", "Esquina, Futuros – Arte e Tecnologia, 2023", T),
              (P, "i-036-047.jpg", "Esquina, vista da instalação", T),
              (P, "i-037-049.jpg", "Esquina e Esquinas I–X", T),
              (P, "i-040-055.jpg", "Esquina, detalhe", T)],
  "esquinas": [(P, "i-041-057.jpg", "Esquinas I–X, vista da exposição A Pele do Mundo", T),
               (P, "i-039-053.jpg", "Esquinas I–X e Esquina", T)],
  "turbina": [(P, "i-053-093.jpg", "Turbina, Futuros – Arte e Tecnologia, 2023", T),
              (P, "i-047-079.jpg", "Turbina e Espreguiçadeiras Sonoras, 2023", T),
              (S, "GRI_4622_fused.webp", "Turbina, Casa de Cultura Laura Alvim, 2013", G),
              (L, "i-011-012.jpg", "Turbina diante da praia de Ipanema, 2013", G)],
  "espreguicadeiras-sonoras": [(M, "i-011-006.jpg", "Espreguiçadeiras Sonoras, Parque das Ruínas, 2016", W),
                               (M, "i-008-003.jpg", "Espreguiçadeiras Sonoras no mirante do Parque das Ruínas", W),
                               (P, "i-048-081.jpg", "Espreguiçadeiras Sonoras, Futuros, 2023", T),
                               (P, "i-049-083.jpg", "Espreguiçadeiras Sonoras, Futuros, 2023", T)],
  "chuveiros-sonoros": [(M, "i-029-025.jpg", "Chuveiros Sonoros", V),
                        (M, "i-030-026.jpg", "Chuveiros Sonoros", V),
                        (P, "i-052-091.jpg", "Chuveiros Sonoros, Futuros, 2023", T),
                        (P, "i-051-089.jpg", "Chuveiros Sonoros, detalhe", T)],
  "mascara-sonora": [(P, "i-033-041.jpg", "Máscara Sonora, videoperformance, Futuros, 2023", T)],
  "muro-de-som": [(M, "i-006-001.jpg", "Muro de Som, Parque das Ruínas, 2016", W),
                  (M, "i-022-017.jpg", "Muro de Som, as duas paredes de alto-falantes", W),
                  (M, "i-012-007.jpg", "Muro de Som, a escada diante da obra", W),
                  (M, "i-038-034.jpg", "Muro de Som", W),
                  (M, "i-025-020.jpg", "Cúpulas Sonoras na escada de acesso", W)],
  "binoculos-sonoros": [(M, "i-014-009.jpg", "Binóculos Sonoros, Parque das Ruínas, 2016", W),
                        (M, "i-016-011.jpg", "Binóculos Sonoros", W),
                        (M, "i-018-013.jpg", "Binóculos Sonoros voltados para a Baía de Guanabara", W)],
  "errancia": [(M, "i-035-031.jpg", "Errância, Centro Cultural Banco do Brasil, 2016", G),
               (M, "i-034-030.jpg", "Errância", G),
               (M, "i-036-032.jpg", "Errância", G)],
  "falante": [("pdf1img", "im-000.jpg", "Falante, São Paulo, 2007", F),
              (S, "romano08-7.webp", "Falante, São Paulo, 2007", F),
              (M, "i-032-028.jpg", "Falante", F)],
  "sonar": [(L, "i-008-008.jpg", "Sonar, Casa de Cultura Laura Alvim, 2013", G),
            (L, "i-007-007.jpg", "O estrangeiro, 2013", G),
            (L, "i-019-024.jpg", "Kafka, 2012", G),
            (L, "i-015-020.jpg", "Desenhos com fita isolante na exposição Sonar", G)],
  "radionovelas": [(S, "GRI_4666_fused.webp", "Radionovelas, Casa de Cultura Laura Alvim, 2013", G),
                   (L, "i-005-003.jpg", "Radionovelas, detalhe", G)],
  "cidade-sonora": [(D, "i-020-020.jpg", "A Cidade Sonora, Palácio Gustavo Capanema, 2012", C),
                      (D, "i-021-021.jpg", "A Cidade Sonora", C)],
  "sapatos-sonoros": [(S, "DSC_0058-7.webp", "Sapatos Sonoros, sapatos pandeiro", A),
                      (S, "DSC_0091-6.webp", "Sapatos Sonoros, sapatos com conchas", A),
                      (D, "i-011-010.ppm", "Sapatos Sonoros, Panorama da Arte Brasileira, MAM São Paulo, 2011", C),
                      (D, "i-013-014.jpg", "Sapatos Sonoros, Panorama da Arte Brasileira", C)],
  "historias-anonimas": [(S, "ha_foto_a.png", "Histórias Anônimas, 2022", A, (0, 100, 0, 0)),
                         (S, "ha_foto_b.png", "Histórias Anônimas, com o artista", A)],
  "cidade-labirinto": [(CL, "i-007-009.jpg", "Cidade Labirinto, Centro Municipal de Arte Hélio Oiticica, 2021", TB),
                       (CL, "i-004-002.jpg", "Cidade Labirinto", TB),
                       (CL, "i-005-003.jpg", "Cidade Labirinto", TB)],
  "cidade-sensivel": [(CL, "i-010-018.jpg", "Cidade Sensível: Pedra do Sal", TB),
                      (CL, "i-011-023.jpg", "Cidade Sensível: Praça Mauá", TB)],
}

def main():
    saida = {}
    for obra, itens in PLANO.items():
        pasta = OUT / obra
        pasta.mkdir(parents=True, exist_ok=True)
        lista = []
        for n, item in enumerate(itens, 1):
            sub, nome, legenda, credito = item[:4]
            corte = item[4] if len(item) > 4 else None
            im = Image.open(SRC / sub / nome).convert("RGB")
            if corte:
                l, t, r, b = corte
                im = im.crop((l, t, im.width - r, im.height - b))
            im.thumbnail((1600, 1600), Image.LANCZOS)
            dest = pasta / f"{obra}-{n:02d}.jpg"
            im.save(dest, quality=84, optimize=True, progressive=True)
            lista.append({"src": f"media/obras/{obra}/{dest.name}", "alt": legenda,
                          "credito": f"{legenda} · Foto: {credito}" if credito != A else f"{legenda} · {A}",
                          "fotografo": credito})
        saida[obra] = lista
    (ROOT / "data" / "imagens.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2))
    tot = sum(len(v) for v in saida.values())
    print(f"{tot} imagens em {len(saida)} obras")

if __name__ == "__main__":
    main()
