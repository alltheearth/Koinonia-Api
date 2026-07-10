import { useState, useRef, useEffect } from "react";
import { Sparkles, Send } from "lucide-react";
import { AppShell } from "../components/layout/AppShell";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { ContactMiniCard } from "../components/assistant/ContactMiniCard";
import { ContactDrawer } from "../components/contacts/ContactDrawer";
import { useContatos } from "../lib/store";
import { answerQuestion, suggestedPrompts } from "../lib/assistant";
import type { Contato } from "../lib/types";

interface Message {
  id: number;
  role: "user" | "assistant";
  text: string;
  contatos?: Contato[];
}

export function Assistant() {
  const { contatos } = useContatos();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: "assistant",
      text:
        "Oi! Sou seu copiloto de acompanhamento de contatos do WhatsApp. Pergunte algo como " +
        '"quem sumiu?" ou "resumo da semana" — hoje respondo com base nos dados mockados.',
    },
  ]);
  const [input, setInput] = useState("");
  const [selected, setSelected] = useState<Contato | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function ask(question: string) {
    const q = question.trim();
    if (!q) return;
    const answer = answerQuestion(q, contatos);
    setMessages((prev) => [
      ...prev,
      { id: prev.length, role: "user", text: q },
      { id: prev.length + 1, role: "assistant", text: answer.text, contatos: answer.contatos },
    ]);
    setInput("");
  }

  return (
    <AppShell title="Assistente">
      <div className="mx-auto flex h-full max-w-3xl flex-col">
        <div className="mb-3">
          <h2 className="flex items-center gap-2 text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            <Sparkles className="h-5 w-5 text-accent-500" />
            Assistente de contatos
          </h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Respostas geradas a partir dos dados mockados — pronto para plugar a API real do WhatsApp depois.
          </p>
        </div>

        <Card className="flex flex-1 flex-col overflow-hidden">
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((m) => (
              <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={
                    m.role === "user"
                      ? "max-w-[85%] rounded-2xl rounded-br-sm bg-accent-600 px-4 py-2.5 text-sm text-white"
                      : "max-w-[85%] space-y-3"
                  }
                >
                  <p className={m.role === "assistant" ? "rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2.5 text-sm text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200" : ""}>
                    {m.text}
                  </p>
                  {m.contatos && m.contatos.length > 0 && (
                    <div className="space-y-1.5">
                      {m.contatos.map((c) => (
                        <ContactMiniCard key={c.id} contato={c} onClick={() => setSelected(c)} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-zinc-200 p-3 dark:border-zinc-800">
            <div className="mb-2 flex flex-wrap gap-1.5">
              {suggestedPrompts.map((p) => (
                <button
                  key={p}
                  onClick={() => ask(p)}
                  className="rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-600 transition-colors hover:border-accent-300 hover:text-accent-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:border-accent-700 dark:hover:text-accent-400"
                >
                  {p}
                </button>
              ))}
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                ask(input);
              }}
              className="flex gap-2"
            >
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Pergunte sobre seus contatos..."
              />
              <Button type="submit" variant="primary" size="md">
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </Card>
      </div>

      <ContactDrawer key={selected?.id ?? "none"} contato={selected} onClose={() => setSelected(null)} />
    </AppShell>
  );
}
