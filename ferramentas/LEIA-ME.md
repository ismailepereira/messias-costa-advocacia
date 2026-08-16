# Ferramentas — padrão de todo projeto

Rodam localmente, sem serviço pago e sem enviar arquivo de cliente pra fora.
Isso importa: você lida com retrato e às vezes documento de terceiros.

## Instalação (uma vez por máquina)

```bash
python -m pip install "rembg[cpu]"
```

O `verificar.py` não precisa de nada além do Python.

---

## `verificar.py` — portão de publicação

Roda a checklist do Provimento 205/2021 do CFOAB e as verificações técnicas.
**Rode sempre antes de mandar link pro cliente e antes de publicar.**

```bash
python ferramentas/verificar.py .              # modo prévia
python ferramentas/verificar.py . --lancamento # modo lançamento
```

Sai com código 1 se houver erro, então dá pra plugar em CI depois.

O que ele checa:

| Verificação | Base |
|---|---|
| Número da OAB presente e preenchido | art. 5º, §2º |
| "especialista" sem certificação | art. 3º, III |
| Honorários, pagamento, gratuidade, desconto | art. 3º, I |
| Promessa de resultado | art. 6º |
| Superlativo e comparação | art. 3º, IV |
| Logotipo da OAB no site | art. 5º, §2º |
| `noindex` e `robots.txt` conforme o modo | — |
| Placeholders `[pendente]` restantes | — |
| `SEU-DOMINIO-AQUI` em robots/sitemap | — |
| Tailwind CDN carregado sem uso | — |
| Contraste dos tons de texto (mínimo 4,5:1) | WCAG AA |
| `alt` nas imagens | WCAG |
| Imagem acima de 900 KB | desempenho |
| Telefone/WhatsApp ainda de exemplo | — |

**Modo prévia** aceita placeholder e noindex (o site ainda está em aprovação).
**Modo lançamento** exige tudo resolvido.

---

## `recortar-retrato.py` — retrato sem fundo

Remove o fundo com o modelo U²-Net (`u2net_human_seg`, treinado em pessoas),
apara o vazio em volta, reduz pro tamanho que o site usa e gera **WebP**
além do PNG — o WebP costuma sair ~90% menor com a mesma transparência.

```bash
python ferramentas/recortar-retrato.py foto-original.jpg src/assets/img/nome-recorte.png
```

O primeiro uso baixa o modelo (~176 MB) e guarda em `~/.u2net`. Depois é
offline e leva segundos.

O template já procura `*-recorte.webp` primeiro, cai no `.png` e, se não
houver nenhum, o hero volta sozinho pra coluna única — nunca fica buraco.

> **Use a foto real do cliente.** Retrato gerado por IA apresentado como foto
> do profissional induz a erro (art. 3º, II) e quem responde é ele.

### Roteiro de foto com celular

Quando o cliente não tiver foto profissional, isso resolve e é replicável:
janela grande de lado (luz suave), fundo liso a dois metros atrás, celular na
altura dos olhos, modo retrato, luz das 9h ou das 16h. Peça vinte fotos em três
enquadramentos — busto, meio corpo e trabalhando — e use três.
