import { Link } from "react-router-dom";
import { AlertTriangle, Clock, MessageCircle, Users } from "lucide-react";
import { AppShell } from "../components/layout/AppShell";
import { StatCard } from "../components/ui/StatCard";
import { Card } from "../components/ui/Card";
import { Avatar } from "../components/ui/Avatar";
import { StatusBadge, PrioridadeBadge } from "../components/contacts/ContactBadges";
import { useContatos } from "../lib/store";
import { daysSince, formatRelative } from "../lib/utils";

export function Dashboard() {
  const { contatos } = useContatos();

  const total = contatos.length;
  const contatadosSemana = contatos.filter((c) => daysSince(c.ultima_mensagem) < 7).length;
  const prioridadeAlta = contatos.filter((c) => c.prioridade === "Alta").length;
  const semResposta = contatos.filter((c) => daysSince(c.ultima_mensagem) >= 14).length;

  const recentes = [...contatos]
    .sort((a, b) => daysSince(a.ultima_mensagem) - daysSince(b.ultima_mensagem))
    .slice(0, 6);

  const precisamAtencao = [...contatos]
    .filter((c) => c.prioridade === "Alta" || c.status === "Sumiu" || c.status === "Pendente")
    .sort((a, b) => daysSince(b.ultima_mensagem) - daysSince(a.ultima_mensagem))
    .slice(0, 6);

  return (
    <AppShell title="Dashboard">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Bom te ver por aqui 👋
          </h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Panorama dos seus contatos de WhatsApp (dados mockados).
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total de contatos" value={total} icon={Users} tone="accent" />
          <StatCard
            label="Falaram nos últimos 7 dias"
            value={contatadosSemana}
            icon={MessageCircle}
            tone="success"
          />
          <StatCard label="Prioridade alta" value={prioridadeAlta} icon={AlertTriangle} tone="warning" />
          <StatCard label="Sem resposta há 14+ dias" value={semResposta} icon={Clock} tone="danger" />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Atividade recente</h3>
              <Link to="/contatos" className="text-xs font-medium text-accent-600 hover:underline dark:text-accent-400">
                Ver todos
              </Link>
            </div>
            <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {recentes.map((c) => (
                <li key={c.id} className="flex items-center gap-3 py-2.5">
                  <Avatar name={c.nome} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-100">{c.nome}</p>
                    <p className="truncate text-xs text-zinc-400 dark:text-zinc-500">{c.participacao}</p>
                  </div>
                  <span className="shrink-0 text-xs text-zinc-400 dark:text-zinc-500">
                    {formatRelative(c.ultima_mensagem)}
                  </span>
                </li>
              ))}
            </ul>
          </Card>

          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Precisam de atenção</h3>
              <Link to="/assistente" className="text-xs font-medium text-accent-600 hover:underline dark:text-accent-400">
                Perguntar ao assistente
              </Link>
            </div>
            <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {precisamAtencao.map((c) => (
                <li key={c.id} className="flex items-center gap-3 py-2.5">
                  <Avatar name={c.nome} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-100">{c.nome}</p>
                    <p className="truncate text-xs text-zinc-400 dark:text-zinc-500">
                      {formatRelative(c.ultima_mensagem)}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5">
                    <PrioridadeBadge prioridade={c.prioridade} />
                    <StatusBadge status={c.status} />
                  </div>
                </li>
              ))}
              {precisamAtencao.length === 0 && (
                <p className="py-4 text-center text-sm text-zinc-400">Tudo em dia por aqui 🎉</p>
              )}
            </ul>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
