export function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function daysSince(dateStr: string): number {
  const then = new Date(dateStr).getTime();
  const now = Date.now();
  return Math.floor((now - then) / (1000 * 60 * 60 * 24));
}

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
}

export function formatRelative(dateStr: string): string {
  const days = daysSince(dateStr);
  if (days <= 0) return "hoje";
  if (days === 1) return "ontem";
  if (days < 7) return `há ${days} dias`;
  const weeks = Math.floor(days / 7);
  if (weeks === 1) return "há 1 semana";
  if (weeks < 5) return `há ${weeks} semanas`;
  const months = Math.floor(days / 30);
  if (months <= 1) return "há 1 mês";
  return `há ${months} meses`;
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/** Deterministic pastel color for an avatar, derived from the name. */
export function avatarColor(name: string): string {
  const palette = [
    "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300",
    "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300",
    "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300",
    "bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300",
    "bg-violet-100 text-violet-700 dark:bg-violet-500/15 dark:text-violet-300",
    "bg-fuchsia-100 text-fuchsia-700 dark:bg-fuchsia-500/15 dark:text-fuchsia-300",
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return palette[Math.abs(hash) % palette.length];
}
