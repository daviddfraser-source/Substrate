# Dependency Graph UI Contract

Date: 2026-02-24
Packet: PRD-4-2

## Delivered Module

- `app/src/ui/dependencyGraph.ts`

## Capabilities

- Graph edge model (`DependencyEdge`)
- Cycle detection (`detectCycles`)
- Blocked/cyclic node state shaping (`buildGraphNodeState`)
- Click-to-navigate route builder (`resolvePacketNavigation`)

## Visualization Semantics

- blocked nodes: `blocked=true`
- cyclic nodes: `cyclic=true`

Nodes may be both blocked and cyclic.

## Validation

- `python3 -m unittest tests/test_dependency_graph_ui.py`
