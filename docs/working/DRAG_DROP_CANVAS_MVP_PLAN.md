# Drag-and-Drop Spatial Canvas — MVP Path to POC

> Implementation plan approved 2026-07-17. Work happens on branch `claude/drag-drop-canvas-mvp-cu6uoy` in each affected repo.

## Context

Pin & Paper's Phase 4 vision is a spatial "desk" where tasks are draggable cards on a pannable/zoomable canvas. Everything from Phase 4.1 onward is specced but unimplemented: `pin_and_paper_canvas` and `pin_and_paper_card_renderer` are empty stubs (`lib/.gitkeep`), the dev harness is docs-only, and the main app (Phase 3.9 + 4.0 sync, DB v12) has no spatial storage or canvas UI.

**Goal — the shortest path to a working POC:**
1. Build the canvas module with a runnable `example/` app (mock cards) to validate gestures in isolation, then integrate into the main app as a "Spatial View" with real tasks. No DevHarnessApp, no sketchpad involvement.
2. Card renderer: MVP slice only — `TaskCardData` + `TagChip` + a simple index-card-styled `TaskCard` (title, tags, due date, completed state). No flip/drawing/textures.
3. Persist positions: DB v12→v13 migration (`canvas_x`, `canvas_y`), `TaskService` update method with `SyncService.logChange`, positions survive restart.

Source-of-truth specs: `docs/module_specs/CANVAS_SPEC.md`, `docs/INTERFACE_CONTRACTS.md`, `docs/PHASE_4_MVP_ROADMAP.md` (§Phase 4.4-MVP), plus pre-approved implementation decisions in `pin_and_paper_canvas/docs/fable-review.md`.

Note: the main app lives nested at `pin-and-paper/pin_and_paper/` inside its repo.

---

## Milestone 1 — Canvas module (`pin_and_paper_canvas`)

### Layout
```
lib/spatial_canvas.dart          # barrel
lib/src/spatial_entity.dart      # abstract: id, position (canvas coords, top-left), rotation, size, zIndex
lib/src/spatial_data_source.dart # abstract ChangeNotifier: getVisibleEntities(Rect), onEntityMoved(id, pos, rot),
                                 #   + concrete no-op onEntityMoving/onEntityTapped/onDoubleTapped/onCanvasTapped/onSelectionChanged
lib/src/viewport_math.dart       # pure functions: screenToCanvas, canvasToScreen, zoomAtFocal, clampPan, viewportMatrix
lib/src/spatial_canvas_controller.dart  # ChangeNotifier: panTo, zoomTo, focusOnEntity, selectEntity, clearSelection;
                                        #   getters visibleRect, currentZoom, selectedIds (attach/detach to state)
lib/src/spatial_canvas.dart      # the widget
example/                         # runnable demo (flutter create . for platforms)
test/viewport_math_test.dart
test/spatial_canvas_test.dart
```
Add `flutter_test`/`flutter_lints` dev deps to the stub pubspec.

### Widget (per CANVAS_SPEC.md + fable-review decisions — plan of record)
```dart
SpatialCanvas({required SpatialDataSource dataSource, required SpatialEntityBuilder entityBuilder,
  required Size canvasSize, SpatialCanvasController? controller,
  double minZoom = 0.5, double maxZoom = 2.0, double? rotationSnapDegrees, double? positionSnapSize})
typedef SpatialEntityBuilder = Widget Function(SpatialEntity entity, bool isSelected);
```
- Rendering: outer `GestureDetector(onScaleStart/Update/End, onTapUp)` → `ClipRect` → `Transform(viewportMatrix)` → canvas-sized `Stack` → per entity (sorted by zIndex, id tie-break): `Positioned` → `RepaintBoundary` → per-card `GestureDetector(onPan*, onTap)` with `ValueKey(entity.id)` → `entityBuilder`. **Not** CustomPaint, **not** InteractiveViewer.
- Viewport: single `onScale*` recognizer — pan via focal delta (pointerCount==1 on empty felt), pinch zoom via `details.scale`, focal-anchored (`newPan = focal - (focal - pan) * (newZoom/oldZoom)`), clamped to min/max zoom; pan clamped to canvas bounds.
- Card drag: child detector wins arena; drag delta ÷ zoom; position clamped to canvasSize; drag tracked in local state (don't mutate entity); `dataSource.onEntityMoved` fired exactly once on `onPanEnd`. Two-finger (pointerCount ≥ 2) cancels an in-flight card drag — viewport wins.
- Tap card → single-select + `onEntityTapped`; tap empty felt → clear selection + `onCanvasTapped(canvasPos)`.
- Listen to dataSource → setState. No viewport culling for MVP (pass full canvas rect).
- **Deferred**: rotation gestures, z-order changes, selection glow, snapping, multi-select, inertia.

### Example app
`MockSpatialDataSource` (per INTERFACE_CONTRACTS.md): ~8 mutable mock entities + a "30 cards" toggle; entityBuilder = colored `Container` with label, border when selected; `onEntityMoved` mutates + `notifyListeners()`. Canvas 2000×1500.

### Tests
- `viewport_math_test.dart`: screen↔canvas round-trips at zoom 0.5/1/2 with nonzero pan; focal-zoom invariant (point under focal stays put); pan clamping at min/max zoom.
- `spatial_canvas_test.dart`: entities render at expected offsets; drag moves card + fires `onEntityMoved` once with correct canvas position (repeat at zoom 2.0 to catch delta÷zoom bugs); edge clamping; tap select/deselect; two-pointer gesture pans viewport and moves no entity; external `notifyListeners` re-renders.

**Checkpoint:** `flutter analyze && flutter test` green in canvas repo; run `example/` on device to feel gestures.

---

## Milestone 2 — Card renderer MVP slice (`pin_and_paper_card_renderer`)

```
lib/card_renderer.dart           # barrel
lib/src/task_card_data.dart      # const TaskCardData{id, title, tags=const[], dueDate?, isCompleted=false, isOverdue=false, notes?}
lib/src/tag_chip.dart            # const TagChip{id, name, Color color, Color textColor}
lib/src/task_card.dart           # StatelessWidget TaskCard{data, isSelected=false, width=220, height=140}
test/task_card_test.dart
```
Index-card styling: cream `Container` (~`0xFFFDF6E3`), rounded 4, soft shadow, thin top accent rule; title with strikethrough + muted when completed (`maxLines`+ellipsis); `Wrap` of tag chips; due-date row (red when overdue); accent border when selected. No sketchpad import (existing path dep stays but unused), no assets.

Test: title renders; completed strikethrough; tag names; due date + overdue styling; no overflow at 220×140 with long title + 5 tags.

**Checkpoint:** `flutter analyze && flutter test` green in card_renderer repo.

---

## Milestone 3 — Main app persistence (DB v13) — shippable independently, no UI change

All in `pin-and-paper/pin_and_paper/`.

1. `lib/utils/constants.dart` → `databaseVersion = 13`.
2. `lib/services/database_service.dart`:
   - After the v12 guard in `_upgradeDB`: `if (oldVersion < 13) await _migrateToV13(db);`
   - `_migrateToV13`: in a transaction, `ALTER TABLE tasks ADD COLUMN canvas_x REAL` + `canvas_y REAL` (nullable; null = never placed). x/y only per approved scope — `canvas_rotation`/`canvas_z` deferred to a later migration when those features land.
   - Add both columns to the tasks `CREATE TABLE` for fresh installs.
3. `lib/models/task.dart`: `double? canvasX/canvasY` fields + `toMap`/`fromMap` (`(map['canvas_x'] as num?)?.toDouble()`) + `copyWith`.
4. `lib/services/task_service.dart` — follow the `updateTaskTitle` pattern:
   ```dart
   Future<void> updateTaskCanvasPosition(String taskId, double x, double y) async {
     // db.update tasks {canvas_x, canvas_y, updated_at}; throw if 0 rows;
     // then SyncService.instance.logChange(tableName: 'tasks', recordId: taskId, operation: 'UPDATE', payload: updateMap);
   }
   ```
   Drag-end only, so no throttling needed. Note in a comment: bumping `updated_at` on drag can win coarse LWW over a concurrent remote edit (pre-existing sync limitation).

**Sync safety (verified):** `localTaskToRemote`/`remoteTaskToLocal` in `sync_service.dart` are explicit column maps, so canvas columns are silently excluded from push/pull and remote merges can't clobber them — Supabase needs no change for the POC. Follow-up to actually sync positions later: Supabase migration adding `canvas_x/canvas_y DOUBLE PRECISION` (+ update `docs/specs/supabase-schema.sql`), then add the fields to both mappers — remote migration must ship first.

**Tests** (existing ffi harness: `test/helpers/test_database_helper.dart`, pattern in `test/services/database_migration_test.dart`):
- v12→v13 upgrade adds columns, data survives; fresh v13 create matches.
- `updateTaskCanvasPosition` round-trip + a `sync_log` row exists with the canvas payload.
- Task `toMap`/`fromMap` canvas-field round-trip incl. nulls.

**Checkpoint:** main app `flutter analyze && flutter test` green; boots on an existing v12 DB.

---

## Milestone 4 — Main app integration (Spatial View)

1. `pubspec.yaml`: path deps `../../pin_and_paper_canvas` and `../../pin_and_paper_card_renderer` (app is nested one level inside its repo; card_renderer transitively pulls sketchpad — verified resolvable).
2. New `lib/spatial/` directory:
   - `task_spatial_entity.dart`: `TaskSpatialEntity implements SpatialEntity` — wraps `Task`, mutable session `position`, `size = Size(220,140)`, `rotation = 0`, `zIndex = task.position` (stable stacking).
   - `task_spatial_data_source.dart`: `TaskSpatialDataSource extends SpatialDataSource` — built from a task snapshot + `TaskService`. `_layout()`: stored `canvasX/canvasY` if non-null, else deterministic grid (~4 cols on a 2000pt canvas: `Offset(40 + col*260, 40 + row*180)`). Grid slots are in-memory only — persisted only when the user drags that card (avoids N sync-log writes on first open). `onEntityMoved`: update entity, `notifyListeners()`, fire-and-forget `taskService.updateTaskCanvasPosition` with error logging.
   - `task_card_adapter.dart`: `taskToCardData(Task, List<Tag>)` per the roadmap, using `TagColors.hexToColor`/`TagColors.getTextColor` (both take the hex string) with `#2196F3`/white fallback; `isOverdue = dueDate < now && !completed`.
3. `lib/screens/canvas_screen.dart`: StatefulWidget; `initState` snapshots `context.read<TaskProvider>().tasks` and builds the data source once (dispose in `dispose`); body = `SpatialCanvas(canvasSize: Size(2000,1500), entityBuilder: (e, sel) => TaskCard(data: taskToCardData((e as TaskSpatialEntity).task, taskProvider.getTagsForTask(id)), isSelected: sel))`. Snapshot semantics: reopening refreshes; live task edits elsewhere don't appear while open (acceptable for POC).
4. `lib/screens/home_screen.dart`: one AppBar `IconButton` (`Icons.space_dashboard_outlined`, tooltip "Spatial View") → `Navigator.push(MaterialPageRoute(builder: (_) => const CanvasScreen()))`, following the existing AppBar-action pattern. No `main.dart` provider changes.
5. Headless integration test: seed tasks with/without stored positions via the ffi helper → build `TaskSpatialDataSource` → assert stored positions honored + null-position tasks get non-overlapping grid slots → `onEntityMoved` → assert DB row updated (headless proxy for "survives restart").

---

## Execution order
1. **M1a** viewport math + tests (pure Dart — surface the focal-zoom math first)
2. **M1b** SpatialCanvas widget + gesture tests + example app
3. **M2** card_renderer slice + test
4. **M3** migration/model/service + tests
5. **M4** deps + adapters + screen + entry button + integration test

Commit per milestone using the harness convention (`feat(canvas): …`, `feat(card): …`, `feat(app): …`); push each repo to `claude/drag-drop-canvas-mvp-cu6uoy`.

## Verification

Headless (CI-able): `flutter analyze && flutter test` in all three repos; `flutter pub get` in the main app proves path-dep resolution; full existing main-app suite as regression.

Device (manual): example app — pan, focal-anchored pinch (clamped 0.5–2.0), drag at zoom≠1 with no drift, two-finger always pans, tap select/deselect. Main app — fresh install **and** v12-upgrade install; open Spatial View → real tasks as index cards → drag several → force-kill → relaunch → positions retained → back to list → no crashes at 20+ tasks; if sync is on, confirm no Supabase errors after a drag.

## Known POC limitations (accepted)
- Undragged cards re-grid on each entry (positions persist only after first drag).
- Canvas is a snapshot; doesn't live-update while open.
- Hierarchy flattened — subtasks appear as their own cards.
- Positions are local-only (excluded from sync mappers) until the Supabase follow-up.

## Risk to watch
Widget-test gesture arena (outer scale recognizer vs child pan) is the flakiest area — it's why M1a/M1b tests come first, before any app wiring depends on the gesture layer.

---

## Progress log (2026-08-03)

- **M1 (canvas module) — done.** `pin_and_paper_canvas`, branch `claude/drag-drop-canvas-mvp-cu6uoy`, commits `4becd12`(M1a viewport math)`..2ee2a5f`. Includes a hit-test fix (`843e79a` — cards beyond the viewport's laid-out bounds were visible but untappable when zoomed out/panned; fixed via `OverflowBox`) and a post-implementation UX round from owner feedback: drag-start now selects the card (`81fbd0b`), dragged/selected cards render above their zIndex tier (`4980e5e`), trackpad is excluded from per-card gestures so it always pans the viewport (`98240b7`), and an optional `background` param delineates the usable canvas (`b6e2374`). See `pin_and_paper_canvas/docs/fable-review.md`'s as-built addendum (top of file) and `docs/INTERFACE_CONTRACTS.md`'s 2026-08-03 notes for the drag-delta and `SpatialDataSource`-is-a-`ChangeNotifier` deviations this milestone landed.
- **M2 (card renderer) — done.** `pin_and_paper_card_renderer`, same branch, commits `32c9361..ba773c7`: `TaskCardData`/`TagChip` render models, the index-card-styled `TaskCard` widget (`kCardSize` 220×140, `kTaskCardSurfaceKey`), and widget tests. Previewed in the canvas module's own `example/` app (`3e705ec`, "preview real TaskCards in the example app") rather than a harness — the pattern Milestone 4 will repeat in the main app. See `docs/INTERFACE_CONTRACTS.md` Part 2 for the as-built `TaskCard` contract.
- **M3 (main app persistence, DB v13) — not started.** `pin-and-paper` is still on `databaseVersion = 12`; no `canvas_x`/`canvas_y` migration, no `updateTaskCanvasPosition` on `TaskService` yet.
- **M4 (main app integration) — not started**, blocked on M3.

## Progress log addendum — 2026-08-03 (late)
- M3 DONE: `bae5bc7` on pin-and-paper branch, verified 65/65, pushed.
- M4 BUILT: `f8348e5` committed locally; full-suite verification was in flight at handoff — verify then push. All addendum items 1-11 implemented incl. landing tray + isTaskOverdue extraction.
- Amethyst desk object + shadow work: see docs/working/HANDOFF-2026-08-03.md.

## Progress log addendum — 2026-08-03 (final)
- M4 DONE: `f8348e5` + test fixes `7b461d7`, verified EXIT=0, pushed. POC
  M1–M4 complete across all three repos. Follow-ups landed on the branch:
  completed-task tray exclusion (`ca5063e`), amethyst on the real desk +
  arrange toggle + tray render cap (`b833c09`), stale-Task canvas-clobber
  fix in toggleTaskCompletion (`2504e9a`).
- REMAINING for POC sign-off: owner manual pass (desktop + Android, fresh
  install AND v12-upgrade install) per §Verification — approved to proceed
  with queued follow-ups while this is pending (owner, 2026-08-03).
