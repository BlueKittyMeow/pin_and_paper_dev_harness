# Prototype: path to the bare-bones GUI

**Date:** 2026-08-02 (rev 2, after review) · **Author:** Fable 5
**Goal:** earliest on-screen proof of the endgame — *your real tasks as cards
you drag around a desk* — sequenced for motivation: visible wins early.

## Plan of record: the approved POC plan

**`docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md` (approved 2026-07-17, branch
`claude/drag-drop-canvas-mvp-cu6uoy`) is the plan of record for the POC.**
Rev 1 of this doc was written without knowledge of it and proposed a heavier
harness-first route; the approved plan is leaner and reaches the same
motivation moments sooner:

1. **Canvas module + its own `example/` app** — drag mock cards, validate
   gestures in isolation. *(Motivation moment #1: the desk exists.)*
2. **Card renderer MVP slice** — `TaskCardData` + `TagChip` + a simple
   index-card `TaskCard`. No flip/drawing/textures.
3. **Main app integration** — DB v13 (`canvas_x`/`canvas_y` on `tasks`,
   POC-scoped), Spatial View with real tasks, positions survive restart.
   *(Motivation moment #2: your actual to-do list on the desk.)*

No DevHarnessApp, no sketchpad involvement — the harness becomes relevant
later, when multiple modules need side-by-side integration testing (see
"After the POC" below).

## Deltas & watch-items against the longer-term wiring plan

The full integration review (`fable-integration-review.md`, 2026-07-09)
remains the map for everything *after* the POC. Two seams to keep eyes on:

- **Spatial columns vs. `task_canvas` table.** The POC puts `canvas_x/y` on
  the `tasks` row; the integration review (§3) recommends a separate
  `task_canvas` table once positions sync (LWW contention, write volume, MCP
  isolation). The POC plan verifiably excludes the columns from sync mappers,
  which defuses most of that for now — but note its `updateTaskCanvasPosition`
  still bumps `updated_at` and writes `sync_log` on drag-end, so task-row LWW
  contention between a drag and a remote edit is possible even pre-sync.
  Accepted for the POC; revisit at the "sync positions" follow-up — that is
  the natural moment to decide columns-forever vs. migrate-to-table.
- **Datasource contract.** `SpatialDataSource` is an abstract
  `ChangeNotifier` (per the approved plan and `pin_and_paper_canvas/docs/
  fable-review.md` §3.1). Do **not** copy the harness skeletons in
  `ARCHITECTURE_AND_HARNESS.md` Part 3 verbatim — they predate this contract
  fix (plain interface, manual callbacks, elided methods) and are shape
  reference only.

## After the POC (the deferred roadmap)

In rough order, all specced already:

1. **Harness app** (`fable-integration-review.md` §2) — becomes worth building
   when sketchpad/journal integration starts; checkpoint: tabs render, canvas
   at 60fps with 100 mock entities (the canvas review's §5 gate — the POC's
   example app should hit this too before integration).
2. **Sync spatial positions** (§3 checklist) + the columns-vs-table decision.
3. **Canvas polish** — rotation, z-order.
4. **Sketchpad serialization → card drawings**, local-only (§4; format specced
   in `pin_and_paper_sketchpad/docs/fable-review.md`).
5. **Phase 5 realism** — "bake, don't simulate"
   (`pin_and_paper_card_renderer/docs/fable-review.md`).
6. **Journal.**

## Housekeeping notes (2026-08-02)

- Disk: stale build artifacts (~13 GB: sketchpad `build/`, three Rust
  `target/` dirs, localsend) were cleared on 2026-08-02; `/home` has ~15 GB
  free. Android builds remain the space hog to avoid for prototype work;
  root `/` is at 95% (~2.2 GB) — keep heavy work under `/home`.
- Main-app data access in step 3 goes through the public `TaskProvider.tasks`
  getter (the `_tasks` field is private).
- Repos touched by the POC: canvas, card_renderer, main app — per the
  approved plan, work on branch `claude/drag-drop-canvas-mvp-cu6uoy` in each.
