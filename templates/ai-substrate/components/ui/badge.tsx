"use client";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info";
  className?: string;
}

const variantStyles: Record<string, string> = {
  default: "bg-[var(--bg-inset)] text-[var(--text-secondary)]",
  success: "bg-[var(--success-50)] text-[var(--success-700)]",
  warning: "bg-[var(--warning-50)] text-[#92400e]",
  danger: "bg-[var(--danger-50)] text-[var(--danger-700)]",
  info: "bg-[var(--primary-50)] text-[var(--primary-800)]",
};

export function Badge({ children, variant = "default", className = "" }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
}
