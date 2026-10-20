# -*- coding: utf-8 -*-
"""Gera a Fase 1 (tutorial) com as novas mecanicas: moto sempre avancando, saltos so por rampas.

Regera Layouts/Fase1.xml e Event sheets/Jogo.xml e acrescenta rampa/rampaG ao .caproj.
Uso:  python tools/gerar_fase_tutorial.py
"""
import os
import re
import itertools
from xml.sax.saxutils import escape

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAPROJ = os.path.join(RAIZ, "Motoboy Ultra Adventures.caproj")
BOM = "\ufeff"

_sid = itertools.count(430000000000001)


def sid():
    return str(next(_sid))


def esc(v):
    return escape(str(v), {'"': "&quot;"})


def attrs(d):
    return " ".join('%s="%s"' % (k, esc(v)) for k, v in d.items())


# ============================================================ EVENTOS (DSL)
def param(i, nome, valor):
    return '<param id="%d" name="%s">%s</param>' % (i, nome, esc(valor))


def _ace(tag, id_, nome, tipo, params=(), behavior=None, inverted=False):
    a = {}
    if behavior:
        a["behavior"] = behavior
    a["id"] = id_
    if inverted:
        a["inverted"] = 1
    a["name"] = nome
    a["sid"] = sid()
    a["type"] = tipo
    if not params:
        return "<%s %s />" % (tag, attrs(a))
    inner = "".join(param(*p) for p in params)
    return "<%s %s>%s</%s>" % (tag, attrs(a), inner, tag)


def cond(*args, **kw):
    return _ace("condition", *args, **kw)


def act(*args, **kw):
    return _ace("action", *args, **kw)


def evento(conds, acts, subs=()):
    s = '<event-block sid="%s"><conditions>%s</conditions><actions>%s</actions>' % (
        sid(), "".join(conds), "".join(acts))
    if subs:
        s += "<sub-events>%s</sub-events>" % "".join(subs)
    return s + "</event-block>"


def comentario(t):
    return "<comment>%s</comment>" % esc(t)


def grupo(titulo, descricao, itens):
    return '<event-group description="%s" sid="%s" title="%s"><sub-events>%s</sub-events></event-group>' % (
        esc(descricao), sid(), esc(titulo), "".join(itens))


def variavel(nome, valor, comentario_="", tipo="number"):
    return '<variable comment="%s" constant="0" name="%s" sid="%s" static="0" type="%s">%s</variable>' % (
        esc(comentario_), nome, sid(), tipo, esc(valor))


# ---- atalhos de condições / ações -----------------------------------
IGUAL, DIFERENTE, MENOR, MENOR_IGUAL, MAIOR, MAIOR_IGUAL = 0, 1, 2, 3, 4, 5


def var_cmp(nome, op, valor):
    return cond(-14, "Compare variable", "System", [(0, "Variable", nome), (1, "Comparison", op), (2, "Value", valor)])


def cmp2(a, op, b):
    return cond(-8, "Compare two values", "System", [(0, "First value", a), (1, "Comparison", op), (2, "Second value", b)])


def tecla(k):
    return cond(2, "Key is down", "Keyboard", [(0, "Key", k)])


def tecla_press(k):
    return cond(0, "On key pressed", "Keyboard", [(0, "Key", k)])


def no_chao(inv=False):
    return cond(2, "Is on floor", "motoCol", behavior="Platform", inverted=inv)


def toca(anim, inv=False):
    return cond(2, "Is playing", "moto", [(0, "Animation", '"%s"' % anim)], inverted=inv)


def uma_vez():
    return cond(-4, "Trigger once while true", "System")


def a_cada(seg):
    return cond(-6, "Every X seconds", "System", [(0, "Interval (seconds)", seg)])


def estado(v):
    return var_cmp("Estado", IGUAL, v)


def set_var(n, v):
    return act(-9, "Set value", "System", [(0, "Variable", n), (1, "Value", v)])


def add_var(n, v):
    return act(-10, "Add to", "System", [(0, "Variable", n), (1, "Value", v)])


def sub_var(n, v):
    return act(-11, "Subtract from", "System", [(0, "Variable", n), (1, "Value", v)])


def set_text(obj, expr):
    return act(0, "Set text", obj, [(0, "Text", expr)])


def set_vis(obj, v):
    return act(-15, "Set visible", obj, [(0, "Visibility", v)])


def set_opac(obj, v):
    return act(-16, "Set opacity", obj, [(0, "Opacity", v)])


def set_cor(obj, expr):
    return act(4, "Set font color", obj, [(0, "Color", expr)])


def set_anim(obj, nome):
    return act(4, "Set animation", obj, [(0, "Animation", '"%s"' % nome), (1, "From", 1)])


def simular(ctrl):
    return act(7, "Simulate control", "motoCol", [(0, "Control", ctrl)], behavior="Platform")


# ---- efeito de texto (SMASH! / CRUNCH! ...) ---------------------------
COR_SMASH = "rgb(255,210,90)"
COR_CRUNCH = "rgb(255,90,220)"
COR_PERFEITO = "rgb(90,240,255)"


def fx(texto, cor, dur=1.0):
    return [set_text("textFx", '"%s"' % texto), set_cor("textFx", cor), set_var("FxTimer", dur)]


def penalidade(segundos, texto, cor, lanche=0):
    """Espinho/queda: perde tempo, zera o combo e volta ao último ponto seguro."""
    a = [sub_var("TempoRestante", segundos), set_var("Combo", 0)]
    if lanche:
        a.append(sub_var("QualidadeLanche", lanche))
    a += [
        act(-3, "Set position", "motoCol", [(0, "X", "SafeBX"), (1, "Y", "SafeBY")]),
        act(8, "Set vector X", "motoCol", [(0, "Vector X", 0)], behavior="Platform"),
        act(9, "Set vector Y", "motoCol", [(0, "Vector Y", 0)], behavior="Platform"),
        set_var("Invul", 1.5), set_var("RotAcum", 0), set_var("FlipsAr", 0),
        act(0, "Shake", "motoCol", [(0, "Magnitude", 12), (1, "Duration", 0.3), (2, "Mode", 0)], behavior="scrollto"),
    ]
    return a + fx(texto, cor)


def flip_acao():
    return [add_var("FlipsAr", 1), add_var("Combo", 1),
            add_var("PontosEstilo", "100 * Combo"), sub_var("QualidadeLanche", 8)] + fx("SMASH!", COR_SMASH)



# ============================================================ OBJETOS (caproj)
def poly(pts):
    return "<collision-poly>%s</collision-poly>" % "".join('<point x="%s" y="%s" />' % p for p in pts)


RET = [(0, 0), (1, 0), (1, 1), (0, 1)]


def sprite_type(nome, anims, behaviors=(), hot=(0.5, 0.5), poligono=RET, origem=""):
    """anims: [(nomeAnim, nFrames, speed)]"""
    s = '        <object-type name="%s" sid="%s">\n            <plugin id="Sprite" />\n' % (nome, sid())
    if behaviors:
        s += "            <behaviors>\n"
        for bn, bid in behaviors:
            s += '                <behavior-type name="%s" sid="%s">\n                    <behavior id="%s" />\n                </behavior-type>\n' % (bn, sid(), bid)
        s += "            </behaviors>\n"
    s += "            <animation-folder>\n"
    for an, nf, sp in anims:
        s += '                <animation framecount="%d" loop="0" name="%s" pingpong="0" repeatcount="1" repeatto="0" sid="%s" speed="%s">\n' % (nf, an, sid(), sp)
        for f in range(nf):
            s += '                    <frame duration="1" hotspotX="%s" hotspotY="%s" original-source="%s">\n                        %s\n                    </frame>\n' % (
                hot[0], hot[1], esc("Animations\\%s\\%s\\%03d.png" % (nome, an, f)), poly(poligono))
        s += "                </animation>\n"
    s += "            </animation-folder>\n        </object-type>\n"
    return s


def text_type(nome):
    return '        <object-type name="%s" sid="%s">\n            <plugin id="Text" />\n        </object-type>\n' % (nome, sid())



# ============================================================ LAYOUT
class Camada:
    def __init__(self, nome, sid_, px, py, fundo="255,255,255", transparente=1):
        self.nome, self.sid_, self.px, self.py = nome, sid_, px, py
        self.fundo, self.transparente = fundo, transparente
        self.itens = []

    def xml(self):
        s = ('        <layer name="%s" sid="%s">\n            <initially-visible>1</initially-visible>\n'
             '            <background-color>%s</background-color>\n            <transparent>%d</transparent>\n'
             '            <parallax>\n                <x>%s</x>\n                <y>%s</y>\n            </parallax>\n'
             '            <zoom-rate>1</zoom-rate>\n            <opacity>1</opacity>\n'
             '            <force-own-texture>0</force-own-texture>\n            <global>0</global>\n'
             '            <use-render-cells>0</use-render-cells>\n            <blend-mode>0</blend-mode>\n'
             '            <effect-fallback>0</effect-fallback>\n            <instances>\n') % (
            self.nome, self.sid_, self.fundo, self.transparente, self.px, self.py)
        s += "".join(self.itens)
        return s + "            </instances>\n            <effects />\n        </layer>\n"


_uid = itertools.count(10)


def inst_sprite(cam, tipo, x, y, w, h, frame=0, behaviors=(), invisivel=False, hot=(0.5, 0.5), colisao=True, props_beh=None):
    z = len(cam.itens)
    s = ('                <instance type="%s" uid="%d">\n                    <properties>\n'
         '                        <initial-visibility>%s</initial-visibility>\n'
         '                        <initial-animation>Default</initial-animation>\n'
         '                        <initial-frame>%d</initial-frame>\n'
         '                        <collisions>%s</collisions>\n                    </properties>\n') % (
        tipo, next(_uid), "Invisible" if invisivel else "Visible", frame, "Enabled" if colisao else "Disabled")
    if behaviors:
        s += "                    <behavior-instances>\n"
        for b in behaviors:
            s += b
        s += "                    </behavior-instances>\n"
    s += ('                    <blend-mode>0</blend-mode>\n                    <effect-fallback>0</effect-fallback>\n'
          '                    <world>\n                        <x>%s</x>\n                        <y>%s</y>\n'
          '                        <z>%d</z>\n                        <width>%s</width>\n                        <height>%s</height>\n'
          '                        <depth>0</depth>\n                        <hotspotX>%s</hotspotX>\n'
          '                        <hotspotY>%s</hotspotY>\n                        <angle>0</angle>\n'
          '                        <opacity>1</opacity>\n                    </world>\n                </instance>\n') % (
        x, y, z, w, h, hot[0], hot[1])
    cam.itens.append(s)


BEH_SOLID = ('                        <behavior-instance type="Solid">\n                            <properties>\n'
             '                                <initial-state>Enabled</initial-state>\n                            </properties>\n'
             '                        </behavior-instance>\n')
BEH_JUMPTHRU = BEH_SOLID.replace('type="Solid"', 'type="Jumpthru"')
BEH_MOTO = ('                        <behavior-instance type="Platform">\n                            <properties>\n'
            '                                <max-speed>340</max-speed>\n                                <acceleration>1200</acceleration>\n'
            '                                <deceleration>1500</deceleration>\n                                <jump-strength>0</jump-strength>\n'
            '                                <gravity>1500</gravity>\n                                <max-fall-speed>1000</max-fall-speed>\n'
            '                                <double-jump>Disabled</double-jump>\n                                <jump-sustain>0</jump-sustain>\n'
            '                                <default-controls>No</default-controls>\n                                <initial-state>Enabled</initial-state>\n'
            '                            </properties>\n                        </behavior-instance>\n'
            '                        <behavior-instance type="ScrollTo">\n                            <properties>\n'
            '                                <initial-state>Enabled</initial-state>\n                            </properties>\n'
            '                        </behavior-instance>\n')


def inst_texto(cam, tipo, texto, x, y, w, h, fonte, cor, halign="Left", invisivel=False):
    z = len(cam.itens)
    cam.itens.append(
        ('                <instance type="%s" uid="%d">\n                    <properties>\n'
         '                        <text>%s</text>\n                        <initial-visibility>%s</initial-visibility>\n'
         '                        <font>%s</font>\n                        <color>%s</color>\n'
         '                        <horizontal-alignment>%s</horizontal-alignment>\n'
         '                        <vertical-alignment>Top</vertical-alignment>\n'
         '                        <hotspot>Top-left</hotspot>\n                        <wrapping>Word</wrapping>\n'
         '                        <line-height>0</line-height>\n                    </properties>\n'
         '                    <blend-mode>0</blend-mode>\n                    <effect-fallback>0</effect-fallback>\n'
         '                    <world>\n                        <x>%s</x>\n                        <y>%s</y>\n'
         '                        <z>%d</z>\n                        <width>%s</width>\n                        <height>%s</height>\n'
         '                        <depth>0</depth>\n                        <hotspotX>0</hotspotX>\n                    </world>\n'
         '                </instance>\n') % (tipo, next(_uid), esc(texto), "Invisible" if invisivel else "Visible",
                                            fonte, cor, halign, x, y, z, w, h))



# ============================================================ NOVAS MECÂNICAS
VEL_NORMAL, VEL_TURBO, VEL_FREIO = 340, 480, 150
ROT_AR = 450            # graus/s girando no ar (antes 280)
ROT_PASSIVA = 25        # graus/s em que o bico desce sozinho quando nenhuma seta é segurada
RAMPAS = {              # tipo: (largura, altura, ângulo da rampa em graus, multiplicador do impulso)
    "rampa": (384, 128, 18.4, 1.0),
    "rampaG": (512, 192, 20.6, 1.4),
}


def tecla_nao(k):
    return cond(2, "Key is down", "Keyboard", [(0, "Key", k)], inverted=True)


def sobre(tipo, dy=8, dx=0, inv=False):
    """motoCol encostada em (sobre) um objeto sólido, testada com pequeno deslocamento."""
    return cond(9, "Is overlapping at offset", "motoCol",
                [(0, "Object", tipo), (1, "X", dx), (2, "Y", dy)], inverted=inv)


def max_speed(v):
    return act(1, "Set max speed", "motoCol", [(0, "Max speed", v)], behavior="Platform")


def vec_y(v):
    return act(9, "Set vector Y", "motoCol", [(0, "Vector Y", v)], behavior="Platform")


def vel_cmp(op, v):
    return cond(1, "Compare speed", "motoCol", [(0, "Comparison", op), (1, "Speed", v)], behavior="Platform")


# ---- dicas do tutorial: (x onde o texto passa a valer, texto) -------------
DICAS = [
    (0, "Sua moto só anda pra frente!   [D] acelera   [A] freia"),
    (520, "Lombada à frente: freie [A], ou o lanche vai sacudir!"),
    (900, "Segure [↑] no chão para empinar (wheelie): vale estilo, mas amassa o lanche"),
    (1450, "RAMPA! A moto só salta em rampas. Não freie e mantenha a velocidade"),
    (2380, "Pouse com as rodas no chão. Pouso torto quebra o combo e amassa o lanche"),
    (2800, "Outra rampa: no ar, [↑] e [↓] giram a moto. Dê um FLIP e pouse reto!"),
    (3680, "Cada flip sobe o COMBO e rende pontos... mas o lanche amassa (olhe a barra)"),
    (4050, "Espinhos custam tempo! Passe por cima deles usando a rampa"),
    (4980, "Encadeie flips sem errar o pouso para multiplicar os pontos"),
    (5130, "Muros travam a moto. Salte por cima com a rampa, sem frear!"),
    (6040, "RAMPÃO final! Segure o giro e tente um flip duplo"),
    (7330, "Chegue à linha de chegada antes que o tempo acabe!"),
]


def build_eventos():
    g = []
    g.append(grupo("Início da fase", "Zera o estado e as variáveis de gameplay a cada início/reinício do layout", [
        evento([cond(-2, "On start of layout", "System")], [
            set_var("Estado", 0), set_var("TempoRestante", "TempoFase"), set_var("QualidadeLanche", 100),
            set_var("Combo", 0), set_var("PontosEstilo", 0), set_var("RotAcum", 0), set_var("FlipsAr", 0),
            set_var("TempoNoAr", 0), set_var("FxTimer", 0), set_var("FimTimer", 0), set_var("IsWheelie", 0),
            set_var("Invul", 0), set_var("RampaLock", 0), set_var("VelAr", 0),
            set_var("SafeAX", "motoCol.X"), set_var("SafeAY", "motoCol.Y"),
            set_var("SafeBX", "motoCol.X"), set_var("SafeBY", "motoCol.Y"),
        ]),
    ]))
    # ----------------------------------------------------------- controles
    c = [
        comentario("A moto SEMPRE anda para frente (Platform com 'Default controls' = No). Não há tecla de pulo: "
                   "só as rampas lançam a moto no ar. D/→ = turbo, A/← = freio (só no chão; no ar a velocidade se mantém)."),
        evento([estado(0)], [simular(1)]),
        evento([estado(0), no_chao()], [max_speed(VEL_NORMAL)]),
        evento([estado(0), no_chao(), tecla(68)], [max_speed(VEL_TURBO)]),
        evento([estado(0), no_chao(), tecla(39)], [max_speed(VEL_TURBO)]),
        evento([estado(0), no_chao(), tecla(65)], [max_speed(VEL_FREIO)]),
        evento([estado(0), no_chao(), tecla(37)], [max_speed(VEL_FREIO)]),
    ]
    g.append(grupo("Controles", "Moto sempre avançando; turbo e freio", c))
    # ------------------------------------------------------------ ciclo da fase
    ciclo = [
        comentario("Cronômetro regressivo: só corre enquanto o jogador está em corrida (Estado = 0)."),
        evento([estado(0)], [sub_var("TempoRestante", "dt")]),
        comentario("Tempo esgotado: mensagem e reinício imediato da fase (sem vidas)."),
        evento([estado(0), var_cmp("TempoRestante", MENOR_IGUAL, 0)],
               [set_var("Estado", 2), set_var("TempoRestante", 0), set_var("FimTimer", 0)] + fx("TEMPO ESGOTADO!", COR_CRUNCH, 3)),
        evento([estado(2)], [add_var("FimTimer", "dt")], [
            evento([var_cmp("FimTimer", MAIOR_IGUAL, 1.5)], [act(-26, "Restart layout", "System")]),
        ]),
        comentario("Alerta visual nos últimos 10 segundos."),
        evento([estado(0), var_cmp("TempoRestante", MENOR_IGUAL, 10), uma_vez()], [set_cor("textTempo", "rgb(255,70,90)")]),
        comentario("Chegada: calcula bônus de tempo + bônus de estilo e abre o resultado."),
        evento([cond(0, "On collision with another object", "motoCol", [(0, "Object", "chegada")]), estado(0)], [
            set_var("Estado", 1), set_var("FxTimer", 0),
            set_var("BonusTempo", "floor(TempoRestante) * 100"),
            set_var("BonusEstilo", "PontosEstilo + round((100 - QualidadeLanche) * 10)"),
            set_var("ScoreFinal", "BonusTempo + BonusEstilo"),
        ]),
        evento([estado(1), var_cmp("QualidadeLanche", MAIOR_IGUAL, 75)], [set_var("FraseLanche", '"O lanche chegou quase intacto... que tédio!"')]),
        evento([estado(1), var_cmp("QualidadeLanche", MENOR, 75), var_cmp("QualidadeLanche", MAIOR_IGUAL, 50)], [set_var("FraseLanche", '"Lanche amassadinho. Cliente reclama, mas come."')]),
        evento([estado(1), var_cmp("QualidadeLanche", MENOR, 50), var_cmp("QualidadeLanche", MAIOR_IGUAL, 25)], [set_var("FraseLanche", '"Lanche esmagado! Isso aí é estilo."')]),
        evento([estado(1), var_cmp("QualidadeLanche", MENOR, 25)], [set_var("FraseLanche", '"Lanche DESTRUÍDO! Estilo máximo!"')]),
        evento([estado(1), uma_vez()], [
            set_vis("painelResultado", 1), set_vis("textResultado", 1),
            set_text("textResultado",
                     '"ENTREGA CONCLUÍDA!" & newline & newline & "Bônus de tempo: " & BonusTempo & newline & '
                     '"Bônus de estilo: " & BonusEstilo & newline & newline & "PONTUAÇÃO FINAL: " & ScoreFinal & newline & newline & '
                     'FraseLanche & newline & newline & "[ENTER] jogar novamente"'),
        ]),
        evento([estado(1), tecla_press(13)], [act(-26, "Restart layout", "System")]),
    ]
    g.append(grupo("Ciclo da fase", "Tempo, chegada, vitória e derrota", ciclo))
    # ------------------------------------------------- rampas (única fonte de salto)
    r = [comentario(
        "Rampa = salto. Quando a moto chega à ponta da rampa recebe um impulso vertical que cresce com a "
        "velocidade e com o tamanho da rampa (rampaG = rampão). RampaLock impede o impulso de repetir no mesmo salto.")]
    for tipo, (w, h, ang, k) in RAMPAS.items():
        r.append(evento([
            estado(0), var_cmp("RampaLock", IGUAL, 0), sobre(tipo),
            cmp2("motoCol.X", MAIOR_IGUAL, "%s.X + %s.Width / 2 - 70" % (tipo, tipo)),
        ], [
            vec_y("-%s * (520 + 0.9 * motoCol.Platform.Speed)" % k),
            set_var("RampaLock", 1), set_var("RotAcum", 0), set_var("FlipsAr", 0), set_var("TempoNoAr", 0),
            sub_var("QualidadeLanche", 1),
        ]))
    r += [
        comentario("Lombada: solavanco em velocidade abala o lanche (freie antes!)."),
        evento([estado(0), sobre("lombada", 6), vel_cmp(MAIOR_IGUAL, 400), uma_vez()],
               [sub_var("QualidadeLanche", 4)] + fx("SOLAVANCO!", COR_SMASH)),
        evento([estado(0), sobre("lombada", 6), vel_cmp(MAIOR_IGUAL, 250), vel_cmp(MENOR, 400), uma_vez()],
               [sub_var("QualidadeLanche", 2)] + fx("SOLAVANCO!", COR_SMASH)),
    ]
    g.append(grupo("Rampas e lombadas", "Salto só por rampa; lombadas sacodem o lanche", r))
    # ------------------------------------------------- acrobacias e estilo
    a = [
        comentario("Rotação no ar (↑ anti-horário, ↓ horário) a %d°/s. RotAcum acumula a rotação para contar os flips." % ROT_AR),
        evento([estado(0), no_chao(True), tecla(38)], [
            act(-19, "Rotate counter-clockwise", "moto", [(0, "Degrees", "%d * dt" % ROT_AR)]), sub_var("RotAcum", "%d * dt" % ROT_AR)]),
        evento([estado(0), no_chao(True), tecla(40)], [
            act(-18, "Rotate clockwise", "moto", [(0, "Degrees", "%d * dt" % ROT_AR)]), add_var("RotAcum", "%d * dt" % ROT_AR)]),
        comentario("Sem nenhuma seta, o bico da moto desce devagar (como uma moto de verdade) para ajudar no pouso."),
        evento([estado(0), no_chao(True), tecla_nao(38), tecla_nao(40)], [
            act(-18, "Rotate clockwise", "moto", [(0, "Degrees", "%d * dt" % ROT_PASSIVA)])]),
        evento([no_chao(True)], [add_var("TempoNoAr", "dt"), set_var("VelAr", "motoCol.Platform.VectorY")]),
        comentario("Cada volta completa (~360°) é um flip: combo +1, pontos x combo, lanche -8%."),
        evento([estado(0), var_cmp("RotAcum", MAIOR_IGUAL, 330)], flip_acao() + [sub_var("RotAcum", 360)]),
        evento([estado(0), var_cmp("RotAcum", MENOR_IGUAL, -330)], flip_acao() + [add_var("RotAcum", 360)]),
        comentario("Wheelie (segurar ↑ no chão, em movimento): pontos de estilo e dano leve no lanche."),
        evento([estado(0)], [set_var("IsWheelie", 0)]),
        evento([estado(0), no_chao(), tecla(38), vel_cmp(MAIOR, 40)], [set_var("IsWheelie", 1)]),
        evento([estado(0), var_cmp("IsWheelie", IGUAL, 1), a_cada(0.5)],
               [sub_var("QualidadeLanche", 0.5), add_var("PontosEstilo", "5 * max(1, Combo)")]),
        comentario("Pouso: até 35° do chão é pouso limpo; acima disso o combo quebra (CRUNCH!). "
                   "O impacto da queda também amassa o lanche (quanto mais alto o salto, mais dano)."),
        evento([estado(0), cond(9, "On landed", "motoCol", behavior="Platform")], [sub_var("QualidadeLanche", "max(0, (VelAr - 700) / 120)")], [
            evento([cmp2("abs(anglediff(moto.Angle, 0))", MENOR_IGUAL, 35)], [], [
                evento([var_cmp("FlipsAr", MAIOR, 0)], [add_var("PontosEstilo", "50 * Combo")] + fx("PERFEITO!", COR_PERFEITO)),
            ]),
            evento([cond(-22, "Else", "System")], [
                set_var("Combo", 0), sub_var("QualidadeLanche", 10), sub_var("TempoRestante", 1),
                act(0, "Shake", "motoCol", [(0, "Magnitude", 10), (1, "Duration", 0.25), (2, "Mode", 0)], behavior="scrollto"),
            ] + fx("CRUNCH!", COR_CRUNCH)),
        ]),
        evento([cond(9, "On landed", "motoCol", behavior="Platform")],
               [set_var("FlipsAr", 0), set_var("RotAcum", 0), set_var("TempoNoAr", 0), set_var("RampaLock", 0)]),
        comentario("No chão a moto acompanha a inclinação da rampa; fora dela volta suavemente a 0°."),
        evento([no_chao(), sobre("rampa", 8, 0, True), sobre("rampaG", 8, 0, True)],
               [act(-8, "Set angle", "moto", [(0, "Angle", "anglelerp(moto.Angle, 0, min(1, 18 * dt))")])]),
        evento([no_chao(), sobre("rampa")],
               [act(-8, "Set angle", "moto", [(0, "Angle", "anglelerp(moto.Angle, -%s, min(1, 18 * dt))" % RAMPAS["rampa"][2])])]),
        evento([no_chao(), sobre("rampaG")],
               [act(-8, "Set angle", "moto", [(0, "Angle", "anglelerp(moto.Angle, -%s, min(1, 18 * dt))" % RAMPAS["rampaG"][2])])]),
        comentario("Limites."),
        evento([var_cmp("QualidadeLanche", MENOR, 0)], [set_var("QualidadeLanche", 0)]),
        evento([var_cmp("Combo", MENOR, 0)], [set_var("Combo", 0)]),
    ]
    g.append(grupo("Acrobacias e estilo", "Ângulo no ar, flips, wheelie e pouso", a))
    # ---------------------------------------------------- obstáculos / queda
    o = [
        comentario("Moeda de estilo (comida): +100 pontos de estilo."),
        evento([cond(0, "On collision with another object", "motoCol", [(0, "Object", "comida")])],
               [add_var("PontosEstilo", 100), act(-9, "Destroy", "comida")]),
        comentario("Invulnerabilidade curta depois de um respawn."),
        evento([var_cmp("Invul", MAIOR, 0)], [sub_var("Invul", "dt")]),
        comentario("Espinho: -3 s, combo zerado, -5% de lanche, volta ao ponto seguro."),
        evento([estado(0), var_cmp("Invul", MENOR_IGUAL, 0), cond(0, "On collision with another object", "motoCol", [(0, "Object", "espinho")])],
               penalidade(3, "AI! ESPINHO!", COR_CRUNCH, 5)),
        comentario("Muro: a moto não passa; bater custa 2 s e 5% de lanche e volta ao ponto seguro (para tentar a rampa de novo)."),
        evento([estado(0), var_cmp("Invul", MENOR_IGUAL, 0), sobre("muro", 0, 6)],
               penalidade(2, "BATEU NO MURO!", COR_CRUNCH, 5)),
        comentario("Queda no vazio: -5 s e volta ao ponto seguro."),
        evento([estado(0), cond(-4, "Is outside layout", "motoCol")], penalidade(5, "QUEDA!", COR_CRUNCH)),
        comentario("Memoriza posições seguras (duas amostras, 0,75 s) no chão e fora das rampas."),
        evento([estado(0), no_chao(), var_cmp("Invul", MENOR_IGUAL, 0), sobre("rampa", 8, 0, True), sobre("rampaG", 8, 0, True), a_cada(0.75)], [
            set_var("SafeBX", "SafeAX"), set_var("SafeBY", "SafeAY"),
            set_var("SafeAX", "motoCol.X"), set_var("SafeAY", "motoCol.Y - 8")]),
        comentario("Logo depois de um respawn libera o impulso da rampa de novo."),
        evento([var_cmp("Invul", MAIOR, 1.3)], [set_var("RampaLock", 0)]),
    ]
    g.append(grupo("Obstáculos e itens", "Espinhos, muros, queda e coletáveis", o))
    # ------------------------------------------------------------- dicas
    d = [comentario("Dicas do tutorial: o texto muda conforme a posição da moto (lista DICAS no gerador).")]
    for i, (x0, txt) in enumerate(DICAS):
        conds = [cmp2("motoCol.X", MAIOR_IGUAL, x0)]
        if i + 1 < len(DICAS):
            conds.append(cmp2("motoCol.X", MENOR, DICAS[i + 1][0]))
        d.append(evento(conds, [set_text("textDica", '"%s"' % txt)]))
    g.append(grupo("Dicas do tutorial", "Textos guiados pela posição na fase", d))
    # ------------------------------------------------------ visual da moto
    v = [
        comentario("Animações lendo o corpo físico motoCol."),
        evento([no_chao(True), toca("Jumping", True)], [set_anim("moto", "Jumping")]),
        evento([no_chao(), var_cmp("IsWheelie", IGUAL, 1), toca("Wheelie", True)], [set_anim("moto", "Wheelie")]),
        evento([no_chao(), var_cmp("IsWheelie", IGUAL, 0), cond(0, "Is moving", "motoCol", behavior="Platform"), toca("Running", True)],
               [set_anim("moto", "Running")]),
        evento([no_chao(), var_cmp("IsWheelie", IGUAL, 0), cond(0, "Is moving", "motoCol", behavior="Platform", inverted=True), toca("Idle", True)],
               [set_anim("moto", "Idle")]),
        comentario("O sprite visual (moto) segue o corpo físico (motoCol); só o visual gira."),
        evento([cond(-1, "Every tick", "System")], [act(-3, "Set position", "moto", [(0, "X", "motoCol.X"), (1, "Y", "motoCol.Y + 1")])]),
    ]
    g.append(grupo("Visual da moto", "Animações e acompanhamento do corpo físico", v))
    # ------------------------------------------------------------------ HUD
    h = [
        evento([cond(-1, "Every tick", "System")], [
            set_var("PontosAtuais", "PontosEstilo + round((100 - QualidadeLanche) * 10)"),
            set_text("textTempo", '"TEMPO " & zeropad(floor(ceil(TempoRestante) / 60), 2) & ":" & zeropad(ceil(TempoRestante) % 60, 2)'),
            set_text("textScore", '"PONTOS " & PontosAtuais'),
            set_text("textLanche", '"LANCHE " & round(QualidadeLanche) & "%"'),
            act(-5, "Set width", "barraLanche", [(0, "Width", "QualidadeLanche * 2")]),
        ]),
        evento([var_cmp("Combo", MAIOR, 0)], [set_text("textCombo", '"COMBO x" & Combo')]),
        evento([var_cmp("Combo", IGUAL, 0)], [set_text("textCombo", '""')]),
        comentario("Indicador de dano do lanche (4 estados)."),
        evento([var_cmp("QualidadeLanche", MAIOR_IGUAL, 75)], [act(5, "Set frame", "iconeLanche", [(0, "Frame number", 0)])]),
        evento([var_cmp("QualidadeLanche", MENOR, 75), var_cmp("QualidadeLanche", MAIOR_IGUAL, 50)], [act(5, "Set frame", "iconeLanche", [(0, "Frame number", 1)])]),
        evento([var_cmp("QualidadeLanche", MENOR, 50), var_cmp("QualidadeLanche", MAIOR_IGUAL, 25)], [act(5, "Set frame", "iconeLanche", [(0, "Frame number", 2)])]),
        evento([var_cmp("QualidadeLanche", MENOR, 25)], [act(5, "Set frame", "iconeLanche", [(0, "Frame number", 3)])]),
        comentario("Efeitos de texto (Smash/Crunch): somem em FxTimer segundos."),
        evento([cond(-1, "Every tick", "System")], [set_opac("textFx", "min(100, max(0, FxTimer * 250))")]),
        evento([var_cmp("FxTimer", MAIOR, 0), estado(0)], [sub_var("FxTimer", "dt")]),
    ]
    g.append(grupo("HUD", "Tempo, combo, pontos e indicador do lanche", h))

    vars_ = [
        comentario("Variáveis globais da partida"),
        variavel("TempoFase", TEMPO_FASE, "Tempo total da fase em segundos (mudar por fase)"),
        variavel("TempoRestante", TEMPO_FASE, "Cronômetro regressivo"),
        variavel("Estado", 0, "0 = correndo, 1 = entrega concluída, 2 = tempo esgotado"),
        variavel("QualidadeLanche", 100, "Percentual do lanche (100 = intacto)"),
        variavel("Combo", 0, "Manobras encadeadas sem pouso ruim (multiplicador)"),
        variavel("PontosEstilo", 0, "Pontos de estilo acumulados por manobras"),
        variavel("PontosAtuais", 0, "Estilo + dano do lanche (mostrado no HUD)"),
        variavel("BonusTempo", 0), variavel("BonusEstilo", 0), variavel("ScoreFinal", 0),
        variavel("FraseLanche", "", "Frase do resultado conforme o estado do lanche", "string"),
        variavel("IsWheelie", 0, "1 enquanto a moto empina no chão"),
        variavel("RotAcum", 0, "Rotação acumulada no ar (graus) para contar flips"),
        variavel("FlipsAr", 0, "Flips feitos no salto atual"),
        variavel("TempoNoAr", 0, "Tempo do salto atual"),
        variavel("RampaLock", 0, "1 depois do impulso da rampa, até pousar"),
        variavel("VelAr", 0, "Velocidade vertical no ar (impacto do pouso)"),
        variavel("FxTimer", 0, "Tempo restante do texto de efeito"),
        variavel("FimTimer", 0, "Espera antes de reiniciar após tempo esgotado"),
        variavel("Invul", 0, "Segundos de invulnerabilidade após respawn"),
        variavel("SafeAX", 0), variavel("SafeAY", 0), variavel("SafeBX", 0), variavel("SafeBY", 0),
    ]
    xml = ('<?xml version="1.0" encoding="utf-8" ?>\n<c2eventsheet>\n'
           '    <!--All the \'name\' attributes are ignored by Construct 2 - they are there for readability only.-->\n'
           '    <name>Jogo</name>\n    <events>%s%s</events>\n</c2eventsheet>\n') % ("".join(vars_), "".join(g))
    return BOM + xml


# ============================================================ caproj
def patch_caproj():
    s = open(CAPROJ, encoding="utf-8-sig").read()
    if 'name="rampa"' in s:
        return
    novos = ""
    for tipo in RAMPAS:
        novos += sprite_type(tipo, [("Default", 1, 5)], behaviors=[("Solid", "solid")],
                             poligono=[(0, 1), (1, 0), (1, 1)])
    s = s.replace("    </object-folder>", novos + "    </object-folder>", 1)
    open(CAPROJ, "w", encoding="utf-8-sig", newline="\r\n").write(s)


# ============================================================ MAPA (tile = 64 px, topo do chão y = 768)
TILE = 64
TOPO = 768
CHAO_H = 192
LARG, ALT = 8000, 960
TEMPO_FASE = 55
TRECHOS = [(0, 32), (37, 52), (57, 105), (112, 124)]       # vãos de 4, 4 e 6 tiles
RAMPAS_FASE = [("rampa", 27), ("rampa", 47), ("rampa", 66), ("rampa", 83), ("rampaG", 98)]   # (tipo, tile da base)
LOMBADAS = [704]
ESPINHOS = [4748, 4812]
MUROS = [5916]
CHEGADA_X = 7640
MOTO_X0 = 200


def arco(tipo, base, ts):
    """Pontos (x, y) da trajetória do salto para posicionar as moedas de estilo (velocidade de cruzeiro)."""
    w, h, _, k = RAMPAS[tipo]
    lip = (base * TILE) + w
    vy = k * (520 + 0.9 * VEL_NORMAL)
    pts = []
    for t in ts:
        x = lip - 70 + VEL_NORMAL * t
        y = TOPO - h - (vy * t - 750 * t * t)
        pts.append((round(x), round(y)))
    return pts


def moedas():
    m = [(1100, 690), (1190, 690), (1280, 690)]
    m += arco("rampa", 27, (0.45, 0.7, 0.95))
    m += arco("rampa", 47, (0.4, 0.6, 0.8, 1.0))
    m += arco("rampa", 66, (0.5, 0.75))
    m += arco("rampa", 83, (0.5, 0.75))
    m += arco("rampaG", 98, (0.5, 0.9, 1.3, 1.6))
    return m


def build_layout():
    ceu = Camada("ceu", "900000000000000", 0.05, 0, fundo="45,20,60", transparente=0)
    predios = Camada("predios", "900000000000100", 0.35, 0)
    letreiros = Camada("letreiros", "900000000000200", 0.55, 0)
    jogo = Camada("plataforma", "646620672273430", 1, 1)
    hud = Camada("HUD", "534375400233089", 0, 0)

    inst_sprite(ceu, "bgCeu", 1504, 450, 3008, 960, colisao=False)
    inst_sprite(predios, "bgPredios", 1504, 690, 3008, 420, colisao=False)
    inst_sprite(predios, "bgPredios", 4512, 690, -3008, 420, colisao=False)      # espelhado: emenda sem corte
    for i in range(8):
        inst_sprite(letreiros, "letreiroNeon%d" % (i % 4 + 1), 300 + i * 650, 400 + (i % 3) * 20, 200, 275, colisao=False)

    for (a, b) in TRECHOS:
        for t in range(a, b + 1):
            inst_sprite(jogo, "chao", t * TILE + 32, TOPO + CHAO_H // 2, 64, 192, frame=t % 3, behaviors=[BEH_SOLID])
    for tipo, base in RAMPAS_FASE:
        w, h, _, _ = RAMPAS[tipo]
        inst_sprite(jogo, tipo, base * TILE + w // 2, TOPO - h // 2, w, h, behaviors=[BEH_SOLID])
    for x in LOMBADAS:
        inst_sprite(jogo, "lombada", x, TOPO - 12, 128, 24, behaviors=[BEH_SOLID])
    for x in ESPINHOS:
        inst_sprite(jogo, "espinho", x, TOPO - 16, 64, 32)
    for x in MUROS:
        inst_sprite(jogo, "muro", x, TOPO - 64, 64, 128, behaviors=[BEH_SOLID])
    for (x, y) in moedas():
        inst_sprite(jogo, "comida", x, y, 60, 43, hot=(0.4965, 0.5024))
    inst_sprite(jogo, "chegada", CHEGADA_X, TOPO - 96, 128, 192)
    inst_sprite(jogo, "motoCol", MOTO_X0, 736, 100, 60, invisivel=True, behaviors=[BEH_MOTO])
    inst_sprite(jogo, "moto", MOTO_X0, 737, 140.017, 85.750008)

    F_G = "Arial,-40,700,0"
    inst_texto(hud, "textTempo", "TEMPO 00:%d" % TEMPO_FASE, 40, 20, 420, 56, F_G, "255,255,255")
    inst_texto(hud, "textScore", "PONTOS 0", 40, 80, 420, 40, "Arial,-28,700,0", "90,240,255")
    inst_texto(hud, "textCombo", "", 560, 20, 480, 60, F_G, "255,90,220", "Center")
    inst_sprite(hud, "iconeLanche", 1290, 58, 64, 64, colisao=False)
    inst_sprite(hud, "barraLancheFundo", 1458, 50, 208, 28, colisao=False)
    inst_sprite(hud, "barraLanche", 1358, 50, 200, 20, hot=(0, 0.5), colisao=False)
    inst_texto(hud, "textLanche", "LANCHE 100%", 1320, 74, 240, 32, "Arial,-22,700,0", "255,170,90", "Right")
    inst_texto(hud, "textFx", "", 300, 180, 1000, 110, "Arial Black,-80,900,0", "255,210,90", "Center")
    inst_texto(hud, "textDica", DICAS[0][1], 40, 850, 1520, 36, "Arial,-26,700,0", "255,236,170", "Center")
    inst_sprite(hud, "painelResultado", 800, 450, 1000, 560, invisivel=True, colisao=False)
    inst_texto(hud, "textResultado", "", 340, 215, 920, 440, "Arial,-34,700,0", "255,255,255", "Center", invisivel=True)

    layers = "".join(c.xml() for c in (ceu, predios, letreiros, jogo, hud))
    xml = ('<?xml version="1.0" encoding="utf-8" ?>\n<c2layout>\n    <name>Fase1</name>\n    <sid>779856328669726</sid>\n'
           '    <event-sheet>Jogo</event-sheet>\n    <size>\n        <width>%d</width>\n        <height>%d</height>\n    </size>\n'
           '    <margins>\n        <horizontal>500</horizontal>\n        <vertical>500</vertical>\n    </margins>\n'
           '    <unbounded-scrolling>0</unbounded-scrolling>\n    <layers>\n%s    </layers>\n'
           '    <nonworld-instances />\n    <effects />\n</c2layout>\n') % (LARG, ALT, layers)
    return BOM + xml


def main():
    ev = build_eventos()
    open(os.path.join(RAIZ, "Event sheets", "Jogo.xml"), "w", encoding="utf-8", newline="\r\n").write(ev)
    ly = build_layout()
    open(os.path.join(RAIZ, "Layouts", "Fase1.xml"), "w", encoding="utf-8", newline="\r\n").write(ly)
    patch_caproj()
    print("ok")


if __name__ == "__main__":
    main()
