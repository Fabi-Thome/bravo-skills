# Como o Ponto de Bloqueio calcula o caminho crítico

> Este documento é a explicação didática do método. Serve para quem quer
> entender o que está por baixo do Gemini Gem antes de confiar nele.
>
> Se você só quer usar a skill, basta abrir o Gem e conversar — você não precisa ler isto.
> Se quer entender, leia. É curto.

---

## O modelo em uma frase

> Cada contratado é um nó. As setas dizem "este só pode entrar quando aquele sair". O algoritmo calcula a data realista de fim da obra e mostra qual sequência de tarefas determina esse prazo.

Tecnicamente: um **DAG** (Directed Acyclic Graph) onde rodamos um **CPM simplificado** sobre as datas de entrada/saída.

---

## 1. O grafo da obra

Cada tarefa é um nó. Cada dependência é uma seta:

```
TRI-01 ──→ SAU-01 ──→ ELE-01
   │
   └─────→ SAU-02
```

- **TRI-01** é raiz (não depende de ninguém).
- **SAU-01** entra após TRI-01 sair.
- **ELE-01** entra após SAU-01 sair.
- **SAU-02** também entra após TRI-01, mas tem outro destino (não bloqueia ELE-01).

**Regra invariante:** o grafo precisa ser **acíclico**. Não pode existir "TRI-01 depende de SAU-01, e SAU-01 depende de TRI-01". O Gem rejeita antes de calcular qualquer coisa.

---

## 2. Forward pass — quando cada tarefa realmente vai começar e terminar

A pergunta é: **dadas as dependências e o que já foi realizado, quando cada tarefa efetivamente entra e sai?**

A regra:

> **Entrada projetada de uma tarefa = a maior data entre (a) sua entrada planejada e (b) a saída projetada do predecessor mais lento.**
>
> **Saída projetada = entrada projetada + duração planejada original.**

Onde **duração planejada = saída planejada − entrada planejada**, preservada ao longo do projeto.

Há três casos especiais com dados reais:

| Situação | Regra |
|---|---|
| Tarefa tem **entrada real** preenchida | Usa entrada real |
| Tarefa tem **saída real** preenchida | Usa saída real (a tarefa terminou) |
| Tarefa **sem dados reais** | Projeta usando a regra padrão |

### Exemplo numérico

Considere 3 tarefas em sequência:

| ID | Entrada planejada | Saída planejada | Entra após | Entrada real | Saída real |
|---|---|---|---|---|---|
| TRI-01 | 01/04 | 30/04 | — | 03/04 | 05/05 |
| SAU-01 | 01/05 | 30/05 | TRI-01 | — | — |
| ELE-01 | 01/06 | 15/06 | SAU-01 | — | — |

**Cálculo:**

- **TRI-01:** já tem saída real = **05/05** (atrasou 5 dias). Pronto.
- **SAU-01:**
  - Entrada planejada: 01/05.
  - Saída projetada do predecessor (TRI-01): 05/05.
  - Entrada projetada = max(01/05, 05/05) = **05/05**.
  - Duração planejada = 30/05 − 01/05 = 29 dias.
  - Saída projetada = 05/05 + 29 dias = **03/06**.
- **ELE-01:**
  - Entrada planejada: 01/06.
  - Saída projetada do predecessor (SAU-01): 03/06.
  - Entrada projetada = max(01/06, 03/06) = **03/06**.
  - Duração planejada = 15/06 − 01/06 = 14 dias.
  - Saída projetada = 03/06 + 14 dias = **17/06**.

**Resultado:** o atraso de 5 dias da Triade propagou. SAU-01 atrasa 4 dias (não os 5 cheios — porque tinha 1 dia de gordura entre a saída de TRI-01 e a entrada planejada de SAU-01). ELE-01 atrasa 2 dias.

A obra inteira atrasou 2 dias (15/06 → 17/06).

---

## 3. Backward pass — até quando cada tarefa pode atrasar sem mover o prazo

A pergunta inversa: **considerando a data atual de término da obra, qual o último momento em que cada tarefa pode terminar sem mover esse prazo?**

A regra é o espelho:

> **Saída-limite de uma tarefa = a menor entrada-limite de seus sucessores.**
>
> **Entrada-limite = saída-limite − duração planejada.**

Para a(s) tarefa(s) sem sucessor (final do grafo), saída-limite = saída projetada (não pode atrasar mais).

### Continuando o exemplo

Saída projetada da obra = **17/06** (final = ELE-01).

- **ELE-01** (final): saída-limite = 17/06; entrada-limite = 17/06 − 14 = 03/06.
- **SAU-01**: saída-limite = entrada-limite de ELE-01 = 03/06; entrada-limite = 03/06 − 29 = 05/05.
- **TRI-01**: saída-limite = entrada-limite de SAU-01 = 05/05; entrada-limite = 05/05 − 29 = 06/04.

---

## 4. Folga (Total Float) — quanto cada tarefa pode atrasar

> **Folga = Saída-limite − Saída projetada** (em dias)

| ID | Saída projetada | Saída-limite | **Folga** |
|---|---|---|---|
| TRI-01 | 05/05 | 05/05 | **0 dias** |
| SAU-01 | 03/06 | 03/06 | **0 dias** |
| ELE-01 | 17/06 | 17/06 | **0 dias** |

Todas as três têm folga zero. **Estão no caminho crítico.**

A interpretação prática:

| Folga | Significado |
|---|---|
| **= 0** | **Caminho crítico.** Qualquer dia de atraso aqui atrasa a obra inteira. |
| **> 0** | A tarefa tem gordura. Pode escorregar X dias sem mover o prazo final. |
| **< 0** | **Vermelho profundo.** A tarefa já está numa rota que não fecha o prazo. Precisa de ação corretiva. |

---

## 5. Caminho crítico

> **Caminho Crítico = a sequência de tarefas, do início ao fim do grafo, em que todas têm folga zero.**

Equivalentemente, é o **caminho mais longo (em duração) no grafo**. Qualquer atraso em qualquer tarefa do caminho crítico atrasa a obra na mesma proporção.

**Por que isso importa:**

> "Eu posso ter 50 tarefas. Mas só ~10–15 estão no caminho crítico. Toda atenção diária deveria estar nessas 10–15. Se uma delas atrasa, a obra atrasa. Se uma das outras 35 atrasa, eu tenho gordura para absorver."

Esse é o ponto. O caminho crítico transforma uma planilha de 50 linhas em uma lista curta de 10–15 que merece o foco do planejador.

---

## 6. As 7 métricas que o Gem reporta

Em cada análise, o Gem devolve estas métricas. Cada uma responde uma pergunta operacional clara:

### 6.1 Data projetada de término
*Considerando o que já aconteceu, quando a obra termina?* Comparada com a planejada original, dá o **slip** (atraso acumulado em dias).

### 6.2 Folga total por tarefa
*Quem está apertado, quem tem gordura?* Tarefas com folga ≤ 5 dias merecem atenção. Folga negativa = vermelho.

### 6.3 Caminho crítico atual
*Quais 10-15 tarefas merecem foco hoje?* Esta lista muda à medida que a obra evolui — uma tarefa que tinha folga pode entrar no caminho crítico se outra acelerar.

### 6.4 Slip por tarefa
*Quem atrasou e quanto?* Para cada tarefa: (saída projetada − saída planejada).

### 6.5 Maior bloqueador
*Qual contratado, se atrasar, derruba mais coisa?* Conta quantas tarefas downstream dependem de cada um. Quem aparece em mais tarefas críticas é o **fator de risco número um**.

### 6.6 Convergências críticas
*Quais tarefas têm 2+ predecessores no caminho crítico?* São pontos de risco máximo: basta um deles deslizar para a tarefa atrasar. Se 3 contratados precisam terminar antes do 4º começar, e os 3 estão críticos, a chance de um deslizar é alta.

### 6.7 Tarefas em risco
*Quais tarefas com folga pequena ainda não começaram?* São candidatas naturais ao caminho crítico no próximo ciclo, especialmente se o ritmo da obra estiver desacelerando.

---

## 7. O que estamos modelando — em uma frase

> "Quando você tem 15 contratados em obra, você não precisa do cronograma de cada um. Você precisa saber **quando cada um entra, quando cada um sai, e quem depende de quem.** Com isso, o caminho crítico se calcula sozinho — e você passa a focar nos 3 ou 4 contratados que realmente importam."

---

## 8. O que não estamos modelando

Veja [`LIMITES-DO-MODELO.md`](../LIMITES-DO-MODELO.md) para a lista completa: lags variáveis, calendário, recursos, datas obrigatórias, probabilidades. Cada item tem o **porquê** e o **workaround**.

---

## 9. A lógica está em código aberto

Tudo isto está implementado em Python na pasta [`scripts/`](../scripts/), sob licença MIT.

| Arquivo | O que faz |
|---|---|
| [`model.py`](../scripts/model.py) | `Task` dataclass + leitura do Excel + construção do grafo |
| [`validate_dag.py`](../scripts/validate_dag.py) | Validação do grafo (acíclico, IDs únicos, predecessores válidos) |
| [`forward_pass.py`](../scripts/forward_pass.py) | Cálculo de entrada/saída projetadas |
| [`critical_path.py`](../scripts/critical_path.py) | Backward pass, folga, caminho crítico, bloqueadores |
| [`render_mermaid.py`](../scripts/render_mermaid.py) | Diagrama Mermaid |
| [`render_png.py`](../scripts/render_png.py) | Imagem PNG via matplotlib |
| [`gen_email.py`](../scripts/gen_email.py) | Texto de e-mail formal |
| [`gen_whatsapp.py`](../scripts/gen_whatsapp.py) | Texto de WhatsApp curto |
| [`analyze.py`](../scripts/analyze.py) | Pipeline orquestrador (CLI) |

Você pode rodar localmente sem o Gem, se quiser auditar o cálculo:

```bash
cd ponto-de-bloqueio/
python -m venv .venv
.venv/Scripts/activate           # Windows; no Linux/Mac: source .venv/bin/activate
pip install -r scripts/requirements.txt
python -m scripts.analyze exemplos/obra-exemplo-completa.xlsx --projeto "Minha obra"
```

---

*Mantido em [github.com/Fabi-Thome/bravo-skills](https://github.com/Fabi-Thome/bravo-skills/blob/main/ponto-de-bloqueio/docs/como-funciona.md).*
