# Messias Costa | Advocacia — Anapú, PA

Site institucional. HTML/CSS/JS puro, sem build. Motion (motion.dev) via CDN para as animações.

> **⚠️ Este site está em MODO PRÉVIA e não deve ser divulgado ainda.**
> Está com `noindex` e `robots.txt` bloqueado de propósito — veja *Antes de publicar* abaixo.

## Rodar localmente

```bash
python -m http.server 5176 --directory src
```

## Antes de publicar (obrigatório)

O Provimento 205/2021 do CFOAB regula a publicidade da advocacia, e quem responde por
infração é o advogado. Nenhum item abaixo é opcional:

- [ ] **Número de inscrição na OAB** — hoje `[pendente]` no hero e no rodapé. **Sem isso o site não sobe** (art. 5º, §2º).
- [ ] **Biografia** real na seção Sobre (hoje é placeholder).
- [ ] **Horário de atendimento** (hoje `[confirmar]`).
- [ ] **Retrato real** do advogado — nunca imagem gerada por IA (induz a erro, art. 3º, II). Slot pronto em `src/index.html`, procure por `hero-photo` e `sobre-photo`.
- [ ] Trocar `SEU-DOMINIO-AQUI` em `src/sitemap.xml`.
- [ ] **Remover o `noindex`** do `<head>` do `src/index.html` e liberar o `src/robots.txt`.

Regras já aplicadas no texto: "atuação em" em vez de "especialista em" (art. 3º, III),
sem valores de honorário (art. 3º, I), sem promessa de resultado (art. 6º),
sem superlativo (art. 3º, IV) e sem logo da OAB (art. 5º, §2º).

## Deploy (GitHub Pages)

`.github/workflows/pages.yml` publica a pasta `src/` a cada push na `main`.
No repositório: **Settings → Pages → Source: GitHub Actions**.

## Estrutura

```
src/
├── index.html              # página única
├── robots.txt · sitemap.xml
└── assets/
    ├── css/styles.css      # tokens de cor/tipografia no :root
    └── js/main.js          # sistema de movimento (Motion)
```

Ao editar CSS ou JS, incremente o `?v=` nos links do `index.html` para o navegador
do cliente não servir a versão antiga.

Escopo, direção visual e pendências: [`docs/briefing.md`](docs/briefing.md).
