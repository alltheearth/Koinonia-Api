import type { HTMLAttributes } from "react";
import { cx } from "../../lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cx(
        "rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900/60",
        className,
      )}
      {...props}
    />
  );
}
