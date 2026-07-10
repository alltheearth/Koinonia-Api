import type { ReactNode } from "react";
import { X } from "lucide-react";
import { cx } from "../../lib/utils";

export function Drawer({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  children: ReactNode;
}) {
  return (
    <div
      className={cx(
        "fixed inset-0 z-50 transition-[visibility]",
        open ? "visible" : "invisible pointer-events-none",
      )}
      aria-hidden={!open}
    >
      <div
        onClick={onClose}
        className={cx(
          "absolute inset-0 bg-black/30 backdrop-blur-[2px] transition-opacity dark:bg-black/50",
          open ? "opacity-100" : "opacity-0",
        )}
      />
      <div
        className={cx(
          "absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-zinc-200 bg-white shadow-2xl transition-transform duration-200 dark:border-zinc-800 dark:bg-zinc-900",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-4 dark:border-zinc-800">
          <div className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{title}</div>
          <button
            onClick={onClose}
            className="rounded-md p-1.5 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
      </div>
    </div>
  );
}
