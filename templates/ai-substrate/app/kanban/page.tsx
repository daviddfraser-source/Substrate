"use client";

import { useState, useEffect } from "react";
import {
  DndContext,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { KpiCard } from "@/components/governance/KpiCard";

type CardData = { id: string; title: string; description: string; label: string; owner: string; columnId: string };
type ColumnData = { id: string; title: string };

const initialColumns: ColumnData[] = [
  { id: "backlog", title: "Backlog" },
  { id: "in-design", title: "In Design" },
  { id: "in-build", title: "In Build" },
  { id: "qa", title: "QA / UAT" },
  { id: "done", title: "Done" },
];

const initialCards: CardData[] = [
  { id: "K-101", title: "Bootstrap workspace", description: "Create baseline repos and ADRs", label: "8 pts", owner: "Platform", columnId: "backlog" },
  { id: "K-102", title: "Define security controls", description: "Document authn/authz acceptance criteria", label: "5 pts", owner: "Security", columnId: "backlog" },
  { id: "K-103", title: "Wireframe template pages", description: "Enterprise-ready IA and UX", label: "3 pts", owner: "Product", columnId: "in-design" },
  { id: "K-104", title: "Implement WBS grid", description: "Tree grid with packet runtime state", label: "13 pts", owner: "Frontend", columnId: "in-build" },
  { id: "K-105", title: "Embed PTY terminal", description: "Session API + stream + resize", label: "8 pts", owner: "Platform", columnId: "in-build" },
  { id: "K-106", title: "Playwright regression", description: "Smoke all template routes", label: "5 pts", owner: "QA", columnId: "qa" },
  { id: "K-099", title: "Governance CLI wired", description: "claim/done/note lifecycle enforced", label: "3 pts", owner: "Platform", columnId: "done" },
];

function SortableCard({ card }: { card: CardData }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: card.id,
    data: { type: "Card", card },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-[10px] p-3 shadow-sm mb-3 cursor-grab break-inside-avoid ${isDragging ? "ring-2 ring-[var(--primary)]" : "hover:border-[var(--border-hover)]"}`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="font-medium text-sm text-[var(--text-primary)]">{card.title}</div>
      </div>
      <div className="text-xs text-[var(--text-secondary)] mb-3">{card.description}</div>
      <div className="flex justify-between items-center text-xs text-[var(--text-tertiary)]">
        <span className="bg-[var(--bg-inset)] px-2 py-1 rounded-full">{card.label}</span>
        <span>{card.owner}</span>
      </div>
    </div>
  );
}

import { useDroppable } from '@dnd-kit/core';

export default function KanbanPage() {
  const [cards, setCards] = useState<CardData[]>(initialCards);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragStart = (event: any) => {
    setActiveId(event.active.id);
  };

  const handleDragOver = (event: any) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    if (activeId === overId) return;

    const isActiveTask = active.data.current?.type === "Card";
    const isOverTask = over.data.current?.type === "Card";

    if (!isActiveTask) return;

    if (isActiveTask && isOverTask) {
      setCards((prev) => {
        const activeIndex = prev.findIndex((t) => t.id === activeId);
        const overIndex = prev.findIndex((t) => t.id === overId);

        if (activeIndex === -1 || overIndex === -1) return prev;

        if (prev[activeIndex].columnId !== prev[overIndex].columnId) {
          const newCards = [...prev];
          newCards[activeIndex] = { ...newCards[activeIndex], columnId: newCards[overIndex].columnId };
          return arrayMove(newCards, activeIndex, overIndex);
        }

        return arrayMove(prev, activeIndex, overIndex);
      });
      return;
    }

    const isOverColumn = over.data.current?.sortable?.containerId !== undefined;
    if (isActiveTask && isOverColumn) {
      setCards((prev) => {
        const activeIndex = prev.findIndex((t) => t.id === activeId);
        if (activeIndex === -1) return prev;

        const colId = over.data.current?.sortable?.containerId || over.id;
        const targetColumnId = typeof colId === "string" ? colId : String(colId);

        if (prev[activeIndex].columnId !== targetColumnId) {
          const newCards = [...prev];
          newCards[activeIndex] = { ...newCards[activeIndex], columnId: targetColumnId };
          return arrayMove(newCards, activeIndex, activeIndex);
        }
        return prev;
      });
    }
  };

  const handleDragEnd = (event: any) => {
    setActiveId(null);
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    if (activeId === overId) return;

    setCards((prev) => {
      const activeIndex = prev.findIndex((t) => t.id === activeId);
      const overIndex = prev.findIndex((t) => t.id === overId);

      if (activeIndex !== -1 && overIndex !== -1) {
        return arrayMove(prev, activeIndex, overIndex);
      }
      return prev;
    });
  };

  if (!isMounted) {
    return <div className="p-6">Loading board...</div>;
  }

  const activeCard = activeId ? cards.find(c => c.id === activeId) : null;

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-col gap-1 mb-4 border-b border-[var(--border-default)] pb-4">
        <h2 className="text-2xl font-semibold m-0 tracking-tight text-[var(--text-primary)]">Kanban Template</h2>
        <span className="text-sm text-[var(--text-secondary)]">
          Powered by `@dnd-kit` with editable lanes, drag/drop, and enterprise backlog workflow semantics.
        </span>
      </div>

      <div className="flex flex-wrap gap-4 mb-4">
        <div className="w-48">
          <KpiCard title="Workstreams" value={initialColumns.length} accent="primary" />
        </div>
        <div className="w-48">
          <KpiCard title="Total Cards" value={cards.length} accent="success" />
        </div>
      </div>

      <Alert
        showIcon
        type="info"
        title="Library-first board"
        description="Use this as the default backlog board starter. Drag to reorder or move cards between columns."
        className="mb-4"
      />

      <div className="flex gap-4 overflow-x-auto pb-4 items-start min-h-[500px]">
        <DndContext
          sensors={sensors}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
          collisionDetection={closestCorners}
        >
          {initialColumns.map((col) => {
            const colCards = cards.filter(c => c.columnId === col.id);
            return (
              <SortableContext key={col.id} id={col.id} items={colCards.map(c => c.id)} strategy={verticalListSortingStrategy}>
                <div key={col.id} className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-[12px] min-w-[290px] w-[290px] flex flex-col pt-3 pb-2 px-3">
                  <div className="mb-3 px-1 flex justify-between items-center">
                    <h3 className="text-sm font-semibold text-[var(--text-primary)]">{col.title}</h3>
                    <span className="bg-[var(--bg-inset)] text-[var(--text-secondary)] px-2 py-0.5 rounded-full text-xs font-medium">
                      {colCards.length}
                    </span>
                  </div>
                  <div className="flex-1 overflow-y-auto min-h-[50px]">
                    {colCards.map((c) => (
                      <SortableCard key={c.id} card={c} />
                    ))}
                  </div>
                </div>
              </SortableContext>
            );
          })}
          <DragOverlay>
            {activeCard ? <SortableCard card={activeCard} /> : null}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
}
