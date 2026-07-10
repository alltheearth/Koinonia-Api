import { useState } from "react";
import { Phone, AtSign, MapPin, Cake } from "lucide-react";
import { Drawer } from "../ui/Drawer";
import { Avatar } from "../ui/Avatar";
import { Button } from "../ui/Button";
import { Select, Textarea } from "../ui/Input";
import { StatusBadge, PrioridadeBadge } from "./ContactBadges";
import { useContatos } from "../../lib/store";
import { formatDate, formatRelative } from "../../lib/utils";
import type { Contato, Prioridade, StatusContato } from "../../lib/types";

export function ContactDrawer({ contato, onClose }: { contato: Contato | null; onClose: () => void }) {
  const { updateContato, historico } = useContatos();
  const [status, setStatus] = useState<StatusContato>(contato?.status ?? "Ativo");
  const [prioridade, setPrioridade] = useState<Prioridade>(contato?.prioridade ?? "Média");
  const [observacoes, setObservacoes] = useState(contato?.observacoes ?? "");

  const contatoHistorico = contato
    ? historico.filter((h) => h.contato_id === contato.id).sort((a, b) => (a.semana_inicio < b.semana_inicio ? 1 : -1))
    : [];

  function handleSave() {
    if (!contato) return;
    updateContato(contato.id, { status, prioridade, observacoes });
    onClose();
  }

  return (
    <Drawer open={!!contato} onClose={onClose} title="Detalhes do contato">
      {contato && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <Avatar name={contato.nome} size="lg" />
            <div>
              <p className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{contato.nome}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                {contato.classificacao} · {contato.faixa_etaria}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5">
            <StatusBadge status={contato.status} />
            <PrioridadeBadge prioridade={contato.prioridade} />
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-300">
              <Phone className="h-3.5 w-3.5 text-zinc-400" /> {contato.telefone}
            </div>
            {contato.rede_social && (
              <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-300">
                <AtSign className="h-3.5 w-3.5 text-zinc-400" /> {contato.rede_social}
              </div>
            )}
            <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-300">
              <MapPin className="h-3.5 w-3.5 text-zinc-400" /> {contato.bairro}
            </div>
            <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-300">
              <Cake className="h-3.5 w-3.5 text-zinc-400" /> {formatDate(contato.aniversario)}
            </div>
          </div>

          <div className="rounded-lg bg-zinc-50 p-3 text-sm dark:bg-zinc-800/50">
            <p className="text-zinc-500 dark:text-zinc-400">Participação</p>
            <p className="mt-0.5 font-medium text-zinc-800 dark:text-zinc-100">{contato.participacao}</p>
            <p className="mt-2 text-zinc-500 dark:text-zinc-400">Envolvimento</p>
            <p className="mt-0.5 font-medium text-zinc-800 dark:text-zinc-100">{contato.envolvimento}</p>
            <p className="mt-2 text-zinc-500 dark:text-zinc-400">Última mensagem</p>
            <p className="mt-0.5 font-medium text-zinc-800 dark:text-zinc-100">
              {formatRelative(contato.ultima_mensagem)} ({formatDate(contato.ultima_mensagem)})
            </p>
          </div>

          <div className="space-y-3 border-t border-zinc-200 pt-4 dark:border-zinc-800">
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Atualizar acompanhamento</p>

            <label className="block space-y-1">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Status</span>
              <Select value={status} onChange={(e) => setStatus(e.target.value as StatusContato)}>
                <option>Ativo</option>
                <option>Pendente</option>
                <option>Inativo</option>
                <option>Sumiu</option>
              </Select>
            </label>

            <label className="block space-y-1">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Prioridade</span>
              <Select value={prioridade} onChange={(e) => setPrioridade(e.target.value as Prioridade)}>
                <option>Alta</option>
                <option>Média</option>
                <option>Baixa</option>
              </Select>
            </label>

            <label className="block space-y-1">
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Observações</span>
              <Textarea rows={3} value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />
            </label>

            <Button variant="primary" className="w-full" onClick={handleSave}>
              Salvar alterações
            </Button>
          </div>

          {contatoHistorico.length > 0 && (
            <div className="space-y-2 border-t border-zinc-200 pt-4 dark:border-zinc-800">
              <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Histórico semanal</p>
              <ul className="space-y-2">
                {contatoHistorico.map((h) => (
                  <li key={h.id} className="flex items-center justify-between rounded-lg bg-zinc-50 px-3 py-2 text-xs dark:bg-zinc-800/50">
                    <span className="text-zinc-500 dark:text-zinc-400">Semana de {formatDate(h.semana_inicio)}</span>
                    <span className="font-medium text-zinc-700 dark:text-zinc-200">{h.status ?? "—"}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Drawer>
  );
}
