#!/usr/bin/env python
"""
Recorta o fundo de um retrato e gera o PNG transparente usado no hero.

Roda 100% local e offline (modelo U^2-Net via rembg) — sem serviço pago,
sem enviar a foto do cliente pra lugar nenhum, o que também é o certo do
ponto de vista de dados pessoais.

Uso:
    python recortar-retrato.py entrada.jpg saida.png

Instalação (uma vez por máquina):
    python -m pip install "rembg[cpu]"

O primeiro uso baixa o modelo (~176 MB) e guarda em cache; do segundo em
diante é offline e leva poucos segundos.

IMPORTANTE: use a foto REAL do cliente. Retrato gerado por IA apresentado
como foto do profissional induz a erro e é vedado pelo art. 3º, II do
Provimento 205/2021 do CFOAB — e quem responde pela infração é ele.
"""
import sys
from pathlib import Path

ALPHA_MATTING = True   # bordas melhores em cabelo; desligue se ficar estranho
MAX_LARGURA = 1600     # largura de trabalho antes de processar
MAX_ALTURA = 1200      # altura final: o hero mostra ~512px, isso já cobre tela retina
QUALIDADE_WEBP = 82


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    entrada, saida = Path(sys.argv[1]), Path(sys.argv[2])
    if not entrada.exists():
        print(f"erro: não encontrei {entrada}")
        return 1

    try:
        from rembg import remove, new_session
        from PIL import Image
    except ImportError:
        print('erro: falta instalar. Rode:  python -m pip install "rembg[cpu]"')
        return 1

    img = Image.open(entrada).convert("RGBA")
    print(f"entrada: {img.width}x{img.height}")

    # reduz antes de processar: mais rápido e o resultado final não perde nada
    if img.width > MAX_LARGURA:
        altura = round(img.height * MAX_LARGURA / img.width)
        img = img.resize((MAX_LARGURA, altura), Image.LANCZOS)
        print(f"redimensionado para: {img.width}x{img.height}")

    print("removendo o fundo (o primeiro uso baixa o modelo, tenha paciência)...")
    # u2net_human_seg é treinado em pessoas — resultado melhor que o genérico
    session = new_session("u2net_human_seg")
    out = remove(
        img,
        session=session,
        alpha_matting=ALPHA_MATTING,
        alpha_matting_foreground_threshold=270,
        alpha_matting_background_threshold=20,
        alpha_matting_erode_size=11,
    )

    # corta o vazio em volta, pra foto encostar na borda do container no site
    caixa = out.getbbox()
    if caixa:
        out = out.crop(caixa)
        print(f"aparado para: {out.width}x{out.height}")

    # o hero exibe ~512px de altura; 1200px já cobre tela retina com folga.
    # Sem isso o PNG sai com megabytes que ninguém no 4G vai esperar baixar.
    if out.height > MAX_ALTURA:
        largura = round(out.width * MAX_ALTURA / out.height)
        out = out.resize((largura, MAX_ALTURA), Image.LANCZOS)
        print(f"reduzido para o uso no site: {out.width}x{out.height}")

    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.suffix.lower() == ".webp":
        out.save(saida, "WEBP", quality=QUALIDADE_WEBP, method=6)
    else:
        out.save(saida, "PNG", optimize=True)
    kb = saida.stat().st_size / 1024
    print(f"\npronto: {saida}  ({kb:.0f} KB)")

    # PNG com transparência é gordo por natureza; o WebP resolve sem perder alfa
    if saida.suffix.lower() != ".webp":
        webp = saida.with_suffix(".webp")
        out.save(webp, "WEBP", quality=QUALIDADE_WEBP, method=6)
        kb_webp = webp.stat().st_size / 1024
        print(f"também gerei: {webp.name}  ({kb_webp:.0f} KB, {100 - kb_webp / kb * 100:.0f}% menor)")
        print("o site usa o .webp automaticamente e cai no .png se precisar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
