# Limites do modelo — Ponto de Bloqueio

> Knowledge file anexado ao Gemini Gem. Quando o usuário pergunta sobre algo
> que não é modelado nesta versão, o Gem cita esta referência.

---

## Princípio geral

O **Ponto de Bloqueio** é uma versão deliberadamente simplificada do método CPM (Critical Path Method). Modelamos:

- Tarefa = um contratado entrando, executando algo, e saindo.
- Dependência = uma tarefa "entra após" outra(s).
- Cálculo = caminho crítico em dias corridos, propagando atrasos reais.

**Tudo que não estiver explicitamente modelado abaixo, não está modelado.** Esta lista é exaustiva.

---

## FAQ — Limitações conhecidas

### 1. Como modelo um lag de 5 dias entre uma tarefa e outra (ex: cura de concreto)?

**Não modelado diretamente.** Nesta versão, a dependência é "fim → início" sem lag.

**Workaround:** crie uma tarefa intermediária representando o lag.

```
SOU-02 → CUR-01 → TRI-01
```

Onde `CUR-01` é uma "tarefa fictícia" com:
- Contratado: `Aguardo Técnico` (ou similar)
- Escopo: `Cura do concreto`
- Duração planejada: 5 dias

**Por quê:** lags de duração variável aumentam complexidade sem aumentar valor proporcionalmente. Tarefa intermediária é explícita, auditável e resolve 100% dos casos.

---

### 2. Como modelo um relacionamento Start-to-Start (SS)? Ex: B começa quando A começa.

**Não modelado.** Apenas Finish-to-Start (FS) — "entra após terminar".

**Workaround:** se A e B começam juntos por contrato, modele-os como tendo o **mesmo predecessor** e datas de início iguais. Em obra, SS puro é raro — quase sempre há uma janela entre o início de uma e da outra.

**Por quê:** ~95% das interfaces de obra são FS. Suportar 4 tipos de relação (FS, SS, FF, SF) quadruplica complexidade sem benefício real para o público-alvo.

---

### 3. Como considero feriados, fins de semana ou intempéries no cálculo?

**Não modelado.** O cálculo é feito em **dias corridos**.

**Workaround:** ajuste a duração planejada de cada tarefa para refletir os dias úteis reais. Por exemplo, se uma tarefa "leva 10 dias úteis" e a janela tem 1 fim de semana e 1 feriado, modele como duração de 13 dias corridos.

**Por quê:** calendário introduz lógica de calendário-recurso (alguns contratados trabalham sábado, outros não), que é outro produto.

---

### 4. Como considero recursos compartilhados (ex: a mesma equipe da Triade trabalha em duas frentes ao mesmo tempo)?

**Não modelado.** Esta skill faz **CPM**, não **RCPSP** (Resource-Constrained Project Scheduling).

**Workaround:** se duas tarefas competem por uma mesma equipe, modele-as como sequenciais (uma "entra após" a outra). Você está dizendo "a equipe vai pra A primeiro, depois pra B".

**Por quê:** recursos é outro problema. Resolvê-lo bem requer outra modelagem — não cabe num MVP simples.

---

### 5. Como modelo uma data obrigatória (must-start-on, deadline contratual)?

**Parcialmente modelado.**

- Para forçar uma data mínima de início: use o campo **Entrada planejada** com a data desejada. A tarefa não começará antes dela mesmo que os predecessores terminem antes.
- Para deadlines (data máxima de fim): **não há campo dedicado**. Você precisa monitorar manualmente o desvio projetado e tomar ação se ele virar positivo (atraso).

**Por quê:** datas obrigatórias são casos especiais. A versão v1 trata o mais comum (mínimo de início) com a coluna existente.

---

### 6. Como faço análise probabilística (Monte Carlo, PERT)?

**Não modelado.** O cálculo é determinístico — uma estimativa por tarefa.

**Workaround:** rode o modelo com 3 cenários (otimista, realista, pessimista), variando as durações planejadas. Compare os 3 resultados.

**Por quê:** análise probabilística requer ferramentas dedicadas (Primavera Risk, @RISK). Para projetos pequenos/médios, o cenário determinístico pessimista é geralmente suficiente.

---

### 7. Como represento o cronograma interno do contratado?

**Não modelado por design.**

A tese desta skill é exatamente o oposto: você **não precisa** do cronograma interno. Modele apenas quando o contratado entra e quando ele sai.

**Workaround:** se você quer mais detalhe, divida o trabalho do contratado em **múltiplas tarefas** ligadas em sequência.

Por exemplo, em vez de:
- `TRI-01` Triade — Estrutura silos (45 dias)

Você pode dividir em:
- `TRI-01` Triade — Estrutura inferior silos (15 dias)
- `TRI-02` Triade — Estrutura superior silos (20 dias)
- `TRI-03` Triade — Acabamento metálico (10 dias)

Mas isso adiciona ruído. Na maioria dos casos, mantenha uma tarefa por contratado/frente.

**Por quê:** cronograma interno é responsabilidade do contratado. A interface contratual é o único ponto que afeta os outros.

---

### 8. Como modelo retrabalho ou loops?

**Não modelado.** O grafo precisa ser acíclico (DAG). Não pode haver "B entra após A; A entra após B".

**Workaround:** se há retrabalho previsível, modele como tarefas distintas:
- `TRI-01` Estrutura inicial
- `TES-01` Teste / inspeção
- `TRI-02` Correções e retrabalho (depende de TES-01)

**Por quê:** loops em CPM são uma fonte clássica de erro. Tornar explícito o retrabalho como tarefa separada é a prática profissional.

---

### 9. Como modelo uma tarefa que pode ser feita por dois contratados alternativos?

**Não modelado.** Cada tarefa tem exatamente um contratado.

**Workaround:** decida o contratado antes de cadastrar. Se a decisão muda, edite a planilha.

**Por quê:** análise de cenários alternativos com diferentes contratados é outro problema. Para casos específicos, faça duas planilhas (uma por contratado) e compare os resultados.

---

### 10. Como funcionam as datas reais quando o contratado ainda não terminou?

- **Apenas Entrada real preenchida (Saída real vazia):** a tarefa está em andamento. O cálculo usa entrada real como ponto de partida e projeta saída = entrada real + duração planejada.
- **Entrada e Saída real preenchidas:** a tarefa terminou. O cálculo usa as datas reais.
- **Nenhuma preenchida:** a tarefa ainda não começou. O cálculo usa as datas planejadas, ajustadas pelos predecessores.

---

### 11. Como removo uma tarefa que tem dependentes?

**Cuidado.** Se você remover `TRI-01` mas `SAU-01` tem `Entra após = TRI-01`, a coluna fica inválida.

**Procedimento:**
1. Antes de remover, identifique quem depende dela: liste tarefas que têm `TRI-01` em "Entra após".
2. Decida: o que essas tarefas vão depender agora? Algum dos predecessores de `TRI-01`? Outra tarefa? Nada (raiz)?
3. Atualize as dependentes ANTES de remover.
4. Remova `TRI-01`.

O Gem alerta sobre isso. Não remova "no escuro".

---

### 12. Por que minha tarefa apareceu como "concluída" se ela ainda não terminou?

A tarefa é tratada como **concluída** se a coluna **Saída real** está preenchida com qualquer data. O Gem (e o cálculo) confiam nesse dado.

Se você preencheu por engano, apague o valor da célula e refaça a análise.

---

### 13. Posso ter mais de uma obra na mesma planilha?

**Não.** Uma planilha = uma obra.

**Por quê:** misturar obras na mesma análise compromete o cálculo de caminho crítico. Cada obra tem seu próprio prazo final e seus próprios bloqueadores.

Para gerenciar várias obras, mantenha planilhas separadas e converse com o Gem em janelas separadas (uma conversa por obra).

---

### 14. Como exporto a análise para um relatório PDF?

**Não modelado nesta versão.** A skill devolve:

- Texto formatado (resumo, e-mail, WhatsApp) — você cola onde precisar.
- Imagem PNG do grafo — você anexa em Word/PowerPoint.
- Diagrama Mermaid — renderiza no GitHub e em Markdown viewers.

Para PDF, copie os textos para um Word ou similar e exporte como PDF de lá.

---

### 15. O modelo considera curva S de avanço físico?

**Não.** Esta skill foca em **interfaces** (entrada/saída), não em **avanço físico** (% completo de cada tarefa).

A BravoCP tem outras ferramentas/serviços para curva S. Para o que esta skill faz — gerenciar a interface entre contratados — avanço físico não é necessário.

---

## Quando NÃO usar esta skill

Esta skill é boa quando:
- Há múltiplos contratados em obra simultaneamente.
- A coordenação de interface (quem entra quando) é o gargalo.
- Você quer respostas rápidas, não análise sofisticada.

**Esta skill NÃO é boa para:**
- Projetos com poucos contratados (1-2). O grafo fica trivial e Excel resolve.
- Projetos onde o desafio é avanço físico, não interface.
- Análises de risco probabilísticas.
- Otimização de recursos ou nivelamento.
- Cronogramas com mais de 50 tarefas (o modelo aceita, mas a UX no chat fica pesada).

Para esses casos, ferramentas dedicadas (Primavera, MS Project, RiskyProject) são a escolha certa — ou a consultoria da [BravoCP](https://www.bravocp.com.br).

---

*Este arquivo é mantido em [github.com/Fabi-Thome/bravo-skills](https://github.com/Fabi-Thome/bravo-skills/blob/main/ponto-de-bloqueio/LIMITES-DO-MODELO.md). Sugestões de FAQ adicional via issue ou pelo grupo de WhatsApp.*
