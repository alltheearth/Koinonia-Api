import { useMemo, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { Card } from "../components/ui/Card";
import { Avatar } from "../components/ui/Avatar";
import { StatusBadge } from "../components/contacts/ContactBadges";
import { useContatos } from "../lib/store";
import { formatDate } from "../lib/utils";

export function HistoryPage() {
  const { contatos, historico } = useContatos();
  const contatoById = useMemo(() => new Map(contatos.map((c) => [c.id, c])), [contatos]);

  const semanas = useMemo(() => {
    const set = new Set(historico.map((h) => h.semana_inicio));
    return Array.from(set).sort((a, b) => (a < b ? 1 : -1));
  }, [historico]);

  const [semana, setSemana] = useState(semanas[0]);

  const linhas = historico
    .filter((h) => h.semana_inicio === semana)
    .filter((h) => contatoById.has(h.contato_id));

  return (
    <AppShell title="Histórico">
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Histórico semanal
            </h2>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              Snapshot de status por semana (dados mockados)
            </p>
          </div>
          <div className="flex gap-1.5 overflow-x-auto">
            {semanas.map((s) => (
              <button
                key={s}
                onClick={() => setSemana(s)}
                className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  s === semana
                    ? "bg-accent-600 text-white"
                    : "bg-white text-zinc-600 border border-zinc-200 hover:bg-zinc-50 dark:bg-zinc-900 dark:text-zinc-300 dark:border-zinc-800"
                }`}
              >
                {formatDate(s)}
              </button>
            ))}
          </div>
        </div>

        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-400 dark:border-zinc-800 dark:text-zinc-500">
                <tr>
                  <th className="px-4 py-2.5 font-medium">Contato</th>
                  <th className="px-4 py-2.5 font-medium">Última mensagem</th>
                  <th className="px-4 py-2.5 font-medium">Status</th>
                  <th className="px-4 py-2.5 font-medium">Observações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {linhas.map((h) => {
                  const c = contatoById.get(h.contato_id)!;
                  return (
                    <tr key={h.id}>
                      <td className="px-4 py-2.5">
                        <div className="flex items-center gap-2.5">
                          <Avatar name={c.nome} size="sm" />
                          <span className="font-medium text-zinc-800 dark:text-zinc-100">{c.nome}</span>
                        </div>
                      </td>
                      <td className="px-4 py-2.5 text-zinc-500 dark:text-zinc-400">
                        {h.ultima_mensagem ? formatDate(h.ultima_mensagem) : "—"}
                      </td>
                      <td className="px-4 py-2.5">{h.status ? <StatusBadge status={h.status} /> : "—"}</td>
                      <td className="max-w-xs truncate px-4 py-2.5 text-zinc-500 dark:text-zinc-400">
                        {h.observacoes || "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
