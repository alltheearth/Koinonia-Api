import { avatarColor, cx, initials } from "../../lib/utils";

export function Avatar({ name, size = "md", className }: { name: string; size?: "sm" | "md" | "lg"; className?: string }) {
  const sizes = { sm: "h-7 w-7 text-xs", md: "h-9 w-9 text-sm", lg: "h-12 w-12 text-base" };
  return (
    <div
      className={cx(
        "flex shrink-0 items-center justify-center rounded-full font-medium",
        sizes[size],
        avatarColor(name),
        className,
      )}
    >
      {initials(name)}
    </div>
  );
}
