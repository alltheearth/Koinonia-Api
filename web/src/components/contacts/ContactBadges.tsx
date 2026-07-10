import { Badge } from "../ui/Badge";
import type { Prioridade, StatusContato } from "../../lib/types";

const statusTone = {
  Ativo: "success",
  Pendente: "warning",
  Inativo: "neutral",
  Sumiu: "danger",
} as const;

const prioridadeTone = {
  Alta: "danger",
  Média: "warning",
  Baixa: "neutral",
} as const;

export function StatusBadge({ status }: { status: StatusContato }) {
  return (
    <Badge tone={statusTone[status]} dot>
      {status}
    </Badge>
  );
}

export function PrioridadeBadge({ prioridade }: { prioridade: Prioridade }) {
  return <Badge tone={prioridadeTone[prioridade]}>{prioridade}</Badge>;
}
