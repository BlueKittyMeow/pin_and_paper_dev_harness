# Fable — Integration Review: Wiring the Modules Together

**Date:** 2026-07-09
**Audience:** Any model or developer implementing Phase 4.x integration.
**Companion docs:** `fable-review.md` in each module repo; `docs/specs/fable-full-project-review.md` in the main app repo (bug findings).

This is the "how does it all connect" review. The module specs (CANVAS_SPEC, CARD_RENDERER_SPEC, SKETCHPAD_SPEC, JOURNAL_SPEC) are good and should be followed — this doc covers what they *don't* cover: the seams between modules, the main app, the database, and sync.

---

## 1. Current state (verified 2026-07-09)

| Piece | Docs say | Reality |
|-------|----------|---------|
| Dev harness app | `lib/` + mocks + pages + pubspec | **Does not exist** — repo is docs-only |
| Sketchpad | Prototype working | True (~1,000 lines, eraser works, no serialization) |
| Canvas | Stub | `.gitkeep` only |
| Card renderer | Stub | `.gitkeep` only |
| Journal | Phase 6 | Placeholder screen only |
| Main app | 16k lines | ~42k lines, now includes Supabase sync + MCP server |

Also: harness `CLAUDE.md` references spec paths (`specs/phase-4.1-canvas-mvp/...`) that exist in no repo — the real specs are `docs/module_specs/*.md` here. And "Phase 4" means *sync* in the main app but *spatial MVP* here. Fix both before pointing another model at this workspace (see §7).

---

## 2. Step 0 — Build the harness app itself

Nothing can be wired until the harness exists. Create in this repo:

```yaml
# pubspec.yaml
name: pin_and_paper_dev_harness
publish_to: 'none'
version: 0.1.0
environment:
  sdk: '>=3.5.0 <4.0.0'
dependencies:
  flutter: {sdk: flutter}
  pin_and_paper_sketchpad: {path: ../pin_and_paper_sketchpad}
  pin_and_paper_canvas: {path: ../pin_and_paper_canvas}
  pin_and_paper_card_renderer: {path: ../pin_and_paper_card_renderer}
  pin_and_paper_journal: {path: ../pin_and_paper_journal}
```

Files (skeletons are fully sketched in `ARCHITECTURE_AND_HARNESS.md` Part 3 — use them):
- `lib/main.dart` — 4-tab app (Sketchpad / Canvas / Cards / Journal)
- `lib/mocks/mock_spatial_source.dart`, `mock_journal_source.dart`, `mock_drawing_source.dart`, `mock_data.dart`
- `lib/pages/*_test_page.dart` (one per tab; empty modules get a "not built yet" placeholder)
- `lib/widgets/dev_controls_drawer.dart`

**Important:** canvas and card_renderer have no code, so the harness won't compile against them until each exports at least a stub (`lib/<name>.dart` with the public classes throwing `UnimplementedError`). Create those stubs as the first commit in each module repo — this locks the API surface early, which is the whole point of the contracts.

**Acceptance:** `flutter run -d linux` in this repo shows 4 tabs; sketchpad tab draws.

---

## 3. The biggest gap: spatial data has nowhere to live

This is the #1 wiring risk. The canvas needs `x, y, rotation, zIndex` per task. Today:

- SQLite `tasks` table has no spatial columns (v12 schema).
- Supabase `tasks` has none.
- `SyncService` converters (`localTaskToRemote` / `remoteTaskToLocal`) enumerate columns explicitly — new columns are silently dropped unless added there too.
- The MCP server's `shift_sibling_positions` churns `position`; spatial fields must not be entangled with that.

### Recommendation: a separate `task_canvas` table, NOT columns on `tasks`

Reasons, in order of importance:

1. **Sync semantics.** Tasks merge with row-level LWW on `updated_at`. If x/y live on the task row, every drag competes with title/notes/completion edits for the same LWW slot — drag a card on the tablet while editing its title on desktop and one device loses a change. A separate row gives spatial state its own LWW timeline.
2. **Write volume.** Dragging produces bursts of writes. On the tasks table those bursts would spam `sync_log`, push cycles, and (remotely) the `updated_at` trigger + realtime channel for every card touched.
3. **MCP isolation.** MCP tools upsert whole task rows; keeping spatial data out of `tasks` means MCP can't accidentally clobber positions and needs no changes.

### Local migration (v13) — sketch

```sql
CREATE TABLE task_canvas (
  task_id TEXT PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  x REAL NOT NULL,
  y REAL NOT NULL,
  rotation REAL NOT NULL DEFAULT 0,       -- degrees
  z_index INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL             -- epoch ms, for LWW
);
```

No `position`-style reindexing needed; z_index compaction can reuse the `_reindexSiblings` pattern if it ever grows unbounded.

### Remote (Supabase) — sketch

```sql
CREATE TABLE task_canvas (
  task_id UUID PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  x DOUBLE PRECISION NOT NULL,
  y DOUBLE PRECISION NOT NULL,
  rotation DOUBLE PRECISION NOT NULL DEFAULT 0,
  z_index INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE task_canvas ENABLE ROW LEVEL SECURITY;
-- four policies identical in shape to tasks_select/insert/update/delete
CREATE TRIGGER task_canvas_updated_at BEFORE INSERT OR UPDATE ON task_canvas
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

Note `BEFORE INSERT OR UPDATE` — do not repeat the tasks-table bug where the trigger skips INSERT and client clocks poison the pull cursor (main-repo review, finding H-4).

### Sync integration checklist

- [ ] `localTaskCanvasToRemote` / `remoteTaskCanvasToLocal` converters in SyncService
- [ ] `logChange(tableName: 'task_canvas', ...)` from the write path — **debounced**: log once when a drag *ends*, never per-frame
- [ ] `mergeTaskCanvas` with LWW on `updated_at` (same shape as `mergeTag`, minus the name-collision machinery)
- [ ] Add `task_canvas` to `pull()`, `fullPush()` (batched upsert), and the realtime subscription
- [ ] `preparePushEntry` case for `task_canvas` (re-read current row, like tasks)

### Conflict policy: accept LWW per card

Two devices dragging the *same card* concurrently → last write wins, one drag is lost. That is fine — don't build operational transforms for card positions. Positions are cheap to re-drag; correctness matters for the task data, not the desk layout.

---

## 4. Second gap: drawings have no persistence format

`CardDrawingSource` and `JournalDataSource.savePage` both traffic in `LayerStack`, but `LayerStack`/`Stroke`/`StrokePoint` have **no toJson/fromJson**. This blocks card drawings (4.5) and the entire journal (6.x). The serialization spec lives in the sketchpad review doc (`pin_and_paper_sketchpad/docs/fable-review.md` §3) — implement it there first.

Storage plan once serialization exists:

- Local: `task_drawings (task_id, side TEXT CHECK(side IN ('front','back')), data TEXT /* JSON */, updated_at, PRIMARY KEY(task_id, side))`, and later `journal_pages (date TEXT PRIMARY KEY, drawings TEXT, notes TEXT, template TEXT, texture TEXT, updated_at)`.
- **Defer syncing drawings.** Stroke JSON is 10–100× bigger than task rows; syncing it through the current row-based LWW pipeline is a garden path. Ship local-only, revisit with Supabase Storage (one JSON blob per card side, LWW on `updated_at`) if cross-device drawings are ever actually wanted.
- Cache a rasterized `ui.Image` (or PNG file) of each drawing for display on the canvas; only open the live vector editor when the user edits. Never run the stroke painter for dozens of cards simultaneously.

---

## 5. Interface contract fixes (small but load-bearing)

The contracts in `INTERFACE_CONTRACTS.md` are 90% right. Adjust before implementation:

1. **`getVisibleEntities(Rect)` is synchronous but the app's data is async.** Don't make it `Future` — instead the main app's implementation holds an in-memory snapshot (it already does: `TaskProvider._tasks`) joined with the `task_canvas` cache, and exposes a `Listenable`/callback the canvas subscribes to for refreshes. Add to the contract: `SpatialDataSource` gains `void addListener(VoidCallback)` / `removeListener`, or simply document that the canvas widget receives a `ChangeNotifier` datasource. This matches the app's no-Streams convention.
2. **Split move callbacks.** `onEntityMoved(id, position, rotation)` should fire **once, on gesture end** (this is the persistence + sync trigger). Add optional `onEntityMoving(id, position, rotation)` for live feedback if the app ever needs it. If a single callback fires per-frame, every drag becomes hundreds of DB writes and sync_log rows — this is the same class of bug as the MCP position churn (main-repo review, M-1).
3. **New tasks need a spawn position.** When a task is created in list view, it has no `task_canvas` row. Contract: entities without a row get a deterministic default (e.g., staggered grid seeded by task id) and a row is written on first touch. Don't write rows for all existing tasks up-front.
4. **Entity size.** `SpatialEntity.size` is a getter, but card size is really the renderer's decision (style-dependent). Make size advisory: the canvas uses it only for hit-testing/culling, and the app's implementation returns the standard card size constant exported by card_renderer.
5. **Completed/deleted tasks on the canvas.** The contract is silent. Decide now: soft-deleted → never on canvas (join filters `deleted_at IS NULL`); completed → app decision, suggest showing muted for `hideThresholdHours` then removing (reuse the existing preference).

---

## 6. Recommended wiring order

Each step has a demo checkpoint; don't start the next until the checkpoint passes.

1. **Harness app + module stubs** (§2). *Checkpoint: 4 tabs render.*
2. **Canvas MVP against mocks** (per CANVAS_SPEC 4.1 and `pin_and_paper_canvas/docs/fable-review.md`). *Checkpoint: drag rectangles in harness, 60fps with 100 mock entities.*
3. **Card renderer static** (CARD_RENDERER_SPEC 4.2). *Checkpoint: card gallery tab; then swap canvas mock's `entityBuilder` to real cards — first integration moment, still zero main-app involvement.*
4. **Main app: `task_canvas` migration + `TaskSpatialDataSource`** (§3, minus sync). Add a Spatial/List view toggle behind a debug flag. *Checkpoint: real tasks draggable on desk, positions survive restart.*
5. **Sync for `task_canvas`** (§3 checklist). *Checkpoint: drag on desktop, position appears on second device.*
6. **Canvas 4.3 polish** (rotation, z-order) — pure module work, low risk.
7. **Sketchpad serialization → card drawings (4.5), local-only** (§4).
8. **Phase 5 lighting/polish** — see card_renderer review doc; explicitly bounded so it can't become a rabbit hole.
9. **Journal (6.x)** — after 7; it reuses serialization + textures + the sheet pattern.

Steps 2–3 are pure module work any model can do from the specs + contracts alone. Steps 4–5 need main-app context (give that model CORE_API.md + the sync review findings). Keep those assignments separate — that's your architecture working as designed.

---

## 7. Cross-repo hygiene (do once, ~30 min)

- [ ] Rewrite this repo's `README.md` to say the harness app is not yet built (or build it, §2, and the README becomes true).
- [ ] Fix `CLAUDE.md` spec table → point at `docs/module_specs/*.md`; remove the nonexistent `specs/phase-*` paths.
- [ ] Rename harness "Phase 4.x" → "Phase S4.x (spatial)" or similar, to stop colliding with the main app's Phase 4.0 sync.
- [ ] Regenerate `CORE_API.md` in the main app: DB v12→(v13 after §3), add SyncService/AuthService, fix `resetDatabase`/`setTestDatabase` (they are static), drop the "no Streams" claim.
- [ ] Update `INTERFACE_CONTRACTS.md` per §5 and stamp a new date.
