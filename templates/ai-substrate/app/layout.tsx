"use client";

import "./globals.css";
import "antd/dist/reset.css";
import "./xterm.css";
import { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/governance/ThemeToggle";
import { CommandPalette } from "@/components/governance/CommandPalette";
import { TtydDock } from "@/components/governance/TtydDock";

interface LayoutProps {
  children: ReactNode;
}

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export default function RootLayout({ children }: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const saved = localStorage.getItem("sidebar-collapsed");
    if (saved === "true") setSidebarCollapsed(true);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(true);
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "`") {
        e.preventDefault();
        setTerminalOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const toggleSidebar = () => {
    const newState = !sidebarCollapsed;
    setSidebarCollapsed(newState);
    localStorage.setItem("sidebar-collapsed", String(newState));
  };

  const navSections: NavSection[] = [
    {
      title: "Governance",
      items: [
        { href: "/dashboard", label: "Dashboard", icon: "📊" },
        { href: "/wbs", label: "WBS Viewer", icon: "🧭" },
        { href: "/packets", label: "Packets", icon: "📦" },
        { href: "/terminal", label: "Embedded CLI", icon: "⌨️" },
        { href: "/audit", label: "Audit Log", icon: "📋" },
        { href: "/risks", label: "Risks", icon: "⚠️" },
        { href: "/graph", label: "Dependency Graph", icon: "🔗" },
        { href: "/settings", label: "Settings", icon: "⚙️" },
      ],
    },
    {
      title: "Template Pages",
      items: [
        { href: "/kanban", label: "Kanban / Gantt", icon: "🗂️" },
        { href: "/gantt", label: "Gantt", icon: "📈" },
        { href: "/timeline", label: "Timeline", icon: "🕒" },
        { href: "/assistant", label: "RAG Assistant", icon: "🤖" },
        { href: "/chat", label: "Governed Chat", icon: "💬" },
        { href: "/knowledge", label: "Knowledge Base", icon: "📚" },
        { href: "/documents", label: "Documents", icon: "📄" },
        { href: "/approvals", label: "Approvals", icon: "✅" },
        { href: "/prompt-lab", label: "Prompt Lab", icon: "🧪" },
        { href: "/agent-console", label: "Agent Console", icon: "🖥️" },
        { href: "/new", label: "New Item Form", icon: "➕" },
      ],
    },
  ];
  const allNavItems = navSections.flatMap((section) => section.items);

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>Substrate Governance</title>
        <meta name="description" content="AI-optimized governance dashboard" />
      </head>
      <body className="bg-token-canvas text-token-primary antialiased">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside
            className={`bg-token-elevated border-r border-token-border-default flex flex-col transition-all duration-300 ${
              sidebarCollapsed ? "w-16" : "w-64"
            }`}
            role="navigation"
            aria-label="Main navigation"
          >
            {/* Logo/Title */}
            <div className="h-14 flex items-center px-4 border-b border-token-border-default">
              {!sidebarCollapsed && (
                <h1 className="text-lg font-semibold text-token-primary">
                  Substrate
                </h1>
              )}
              {sidebarCollapsed && <span className="text-xl">📐</span>}
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4">
              <div className="px-2 space-y-4">
                {navSections.map((section) => (
                  <div key={section.title}>
                    {!sidebarCollapsed && (
                      <p className="px-2 mb-1 text-[11px] uppercase tracking-wide text-token-tertiary">
                        {section.title}
                      </p>
                    )}
                    <ul className="space-y-1 list-none m-0 p-0">
                      {section.items.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                          <li key={item.href}>
                            <Link
                              href={item.href}
                              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                isActive
                                  ? "bg-token-primary text-white"
                                  : "text-token-secondary hover:bg-token-inset hover:text-token-primary"
                              }`}
                              title={sidebarCollapsed ? item.label : undefined}
                            >
                              <span className="text-lg" aria-hidden="true">
                                {item.icon}
                              </span>
                              {!sidebarCollapsed && <span>{item.label}</span>}
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            </nav>

            {/* Sidebar Controls */}
            <div className="p-2 border-t border-token-border-default space-y-2">
              {!sidebarCollapsed && <ThemeToggle />}
              <button
                onClick={toggleSidebar}
                className="w-full flex items-center justify-center px-3 py-2 text-sm text-token-secondary hover:text-token-primary hover:bg-token-inset rounded-md transition-colors"
                aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                aria-expanded={!sidebarCollapsed}
              >
                {sidebarCollapsed ? "→" : "←"}
              </button>
            </div>
          </aside>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <header className="h-14 bg-token-elevated border-b border-token-border-default flex items-center justify-between px-6">
              <div className="flex items-center gap-4">
                <h2 className="text-sm font-medium text-token-secondary">
                  {allNavItems.find((item) => pathname === item.href || pathname?.startsWith(item.href + "/"))?.label || "Governance"}
                </h2>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setTerminalOpen(true)}
                  className="px-3 py-1.5 text-xs text-token-tertiary bg-token-inset rounded border border-token-border-default hover:border-token-border-strong transition-colors"
                  title="Open terminal (Ctrl+`)"
                >
                  <span className="font-mono">CLI</span>
                </button>
                <button
                  onClick={() => setCommandPaletteOpen(true)}
                  className="px-3 py-1.5 text-xs text-token-tertiary bg-token-inset rounded border border-token-border-default hover:border-token-border-strong transition-colors"
                >
                  <kbd className="font-mono">⌘K</kbd>
                </button>
              </div>
            </header>

            {/* Page Content */}
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>

        {/* Command Palette */}
        <CommandPalette
          open={commandPaletteOpen}
          onClose={() => setCommandPaletteOpen(false)}
        />
        <TtydDock open={terminalOpen} onClose={() => setTerminalOpen(false)} />
      </body>
    </html>
  );
}
