import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { mockContatos, mockHistorico } from "./mock-data";
import type { Contato, HistoricoContato } from "./types";

interface ContatosContextValue {
  contatos: Contato[];
  historico: HistoricoContato[];
  updateContato: (id: number, patch: Partial<Contato>) => void;
  addContato: (contato: Omit<Contato, "id">) => void;
}

const ContatosContext = createContext<ContatosContextValue | null>(null);

/**
 * In-memory data layer shaped like the future real API (GET/POST/PATCH
 * /contatos). Swapping mocks for `fetch` calls later only touches this file.
 */
export function ContatosProvider({ children }: { children: ReactNode }) {
  const [contatos, setContatos] = useState<Contato[]>(mockContatos);
  const [historico] = useState<HistoricoContato[]>(mockHistorico);

  const value = useMemo<ContatosContextValue>(
    () => ({
      contatos,
      historico,
      updateContato: (id, patch) =>
        setContatos((prev) => prev.map((c) => (c.id === id ? { ...c, ...patch } : c))),
      addContato: (contato) =>
        setContatos((prev) => [...prev, { ...contato, id: Math.max(0, ...prev.map((c) => c.id)) + 1 }]),
    }),
    [contatos, historico],
  );

  return <ContatosContext.Provider value={value}>{children}</ContatosContext.Provider>;
}

export function useContatos() {
  const ctx = useContext(ContatosContext);
  if (!ctx) throw new Error("useContatos must be used within ContatosProvider");
  return ctx;
}
