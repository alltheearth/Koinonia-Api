import { useMemo, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { Card } from "../components/ui/Card";
import { Avatar } from "../components/ui/Avatar";
import { Select } from "../components/ui/Input";
import { StatusBadge, PrioridadeBadge } from "../components/contacts/ContactBadges";
import { ContactDrawer } from "../components/contacts/ContactDrawer";
import { useContatos } from "../lib/store";
import { formatRelative } from "../lib/utils";
import type { Contato, Prioridade, StatusContato } from "../lib/types";

const STATUS_OPTIONS: (StatusContato | "Todos")[] = ["Todos", "Ativo", "Pendente", "Inativo", "Sumiu"];
const PRIORIDADE_OPTIONS: (Prioridade | "Todas")[] = ["Todas", "Alta", "Média", "Baixa"];

export function Contacts() {
  const { contatos } = useContatos();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<(typeof STATUS_OPTIONS)[number]>("Todos");
  const [prioridade, setPrioridade] = useState<(typeof PRIORIDADE_OPTIONS)[number]>("Todas");
  const [selected, setSelected] = useState<Contato | null>(null);

  const filtered = useMemo(() => {
    return contatos
      .filter((c) => (status === "Todos" ? true : c.status === status))
      .filter((c) => (prioridade === "Todas" ? true : c.prioridade === prioridade))
      .filter((c) => c.nome.toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => a.nome.localeCompare(b.nome));
  }, [contatos, search, status, prioridade]);

  return (
    <AppShell title="Contatos" onSearch={setSearch}>
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">Contatos</h2>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              {filtered.length} de {contatos.length} contatos
            </p>
          </div>
          <div className="flex gap-2">
            <Select value={status} onChange={(e) => setStatus(e.target.value as typeof status)} className="w-36">
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s === "Todos" ? "Todos os status" : s}
                </option>
              ))}
            </Select>
            <Select
              value={prioridade}
              onChange={(e) => setPrioridade(e.target.value as typeof prioridade)}
              className="w-36"
            >
              {PRIORIDADE_OPTIONS.map((p) => (
                <option key={p} value={p}>
                  {p === "Todas" ? "Toda prioridade" : p}
                </option>
              ))}
            </Select>
          </div>
        </div>

        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-400 dark:border-zinc-800 dark:text-zinc-500">
                <tr>
                  <th className="px-4 py-2.5 font-medium">Nome</th>
                  <th className="px-4 py-2.5 font-medium">Classificação</th>
                  <th className="px-4 py-2.5 font-medium">Bairro</th>
                  <th className="px-4 py-2.5 font-medium">Última mensagem</th>
                  <th className="px-4 py-2.5 font-medium">Prioridade</th>
                  <th className="px-4 py-2.5 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {filtered.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setSelected(c)}
                    className="cursor-pointer transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-900/60"
                  >
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2.5">
                        <Avatar name={c.nome} size="sm" />
                        <span className="font-medium text-zinc-800 dark:text-zinc-100">{c.nome}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-zinc-500 dark:text-zinc-400">{c.classificacao}</td>
                    <td className="px-4 py-2.5 text-zinc-500 dark:text-zinc-400">{c.bairro}</td>
                    <td className="px-4 py-2.5 text-zinc-500 dark:text-zinc-400">
                      {formatRelative(c.ultima_mensagem)}
                    </td>
                    <td className="px-4 py-2.5">
                      <PrioridadeBadge prioridade={c.prioridade} />
                    </td>
                    <td className="px-4 py-2.5">
                      <StatusBadge status={c.status} />
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-sm text-zinc-400">
                      Nenhum contato encontrado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <ContactDrawer key={selected?.id ?? "none"} contato={selected} onClose={() => setSelected(null)} />
    </AppShell>
  );
}
