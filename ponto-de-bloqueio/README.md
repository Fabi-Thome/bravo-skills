# Ponto de Bloqueio

> Mapeie as interfaces entre contratados em obra, identifique o caminho crítico e veja onde está o bloqueio — tudo conversando com uma IA.
>
> Primeira skill da família **[Bravo Skills](../README.md)**.

---

## O problema

Em obras com muitos contratados — silos, frigoríficos, esmagadoras, terminais portuários — o fator mais crítico de coordenação não é o cronograma de cada fornecedor. É **a interface entre eles**: quando um precisa entrar, quando o anterior precisa ter saído, e quem fica bloqueado quando alguém atrasa.

A maioria das ferramentas pede que você consolide tudo num cronograma master. É trabalhoso, frágil e quase nunca espelha a realidade.

## A solução

**Não consolide. Conecte.**

- Cada contratado é uma linha simples na planilha: entrada, saída, de quem depende.
- O algoritmo monta o grafo, calcula o caminho crítico e mostra onde está o bloqueio.
- Você atualiza a planilha semanalmente conforme a obra evolui — a IA recalcula tudo.

---

## Status

🚧 **Em desenvolvimento ativo.** Os scripts Python, templates e documentação estão prontos. O Gemini Gem público está em fase final de configuração.

📅 **Lançamento previsto:** primeira metade de Maio/2026.

Quando estiver no ar, este README terá o link público do Gem aqui no topo.

---

## Como vai funcionar

### Caminho 1 — Você já tem dados

1. Baixe o [template Excel](./templates/obra-template.xlsx).
2. Preencha uma linha por tarefa: contratado, escopo, entra após (IDs), datas planejadas, datas reais (quando aplicável).
3. Faça upload no [Gem](#) (link em breve).
4. A IA valida, calcula caminho crítico, gera diagrama, e devolve textos prontos para WhatsApp/e-mail.

### Caminho 2 — Começar do zero

1. Abra o Gem.
2. Diga "vamos cadastrar uma obra nova".
3. A IA conduz a conversa: nome da obra, contratados, tarefas, dependências.
4. Ao final, baixe a planilha Excel para você manter o estado.

### Caminho 3 — Ver um exemplo

1. Baixe o [exemplo completo](./exemplos/obra-exemplo-completa.xlsx) — armazém graneleiro com 14 tarefas e 6 contratados.
2. Faça upload no Gem.
3. Veja a análise completa: caminho crítico, bloqueadores, riscos, textos prontos.

---

## O que está aqui

```
ponto-de-bloqueio/
├── README.md                     ← você está aqui
├── GEM-INSTRUCTIONS.md           ← system prompt do Gemini Gem
├── LIMITES-DO-MODELO.md          ← FAQ de limitações conscientes do modelo
│
├── templates/
│   └── obra-template.xlsx        ← planilha em branco para você preencher
│
├── exemplos/
│   └── obra-exemplo-completa.xlsx ← obra real demo (Armazém Sorriso/MT, 14 tarefas)
│
├── scripts/                      ← lógica em Python (auditável, MIT)
│   ├── model.py
│   ├── validate_dag.py
│   ├── forward_pass.py
│   ├── critical_path.py
│   ├── render_mermaid.py
│   ├── render_png.py
│   ├── gen_email.py
│   ├── gen_whatsapp.py
│   ├── analyze.py                ← orquestrador CLI
│   ├── generate_template.py      ← gera o template Excel
│   ├── generate_example.py       ← gera o exemplo completo
│   └── requirements.txt
│
└── docs/
    ├── como-funciona.md          ← explicação didática do método CPM
    └── faq.md                    ← perguntas frequentes
```

---

## Como o cálculo é feito

Veja [`docs/como-funciona.md`](docs/como-funciona.md) para a explicação completa, com exemplo numérico passo a passo.

Resumo de uma linha: **forward pass + backward pass em DAG** (NetworkX) → folga total por tarefa → caminho crítico = sequência de tarefas com folga zero.

A IA do Gemini Gem **não calcula caminho crítico de cabeça** — ela executa código Python equivalente aos [scripts](./scripts/) deste repositório, em sandbox isolado.

---

## Rodando localmente (opcional, para usuários técnicos)

```bash
# Clone o repo
git clone https://github.com/Fabi-Thome/bravo-skills
cd bravo-skills/ponto-de-bloqueio

# Setup do venv
python -m venv .venv
.venv/Scripts/activate           # Windows
# source .venv/bin/activate      # Linux/Mac
pip install -r scripts/requirements.txt

# Rode contra o exemplo
python -m scripts.analyze exemplos/obra-exemplo-completa.xlsx \
    --projeto "Armazém Sorriso/MT" \
    --autor "Fabiano Thomé / BravoCP" \
    --out output/

# Veja os artefatos gerados em ./output:
#   grafo.md     ← diagrama Mermaid (cole em viewer Markdown)
#   grafo.png    ← imagem para anexar em e-mail/WhatsApp
#   whatsapp.txt ← texto pronto
#   email.txt    ← assunto + corpo
```

Se você é desenvolvedor e quer regenerar o template ou o exemplo:

```bash
python -m scripts.generate_template   # gera templates/obra-template.xlsx
python -m scripts.generate_example    # gera exemplos/obra-exemplo-completa.xlsx
```

---

## Limites do modelo

Esta versão é **deliberadamente simplificada**. Não modelamos:

- Lags variáveis (cura de concreto, intervalo entre tarefas);
- Tipos de relação além de Finish-to-Start (FS);
- Calendários (feriados, fins de semana);
- Recursos (mão-de-obra, equipamentos compartilhados);
- Datas obrigatórias / deadlines contratuais;
- Análise probabilística (PERT, Monte Carlo);
- Cronograma interno de cada contratado.

A explicação completa de cada item — incluindo o **porquê** ficou de fora e o **workaround** — está em [`LIMITES-DO-MODELO.md`](LIMITES-DO-MODELO.md).

---

## Comunidade

Existe um grupo de WhatsApp dedicado a gestão de projetos onde discutimos uso, melhorias e cases reais. Para entrar, mande mensagem direta no LinkedIn:

🔗 [linkedin.com/in/fabianothome](https://www.linkedin.com/in/fabianothome/)

---

## Licença

[MIT](../LICENSE) — você pode usar, modificar, distribuir e até comercializar livremente, mantendo o aviso de copyright.

---

*Mantido por Fabiano Thomé / [BravoCP](https://www.bravocp.com.br) — Engenharia do Proprietário.*
