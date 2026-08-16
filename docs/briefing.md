# Spec — Site Dr. Messias Costa Advocacia

**Data:** 2026-08-16
**Cliente:** Messias Costa — Advogado (Anapú, PA)

## Contexto do negócio

- Instagram: [@advogadomessiascosta](https://www.instagram.com/advogadomessiascosta/) (~206 mil seguidores — perfil grande, produz conteúdo/palestras)
- Facebook: [Dr. Messias Costa](https://www.facebook.com/dr.messiascosta/) (1,3 mil seguidores)
- Endereço (Facebook): Goiás, Nº 10, São Luís, Anapú, PA
- Telefone/WhatsApp: (91) 99341-5370 — `https://wa.me/5591993415370`
- E-mail: messiascosta.adv@gmail.com
- **Número da OAB: não encontrado publicamente — pendente de confirmação com o cliente** (obrigatório exibir no site, ver nota ética abaixo)
- Áreas de atuação (conforme bio do Instagram): Salário-Maternidade, Aposentadorias e Benefícios do INSS (Direito Previdenciário), Defesa Criminal, também atua em Cível e Família (destaques do Instagram). Também é palestrante.
- Atuação: sediado em Anapú-PA, mas com alcance nacional (bio diz "Atuação Nacional" — provável atendimento remoto, comum em advocacia previdenciarista que cresce via conteúdo).

## Objetivo

Site institucional de vitrine (página única) que reforce a autoridade que ele já construiu no Instagram — apresentar áreas de atuação, gerar contato via WhatsApp (canal primário dele hoje), e servir de "cartão de visita" formal/profissional pra quem chega por indicação ou pesquisa no Google (público que não segue Instagram).

## Escopo confirmado com o cliente

- **Seções:** Hero · Áreas de atuação · Sobre/Autoridade · Atendimento (Anapú-PA + nacional/online) · Contato (rodapé). Sem blog nesta fase (conteúdo já é feito no Instagram).
- **Foto do advogado:** placeholder — cliente envia foto profissional depois.
- **Textos das áreas de atuação:** placeholder a partir do que está público no Instagram — cliente revisa e confirma escopo exato de cada área.
- **OAB:** campo placeholder `[nº OAB pendente]` visível no rodapé — **não publicar o site sem preencher**, é exigência da regulamentação da advocacia.
- **Repositório:** novo repositório GitHub dedicado (`messias-costa-advocacia`), deploy automático via GitHub Pages.

## ⚠️ Nota ética/regulatória (importante pra advocacia)

Publicidade de advogado no Brasil segue o **Provimento 205/2021 do CFOAB** (Código de Ética + regras de publicidade): tom sóbrio e informativo, proibido linguagem mercantilista, proibida promessa de resultado, proibida comparação com outros advogados, **número de inscrição na OAB deve constar** em qualquer peça publicitária/site profissional. O template já segue tom sóbrio por padrão (sem "somos os melhores", sem depoimentos exagerados) — ao preencher os textos reais, manter essa linha e confirmar com o cliente/OAB local se há exigência adicional antes de publicar.

## Direção visual aprovada

**Referência:** [advocaciasimonelli.com.br](https://advocaciasimonelli.com.br/) — escritório clássico, hero centralizado sobre foto escura, headline serifada com linha central em itálico dourado, numerais romanos nas seções, faixa de números.

Elementos adotados dessa referência:
- Hero **centralizado**, com vinheta escura e ponto de luz quente ao fundo
- **Lockup** de logo: nome em serifada caixa-alta + "ADVOCACIA" em dourado espaçado
- Eyebrow dourado com **número da OAB** (a referência também o exibe no hero)
- Headline em 3 linhas com a **linha do meio em itálico dourado**
- **Régua dourada** curta abaixo do título
- Parágrafo com **destaques em negrito** nos termos-chave
- Dois CTAs em **caixa alta espaçada** (dourado sólido + contorno)
- Numerais **romanos** (I. II. III. IV.) nas áreas de atuação e nos passos
- **Faixa de números** com valores em serifada dourada
- **Botão flutuante de WhatsApp**
- Moldura deslocada na foto da seção Sobre

**Paleta:** azul-marinho `#0a1420` / `#0d1826` · dourado `#c9a227` · texto creme `#ece8df`
**Tipografia:** Cormorant Garamond (display, com itálico de destaque) + Inter (corpo)

## Arquitetura técnica

Segue o padrão do `_template` (ver `sites-clientes/docs/stack.md`): HTML/CSS/JS puro, Tailwind CDN + Motion. Pasta `src/` é a única coisa publicada.

## Pendências que bloqueiam a publicação

| Item | Onde | Situação |
|---|---|---|
| **Número da OAB** | hero (eyebrow) e rodapé | `[pendente]` — **obrigatório**, não publicar sem |
| Anos de atuação | faixa de números | `[ ]` — só preencher com o número real |
| Biografia | seção Sobre | parágrafo placeholder marcado |
| Horário de atendimento | rodapé | `[confirmar]` |
| Foto do escritório/retrato | hero e Sobre | usando fundo abstrato + monograma "MC"; slots prontos no HTML |
| Domínio | `robots.txt`, `sitemap.xml` | trocar `SEU-DOMINIO-AQUI` |

## Fora de escopo (nesta fase)

- Blog / conteúdo jurídico no site (o Instagram já cumpre esse papel)
- Formulário de contato com backend (usa WhatsApp direto, canal que ele já usa e domina)
- Área de cliente / peticionamento online
- Confirmação do número da OAB — pendente, bloqueia publicação

## Testes / verificação

Após implementação: abrir no preview, checar scroll completo, responsividade mobile (público de Instagram acessa majoritariamente por celular), e conferir que o placeholder de OAB está visível e claramente marcado como pendente até ser preenchido.
