# FAQ — Ponto de Bloqueio

Perguntas frequentes para quem chegou aqui pelo LinkedIn ou pela busca.

---

## O que é isto?

O **Ponto de Bloqueio** é um assistente conversacional que ajuda planejadores de obra a mapear interfaces entre contratados e identificar o caminho crítico, sem precisar consolidar cronogramas.

A ideia central: você não precisa do cronograma interno de cada contratado. Você precisa saber **quando cada um entra**, **quando cada um sai**, e **quem depende de quem**. Com isso, o algoritmo calcula o caminho crítico e mostra onde está o bloqueio.

---

## Para quem foi feito?

- Planejadores e gerentes de obra que coordenam múltiplos contratados.
- Engenheiros de projetos de capital (silos, frigoríficos, esmagadoras, terminais portuários, fábricas).
- Profissionais que querem uma ferramenta leve para apoiar a rotina semanal de status.

Não é otimizado para projetos com 1-2 contratados (Excel resolve) nem para projetos com 50+ tarefas (a UX no chat fica pesada).

---

## Quanto custa?

**Grátis.** Você usa um Gemini Gem público — gratuito até o limite diário de mensagens da sua conta Google.

A skill é mantida pela [BravoCP](https://www.bravocp.com.br) como contribuição ao mercado de gestão de projetos. Não há plano pago, plano premium, paywall ou pegadinha.

---

## Como começar?

1. Abra o link do Gem no Gemini (vai estar publicado neste repositório quando o Gem estiver disponível).
2. Faça login com sua conta Google.
3. Comece a conversa. O Gem te conduz.

Caminhos típicos:
- **Você já tem dados:** baixe [o template Excel](../templates/obra-template.xlsx), preencha, faça upload no Gem.
- **Quer começar do zero:** diga "vamos cadastrar uma obra nova" e responda as perguntas.
- **Quer ver um exemplo:** baixe o [exemplo completo](../exemplos/obra-exemplo-completa.xlsx) e suba no Gem.

---

## Preciso instalar alguma coisa?

**Não.** Tudo roda no Gemini, no servidor do Google.

Se quiser auditar a lógica ou rodar localmente (opcional, para usuários técnicos), a [pasta scripts/](../scripts/) tem os scripts Python equivalentes.

---

## Meus dados ficam onde?

- **No seu computador** — você mantém a planilha Excel.
- **Na sua conversa do Gemini** — durante a sessão. As políticas de privacidade do Google se aplicam.
- **Não temos servidor.** A BravoCP não armazena nada da sua obra. Não há cadastro, não há backend.

A planilha é a fonte da verdade. Você decide com quem compartilhar.

---

## Posso usar em obras confidenciais?

Tecnicamente sim, mas **avalie a política de privacidade do Google** para o Gemini antes de subir dados sensíveis. A BravoCP recomenda anonimizar nomes de contratados e clientes se houver NDA em vigor.

---

## E se eu quiser usar com ChatGPT em vez de Gemini?

Atualmente o Ponto de Bloqueio é distribuído como **Gemini Gem**. Os scripts Python no repositório funcionam em qualquer ambiente — se você usa ChatGPT Plus com Code Interpreter, pode adaptar as instruções de [`GEM-INSTRUCTIONS.md`](../GEM-INSTRUCTIONS.md) para um GPT customizado.

Versão para Claude Code (skill nativa) está no roadmap.

---

## Como eu reporto um bug ou sugiro melhoria?

Três formas:

1. Abra uma **issue** no GitHub: [github.com/Fabi-Thome/bravo-skills/issues](https://github.com/Fabi-Thome/bravo-skills/issues)
2. Mande mensagem direta no LinkedIn: [linkedin.com/in/fabianothome](https://www.linkedin.com/in/fabianothome/)
3. Entre na **comunidade WhatsApp** (link via LinkedIn).

Casos reais ajudam mais do que sugestões abstratas. Conte o que tentou, o que esperava e o que aconteceu.

---

## Posso contribuir com código?

Sim. Veja [CONTRIBUTING.md](../../CONTRIBUTING.md) na raiz do repositório. Para mudanças não-triviais, abra uma issue antes para conversarmos.

---

## Por que "Ponto de Bloqueio"?

Porque o produto mapeia exatamente isso: os pontos onde um contratado bloqueia o trabalho de outro. É o fator mais crítico de coordenação em obras com muitos fornecedores — e quase nunca é tratado de forma sistemática.

---

## Quem fez isto?

[Fabiano Thomé](https://www.linkedin.com/in/fabianothome/) — sócio fundador da [BravoCP](https://www.bravocp.com.br/), uma consultoria de Engenharia do Proprietário focada em projetos de capital no agronegócio brasileiro.

O Ponto de Bloqueio é o primeiro de uma família planejada de **Bravo Skills** — pequenas ferramentas que codificam métodos de gestão de projetos em IA.

---

## Por que grátis?

Construir autoridade no tema "gestão de interfaces em obras" é mais valioso do que cobrar pelo software. Cases simples são resolvidos pela skill. Cases complexos voltam como projeto da BravoCP.

E porque o conhecimento por trás da skill é, em última análise, repetido — codificá-lo em IA e distribuir ajuda mais gente do que cobrar uma licença.

---

## Como o caminho crítico é calculado?

Veja [como-funciona.md](como-funciona.md) — explicação didática completa, com exemplos numéricos.

---

## Quais são os limites do modelo?

Veja [LIMITES-DO-MODELO.md](../LIMITES-DO-MODELO.md) — lista completa do que NÃO é modelado e por quê.

---

*FAQ atualizado em [github.com/Fabi-Thome/bravo-skills](https://github.com/Fabi-Thome/bravo-skills/blob/main/ponto-de-bloqueio/docs/faq.md). Sugira novas perguntas via issue.*
