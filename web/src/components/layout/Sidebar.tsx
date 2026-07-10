import { NavLink } from "react-router-dom";
import { LayoutDashboard, Users, History, Sparkles, MessageCircle } from "lucide-react";
import { cx } from "../../lib/utils";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/contatos", label: "Contatos", icon: Users },
  { to: "/historico", label: "Histórico", icon: History },
  { to: "/assistente", label: "Assistente", icon: Sparkles },
];

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 md:flex">
      <div className="flex h-14 items-center gap-2 px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent-600 text-white">
          <MessageCircle className="h-4 w-4" />
        </div>
        <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Koinonia</span>
      </div>

      <nav className="flex-1 space-y-0.5 px-2 py-2">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              cx(
                "flex items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent-50 text-accent-700 dark:bg-accent-500/10 dark:text-accent-400"
                  : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-900",
              )
            }
          >
            <item.icon className="h-4 w-4" strokeWidth={2} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-zinc-200 p-3 dark:border-zinc-800">
        <p className="px-1 text-xs text-zinc-400 dark:text-zinc-600">
          Dados mockados · pronto para conectar a API do WhatsApp
        </p>
      </div>
    </aside>
  );
}
