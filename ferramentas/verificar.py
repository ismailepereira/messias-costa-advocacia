#!/usr/bin/env python
"""
Verificador de pré-publicação para sites de advocacia.

Roda a checklist do Provimento 205/2021 do CFOAB e as verificações técnicas
que já nos pegaram na prática. Só depende da biblioteca padrão do Python.

Uso:
    python verificar.py <pasta-do-projeto>              # modo prévia
    python verificar.py <pasta-do-projeto> --lancamento # modo lançamento

Modo prévia   : aceita placeholders e noindex (site ainda em aprovação).
Modo lançamento: exige tudo preenchido. É o portão antes de publicar.

Código de saída 1 se houver ERRO — dá pra usar em CI depois.
"""
import re
import sys
from pathlib import Path

ERROS: list[str] = []
AVISOS: list[str] = []
OKS: list[str] = []


def erro(msg: str) -> None: ERROS.append(msg)
def aviso(msg: str) -> None: AVISOS.append(msg)
def ok(msg: str) -> None: OKS.append(msg)


# --------------------------------------------------------------------------
# contraste (WCAG)
# --------------------------------------------------------------------------
def _lum(hexcor: str) -> float:
    h = hexcor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    canais = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def contraste(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# --------------------------------------------------------------------------
# regras de publicidade (Provimento 205/2021)
# --------------------------------------------------------------------------
def checar_oab(texto: str, lancamento: bool) -> None:
    if not re.search(r"OAB", texto, re.I):
        erro("OAB ausente. Art. 5º, §2º exige o número de inscrição. Sem isso o site não pode ir ao ar.")
        return
    pendente = re.search(r"OAB[^<\n]{0,40}(\[pendente|\[confirmar|n°\s*\[|nº\s*\[|XXX|000)", texto, re.I)
    if pendente:
        (erro if lancamento else aviso)(
            "Número da OAB ainda é placeholder. Art. 5º, §2º — obrigatório antes de publicar."
        )
    else:
        ok("Número da OAB preenchido.")


def checar_vedacoes(texto: str, html_cru: str) -> None:
    """`texto` é só o conteúdo visível — comentário do código não chega ao
    usuário final e não pode disparar alarme. Só a regra do logotipo olha o
    HTML cru, porque precisa enxergar o atributo src da <img>."""
    regras = [
        (r"\bespecialist[ae]\b", "erro",
         'Uso de "especialista". Art. 3º, III veda anunciar especialidade sem certificação — troque por "atuação em".'),
        (r"(R\$\s*\d|honorário|parcelamos|parcelamento|primeira consulta grátis|consulta gratuita|desconto)", "erro",
         "Referência a honorários, pagamento, gratuidade ou desconto. Art. 3º, I."),
        (r"(garantimos|garantido o|resultado garantido|com certeza você (vai|ganha)|100% de êxito)", "erro",
         "Promessa de resultado. Art. 6º."),
        (r"(o melhor (escritório|advogado)|o maior (escritório|da região)|líder em|nº ?1 em|referência nacional)", "aviso",
         "Possível expressão de autoengrandecimento ou comparação. Art. 3º, IV — revise."),
    ]
    achou = False

    # regra do logotipo: precisa do HTML cru, mas ignorando comentários
    html_sem_comentario = re.sub(r"<!--.*?-->", " ", html_cru, flags=re.S)
    m_logo = re.search(r"<img[^>]+src=[\"'][^\"']*oab[^\"']*\.(png|jpg|jpeg|svg|webp)",
                       html_sem_comentario, re.I)
    if m_logo:
        achou = True
        erro("Parece haver logotipo da OAB. Art. 5º, §2º veda o uso de símbolos oficiais da Ordem.")

    for padrao, nivel, msg in regras:
        m = re.search(padrao, texto, re.I)
        if m:
            achou = True
            trecho = m.group(0)[:60]
            (erro if nivel == "erro" else aviso)(f'{msg}  [encontrado: "{trecho}"]')
    if not achou:
        ok("Nenhuma vedação de publicidade detectada no texto.")


# --------------------------------------------------------------------------
# técnicas
# --------------------------------------------------------------------------
def checar_indexacao(html: str, robots: str | None, lancamento: bool) -> None:
    noindex = re.search(r'name=["\']robots["\'][^>]*noindex', html, re.I)
    bloqueado = robots is not None and re.search(r"^\s*Disallow:\s*/\s*$", robots, re.M)

    if lancamento:
        if noindex:
            erro("meta robots=noindex ainda presente — o Google não vai indexar o site.")
        if bloqueado:
            erro("robots.txt com 'Disallow: /' — remove o site inteiro da busca.")
        if not noindex and not bloqueado:
            ok("Indexação liberada.")
    else:
        if noindex or bloqueado:
            ok("Modo prévia: indexação bloqueada, como esperado.")
        else:
            aviso("Prévia sem noindex — o Google pode indexar uma versão incompleta.")


def checar_placeholders(html: str, lancamento: bool) -> None:
    achados = re.findall(r"\[(pendente|confirmar|biografia|a incluir)[^\]]*\]", html, re.I)
    if achados:
        (erro if lancamento else aviso)(
            f"{len(achados)} placeholder(s) ainda no texto: " + ", ".join(sorted({a.lower() for a in achados}))
        )
    else:
        ok("Sem placeholders no texto.")

    if "SEU-DOMINIO-AQUI" in html:
        erro("SEU-DOMINIO-AQUI ainda no HTML.")


def checar_dominio(robots: str | None, sitemap: str | None, lancamento: bool) -> None:
    for nome, conteudo in (("robots.txt", robots), ("sitemap.xml", sitemap)):
        if conteudo and "SEU-DOMINIO-AQUI" in conteudo:
            (erro if lancamento else aviso)(f"{nome} ainda com SEU-DOMINIO-AQUI.")


def checar_tailwind(html: str) -> None:
    if "cdn.tailwindcss.com" not in html:
        return
    # procura classes utilitárias do Tailwind nos atributos class
    classes = " ".join(re.findall(r'class=["\']([^"\']+)["\']', html))
    util = re.search(
        r"\b(flex|grid|hidden|p[xytrbl]?-\d|m[xytrbl]?-\d|w-\d|h-\d|text-(xs|sm|lg|xl)|bg-\w+-\d|rounded|gap-\d)\b",
        classes)
    if util:
        aviso("Tailwind via CDN em uso. É um compilador rodando no navegador do cliente — considere CSS próprio.")
    else:
        erro("Tailwind via CDN carregado com ZERO utilitário em uso. Peso morto puro: remova a tag <script>.")


def checar_acessibilidade(html: str, css: str) -> None:
    # alt em imagens
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    sem_alt = [i for i in imgs if not re.search(r"\balt=", i, re.I)]
    if sem_alt:
        aviso(f"{len(sem_alt)} <img> sem atributo alt.")
    elif imgs:
        ok(f"Todas as {len(imgs)} imagens têm alt.")

    # contraste dos tokens de cor contra o fundo
    tokens = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;", css))
    fundo = tokens.get("--bg")
    if not fundo:
        return
    ruins = []
    for nome, cor in tokens.items():
        if nome == "--bg" or not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
            continue
        if not re.search(r"(ink|text|bone|fg|dim|faint|meta|muted)", nome):
            continue
        r = contraste(cor, fundo)
        if r < 4.5:
            ruins.append(f"{nome} ({cor}) = {r}:1")
    if ruins:
        aviso("Contraste abaixo de 4,5:1 (mínimo AA) — atenção à linha da OAB: " + "; ".join(ruins))
    else:
        ok("Todos os tons de texto passam o contraste mínimo AA.")


def checar_peso(pasta: Path) -> None:
    grandes = []
    total = 0
    for p in pasta.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
            kb = p.stat().st_size / 1024
            total += kb
            if kb > 900:
                grandes.append(f"{p.name} ({kb:.0f} KB)")
    if grandes:
        aviso("Imagem(ns) acima de 900 KB — o público acessa por 4G: " + "; ".join(grandes))
    elif total:
        ok(f"Imagens somam {total:.0f} KB.")


def checar_retrato_provisorio(src: Path, lancamento: bool) -> None:
    """Trava contra o acidente mais caro: publicar com retrato provisório
    (imagem de banco ou gerada por IA) no lugar da foto real do cliente."""
    marcadores = list(src.rglob("RETRATO-PROVISORIO*")) + list(src.rglob("FOTO-PROVISORIA*"))
    if marcadores:
        (erro if lancamento else aviso)(
            "Retrato PROVISÓRIO em uso — não é foto real do cliente. Art. 3º, II. "
            f"Substitua e apague {marcadores[0].name}."
        )
    else:
        ok("Nenhum marcador de retrato provisório.")


def checar_contato(html: str) -> None:
    if not re.search(r"wa\.me/\d{12,13}", html):
        aviso("Não encontrei link de WhatsApp no formato wa.me/55DDDNUMERO.")
    else:
        ok("Link de WhatsApp presente.")
    if re.search(r"(wa\.me/5500000000000|tel:\+?5500000000000|00\) 0000-0000)", html):
        erro("Telefone/WhatsApp ainda com número de exemplo do template.")


# --------------------------------------------------------------------------
def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    raiz = Path(sys.argv[1])
    lancamento = "--lancamento" in sys.argv
    src = raiz / "src"
    if not src.is_dir():
        print(f"erro: não encontrei {src}")
        return 2

    index = src / "index.html"
    if not index.exists():
        print(f"erro: não encontrei {index}")
        return 2

    html = index.read_text(encoding="utf-8")
    css = "\n".join(p.read_text(encoding="utf-8") for p in (src / "assets" / "css").glob("*.css")) \
        if (src / "assets" / "css").is_dir() else ""
    robots = (src / "robots.txt").read_text(encoding="utf-8") if (src / "robots.txt").exists() else None
    sitemap = (src / "sitemap.xml").read_text(encoding="utf-8") if (src / "sitemap.xml").exists() else None

    # texto visível, sem tags nem comentários (comentário não vai pro usuário final)
    visivel = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    visivel = re.sub(r"<(script|style)\b.*?</\1>", " ", visivel, flags=re.S | re.I)
    visivel = re.sub(r"<[^>]+>", " ", visivel)

    modo = "LANÇAMENTO" if lancamento else "PRÉVIA"
    print(f"\n  Verificando: {raiz.name}   [modo {modo}]\n" + "  " + "-" * 58)

    checar_oab(visivel, lancamento)
    checar_vedacoes(visivel, html)
    checar_indexacao(html, robots, lancamento)
    checar_placeholders(visivel, lancamento)
    checar_dominio(robots, sitemap, lancamento)
    checar_tailwind(html)
    checar_acessibilidade(html, css)
    checar_peso(src)
    checar_retrato_provisorio(src, lancamento)
    checar_contato(html)

    for m in OKS:
        print(f"  ok    {m}")
    for m in AVISOS:
        print(f"  AVISO {m}")
    for m in ERROS:
        print(f"  ERRO  {m}")

    print("  " + "-" * 58)
    if ERROS:
        print(f"  {len(ERROS)} erro(s), {len(AVISOS)} aviso(s). NÃO PUBLIQUE ainda.\n")
        return 1
    if lancamento:
        print(f"  Sem erros, {len(AVISOS)} aviso(s). Liberado para publicar.\n")
    else:
        print(f"  Prévia ok, {len(AVISOS)} aviso(s) a resolver antes do lançamento.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
