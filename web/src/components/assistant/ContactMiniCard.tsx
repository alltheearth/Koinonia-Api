import { Avatar } from "../ui/Avatar";
import { StatusBadge, PrioridadeBadge } from "../contacts/ContactBadges";
import { formatRelative } from "../../lib/utils";
import type { Contato } from "../../lib/types";

export function ContactMiniCard({ contato, onClick }: { contato: Contato; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-2.5 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-left transition-colors hover:border-accent-300 hover:bg-accent-50/50 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-accent-700 dark:hover:bg-accent-500/5"
    >
      <Avatar name={contato.nome} size="sm" />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-100">{contato.nome}</p>
        <p className="truncate text-xs text-zinc-400 dark:text-zinc-500">
          {formatRelative(contato.ultima_mensagem)} · {contato.bairro}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        <PrioridadeBadge prioridade={contato.prioridade} />
        <StatusBadge status={contato.status} />
      </div>
    </button>
  );
}
