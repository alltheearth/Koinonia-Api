# Koinonia — Painel de Contatos

Frontend do Koinonia: dashboard de acompanhamento de contatos de WhatsApp e um
assistente que responde perguntas sobre a base de contatos. Hoje roda 100%
sobre dados mockados (`src/lib/mock-data.ts`), com a mesma forma dos dados da
API (`contatos` / `historico_contatos`) para facilitar a troca por chamadas
reais depois.

## Rodando localmente

```bash
npm install
npm run dev
```

## Stack

- React + TypeScript + Vite
- TailwindCSS v4
- react-router-dom

## Estrutura

- `src/lib/types.ts` — tipos `Contato` e `HistoricoContato`, espelhando o schema da API.
- `src/lib/mock-data.ts` — dataset mockado.
- `src/lib/store.tsx` — camada de dados em memória (`useContatos`), com a mesma assinatura que uma futura API real teria.
- `src/lib/assistant.ts` — motor de respostas do assistente (baseado em regras sobre os mocks, sem LLM).
- `src/pages/` — Dashboard, Contatos, Histórico, Assistente.
- `src/components/` — layout (Sidebar/Topbar/AppShell), UI base (Button/Card/Badge/...), e componentes de domínio (contatos/assistente).

## Próximos passos sugeridos

Substituir `src/lib/store.tsx` por chamadas `fetch` para a API real
(`/contatos`, `/history`) e o corpo de `answerQuestion` em
`src/lib/assistant.ts` por uma chamada a um modelo de linguagem real.
