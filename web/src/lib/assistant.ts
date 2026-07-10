import type { Contato } from "./types";
import { daysSince, formatRelative } from "./utils";

export interface AssistantAnswer {
  text: string;
  contatos: Contato[];
}

const norm = (s: string) =>
  s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

function upcomingBirthdays(contatos: Contato[], withinDays = 30): Contato[] {
  const today = new Date();
  return contatos
    .filter((c) => {
      const bday = new Date(c.aniversario);
      const next = new Date(today.getFullYear(), bday.getMonth(), bday.getDate());
      if (next < today) next.setFullYear(today.getFullYear() + 1);
      const diff = (next.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
      return diff <= withinDays;
    })
    .sort((a, b) => new Date(a.aniversario).getMonth() - new Date(b.aniversario).getMonth());
}

/**
 * Rule-based "copilot" over the mocked contact list. Stands in for a real
 * LLM/API call later — same input/output shape, so wiring a real backend
 * only means replacing this function's body.
 */
export function answerQuestion(rawQuery: string, contatos: Contato[]): AssistantAnswer {
  const q = norm(rawQuery.trim());

  const diasMatch = q.match(/(\d+)\s*dias?/);
  const semanasMatch = q.match(/(\d+)\s*semanas?/);

  if (diasMatch || semanasMatch) {
    const threshold = diasMatch ? Number(diasMatch[1]) : Number(semanasMatch![1]) * 7;
    const found = contatos
      .filter((c) => daysSince(c.ultima_mensagem) >= threshold)
      .sort((a, b) => daysSince(b.ultima_mensagem) - daysSince(a.ultima_mensagem));
    return {
      text: found.length
        ? `${found.length} contato(s) sem mensagem há pelo menos ${threshold} dias:`
        : `Ninguém está sem mensagem há ${threshold} dias ou mais. Tudo em dia!`,
      contatos: found,
    };
  }

  if (/sumi|sumin|nao respond|nao fala|desaparec/.test(q)) {
    const found = contatos
      .filter((c) => c.status === "Sumiu")
      .sort((a, b) => daysSince(b.ultima_mensagem) - daysSince(a.ultima_mensagem));
    return {
      text: found.length
        ? `${found.length} pessoa(s) marcadas como "Sumiu". Recomendo uma ligação ao invés de mensagem:`
        : "Ninguém está marcado como sumido agora. 🎉",
      contatos: found,
    };
  }

  if (/prioridade alta|urgente|urgencia/.test(q)) {
    const found = contatos.filter((c) => c.prioridade === "Alta");
    return {
      text: found.length
        ? `${found.length} contato(s) com prioridade alta:`
        : "Nenhum contato com prioridade alta no momento.",
      contatos: found,
    };
  }

  if (/anivers/.test(q)) {
    const found = upcomingBirthdays(contatos);
    return {
      text: found.length
        ? `${found.length} aniversariante(s) nos próximos 30 dias:`
        : "Ninguém faz aniversário nos próximos 30 dias.",
      contatos: found,
    };
  }

  if (/novo convertido|novos convertidos/.test(q)) {
    const found = contatos.filter((c) => c.classificacao === "Novo Convertido");
    return { text: `${found.length} novo(s) convertido(s) na base:`, contatos: found };
  }

  if (/lider|lideres/.test(q)) {
    const found = contatos.filter((c) => c.classificacao === "Líder");
    return { text: `${found.length} líder(es) cadastrados:`, contatos: found };
  }

  if (/pendente/.test(q)) {
    const found = contatos.filter((c) => c.status === "Pendente");
    return { text: `${found.length} contato(s) com follow-up pendente:`, contatos: found };
  }

  if (/inativo/.test(q)) {
    const found = contatos.filter((c) => c.status === "Inativo");
    return { text: `${found.length} contato(s) inativo(s):`, contatos: found };
  }

  if (/ativo/.test(q)) {
    const found = contatos.filter((c) => c.status === "Ativo");
    return { text: `${found.length} contato(s) ativos:`, contatos: found };
  }

  if (/resumo|visao geral|panorama|como estamos/.test(q)) {
    const sumiu = contatos.filter((c) => c.status === "Sumiu").length;
    const pendente = contatos.filter((c) => c.status === "Pendente").length;
    const altaPrioridade = contatos.filter((c) => c.prioridade === "Alta").length;
    const semContatoSemana = contatos.filter((c) => daysSince(c.ultima_mensagem) >= 7).length;
    return {
      text:
        `Resumo de ${contatos.length} contatos: ${sumiu} sumiram, ${pendente} com follow-up pendente, ` +
        `${altaPrioridade} com prioridade alta, e ${semContatoSemana} sem mensagem há 7+ dias. ` +
        `Sugiro começar pelos de prioridade alta que sumiram.`,
      contatos: contatos
        .filter((c) => c.status === "Sumiu" || c.prioridade === "Alta")
        .sort((a, b) => daysSince(b.ultima_mensagem) - daysSince(a.ultima_mensagem))
        .slice(0, 6),
    };
  }

  // fallback: try to match by name
  const byName = contatos.filter((c) => norm(c.nome).includes(q) && q.length > 2);
  if (byName.length) {
    return {
      text: `Encontrei ${byName.length} contato(s) chamados "${rawQuery}":`,
      contatos: byName,
    };
  }

  return {
    text:
      'Não entendi bem 🤔. Tente algo como "quem sumiu?", "prioridades altas", ' +
      '"aniversariantes do mês", "quem não fala há 2 semanas?" ou "resumo da semana".',
    contatos: [],
  };
}

export const suggestedPrompts = [
  "Quem sumiu?",
  "Prioridades altas",
  "Aniversariantes do mês",
  "Resumo da semana",
  "Quem não fala há 2 semanas?",
];

export { formatRelative };
