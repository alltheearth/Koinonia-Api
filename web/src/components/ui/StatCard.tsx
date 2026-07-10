import type { LucideIcon } from "lucide-react";
import { Card } from "./Card";
import { cx } from "../../lib/utils";

export function StatCard({
  label,
  value,
  icon: Icon,
  tone = "neutral",
  hint,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "neutral" | "accent" | "success" | "warning" | "danger";
  hint?: string;
}) {
  const iconTones = {
    neutral: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
    accent: "bg-accent-50 text-accent-600 dark:bg-accent-500/15 dark:text-accent-400",
    success: "bg-whatsapp-50 text-whatsapp-600 dark:bg-whatsapp-500/15 dark:text-whatsapp-400",
    warning: "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-warning-500",
    danger: "bg-danger-50 text-danger-600 dark:bg-danger-500/15 dark:text-danger-500",
  };

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{label}</p>
          <p className="mt-1.5 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">{value}</p>
          {hint && <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">{hint}</p>}
        </div>
        <div className={cx("flex h-9 w-9 items-center justify-center rounded-lg", iconTones[tone])}>
          <Icon className="h-4 w-4" strokeWidth={2} />
        </div>
      </div>
    </Card>
  );
}
