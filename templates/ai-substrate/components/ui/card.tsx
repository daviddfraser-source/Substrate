"use client";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className = "", hover = true }: CardProps) {
  return (
    <div className={`bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-[var(--radius-xl)] p-4 transition-shadow ${hover ? "hover:shadow-[var(--shadow-sm)]" : ""} ${className}`}>
      {children}
    </div>
  );
}
