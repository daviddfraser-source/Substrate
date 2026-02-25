"use client";

import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  route: "safe" | "review" | "restricted";
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "M-1", role: "assistant", text: "Template chat online. Ask about delivery status, risks, or packet scope.", route: "safe" },
  ]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("gpt-5");
  const [budgetUsed, setBudgetUsed] = useState(18);

  const currentRoute = useMemo(() => {
    const lower = input.toLowerCase();
    if (lower.includes("delete") || lower.includes("override") || lower.includes("bypass")) return "restricted";
    if (lower.includes("deploy") || lower.includes("change") || lower.includes("approve")) return "review";
    return "safe";
  }, [input]);

  function send() {
    const text = input.trim();
    if (!text) return;
    const nextRoute = currentRoute;
    setMessages((prev) => [
      ...prev,
      { id: `M-${prev.length + 1}`, role: "user", text, route: nextRoute },
      { id: `M-${prev.length + 2}`, role: "assistant", text: `Template response routed through ${nextRoute} policy path.`, route: nextRoute },
    ]);
    setBudgetUsed((value) => Math.min(100, value + 6));
    setInput("");
  }

  return (
    <div className="p-6 space-y-4 h-full flex flex-col">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Governed Chat Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">Enterprise chat scaffold with policy route awareness and model/runtime controls.</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1 min-h-[500px]">
        <Card className="lg:col-span-3 flex flex-col p-3">
          <div className="flex-1 overflow-y-auto space-y-3 p-1 min-h-[400px]">
            {messages.map((message) => (
              <div key={message.id} className={`max-w-[80%] rounded-xl p-3 ${message.role === "user" ? "ml-auto bg-[var(--primary)] text-white" : "bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-primary)]"}`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${message.role === "user" ? "bg-white/20" : "bg-[var(--bg-inset)]"}`}>
                    {message.role === "user" ? "U" : "A"}
                  </div>
                  <Badge variant={message.route === "restricted" ? "danger" : message.route === "review" ? "warning" : "success"}>{message.route}</Badge>
                </div>
                <div className={`text-sm ${message.role === "user" ? "text-white" : "text-[var(--text-primary)]"}`}>
                  {message.text}
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-2 mt-4">
            <div className="flex-1">
              <Input
                value={input}
                placeholder="Ask a governed question..."
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              />
            </div>
            <Button variant="primary" onClick={send}>Send</Button>
          </div>
        </Card>

        <Card>
          <div className="flex flex-col gap-6">
            <h3 className="font-semibold text-lg border-b border-[var(--border-default)] pb-2 mb-2">Controls</h3>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-[var(--text-secondary)] mb-2">Model</div>
                <div className="flex flex-col border border-[var(--border-default)] rounded p-1 bg-[var(--bg-secondary)] text-sm">
                  {(["gpt-5", "gpt-4.1", "local-safe"]).map((m) => (
                    <button
                      key={m}
                      onClick={() => setModel(m)}
                      className={`px-3 py-1.5 rounded text-left transition-colors ${model === m
                          ? "bg-[var(--bg-primary)] shadow-sm font-medium"
                          : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                        }`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-sm text-[var(--text-secondary)] mb-2 flex justify-between">
                  <span>Budget</span>
                  <span>{100 - budgetUsed}%</span>
                </div>
                <div className="w-full bg-[var(--bg-inset)] rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${budgetUsed > 85 ? "bg-[var(--danger)]" : "bg-[var(--primary)]"}`}
                    style={{ width: `${100 - budgetUsed}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="text-sm text-[var(--text-secondary)] mb-2">Current policy route</div>
                <Badge variant={currentRoute === "restricted" ? "danger" : currentRoute === "review" ? "warning" : "success"}>{currentRoute}</Badge>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
