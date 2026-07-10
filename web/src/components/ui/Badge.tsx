import type { ReactNode } from "react";
import { cx } from "../../lib/utils";

const tones = {
  neutral: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  accent: "bg-accent-50 text-accent-700 dark:bg-accent-500/15 dark:text-accent-400",
  success: "bg-whatsapp-50 text-whatsapp-600 dark:bg-whatsapp-500/15 dark:text-whatsapp-400",
  warning: "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-warning-500",
  danger: "bg-danger-50 text-danger-600 dark:bg-danger-500/15 dark:text-danger-500",
} as const;

export type BadgeTone = keyof typeof tones;

export function Badge({
  children,
  tone = "neutral",
  dot = false,
  className,
}: {
  children: ReactNode;
  tone?: BadgeTone;
  dot?: boolean;
  className?: string;
}) {
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
    >
      {dot && <span className={cx("h-1.5 w-1.5 rounded-full", dotColor[tone])} />}
      {children}
    </span>
  );
}

const dotColor: Record<BadgeTone, string> = {
  neutral: "bg-zinc-400",
  accent: "bg-accent-500",
  success: "bg-whatsapp-500",
  warning: "bg-warning-500",
  danger: "bg-danger-500",
};
