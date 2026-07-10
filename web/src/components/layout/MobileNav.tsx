import { NavLink } from "react-router-dom";
import { LayoutDashboard, Users, History, Sparkles } from "lucide-react";
import { cx } from "../../lib/utils";

const nav = [
  { to: "/", label: "Início", icon: LayoutDashboard, end: true },
  { to: "/contatos", label: "Contatos", icon: Users },
  { to: "/historico", label: "Histórico", icon: History },
  { to: "/assistente", label: "Assistente", icon: Sparkles },
];

export function MobileNav() {
  return (
    <nav className="flex h-14 shrink-0 items-center justify-around border-t border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 md:hidden">
      {nav.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            cx(
              "flex flex-col items-center gap-0.5 px-3 py-1 text-[11px] font-medium",
              isActive ? "text-accent-600 dark:text-accent-400" : "text-zinc-500 dark:text-zinc-400",
            )
          }
        >
          <item.icon className="h-5 w-5" strokeWidth={2} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
