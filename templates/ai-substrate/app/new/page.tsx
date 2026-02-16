"use client";

import { useState } from "react";
import type { FormEvent } from "react";

export default function NewItemForm() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  async function createItem() {
    await fetch("/api/items", {
      method: "POST",
      body: JSON.stringify({ title, description }),
      headers: { "content-type": "application/json" }
    });
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void createItem();
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <label className="block text-sm font-medium text-slate-200">
        Title
        <input
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/70 p-2 text-sm text-slate-100"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
      </label>
      <label className="block text-sm font-medium text-slate-200">
        Description
        <textarea
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900/70 p-2 text-sm text-slate-100"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </label>
      <button
        type="button"
        className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-400"
        onClick={createItem}
      >
        Create
      </button>
    </form>
  );
}
