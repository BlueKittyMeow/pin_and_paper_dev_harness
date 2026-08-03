# Prototype: the bare-bones GUI (walking skeleton)

**Date:** 2026-08-02 · **Author:** Fable 5
**Goal:** the earliest possible on-screen proof that Pin and Paper's endgame —
*your real tasks as cards you drag around a desk* — works. Motivation build,
not production build. Everything here is a distillation of
`fable-integration-review.md` (the full wiring plan); read that when a step
needs depth. Milestones A–D below = wiring-order steps 1–4 there.

---

## 0. Disk space first (blocking, 5 min)

MysteryOfGlass `/home` has ~1.4 GB free. A Flutter desktop build needs room.

- `pin_and_paper_sketchpad/build/` is **2.2 GB of stale build output** (gitignored,
  regenerates). `cd ../pin_and_paper_sketchpad && flutter clean` reclaims it →
  ~3.6 GB free. Do this before anything else.
- Build **only the harness** for Linux desktop; never run Android builds for
  prototype work (Gradle caches are multi-GB).
- After heavy iteration, `flutter clean` in the harness repo is always safe.

## 1. What exists today (so you know how bare "bare bones" is)

| Piece | Reality |
|-------|---------|
| Dev harness app | Nothing — this repo is docs-only. |
| Sketchpad | Working prototype (~1k lines, draws, erases). Not needed for the skeleton. |
| Canvas | Empty `lib/`. |
| Card renderer | Empty `lib/`. |
| Journal | Placeholder only. Not in the skeleton. |
| Main app | Full task DB + sync. Source of real tasks in Milestone D. |

## 2. Milestone A — the harness runs (one sitting)

Scaffold this repo into a Flutter app: `pubspec.yaml` with path deps on the four
modules (exact block in `fable-integration-review.md` §2), `lib/main.dart` with
a 4-tab shell, one page per module, "not built yet" placeholders. Skeleton code
is fully sketched in `ARCHITECTURE_AND_HARNESS.md` Part 3 — copy, don't
re-derive. Canvas and card_renderer must each get a first-commit stub barrel
file (`lib/pin_and_paper_canvas.dart` etc., public classes throwing
`UnimplementedError`) or the harness won't compile.

**Checkpoint:** `flutter run -d linux` → 4 tabs, sketchpad tab draws.
This is also the moment the repo's README/CLAUDE.md stop lying (see
integration review §7 hygiene list — do the 30-min cleanup here).

## 3. Milestone B — dumb rectangles on a desk (the real canvas MVP)

Canvas module, against **mock data only** (`MockSpatialDataSource`, ~20 fake
entities). Scope per `pin_and_paper_canvas/docs/fable-review.md` (pre-build
decisions are already made there: Stack + Transform rendering, custom viewport
— *not* InteractiveViewer — gesture arbitration, coordinate rules):

- pan/zoom the surface, drag colored rectangles, tap to select
- `onEntityMoved` fires **once per gesture end** (contract fix §5.2 — never per frame)
- nothing persists yet; mock holds positions in memory

**Checkpoint:** drag rectangles smoothly in the harness canvas tab.
**This is the motivation moment #1** — the desk exists.

## 4. Milestone C — rectangles become cards (first integration)

Card renderer static MVP: a `TaskCard` widget that takes `TaskCardData` (title,
done, tags) and looks like a paper card — flat color, rounded corner, one
shadow. **No realism yet**: no textures, no torn edges, no lighting (that's
Phase 5; see the card_renderer review's "bake, don't simulate" guide and its
do-NOT table). Add a card-gallery tab, then swap the canvas mock's
`entityBuilder` from rectangles to `TaskCard`.

**Checkpoint:** dragging *cards* around the desk, zero main-app involvement.

## 5. Milestone D — your real tasks on the desk

First (and only) main-app work in the skeleton:

1. `task_canvas` table, local migration v13 — SQL sketched in integration
   review §3. **No Supabase, no sync** for the prototype (that's step 5 of the
   full plan, explicitly deferred).
2. `TaskSpatialDataSource` implementing the canvas contract over
   `TaskProvider._tasks` + a `task_canvas` cache. Tasks without a row get a
   deterministic staggered-grid default position; write a row on first drag
   (contract fix §5.3).
3. A Spatial view behind a debug flag/toggle in the main app — or, cheaper,
   point the harness at a **copy** of the real DB file first if wiring the
   main-app toggle balloons.

**Checkpoint:** your actual to-do list as draggable cards; positions survive
restart. **Motivation moment #2 — the end goal, demonstrated.**

## 6. What the skeleton deliberately skips

Sync of spatial data (LWW design is ready when wanted) · drawings/sketchpad
serialization (blocks journal, not the desk) · realism (parameters later, not
systems) · rotation & z-order polish · journal. Each has its slot in the
9-step order; none blocks the demo.

## 7. Who can build what

Milestones A–C are pure module work — any model can do them from the specs +
`fable-review.md` docs in each repo, no main-app knowledge needed. Milestone D
needs main-app context (`CORE_API.md` + sync review findings). Keep those as
separate sessions/agents; the module boundaries are the architecture working.
