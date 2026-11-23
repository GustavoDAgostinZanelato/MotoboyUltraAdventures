# -*- coding: utf-8 -*-
"""Gera o sistema de menu: layouts Menu, ComoJogar e Creditos + event sheets + ajustes no .caproj e no Jogo.xml.

Uso:  python tools/gerar_menu.py     (idempotente: pode rodar de novo)
"""
import os
import re
from xml.sax.saxutils import escape

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAPROJ = os.path.join(RAIZ, "Motoboy Ultra Adventures.caproj")
JOGO = os.path.join(RAIZ, "Event sheets", "Jogo.xml")
BOM = "﻿"
BS = chr(92)  # barra invertida
W, H = 1600, 900
_n = [700000000000000]
_uid = [9000]


def sid():
    _n[0] += 1
    return str(_n[0])


def uid():
    _uid[0] += 1
    return _uid[0]


def esc(v):
    return escape(str(v), {'"': "&quot;"})


# ------------------------------------------------------------ eventos
def P(i, n, v):
    return '<param id="%d" name="%s">%s</param>' % (i, n, esc(v))


def ace(tag, id_, nome, tipo, params=()):
    a = 'id="%d" name="%s" sid="%s" type="%s"' % (id_, nome, sid(), tipo)
    if not params:
        return "<%s %s />" % (tag, a)
    return "<%s %s>%s</%s>" % (tag, a, "".join(P(*p) for p in params), tag)


def cond(*a):
    return ace("condition", *a)


def act(*a):
    return ace("action", *a)


def ev(conds, acts):
    return '<event-block sid="%s"><conditions>%s</conditions><actions>%s</actions></event-block>' % (
        sid(), "".join(conds), "".join(acts))


def key_press(k):
    return cond(0, "On key pressed", "Keyboard", [(0, "Key", k)])


def ev_teclas(keys, acts, extra=()):
    """Um evento por tecla (equivale a um OR, sem depender de OR-block no XML)."""
    return "".join(ev([key_press(k)] + list(extra), acts) for k in keys)


def var(nome, valor, tipo="number"):
    return '<variable comment="" constant="0" name="%s" sid="%s" static="0" type="%s">%s</variable>' % (
        nome, sid(), tipo, esc(valor))


def set_var(n, v):
    return act(-9, "Set value", "System", [(0, "Variable", n), (1, "Value", v)])


def add_var(n, v):
    return act(-10, "Add to", "System", [(0, "Variable", n), (1, "Value", v)])


def var_cmp(n, op, v):
    return cond(-14, "Compare variable", "System", [(0, "Variable", n), (1, "Comparison", op), (2, "Value", v)])


def go(layout):
    return act(-25, "Go to layout", "System", [(0, "Layout", '"%s"' % layout)])


def set_text(o, e):
    return act(0, "Set text", o, [(0, "Text", e)])


def set_cor(o, e):
    return act(4, "Set font color", o, [(0, "Color", e)])


def comentario(t):
    return "<comment>%s</comment>" % esc(t)


def every_tick():
    return cond(-1, "Every tick", "System")


def on_start():
    return cond(-2, "On start of layout", "System")


# IDs das condicoes do plugin Mouse AINDA NAO CONFIRMADOS (5 = "Cursor is over object" deu erro no Construct 2).
# Ate confirmar, os eventos de mouse ficam desligados.
MOUSE_ATIVO = False
ID_MOUSE_SOBRE = 5
ID_MOUSE_CLIQUE = 4


def sobre(obj):
    return cond(ID_MOUSE_SOBRE, "Cursor is over object", "Mouse", [(0, "Object", obj)])


def clicado(obj):
    return cond(ID_MOUSE_CLIQUE, "On object clicked", "Mouse", [(0, "Mouse button", 0), (1, "Click type", 0), (2, "Object clicked", obj)])


def uma_vez():
    return cond(-4, "Trigger once while true", "System")



def folha(nome, eventos):
    return (BOM + '<?xml version="1.0" encoding="utf-8" ?>\n<c2eventsheet>\n'
            "    <!--All the 'name' attributes are ignored by Construct 2 - they are there for readability only.-->\n"
            "    <name>%s</name>\n    <events>%s</events>\n</c2eventsheet>\n" % (nome, "".join(eventos)))


# ------------------------------------------------------------ layout
def inst_sprite(tipo, x, y, w, h, z=0, anim="Default"):
    return ('<instance type="%s" uid="%d"><properties><initial-visibility>Visible</initial-visibility>'
            '<initial-animation>%s</initial-animation><initial-frame>0</initial-frame><collisions>Disabled</collisions></properties>'
            '<blend-mode>0</blend-mode><effect-fallback>0</effect-fallback><world><x>%s</x><y>%s</y><z>%d</z>'
            '<width>%s</width><height>%s</height><depth>0</depth><hotspotX>0.5</hotspotX><hotspotY>0.5</hotspotY>'
            '<angle>0</angle><opacity>1</opacity></world></instance>') % (tipo, uid(), anim, x, y, z, w, h)


def inst_texto(tipo, texto, x, y, w, h, fonte, cor, ali="Center", z=10):
    return ('<instance type="%s" uid="%d"><properties><text>%s</text><initial-visibility>Visible</initial-visibility>'
            '<font>%s</font><color>%s</color><horizontal-alignment>%s</horizontal-alignment>'
            '<vertical-alignment>Top</vertical-alignment><hotspot>Top-left</hotspot><wrapping>Word</wrapping>'
            '<line-height>0</line-height></properties><blend-mode>0</blend-mode><effect-fallback>0</effect-fallback>'
            '<world><x>%s</x><y>%s</y><z>%d</z><width>%s</width><height>%s</height><depth>0</depth><hotspotX>0</hotspotX></world></instance>'
            ) % (tipo, uid(), esc(texto), fonte, cor, ali, x, y, z, w, h)


def camada(nome, instancias, bg="255,255,255", transp=1):
    return ('<layer name="%s" sid="%s"><initially-visible>1</initially-visible><background-color>%s</background-color>'
            '<transparent>%d</transparent><parallax><x>0</x><y>0</y></parallax><zoom-rate>1</zoom-rate><opacity>1</opacity>'
            '<force-own-texture>0</force-own-texture><global>0</global><use-render-cells>0</use-render-cells>'
            '<blend-mode>0</blend-mode><effect-fallback>0</effect-fallback><instances>%s</instances><effects /></layer>'
            ) % (nome, sid(), bg, transp, "".join(instancias))


BTN_W, BTN_H = 460, 60
CEU_W = round(H * 3000 / 960)           # ceu na proporcao original (3000x960)
PREDIO_H = H // 3                      # predios ocupam 1/3 da altura da tela
PREDIO_W = round(PREDIO_H * 3000 / 420)  # 2143 px (imagem 3000x420)
VEL_CIDADE = 45                        # px/s, esquerda -> direita


def layout(nome, folha_nome, ui_instancias):
    # 4 telhas lado a lado (normal, espelhada, normal, espelhada) => emenda continua ao rolar
    telhas = []
    for k in range(4):
        cx = PREDIO_W / 2 + (k - 2) * PREDIO_W
        telhas.append(inst_sprite("bgPredios", cx, H - PREDIO_H / 2, PREDIO_W if k % 2 == 0 else -PREDIO_W, PREDIO_H, z=k))
    camadas = [
        camada("ceu", [inst_sprite("bgCeu", CEU_W / 2, H // 2, CEU_W, H)], bg="45,20,60", transp=0),  # trecho esquerdo do ceu (sem a lua)
        camada("predios", telhas),
        camada("ui", list(ui_instancias)),
    ]
    return (BOM + '<?xml version="1.0" encoding="utf-8" ?>\n<c2layout>\n    <name>%s</name>\n    <sid>%s</sid>\n'
            "    <event-sheet>%s</event-sheet>\n    <size><width>%d</width><height>%d</height></size>\n"
            "    <margins><horizontal>0</horizontal><vertical>0</vertical></margins>\n"
            "    <unbounded-scrolling>0</unbounded-scrolling>\n"
            "    <layers>%s</layers>\n    <nonworld-instances />\n    <effects />\n</c2layout>\n"
            % (nome, sid(), folha_nome, W, H, "".join(camadas)))


def evento_cidade():
    """Cidade passando da esquerda para a direita; telha que sai pela direita volta para a esquerda."""
    x = "bgPredios.X + %d*dt - %d*(bgPredios.X > %s)" % (VEL_CIDADE, 4 * PREDIO_W, W + PREDIO_W / 2)
    return [comentario("Fundo: cidade passando da esquerda para a direita (loop infinito)"),
            ev([every_tick()], [act(-3, "Set position", "bgPredios", [(0, "X", x), (1, "Y", "bgPredios.Y")])])]


MAG, CIA, AMA, BRA, CINZA = "255,90,220", "90,240,255", "255,210,90", "255,255,255", "170,150,200"


def F(px):
    return "Arial,-%d,700,0" % px


# ------------------------------------------------------------ telas
LOGO_W = 600
LOGO_H = round(LOGO_W * 603 / 1680)     # 215
LOGO_Y = 300
BTN_Y0, BTN_DY = 510, 80                # centro do 1o botao e espacamento
HOVER = "255,255,160"                   # amarelo do Minecraft
BOTOES = [("botaoJogar", "textOp1", "JOGAR", "Fase1"),
          ("botaoComo", "textOp2", "COMO JOGAR", "ComoJogar"),
          ("botaoCreditos", "textOp3", "CREDITOS", "Creditos")]


def tela_menu():
    ui = [inst_sprite("logoMenu", W // 2, LOGO_Y, LOGO_W, LOGO_H, z=10)]
    for i, (bt, tx, rot, _) in enumerate(BOTOES):
        ui.append(inst_sprite(bt, W // 2, BTN_Y0 + i * BTN_DY, BTN_W, BTN_H, z=20))
    ui.append(inst_sprite("botaoSel", W // 2, BTN_Y0, BTN_W, BTN_H, z=21))
    for i, (bt, tx, rot, _) in enumerate(BOTOES):
        ui.append(inst_texto(tx, rot, W // 2 - BTN_W // 2, BTN_Y0 + i * BTN_DY - 20, BTN_W, 40, F(30), BRA, "Center", z=30))
    ui.append(inst_texto("textRodape", "Mouse ou Setas / W S + Enter", 0, 840, W, 36, F(22), CINZA, "Center", z=30))
    ev_ = [
        comentario("MENU PRINCIPAL - Sel: 0 = Jogar, 1 = Como jogar, 2 = Creditos (teclado e mouse)"),
        var("Sel", 0),
        ev([on_start()], [set_var("Sel", 0)]),
        comentario("Teclado: cima/baixo com loop"),
        ev_teclas([38, 87], [add_var("Sel", -1)]),
        ev_teclas([40, 83], [add_var("Sel", 1)]),
        ev([var_cmp("Sel", 2, 0)], [set_var("Sel", 2)]),
        ev([var_cmp("Sel", 4, 2)], [set_var("Sel", 0)]),
        comentario("Mouse: ao entrar com o cursor no botao ele vira a opcao selecionada; clique confirma"),
    ]
    for i, (bt, tx, rot, lay) in enumerate(BOTOES):
        if MOUSE_ATIVO:
            ev_.append(ev([sobre(bt), uma_vez()], [set_var("Sel", i)]))
            ev_.append(ev([clicado(bt)], [go(lay)]))
    ev_ += [
        comentario("Moldura de destaque segue a opcao selecionada; texto dela fica amarelo"),
        ev([every_tick()], [act(-3, "Set position", "botaoSel",
                                [(0, "X", W // 2), (1, "Y", "%d + Sel*%d" % (BTN_Y0, BTN_DY))])]),
    ]
    for i, (bt, tx, rot, lay) in enumerate(BOTOES):
        ev_.append(ev([every_tick(), var_cmp("Sel", 0, i)], [set_cor(tx, "rgb(255,255,160)")]))
        ev_.append(ev([every_tick(), var_cmp("Sel", 1, i)], [set_cor(tx, "rgb(255,255,255)")]))
    ev_.append(comentario("Confirmar pelo teclado (Enter ou Espaco)"))
    for k in (13, 32):
        for i, (bt, tx, rot, lay) in enumerate(BOTOES):
            ev_.append(ev([key_press(k), var_cmp("Sel", 0, i)], [go(lay)]))
    ev_ += evento_cidade()
    return layout("Menu", "Menu", ui), folha("Menu", ev_)


PAINEL_W, PAINEL_H, PAINEL_Y = 1000, 500, 435
VOLTAR_Y = 770


def tela_texto(nome, titulo, corpo, tam):
    ui = [inst_texto("textTitulo2", titulo, 0, 95 - 33, W, 66, F(54), BRA, "Center", z=30),
          inst_sprite("modalPainel", W // 2, PAINEL_Y, PAINEL_W, PAINEL_H, z=20),
          inst_texto("textCorpo", corpo, W // 2 - PAINEL_W // 2 + 30, PAINEL_Y - PAINEL_H // 2 + 25,
                     PAINEL_W - 60, PAINEL_H - 50, F(tam), BRA, "Center", z=30),
          inst_sprite("botaoVoltar", W // 2, VOLTAR_Y, BTN_W, BTN_H, z=20),
          inst_sprite("botaoSel", W // 2, VOLTAR_Y, BTN_W, BTN_H, z=21),
          inst_texto("textVoltar", "VOLTAR", W // 2 - BTN_W // 2, VOLTAR_Y - 20, BTN_W, 40, F(30), HOVER, "Center", z=30)]
    ev_ = [comentario("Tela %s: botao VOLTAR (mouse) ou Esc / Enter / Espaco volta ao menu" % nome),
           ] + ([ev([clicado("botaoVoltar")], [go("Menu")])] if MOUSE_ATIVO else []) + [
           ev_teclas([27, 13, 32], [go("Menu")])] + evento_cidade()
    return layout(nome, nome, ui), folha(nome, ev_)



COMO = ("MOVIMENTO\n"
        "D / Seta direita .... turbo\n"
        "A / Seta esquerda ... freio (no chao)\n"
        "A moto sempre avanca sozinha!\n\n"
        "ACROBACIAS\n"
        "Rampas lancam a moto - quanto mais rapido, mais alto\n"
        "Seta cima / baixo no ar: gira (cambalhota)\n"
        "Seta cima no chao: empinar (wheelie)\n"
        "Pouse com a moto nivelada para manter o combo\n\n"
        "OBJETIVO\n"
        "Chegue ao fim antes do tempo acabar. Cada manobra estraga\n"
        "o lanche... e rende mais pontos de estilo!\n"
        "Esc: voltar ao menu durante a fase")

CRED = ("Artur Bristot ........ Game Designer / Level Designer\n"
        "Eric Garcia ........... Sound Designer / Narrative Designer\n"
        "Gabriel Rodolfo ....... Programador Principal\n"
        "Gustavo D'Agostin ..... Artista Visual / UI Designer\n\n"
        "Projeto da disciplina de Desenvolvimento de Jogos\n"
        "Engenharia de Software - UniSATC\n"
        "Engine: Construct 2\n\n"
        "Inspirado em Urban Trial Playground, Elasto Mania, Joe Danger e Trials Rising.")


# ------------------------------------------------------------ caproj / Jogo.xml
def patch_caproj():
    s = open(CAPROJ, encoding="utf-8-sig").read()

    def spr(nome):
        return ('        <object-type name="%s" sid="%s">\n            <plugin id="Sprite" />\n            <animation-folder>\n'
                '                <animation framecount="1" loop="0" name="Default" pingpong="0" repeatcount="1" repeatto="0" sid="%s" speed="5">\n'
                '                    <frame duration="1" hotspotX="0.5" hotspotY="0.5" original-source="Animations%s%s%sDefault%s000.png">\n'
                '                        <collision-poly><point x="0" y="0" /><point x="1" y="0" /><point x="1" y="1" /><point x="0" y="1" /></collision-poly>\n'
                '                    </frame>\n                </animation>\n            </animation-folder>\n        </object-type>\n'
                ) % (nome, sid(), sid(), BS, nome, BS, BS)

    for velho in ("textTitulo1", "textSub", "botaoMenu"):  # sobras de versoes anteriores
        s = re.sub(r'\s*<object-type name="%s" sid="\d+">.*?</object-type>' % velho, "", s, flags=re.S)
    sprites = ("logoMenu", "botaoJogar", "botaoComo", "botaoCreditos", "botaoVoltar", "botaoSel", "modalPainel")
    s = s.replace("    </object-folder>", "".join(spr(n) for n in sprites if 'name="%s"' % n not in s) + "    </object-folder>", 1)
    textos = [n for n in ("textTitulo2", "textOp1", "textOp2", "textOp3", "textRodape", "textCorpo", "textVoltar") if 'name="%s"' % n not in s]
    tipos = "".join('        <object-type name="%s" sid="%s">\n            <plugin id="Text" />\n'
                    '        </object-type>\n' % (n, sid()) for n in textos)
    s = s.replace("    </object-folder>", tipos + "    </object-folder>", 1)
    if 'id="Mouse"' not in s:
        s = s.replace('        <plugin author="Scirra" id="Keyboard" version="1">Keyboard</plugin>\n',
                      '        <plugin author="Scirra" id="Keyboard" version="1">Keyboard</plugin>\n'
                      '        <plugin author="Scirra" id="Mouse" version="1">Mouse</plugin>\n', 1)
        s = s.replace("    </object-folder>", '        <object-type name="Mouse" sid="%s">\n            <plugin id="Mouse" />\n'
                      '        </object-type>\n    </object-folder>' % sid(), 1)
        s = s.replace('        <global-instance type="Keyboard" uid="3" />\n',
                      '        <global-instance type="Keyboard" uid="3" />\n        <global-instance type="Mouse" uid="9999" />\n', 1)
    for velho in ("textTitulo1", "textSub"):  # sobras da 1a versao do menu
        s = re.sub(r'\s*<object-type name="%s" sid="\d+">\s*<plugin id="Text" />\s*</object-type>' % velho, "", s)
    s = re.sub(r"<layout-folder>.*?</layout-folder>",
               "<layout-folder>\n        <layout>Menu.xml</layout>\n        <layout>ComoJogar.xml</layout>\n"
               "        <layout>Creditos.xml</layout>\n        <layout>Fase1.xml</layout>\n    </layout-folder>",
               s, flags=re.S)
    s = re.sub(r"<event-folder>.*?</event-folder>",
               "<event-folder>\n        <event-sheet>Menu.xml</event-sheet>\n        <event-sheet>ComoJogar.xml</event-sheet>\n"
               "        <event-sheet>Creditos.xml</event-sheet>\n        <event-sheet>Jogo.xml</event-sheet>\n    </event-folder>",
               s, flags=re.S)
    open(CAPROJ, "w", encoding="utf-8-sig", newline="\r\n").write(s)


def patch_jogo():
    s = open(JOGO, encoding="utf-8-sig").read()
    if "VOLTAR AO MENU" in s:
        return
    bloco = comentario("VOLTAR AO MENU (Esc)") + ev([key_press(27)], [go("Menu")])
    s = s.replace("</events>", bloco + "</events>", 1)
    open(JOGO, "w", encoding="utf-8-sig", newline="\r\n").write(s)


def grava(rel, txt):
    open(os.path.join(RAIZ, rel), "w", encoding="utf-8", newline="\r\n").write(txt)


def main():
    l, e = tela_menu()
    grava("Layouts/Menu.xml", l)
    grava("Event sheets/Menu.xml", e)
    l, e = tela_texto("ComoJogar", "COMO JOGAR", COMO, 23)
    grava("Layouts/ComoJogar.xml", l)
    grava("Event sheets/ComoJogar.xml", e)
    l, e = tela_texto("Creditos", "CREDITOS", CRED, 26)
    grava("Layouts/Creditos.xml", l)
    grava("Event sheets/Creditos.xml", e)
    patch_caproj()
    patch_jogo()
    print("Menu gerado.")


if __name__ == "__main__":
    main()
