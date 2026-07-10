export type FaixaEtaria = "Criança" | "Adolescente" | "18-25" | "26-35" | "36-45" | "46-60" | "60+";

export type Classificacao = "Membro" | "Visitante" | "Novo Convertido" | "Líder" | "Congregado";

export type Envolvimento = "Alto" | "Médio" | "Baixo" | "Nenhum";

export type Prioridade = "Alta" | "Média" | "Baixa";

export type StatusContato = "Ativo" | "Pendente" | "Inativo" | "Sumiu";

export interface Contato {
  id: number;
  nome: string;
  telefone: string;
  foto?: string;
  faixa_etaria: FaixaEtaria;
  classificacao: Classificacao;
  envolvimento: Envolvimento;
  participacao: string;
  aniversario: string;
  rede_social?: string;
  bairro: string;
  prioridade: Prioridade;
  ultima_mensagem: string;
  status: StatusContato;
  observacoes: string;
}

export interface HistoricoContato {
  id: number;
  contato_id: number;
  semana_inicio: string;
  ultima_mensagem: string | null;
  status: StatusContato | null;
  prioridade: Prioridade | null;
  observacoes: string | null;
}
