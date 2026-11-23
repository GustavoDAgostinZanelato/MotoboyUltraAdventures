# -*- coding: utf-8 -*-
"""Gera os PNGs do menu: logo com fundo transparente + botoes (normal e selecionado).

Uso:  python tools/gerar_assets_menu.py "<caminho>/Logo/2.png"
(a logo 2.png tem fundo cinza escuro solido e subtitulo branco)
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def salvar(img, nome):
    pasta = os.path.join(RAIZ, "Animations", nome, "Default")
    os.makedirs(pasta, exist_ok=True)
    img.save(os.path.join(pasta, "000.png"))


def logo(origem):
    a = np.asarray(Image.open(origem).convert("RGB")).astype(float)
    bg = a[5, 5]
    d = np.linalg.norm(a - bg, axis=2)
    nucleo = d > 100
    # cor "pura" do primeiro plano = pixel de nucleo mais proximo
    idx = ndimage.distance_transform_edt(~nucleo, return_distances=False, return_indices=True)
    fg = a[idx[0], idx[1]]
    v = fg - bg
    alpha = np.clip(((a - bg) * v).sum(2) / np.maximum((v * v).sum(2), 1), 0, 1)
    alpha[d < 6] = 0
    out = np.dstack([fg, alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    return img.crop(img.getbbox())


def botao_mc():
    """Botao estilo Minecraft: pedra cinza com chanfro (claro em cima/esquerda, escuro embaixo/direita)."""
    w, h = 460, 60
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, w - 3, h - 3], fill=(112, 112, 112, 255))
    d.rectangle([2, 2, w - 3, 5], fill=(176, 176, 176, 255))          # topo
    d.rectangle([2, 2, 5, h - 3], fill=(176, 176, 176, 255))          # esquerda
    d.rectangle([2, h - 7, w - 3, h - 3], fill=(62, 62, 62, 255))     # base
    d.rectangle([w - 7, 2, w - 3, h - 3], fill=(62, 62, 62, 255))     # direita
    d.rectangle([6, 6, w - 8, h - 8], fill=(112, 112, 112, 255))
    return img


def botao_sel():
    """Moldura branca + brilho azulado que acompanha a opcao selecionada."""
    w, h = 460, 60
    img = Image.new("RGBA", (w, h), (120, 130, 255, 70))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255, 255), width=4)
    return img


def modal():
    """Painel translucido escuro para o conteudo das telas Como jogar / Creditos."""
    w, h = 1000, 500
    img = Image.new("RGBA", (w, h), (0, 0, 0, 175))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255, 140), width=3)
    return img


if __name__ == "__main__":
    im = logo(sys.argv[1])
    print("logo", im.size)
    salvar(im, "logoMenu")
    for n in ("botaoJogar", "botaoComo", "botaoCreditos", "botaoVoltar"):
        salvar(botao_mc(), n)
    salvar(botao_sel(), "botaoSel")
    salvar(modal(), "modalPainel")
