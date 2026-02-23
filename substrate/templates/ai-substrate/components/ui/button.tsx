import clsx from "clsx";

type Intent = "primary" | "ghost";

export const buttonVariants = ({ intent }: { intent?: Intent } = {}) => {
  const base = "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition";
  const intentClasses =
    intent === "ghost"
      ? "border border-slate-700 bg-transparent text-slate-200 hover:border-slate-500"
      : "bg-sky-500 text-slate-950 hover:bg-sky-400";
  return clsx(base, intentClasses);
};
