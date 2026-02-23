import { getItems } from "@/lib/data/items";
import { buttonVariants } from "@/components/ui/button";
import Link from "next/link";

export default async function Page() {
  const items = await getItems();
  return (
    <section>
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-semibold text-slate-50">AI-Optimized Substrate</h1>
        <Link href="/new">
          <span className={buttonVariants({ intent: "primary" })}>Create record</span>
        </Link>
      </header>
      <div className="grid gap-4">
        {items.map((item) => (
          <article key={item.id} className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <h2 className="text-xl font-medium text-slate-200">{item.title}</h2>
            <p className="text-sm text-slate-400">{item.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
