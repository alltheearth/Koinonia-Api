import { Moon, Search, Sun } from "lucide-react";
import { useTheme } from "../../lib/theme";
import { Badge } from "../ui/Badge";
import { Avatar } from "../ui/Avatar";

export function Topbar({ title, onSearch }: { title: string; onSearch?: (value: string) => void }) {
  const { theme, toggle } = useTheme();

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-4 border-b border-zinc-200 bg-white/80 px-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80 md:px-6">
      <h1 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{title}</h1>

      <div className="flex flex-1 items-center justify-end gap-3">
        {onSearch && (
          <div className="relative hidden w-full max-w-xs sm:block">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              placeholder="Buscar contato..."
              onChange={(e) => onSearch(e.target.value)}
              className="w-full rounded-lg border border-zinc-200 bg-zinc-50 py-1.5 pl-8 pr-3 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-colors focus:border-accent-500 focus:bg-white focus:ring-2 focus:ring-accent-500/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100 dark:focus:bg-zinc-900"
            />
          </div>
        )}

        <Badge tone="warning" dot>
          Modo mock
        </Badge>

        <button
          onClick={toggle}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-500 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-900"
          aria-label="Alternar tema"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <Avatar name="Você" size="sm" />
      </div>
    </header>
  );
}
