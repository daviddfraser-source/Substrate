import "./globals.css";
import { ReactNode } from "react";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI-Optimized Substrate",
  description: "Typed, AI-friendly Next.js template"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50">
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
          <main className="mx-auto max-w-5xl px-4 py-16">{children}</main>
        </div>
      </body>
    </html>
  );
}
