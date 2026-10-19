"""Gera os sprites em pixel art do Motoboy Ultra Adventures (cenário/obstáculos/HUD).

Uso:  python tools/gerar_sprites.py

Cada sprite é desenhado numa grade pequena (1 "pixel de arte" = ESC pixels reais)
e ampliado com vizinho mais próximo, para manter o visual pixel art nítido.
Paleta tirada dos prédios do cenário (bg_predios_fase1.png).
Saída: Animations/<objeto>/<animação>/<frame>.png (estrutura do Construct 2).
"""
import os
import random
from PIL import Image, ImageDraw

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ESC = 4  # tamanho de cada "pixel de arte"

# ---- paleta -----------------------------------------------------------
def h(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

INK = h("#0d0820")
D0 = h("#140c24")
D1 = h("#1a102e")
D2 = h("#211438")
D3 = h("#2e1b4d")
D4 = h("#3d2663")
D5 = h("#55368a")
D6 = h("#7a5cc0")
HI = h("#c9b8ff")
CY = h("#5af0ff")
CYD = h("#2a7e86")
MG = h("#ff5adc")
MGD = h("#a02f8a")
YL = h("#ffd25a")
YLD = h("#c08a22")
OR = h("#ffaa5a")
OR2 = h("#ef7c3d")
OR3 = h("#b65c51")
BRN = h("#88443b")
BRN2 = h("#5a2a28")
GRN = h("#5af070")
GRN2 = h("#2fa84f")
RED = h("#ff4a5a")
CREME = h("#ffe8b6")
NADA = (0, 0, 0, 0)


def tela(w, h_):
    return Image.new("RGBA", (w, h_), NADA)


def px(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), c)


def ret(im, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(im, x, y, c)


def salvar(im, objeto, anim="Default", frame=0):
    big = im.resize((im.width * ESC, im.height * ESC), Image.NEAREST)
    pasta = os.path.join(RAIZ, "Animations", objeto, anim)
    os.makedirs(pasta, exist_ok=True)
    big.save(os.path.join(pasta, "%03d.png" % frame))
    return big.size


# ---- chão (topo de prédio / rua) ---------------------------------------
def chao(variante):
    im = tela(16, 48)
    rnd = random.Random(100 + variante)
    # fachada do prédio
    ret(im, 0, 0, 15, 47, D2)
    # superfície da rua
    ret(im, 0, 0, 15, 0, CY)
    ret(im, 0, 1, 15, 1, CYD)
    ret(im, 0, 2, 15, 4, D3)
    ret(im, 0, 2, 15, 2, D4)
    # faixa tracejada amarela
    for x in range(2 + (variante * 3) % 5, 16, 8):
        ret(im, x, 3, min(15, x + 3), 3, YLD)
    # meio-fio / sombra
    ret(im, 0, 5, 15, 5, INK)
    ret(im, 0, 6, 15, 6, D1)
    # painéis da fachada
    for y in (13, 25, 37):
        ret(im, 0, y, 15, y, D1)
    px(im, 0, 7, D1)
    for y in range(7, 48):
        px(im, 0, y, D1)
        px(im, 15, y, D3)
    # janelas acesas
    cores = [CY, MG, YL, CYD, D4]
    for linha in range(3):
        y0 = 8 + linha * 12
        for col in range(3):
            x0 = 2 + col * 5
            c = cores[rnd.randrange(len(cores))]
            ret(im, x0, y0, x0 + 2, y0 + 3, c)
            if c in (CY, MG, YL):
                px(im, x0, y0, HI if c == CY else c)
    # escurece a base (dither)
    for y in range(38, 48):
        for x in range(16):
            if (x + y) % 2 == 0 or y > 43:
                px(im, x, y, D1 if y < 44 else D0)
    return im


# ---- plataforma suspensa (192x32) --------------------------------------
def plataforma():
    im = tela(48, 8)
    ret(im, 0, 0, 47, 7, D4)
    ret(im, 0, 0, 47, 0, CY)          # luz de neon no topo
    ret(im, 0, 1, 47, 1, HI)
    ret(im, 0, 2, 47, 2, D5)
    ret(im, 0, 3, 47, 5, D4)
    ret(im, 0, 5, 47, 5, D3)
    ret(im, 0, 6, 47, 6, D1)
    ret(im, 0, 7, 47, 7, MG)          # brilho magenta embaixo
    for x in range(3, 48, 8):         # rebites
        px(im, x, 3, CYD)
        px(im, x, 4, D2)
    for x in range(0, 48, 12):        # emendas
        ret(im, x, 2, x, 6, D2)
    # cantos escurecidos
    for yy in range(8):
        px(im, 0, yy, D2)
        px(im, 47, yy, D2)
    px(im, 0, 0, NADA)
    px(im, 47, 0, NADA)
    px(im, 0, 7, MGD)
    px(im, 47, 7, MGD)
    return im


# ---- bloco / contêiner (64x64) -----------------------------------------
def bloco():
    im = tela(16, 16)
    ret(im, 0, 0, 15, 15, INK)
    ret(im, 1, 1, 14, 14, D4)
    ret(im, 1, 1, 14, 1, D6)          # chanfro claro (cima/esquerda)
    ret(im, 1, 1, 1, 14, D6)
    ret(im, 14, 2, 14, 14, D2)        # chanfro escuro (baixo/direita)
    ret(im, 2, 14, 14, 14, D2)
    for i in range(2, 14):            # reforço em X
        px(im, i, i, D3)
        px(im, 15 - i, i, D3)
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):  # rebites neon
        px(im, x, y, CY)
    # faixa de aviso no topo
    for x in range(2, 14):
        px(im, x, 3, YL if (x // 2) % 2 == 0 else INK)
    ret(im, 6, 7, 9, 9, D1)           # placa central
    px(im, 7, 8, MG)
    px(im, 8, 8, MG)
    return im


# ---- espinhos (64x32) ---------------------------------------------------
def espinho():
    im = tela(16, 8)
    ret(im, 0, 6, 15, 7, INK)         # base
    ret(im, 0, 6, 15, 6, D4)
    for i in range(4):
        x0 = i * 4
        # tronco do espinho
        ret(im, x0 + 1, 2, x0 + 2, 5, HI)
        ret(im, x0, 4, x0 + 3, 5, HI)
        ret(im, x0 + 2, 2, x0 + 3, 5, D6)   # lado sombreado
        px(im, x0 + 3, 4, D6)
        px(im, x0 + 3, 5, D5)
        # ponta em magenta (aviso)
        px(im, x0 + 1, 0, MG)
        px(im, x0 + 2, 0, MGD)
        px(im, x0 + 1, 1, MG)
        px(im, x0 + 2, 1, MGD)
        px(im, x0 + 1, 2, MG)
        px(im, x0 + 2, 2, MGD)
    for x in range(1, 16, 4):
        px(im, x, 7, D3)
    return im


# ---- lombada (128x24) ---------------------------------------------------
def lombada():
    im = tela(32, 6)
    for y in range(6):
        recuo = 8 - round(y * 8 / 5.0)     # topo estreito, base larga
        recuo = max(0, recuo)
        for x in range(recuo, 32 - recuo):
            faixa = ((x + y) // 4) % 2 == 0
            c = YL if faixa else INK
            if y == 0:
                c = YL if faixa else D3
            px(im, x, y, c)
    for x in range(0, 32):
        if im.getpixel((x, 5))[3]:
            px(im, x, 5, YLD if im.getpixel((x, 5)) == YL else D0)
    return im


# ---- muro de concreto (64x128) -----------------------------------------
def muro():
    im = tela(16, 32)
    ret(im, 0, 0, 15, 31, INK)
    ret(im, 1, 1, 14, 30, D5)
    ret(im, 1, 1, 14, 1, D6)
    ret(im, 11, 2, 14, 30, D4)         # sombra lateral
    for y in (10, 18, 26):             # emendas do concreto
        ret(im, 1, y, 14, y, D3)
    # faixa de risco (magenta/ink)
    for y in range(3, 8):
        for x in range(1, 15):
            px(im, x, y, MG if ((x + y) // 2) % 2 == 0 else INK)
    ret(im, 1, 2, 14, 2, INK)
    ret(im, 1, 8, 14, 8, INK)
    # fita neon na base
    ret(im, 1, 29, 14, 29, CYD)
    ret(im, 1, 30, 14, 30, CY)
    for (x, y) in ((3, 13), (12, 13), (3, 21), (12, 21)):
        px(im, x, y, D3)
    return im


# ---- chegada (128x192) --------------------------------------------------
LETRAS = {
    "E": ["111", "100", "110", "100", "111"],
    "N": ["101", "111", "111", "101", "101"],
    "T": ["111", "010", "010", "010", "010"],
    "R": ["110", "101", "110", "101", "101"],
    "G": ["111", "100", "101", "101", "111"],
    "A": ["010", "101", "111", "101", "101"],
}


def chegada():
    im = tela(32, 48)
    # pilares
    for x0 in (2, 27):
        ret(im, x0, 12, x0 + 2, 47, D3)
        ret(im, x0, 12, x0, 47, D5)
        for y in range(12, 46, 4):    # faixa quadriculada de chegada
            ret(im, x0 + 1, y, x0 + 2, y + 1, CY if (y // 4) % 2 == 0 else INK)
        ret(im, x0 - 1, 46, x0 + 3, 47, D4)   # base
    # placa
    ret(im, 0, 1, 31, 11, MG)
    ret(im, 1, 2, 30, 10, D1)
    ret(im, 1, 2, 30, 2, MGD)
    texto = "ENTREGA"
    x = 2
    for ch in texto:
        for ry, linha in enumerate(LETRAS[ch]):
            for rx, v in enumerate(linha):
                if v == "1":
                    px(im, x + rx, 4 + ry, YL)
        x += 4
    # cabos de luz neon
    ret(im, 4, 0, 4, 0, CY)
    ret(im, 27, 0, 27, 0, CY)
    # faixa de chegada no chão
    for xx in range(5, 27):
        px(im, xx, 46, CY if (xx // 2) % 2 == 0 else INK)
        px(im, xx, 47, INK if (xx // 2) % 2 == 0 else CY)
    return im


# ---- ícone do lanche (4 estados de dano) --------------------------------
def lanche(estado):
    im = tela(16, 16)
    if estado == 0:      # intacto
        ret(im, 3, 2, 12, 2, INK)
        ret(im, 2, 3, 13, 6, OR)
        ret(im, 2, 5, 13, 6, OR2)
        ret(im, 3, 2, 12, 2, OR)
        for (x, y) in ((5, 3), (8, 3), (10, 4), (6, 5)):
            px(im, x, y, CREME)
        ret(im, 1, 7, 14, 7, GRN)
        for x in range(1, 15, 2):
            px(im, x, 8, GRN2)
        ret(im, 2, 8, 13, 8, YL)
        ret(im, 2, 9, 13, 10, BRN)
        ret(im, 2, 10, 13, 10, BRN2)
        ret(im, 2, 11, 13, 11, RED)
        ret(im, 3, 12, 12, 13, OR2)
        ret(im, 3, 13, 12, 13, OR3)
    elif estado == 1:    # amassado
        ret(im, 3, 4, 12, 4, OR)
        ret(im, 2, 5, 13, 7, OR)
        ret(im, 2, 6, 13, 7, OR2)
        for (x, y) in ((5, 5), (9, 5)):
            px(im, x, y, CREME)
        ret(im, 1, 8, 14, 8, GRN)
        ret(im, 3, 9, 14, 9, YL)
        ret(im, 2, 10, 13, 11, BRN)
        ret(im, 2, 11, 13, 11, BRN2)
        ret(im, 3, 12, 12, 13, OR2)
        ret(im, 3, 13, 12, 13, OR3)
        px(im, 14, 10, RED)
    elif estado == 2:    # esmagado
        ret(im, 2, 7, 13, 8, OR)
        ret(im, 2, 8, 13, 8, OR2)
        px(im, 6, 7, CREME)
        px(im, 10, 7, CREME)
        ret(im, 0, 9, 15, 9, GRN)
        ret(im, 1, 10, 15, 10, YL)
        ret(im, 1, 11, 14, 11, BRN)
        ret(im, 2, 12, 13, 13, OR2)
        ret(im, 2, 13, 13, 13, OR3)
        for (x, y) in ((1, 12), (15, 11), (14, 12)):   # molho escorrendo
            px(im, x, y, RED)
        px(im, 15, 13, RED)
    else:                # destruído
        ret(im, 1, 10, 6, 11, OR)       # metade do pão
        ret(im, 2, 11, 6, 11, OR2)
        ret(im, 9, 12, 14, 13, OR2)     # base do pão
        ret(im, 9, 13, 14, 13, OR3)
        ret(im, 7, 13, 8, 14, BRN)      # hambúrguer espalhado
        for (x, y) in ((3, 8), (11, 7), (13, 9), (8, 5)):
            px(im, x, y, GRN)
        for (x, y) in ((5, 7), (12, 10)):
            px(im, x, y, YL)
        for (x, y) in ((2, 13), (10, 10), (4, 12)):
            px(im, x, y, RED)
        px(im, 6, 4, CREME)
        px(im, 9, 3, CREME)
        px(im, 2, 5, CREME)
    return im


# ---- HUD ----------------------------------------------------------------
def barra_fundo():
    im = tela(52, 7)
    ret(im, 0, 0, 51, 6, INK)
    ret(im, 1, 1, 50, 5, CY)
    ret(im, 2, 2, 49, 4, D1)
    return im


def barra_fill():
    im = tela(50, 5)
    ret(im, 0, 0, 49, 4, OR2)
    ret(im, 0, 0, 49, 1, OR)
    ret(im, 0, 4, 49, 4, OR3)
    for x in range(0, 50, 5):
        px(im, x, 2, YL)
    return im


def painel():
    im = tela(250, 140)
    corpo = (20, 12, 36, 235)
    ret(im, 0, 0, 249, 139, corpo)
    ret(im, 0, 0, 249, 1, CY)
    ret(im, 0, 138, 249, 139, MG)
    ret(im, 0, 0, 1, 139, CY)
    ret(im, 248, 0, 249, 139, MG)
    ret(im, 3, 3, 246, 3, D4)
    ret(im, 3, 136, 246, 136, D4)
    for (cx, cy) in ((0, 0), (249, 0), (0, 139), (249, 139)):   # cantos recortados
        ret(im, min(cx, cx + (3 if cx == 0 else -3)), cy, max(cx, cx + (3 if cx == 0 else -3)), cy, NADA)
    return im


def moto_col():
    return tela(25, 15)


def main():
    info = {}
    for v in range(3):
        info["chao"] = salvar(chao(v), "chao", "Default", v)
    info["plataforma"] = salvar(plataforma(), "plataforma")
    info["bloco"] = salvar(bloco(), "bloco")
    info["espinho"] = salvar(espinho(), "espinho")
    info["lombada"] = salvar(lombada(), "lombada")
    info["muro"] = salvar(muro(), "muro")
    info["chegada"] = salvar(chegada(), "chegada")
    for e in range(4):
        info["iconeLanche"] = salvar(lanche(e), "iconeLanche", "Default", e)
    info["barraLancheFundo"] = salvar(barra_fundo(), "barraLancheFundo")
    info["barraLanche"] = salvar(barra_fill(), "barraLanche")
    info["painelResultado"] = salvar(painel(), "painelResultado")
    info["motoCol"] = salvar(moto_col(), "motoCol")
    for k, v in info.items():
        print(k, v)


if __name__ == "__main__":
    main()
