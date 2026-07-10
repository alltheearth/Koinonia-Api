import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { MobileNav } from "./MobileNav";

export function AppShell({
  title,
  onSearch,
  children,
}: {
  title: string;
  onSearch?: (value: string) => void;
  children: ReactNode;
}) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-zinc-50 dark:bg-zinc-950">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar title={title} onSearch={onSearch} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
        <MobileNav />
      </div>
    </div>
  );
}
