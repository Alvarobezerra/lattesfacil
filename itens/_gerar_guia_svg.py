"""Gera as ilustrações do guia de instalação da extensão (static/img/guia/*.svg). Rodar: python itens/_gerar_guia_svg.py"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "static" / "img" / "guia"
FONT = "Segoe UI, Arial, sans-serif"
RED = "#e5484d"


def t(x, y, s, size=14, fill="#222", weight="400", anchor="start", mono=False):
    fam = "Consolas, monospace" if mono else FONT
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'


def rect(x, y, w, h, fill="#fff", stroke="none", r=0, sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def hl(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{RED}" stroke-width="4"/>'


def badge(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="15" fill="{RED}"/>' + t(x, y + 6, str(n), 17, "#fff", "700", "middle")


def arrow(x1, y1, x2, y2):
    return (f'<defs><marker id="h" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RED}" stroke-width="4" marker-end="url(#h)"/>')


def label(x, y, s, w=None):
    w = w or (len(s) * 8.6 + 24)
    return rect(x, y, w, 30, RED, r=8) + t(x + w / 2, y + 20, s, 14, "#fff", "700", "middle")


def svg(body, w=800, h=450):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="#e9eef5"/>{body}</svg>')


def browser(url, content, aba="LattesData", puzzle=False, w=800, h=450):
    b = rect(14, 14, w - 28, h - 28, "#fff", "#c7d0dc", 10)
    b += rect(14, 14, w - 28, 38, "#dde3ec", r=10) + rect(14, 40, w - 28, 12, "#dde3ec")
    b += rect(26, 22, 170, 30, "#fff", r=8) + t(40, 42, aba, 13, "#222")
    b += t(184, 41, "×", 14, "#666")
    b += rect(14, 52, w - 28, 44, "#fff")
    b += t(30, 80, "←   →   ⟳", 17, "#666")
    b += rect(118, 58, w - 118 - (86 if puzzle else 40), 32, "#eef2f7", r=16) + t(136, 79, url, 14, "#333")
    if puzzle:
        b += t(w - 80, 80, "🧩", 18, "#555") + t(w - 50, 80, "⋮", 18, "#555")
    else:
        b += t(w - 44, 80, "⋮", 18, "#555")
    b += f'<line x1="14" y1="96" x2="{w-14}" y2="96" stroke="#e1e6ee"/>' + content
    return b


def winexplorer(title, content, w=800, h=450):
    b = rect(14, 14, w - 28, h - 28, "#fff", "#c7d0dc", 8)
    b += rect(14, 14, w - 28, 34, "#f3f6fa", r=8) + t(30, 37, "📁 " + title, 13, "#222")
    b += t(w - 34, 36, "✕", 14, "#444") + rect(14, 48, w - 28, 38, "#f7f9fc") + t(30, 72, "Novo ▾   ✂   ⧉   ⌦   Classificar ▾   Exibir ▾", 12, "#444")
    b += content
    return b


def lattes_login():
    c = rect(0, 96, 800, 340, "#0b192c")
    c += t(400, 150, "Lattes DATA", 26, "#fff", "700", "middle")
    c += rect(270, 170, 260, 36, "#16283f", "#2d4a6e", 8) + t(284, 193, "Aramys Silva dos Reis   ▾", 14, "#dfe8f3")
    c += rect(270, 218, 260, 36, "#16283f", "#2d4a6e", 8) + t(284, 241, "•••••••••••", 16, "#dfe8f3")
    c += rect(270, 268, 260, 38, "#00a3c4", r=8) + t(400, 293, "Entrar", 15, "#04202a", "700", "middle")
    return c


S = {}

# 1) abrir o site
c = rect(0, 96, 800, 340, "#fff") + t(400, 240, "Digite o endereço e aperte Enter", 18, "#667", anchor="middle")
S["01-abrir-site"] = svg(browser("lattesfacil.onrender.com", c, "Nova guia") + hl(116, 56, 560, 36) + badge(700, 74, 1) + label(300, 380, "Digite o endereço do site aqui"))

# 2) login
S["02-login"] = svg(browser("lattesfacil.onrender.com/login", lattes_login(), "LattesData — Acesso")
                    + hl(266, 166, 268, 44) + hl(266, 214, 268, 44) + hl(266, 264, 268, 46)
                    + badge(250, 188, 1) + badge(250, 236, 2) + badge(250, 287, 3)
                    + t(545, 193, "1  escolha seu nome", 13, "#fff") + t(545, 241, "2  digite o código de acesso", 13, "#fff") + t(545, 292, "3  clique em Entrar", 13, "#fff"))

# 3) menu instalar extensão
c = rect(0, 96, 800, 340, "#f4f8fb") + rect(0, 96, 800, 50, "#fff") + t(40, 128, "Lattes DATA", 18, "#0b192c", "700")
c += t(330, 128, "Início", 14, "#00829c", "700") + t(410, 128, "Enviar documentos", 14, "#546580") + t(580, 128, "Instalar extensão", 14, "#546580")
c += rect(40, 170, 720, 150, "#fff", "#dbe4ee", 12) + t(60, 205, "Olá, Aramys", 22, "#0b192c", "700") + t(60, 235, "Seus indicadores aparecem aqui…", 14, "#546580")
S["03-menu-instalar"] = svg(browser("lattesfacil.onrender.com/abertura.html", c) + hl(568, 108, 150, 30) + badge(643, 160, 1) + arrow(643, 200, 643, 150) + label(520, 205, "Clique em “Instalar extensão”"))

# 4) botão baixar
c = rect(0, 96, 800, 340, "#f4f8fb") + t(40, 140, "Instalar a extensão em outro computador", 20, "#0b192c", "700")
c += rect(40, 170, 720, 120, "#fff", "#dbe4ee", 12) + t(60, 205, "2  Baixe o arquivo da extensão", 16, "#0b192c", "700") + rect(60, 225, 250, 40, "#00a3c4", r=10) + t(185, 251, "📥 Baixar extensão (.zip)", 14, "#04202a", "700", "middle")
S["04-baixar"] = svg(browser("lattesfacil.onrender.com/instalar-extensao.html", c) + hl(56, 221, 258, 48) + badge(340, 245, 1) + label(360, 232, "Clique no botão azul"))

# 5) download concluído
c = rect(0, 96, 800, 340, "#f4f8fb") + rect(470, 100, 300, 130, "#fff", "#c7d0dc", 10)
c += t(488, 128, "Downloads", 14, "#222", "700") + t(488, 158, "📦 lattesdata-extensao.zip", 13, "#222") + t(488, 177, "Concluído", 12, "#2a8f5a")
c += t(488, 212, "Mostrar na pasta", 13, "#1a6fd6", "700")
S["05-download-ok"] = svg(browser("lattesfacil.onrender.com/instalar-extensao.html", c) + hl(480, 197, 140, 22) + badge(650, 208, 1) + label(380, 300, "Clique em “Mostrar na pasta”"))

# 6) botão direito → extrair tudo
c = rect(30, 100, 740, 40, "#fff") + t(40, 126, "Downloads", 14, "#222", "700")
c += rect(40, 160, 400, 34, "#cfe3ff", r=4) + t(56, 183, "📦  lattesdata-extensao.zip", 14, "#222")
c += rect(150, 190, 260, 150, "#fdfdfd", "#c7d0dc", 8) + t(170, 220, "Abrir", 14) + t(170, 250, "Extrair tudo…", 14, "#000", "700") + t(170, 280, "Copiar", 14) + t(170, 310, "Propriedades", 14)
S["06-extrair-menu"] = svg(winexplorer("Downloads", c) + hl(158, 232, 244, 30) + badge(130, 247, 2) + badge(30, 177, 1) + label(430, 232, "Botão direito no arquivo → Extrair tudo…", 330))

# 7) janela extrair
c = rect(150, 110, 500, 290, "#fff", "#aab5c5", 8) + t(170, 140, "Extrair Pastas Compactadas (Zip)", 15, "#222", "700")
c += t(170, 175, "Selecione um destino:", 13) + rect(170, 188, 380, 30, "#fff", "#8a96a8", 4) + t(180, 208, "C:\\Users\\Aramys\\Downloads\\lattesdata-extensao", 12, "#222", mono=True)
c += rect(170, 240, 14, 14, "#fff", "#555", 2) + t(192, 252, "Mostrar pastas extraídas quando concluído", 13) + rect(500, 340, 120, 34, "#0067c0", r=6) + t(560, 362, "Extrair", 14, "#fff", "700", "middle")
S["07-extrair-janela"] = svg(winexplorer("Downloads", c) + hl(495, 335, 130, 44) + badge(655, 357, 1) + label(430, 300, "Clique em “Extrair”"))

# 8) pasta extraída
c = t(40, 126, "Downloads  ›  lattesdata-extensao", 14, "#222", "700")
for i, (n, ico) in enumerate([("manifest.json", "📄"), ("background.js", "📜"), ("content-app.js", "📜"), ("content-lattes.js", "📜"), ("autofill_core.js", "📜")]):
    c += t(60, 170 + i * 34, f"{ico}  {n}", 15, "#222", "700" if i == 0 else "400")
S["08-pasta-extraida"] = svg(winexplorer("lattesdata-extensao", c) + hl(50, 150, 220, 30) + badge(300, 165, 1) + label(330, 150, "Tem que ter o manifest.json aqui dentro", 330) + label(330, 200, "Guarde essa pasta num lugar fixo", 290))

# 9) abrir chrome://extensions
c = rect(0, 96, 800, 340, "#fff") + t(400, 260, "Nova guia", 18, "#99a", anchor="middle")
S["09-abrir-extensoes"] = svg(browser("chrome://extensions", c, "Nova guia") + hl(116, 56, 560, 36) + badge(700, 74, 1) + label(250, 380, "Cole  chrome://extensions  e aperte Enter (Edge: edge://extensions)", 520))

# 10) modo desenvolvedor
c = rect(0, 96, 800, 340, "#f1f3f4") + rect(0, 96, 800, 50, "#fff") + t(30, 128, "☰   Extensões", 18, "#222")
c += t(560, 128, "Modo do desenvolvedor", 13, "#444") + rect(716, 112, 40, 22, "#bdc1c6", r=11) + '<circle cx="727" cy="123" r="8" fill="#fff"/>'
c += rect(30, 170, 740, 80, "#fff", "#dadce0", 8) + t(50, 205, "Nenhuma extensão instalada ainda", 15, "#666")
S["10-modo-dev"] = svg(browser("chrome://extensions", c, "Extensões") + hl(548, 106, 218, 34) + badge(530, 123, 1) + arrow(640, 190, 740, 142) + label(450, 290, "Clique na chave para ligar (fica azul)", 330))

# 11) carregar sem compactação
c = rect(0, 96, 800, 340, "#f1f3f4") + rect(0, 96, 800, 50, "#fff") + t(30, 128, "☰   Extensões", 18, "#222") + t(560, 128, "Modo do desenvolvedor", 13, "#444") + rect(716, 112, 40, 22, "#1a73e8", r=11) + '<circle cx="745" cy="123" r="8" fill="#fff"/>'
c += rect(0, 146, 800, 46, "#e8f0fe") + rect(24, 154, 210, 30, "#fff", "#1a73e8", 16) + t(129, 175, "Carregar sem compactação", 13, "#1a73e8", "700", "middle") + rect(246, 154, 130, 30, "#fff", "#c7d0dc", 16) + t(311, 175, "Compactar extensão", 12, "#555", "700", "middle") + rect(388, 154, 90, 30, "#fff", "#c7d0dc", 16) + t(433, 175, "Atualizar", 12, "#555", "700", "middle")
S["11-carregar"] = svg(browser("chrome://extensions", c, "Extensões") + hl(20, 150, 218, 38) + badge(258, 208, 1) + arrow(258, 230, 200, 196) + label(280, 220, "Agora clique em “Carregar sem compactação”", 380))

# 12) escolher pasta
c = rect(120, 100, 560, 320, "#fff", "#aab5c5", 8) + t(140, 130, "Selecione a pasta da extensão", 15, "#222", "700")
c += rect(140, 150, 520, 180, "#fafbfc", "#dde3ec", 4) + t(160, 180, "📁  Documentos", 14) + rect(150, 194, 500, 30, "#cfe3ff", r=3) + t(160, 214, "📁  lattesdata-extensao", 14, "#222", "700") + t(160, 250, "📁  Imagens", 14)
c += rect(430, 360, 140, 34, "#0067c0", r=6) + t(500, 382, "Selecionar pasta", 13, "#fff", "700", "middle") + rect(580, 360, 80, 34, "#fff", "#aab5c5", 6) + t(620, 382, "Cancelar", 13, "#222", "700", "middle")
S["12-escolher-pasta"] = svg(winexplorer("Escolha a pasta", c) + hl(146, 190, 508, 38) + badge(128, 209, 1) + hl(424, 355, 152, 44) + badge(590, 345, 2))

# 13) extensão instalada
c = rect(0, 96, 800, 340, "#f1f3f4") + rect(0, 96, 800, 50, "#fff") + t(30, 128, "☰   Extensões", 18, "#222") + t(560, 128, "Modo do desenvolvedor", 13, "#444") + rect(716, 112, 40, 22, "#1a73e8", r=11) + '<circle cx="745" cy="123" r="8" fill="#fff"/>'
c += rect(30, 170, 420, 150, "#fff", "#dadce0", 10) + rect(48, 190, 44, 44, "#00a3c4", r=10) + t(70, 220, "L", 24, "#04202a", "700", "middle")
c += t(106, 208, "LattesData — Automação", 15, "#222", "700") + t(106, 228, "Currículo Lattes  0.9.3", 13, "#666") + t(48, 280, "Detalhes        Remover", 13, "#1a73e8", "700")
c += rect(380, 290, 40, 22, "#1a73e8", r=11) + '<circle cx="409" cy="301" r="8" fill="#fff"/>'
S["13-instalada"] = svg(browser("chrome://extensions", c, "Extensões", puzzle=True) + hl(26, 166, 428, 158) + badge(470, 190, 1) + hl(376, 286, 48, 30) + badge(440, 301, 2)
                        + label(480, 215, "A extensão apareceu na lista", 270) + label(480, 300, "Chave azul = ativada", 190))

# 14) voltar ao site e F5
c = rect(0, 96, 800, 340, "#f4f8fb") + rect(0, 96, 800, 50, "#fff") + t(40, 128, "Lattes DATA", 18, "#0b192c", "700")
c += rect(40, 170, 720, 56, "#fff", "#10b981", 12) + '<circle cx="64" cy="198" r="7" fill="#10b981"/>' + t(84, 204, "Extensão instalada e ativa neste computador (versão 0.9.3).", 15, "#222", "700")
S["14-verde"] = svg(browser("lattesfacil.onrender.com/instalar-extensao.html", c) + hl(36, 166, 728, 64) + badge(780, 198, 2)
                    + hl(26, 58, 80, 32) + badge(66, 112, 1) + label(330, 280, "1  Aperte F5 (ou ⟳)    2  Aviso verde = pronto!", 380))

OUT.mkdir(parents=True, exist_ok=True)
for nome, conteudo in S.items():
    (OUT / f"{nome}.svg").write_text(conteudo, encoding="utf-8")
print(len(S), "ilustrações em", OUT)
