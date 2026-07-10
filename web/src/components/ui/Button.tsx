import type { ButtonHTMLAttributes } from "react";
import { cx } from "../../lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

const base =
  "inline-flex items-center justify-center gap-1.5 rounded-lg font-medium transition-colors " +
  "disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 " +
  "focus-visible:ring-accent-500/50";

const variants: Record<Variant, string> = {
  primary: "bg-accent-600 text-white hover:bg-accent-700 shadow-sm",
  secondary:
    "bg-white text-zinc-700 border border-zinc-200 hover:bg-zinc-50 " +
    "dark:bg-zinc-900 dark:text-zinc-200 dark:border-zinc-800 dark:hover:bg-zinc-800",
  ghost: "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800",
  danger: "bg-danger-600 text-white hover:bg-danger-500",
};

const sizes: Record<Size, string> = {
  sm: "h-8 px-2.5 text-sm",
  md: "h-9 px-3.5 text-sm",
};

export function Button({
  variant = "secondary",
  size = "md",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button className={cx(base, variants[variant], sizes[size], className)} {...props} />;
}
