# Interface Contracts

**Purpose:** This document defines the interfaces between the main Pin and Paper app and the visual modules (canvas, card_renderer, journal). Module developers only need this document — not the full CORE_API.md.

**Source:** Extracted from CORE_API.md (main app)
**Last Updated:** 2026-01-30 (Parts 1, 2, and the Part 7 canvas mock example refreshed **2026-08-03** against the as-built `pin_and_paper_canvas`/`pin_and_paper_card_renderer` code, now that Milestones 1–2 of `docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md` are built — see inline "as-built" notes for what changed and why. Parts 3–6 are untouched; journal is still Phase 6/unimplemented.)

---

## Overview

Visual modules don't access the database or business logic directly. Instead, they:
1. Receive data through **DataSource interfaces** (implemented by main app)
2. Call back through interface methods when user interacts
3. Work with **simplified data types** (not the full Task model)

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   Main App      │────────▶│  Visual Module  │
│                 │         │                 │
│   implements    │◀────────│   calls back    │
│   DataSource    │         │   via interface │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
```

---

## Part 1: Spatial Canvas Interfaces

Used by `pin_and_paper_canvas` module.

### SpatialEntity

Anything that can be positioned on the spatial canvas.

```dart
/// Implemented by main app for Task objects
abstract class SpatialEntity {
  /// Unique identifier
  String get id;
  
  /// Position on canvas (top-left corner)
  Offset get position;
  
  /// Rotation in degrees (0 = upright, positive = clockwise)
  double get rotation;
  
  /// Advisory visual size of the entity, in canvas units.
  Size get size;
  
  /// Z-order for layering (higher = on top)
  int get zIndex;
}
```

> **As-built note (2026-08-03):** confirmed unchanged from this draft. But `size` is not merely advisory in practice — `SpatialCanvas` clamps drag position so the entity's `size` rectangle never leaves `canvasSize`'s bounds (`0 ≤ position.dx ≤ canvasSize.width - entity.size.width`, same for Y/height). It's also what the canvas uses for hit-testing and (later) culling. Keep it in sync with whatever `entityBuilder` actually renders — `pin_and_paper_card_renderer`'s `kCardSize` (220×140) is deliberately equal to the size a `TaskCard`-backed entity should report.

### SpatialDataSource

Canvas module calls these methods; main app implements.

```dart
/// As-built (2026-08-03): this is an abstract class extending
/// ChangeNotifier, NOT a plain interface as originally drafted below. The
/// canvas widget calls addListener on the data source it's given and
/// re-queries getVisibleEntities() whenever the source calls
/// notifyListeners() — e.g. after an external edit to the task list —
/// without waiting for a gesture. Only getVisibleEntities and onEntityMoved
/// are abstract; every other member has a no-op default body so minimal
/// data sources (mocks, tests) don't have to implement callbacks they don't
/// care about.
abstract class SpatialDataSource extends ChangeNotifier {
  /// Get all entities that should render in the given viewport.
  /// 
  /// MVP note: the canvas does not cull for this milestone — it always
  /// passes the full canvas rect — so implementations may ignore
  /// [viewport], but should still honor it when cheap (future culling,
  /// larger datasets). Called frequently during pan/zoom — keep it fast.
  List<SpatialEntity> getVisibleEntities(Rect viewport);
  
  /// Called exactly once, on gesture end, when the user finishes dragging
  /// an entity. [position] is the new top-left in canvas coordinates,
  /// already clamped to canvas bounds. This is a hard contract requirement
  /// (fable-review.md §1.5): the canvas must not call this per-frame during
  /// a drag, only once on release — implementations should persist to the
  /// database here, not trigger a full reload (the entity already moved
  /// visually).
  void onEntityMoved(String id, Offset position, double rotation);

  /// **New in the as-built API** (not in the original draft above):
  /// optional live-update hook, called on every drag frame while an entity
  /// is being dragged. Default no-op; most data sources should ignore it
  /// and rely on [onEntityMoved]. Exists for consumers that want to mirror
  /// in-progress drags elsewhere (e.g. a minimap) without persisting.
  void onEntityMoving(String id, Offset position, double rotation) {}
  
  /// Called when user single-taps an entity (selects it).
  ///
  /// **Deviation from the original draft (2026-08-03):** this is NOT the
  /// only path to selection. Starting a drag also selects the card —
  /// `SpatialCanvas` fires `onSelectionChanged` at drag-start, not
  /// `onEntityTapped` (owner feedback 2026-08-03: the selection glow never
  /// appeared on drag-only interactions). Taps and drags stay distinct
  /// events; watch `onSelectionChanged`, not just `onEntityTapped`, if you
  /// need to know whenever the selected set changes.
  void onEntityTapped(String id) {}
  
  /// Called when user double-taps an entity.
  void onEntityDoubleTapped(String id) {}
  
  /// Called when user taps empty canvas ("felt"). The canvas clears its own
  /// selection state before calling this.
  void onCanvasTapped(Offset position) {}
  
  /// Called whenever the canvas's selection set changes, with the full
  /// current set of selected ids.
  void onSelectionChanged(Set<String> selectedIds) {}
}
```

### SpatialCanvas (the widget)

**New section (2026-08-03).** The original contract draft covered only the data types module developers implement against — it didn't cover the widget itself. Anyone integrating the canvas (writing an `entityBuilder`, wiring up the main app) needs this too:

```dart
class SpatialCanvas extends StatefulWidget {
  const SpatialCanvas({
    required SpatialDataSource dataSource,
    required SpatialEntityBuilder entityBuilder,
    required Size canvasSize,
    SpatialCanvasController? controller,
    double minZoom = 0.5,
    double maxZoom = 2.0,
    double? rotationSnapDegrees,
    double? positionSnapSize,
    Widget? background,
  });
}

typedef SpatialEntityBuilder = Widget Function(SpatialEntity entity, bool isSelected);
```

- `canvasSize` — the bounded desk's dimensions. Entities can't be dragged outside it; the viewport can't pan past it beyond a ~50px felt margin.
- `minZoom`/`maxZoom` — default 0.5–2.0 (matches CANVAS_SPEC.md).
- `rotationSnapDegrees` / `positionSnapSize` — **accepted but inert in this milestone.** They exist only for API-shape parity with CANVAS_SPEC.md and later milestones; no gesture wires them up yet (there is no rotation gesture at all yet, and drags aren't snapped).
- `background` — optional decorative backdrop painted at exactly `canvasSize`, beneath every entity, wrapped in `IgnorePointer` so it never intercepts hit-testing.

**Behavioral notes (as-built, 2026-08-03):**
- Dragged and selected cards always render *above* their zIndex tier — data-side `zIndex` still governs stacking within a tier (dragged > selected > plain), but "currently being touched" or "currently selected" wins over it for paint/hit-test order, so the card you're interacting with is never buried mid-gesture.
- The per-card `GestureDetector` excludes `PointerDeviceKind.trackpad` — a two-finger trackpad pan/pinch over a card always falls through to the outer canvas viewport gesture, never gets claimed by the card's own drag/tap recognizers.
- **Known deviation from fable-review.md §1.3/§1.4's literal text** ("drag delta must be divided by zoom"): the as-built handler does *not* divide the drag delta by zoom, and this is correct, not a bug — Flutter's `DragUpdateDetails.delta` is already expressed in the local (post-scale) coordinate space of the widget receiving the gesture, since the per-card `GestureDetector` lives inside `Transform(viewportMatrix)`. Dividing again would double-divide (invisible at zoom 1.0, silently halves every drag at zoom 2.0). See `pin_and_paper_canvas/docs/fable-review.md`'s as-built addendum (top of file) and `test/spatial_canvas_test.dart`'s zoom-2.0 drag test, which is what caught this.

### SpatialCanvasController

Optional controller for programmatic canvas manipulation.

```dart
abstract class SpatialCanvasController {
  /// Pan viewport to center on position
  void panTo(Offset position);
  
  /// Set zoom level (1.0 = 100%)
  void zoomTo(double scale);
  
  /// Programmatically select an entity
  void selectEntity(String id);
  
  /// Clear all selections
  void clearSelection();
  
  /// Get currently visible rectangle in canvas coordinates
  Rect get visibleRect;
  
  /// Get current zoom level
  double get currentZoom;
}
```

> **As-built note (2026-08-03):** the shape above is close but incomplete. The real `SpatialCanvasController` is a **concrete class extending `ChangeNotifier`** (the standard Flutter controller pattern, cf. `ScrollController`) — not an abstract interface module developers implement. It doesn't hold viewport state itself; it attaches to whichever `SpatialCanvas` widget instance is currently using it and delegates to that widget's state. Before attachment (or after the widget disposes), getters return sensible defaults and imperative calls are no-ops. Two more differences:
> - Every imperative method takes an `{bool animate = true}` named parameter (`panTo`, `zoomTo`), omitted above.
> - There's a fourth imperative method not listed above: `void focusOnEntity(String id, {bool animate = true})` — pans (and, in the future, could zoom out) so the entity with `id` is visible and centered; no-op if `id` isn't currently known to the data source.
> - There's a third getter not listed above: `Set<String> get selectedIds` — currently selected entity ids; empty before attachment.

---

## Part 2: Card Renderer Interfaces

Used by `pin_and_paper_card_renderer` module.

### TaskCardData

Simplified task data for rendering. NOT the full Task model.

```dart
/// What the card renderer needs to display a task
class TaskCardData {
  /// Unique identifier (matches Task.id)
  final String id;
  
  /// Task title text
  final String title;
  
  /// Tags to display as chips
  final List<TagChip> tags;
  
  /// Due date (null = no due date)
  final DateTime? dueDate;
  
  /// Whether task is completed
  final bool isCompleted;
  
  /// Whether task is past due
  final bool isOverdue;
  
  /// Optional notes/description
  final String? notes;
  
  const TaskCardData({
    required this.id,
    required this.title,
    this.tags = const [],
    this.dueDate,
    this.isCompleted = false,
    this.isOverdue = false,
    this.notes,
  });
}
```

### TagChip

Minimal tag info for display.

```dart
/// Tag display data
class TagChip {
  final String id;
  final String name;
  final Color color;
  final Color textColor;  // WCAG AA compliant
  
  const TagChip({
    required this.id,
    required this.name,
    required this.color,
    required this.textColor,
  });
}
```

> **As-built note (2026-08-03):** `TaskCardData` and `TagChip` are confirmed unchanged from this draft — field-for-field match in `pin_and_paper_card_renderer/lib/src/task_card_data.dart` and `tag_chip.dart`.

### TaskCard (the widget)

**New section (2026-08-03).** The original draft covered the data types but not the rendering widget itself, which now exists (Milestone 2 of `docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md`):

```dart
class TaskCard extends StatelessWidget {
  const TaskCard({
    required TaskCardData data,
    bool isSelected = false,
    double width = 220,
    double height = 140,
  });
}

/// Standard card footprint — width/height above are kept in sync with this
/// by hand (task_card_test.dart asserts they're equal, since Size's fields
/// aren't const-foldable into the constructor defaults).
const Size kCardSize = Size(220, 140);

/// Key on the card's outer decorated surface, for tests to assert on
/// selection styling without depending on widget-tree traversal order.
const Key kTaskCardSurfaceKey = Key('pin_and_paper_card_renderer.task_card.surface');
```

- Renders title (2 lines, ellipsis; strikethrough + muted ink when `isCompleted`), a scrollable `Wrap` of tag chips, and a due-date row (red when `isOverdue`) — index-card styling (cream background, thin gold top rule, amber selection border+glow).
- **MVP slice only:** no flip, no drawing integration, no torn edges/paper texture/dynamic lighting — those are explicitly deferred to Phase 5 per `CARD_RENDERER_SPEC.md` and fable-review.md's "bake, don't simulate" guide. `TaskCardData.notes` is accepted by the constructor but unused by `TaskCard` today (forward-compat for a future card-back/detail view).
- Stateless by design: every visual state (selected/completed/overdue) derives purely from `data`/`isSelected`, so a data source can rebuild this on every change with no card-local state to reconcile.
- `kCardSize` is what a canvas entity backing a task card should report as `SpatialEntity.size` — see the as-built note on `SpatialEntity.size` in Part 1: the canvas's drag-clamping is tight to entity size, and `TaskCard` is tuned to read well at exactly this footprint.

### CardDrawingSource

For persisting drawings on cards.

```dart
abstract class CardDrawingSource {
  /// Get drawing layers for a card side.
  /// Returns null if no drawing exists.
  Future<LayerStack?> getDrawing(String cardId, CardSide side);
  
  /// Save drawing layers for a card side.
  Future<void> saveDrawing(String cardId, CardSide side, LayerStack layers);
  
  /// Delete drawing for a card side.
  Future<void> deleteDrawing(String cardId, CardSide side);
}

enum CardSide { front, back }
```

> **Status (2026-08-03):** specified here, not yet implemented. There is no drawing integration anywhere in `pin_and_paper_card_renderer` yet — `CardDrawingSource` describes a Phase 5 contract, not as-built code. Don't expect to find this type in the module today.

---

## Part 3: Journal Interfaces

Used by `pin_and_paper_journal` module.

### CompletedTaskEntry

A task as it appears in the journal.

```dart
/// Completed task for journal display
class CompletedTaskEntry {
  /// Task ID (for navigation back to task)
  final String taskId;
  
  /// Task title at time of completion
  final String title;
  
  /// When the task was completed
  final DateTime completedAt;
  
  /// Tags at time of completion
  final List<TagChip> tags;
  
  const CompletedTaskEntry({
    required this.taskId,
    required this.title,
    required this.completedAt,
    this.tags = const [],
  });
}
```

### JournalPage

A single day's journal page.

```dart
/// Journal page data
class JournalPage {
  /// The date this page represents
  final DateTime date;
  
  /// Tasks completed on this date (auto-populated)
  final List<CompletedTaskEntry> tasks;
  
  /// User drawings on this page (null = no drawings yet)
  final LayerStack? drawings;
  
  /// User notes/text (null = no notes yet)
  final String? userNotes;
  
  /// Page layout template
  final PageTemplate template;
  
  /// Paper texture/background
  final PaperTexture texture;
  
  const JournalPage({
    required this.date,
    this.tasks = const [],
    this.drawings,
    this.userNotes,
    this.template = PageTemplate.daily,
    this.texture = PaperTexture.cream,
  });
  
  /// Whether user has added any content
  bool get hasUserContent => drawings != null || userNotes != null;
  
  /// Whether page has any content at all
  bool get isEmpty => tasks.isEmpty && !hasUserContent;
  
  JournalPage copyWith({...});
}

enum PageTemplate { daily, weeklySpread, blank }

enum PaperTexture { cream, kraft, dotGrid, lined, graph }
```

### JournalDataSource

Journal module calls these; main app implements.

```dart
abstract class JournalDataSource {
  /// Get all tasks completed on a specific date.
  /// 
  /// Date should be normalized to midnight.
  /// Returns empty list if no completions that day.
  Future<List<CompletedTaskEntry>> getCompletedTasks(DateTime date);
  
  /// Load journal page data.
  /// 
  /// If no page exists, returns a new page with:
  /// - Auto-populated completed tasks for that date
  /// - Default template and texture
  /// - No drawings or notes
  Future<JournalPage> getPage(DateTime date);
  
  /// Save journal page data.
  /// 
  /// Persists drawings, notes, template, texture.
  /// Does NOT modify completed tasks (those are read-only in journal).
  Future<void> savePage(JournalPage page);
  
  /// User tapped a completed task in the journal.
  /// 
  /// Implementation should navigate to that task in list/spatial view.
  void navigateToTask(String taskId);
  
  /// Get the date range containing completed tasks.
  /// 
  /// Used for:
  /// - Navigation bounds (don't let user scroll to 1970)
  /// - Activity indicators (which dates have content)
  Future<DateTimeRange> getActivityRange();
}
```

### JournalController

For programmatic journal control.

```dart
abstract class JournalController {
  /// Open the journal sheet
  void open();
  
  /// Close the journal sheet
  void close();
  
  /// Navigate to specific date
  void goToDate(DateTime date);
  
  /// Navigate to today
  void goToToday();
  
  /// Current open state
  bool get isOpen;
  
  /// Currently displayed date
  DateTime get currentDate;
}
```

---

## Part 4: Shared Types

Types used across multiple modules.

### Colors

```dart
/// Pin and Paper color palette
class PinAndPaperColors {
  static const Color warmWood = Color(0xFF8B7355);
  static const Color kraftPaper = Color(0xFFD4B896);
  static const Color creamPaper = Color(0xFFF5F1E8);
  static const Color deepShadow = Color(0xFF4A3F35);
  static const Color mutedLavender = Color(0xFF9B8FA5);
  
  // Ink colors for drawing
  static const Color inkBlack = Color(0xFF2D2D2D);
  static const Color inkBrown = Color(0xFF4A3F35);
  
  // State colors
  static const Color overdue = Color(0xFFC75B4A);
  static const Color completed = Color(0xFF5B8C7A);
}
```

### Tag Preset Colors

```dart
/// The 12 Material Design preset colors for tags
/// All are WCAG AA compliant with their text colors
class TagColors {
  static const List<Color> presets = [
    Color(0xFF2196F3),  // Blue (default)
    Color(0xFF4CAF50),  // Green
    Color(0xFFFF9800),  // Orange
    Color(0xFFF44336),  // Red
    Color(0xFF9C27B0),  // Purple
    Color(0xFF00BCD4),  // Cyan
    Color(0xFFFFEB3B),  // Yellow
    Color(0xFF795548),  // Brown
    Color(0xFF607D8B),  // Blue Grey
    Color(0xFFE91E63),  // Pink
    Color(0xFF3F51B5),  // Indigo
    Color(0xFF009688),  // Teal
  ];
  
  /// Get text color (black or white) for a background color
  /// Ensures WCAG AA compliance (4.5:1 contrast ratio)
  static Color getTextColor(Color background) {
    final luminance = background.computeLuminance();
    return luminance > 0.5 ? Colors.black : Colors.white;
  }
}
```

### User Display Preferences

Settings that affect how visual modules render.

```dart
/// Display preferences from UserSettings
/// Visual modules receive these, don't modify them
class DisplayPreferences {
  /// 12-hour (false) or 24-hour (true) time display
  final bool use24HourTime;
  
  /// What hour "today" rolls over for night owls (e.g., 4 = 4:59 AM)
  final int todayCutoffHour;
  
  /// First day of week (0 = Sunday, 1 = Monday, etc.)
  final int weekStartDay;
  
  /// User's timezone ID (IANA format)
  final String? timezoneId;
  
  const DisplayPreferences({
    this.use24HourTime = false,
    this.todayCutoffHour = 4,
    this.weekStartDay = 0,
    this.timezoneId,
  });
}
```

---

## Part 5: Sketchpad Types

Re-exported from `pin_and_paper_sketchpad` for other modules.

```dart
// These are defined in sketchpad module but used by card_renderer and journal

/// A stack of drawing layers
class LayerStack {
  List<DrawingLayer> layers;
  int activeLayerIndex;
  
  DrawingLayer get activeLayer;
  Iterable<DrawingLayer> get visibleLayers;
  
  void addStrokeToActiveLayer(Stroke stroke);
  void undoOnActiveLayer();
  void toggleLayerVisibility(int index);
}

/// A single drawing layer
class DrawingLayer {
  String id;
  String name;
  bool visible;
  double opacity;
  BlendMode blendMode;
  List<Stroke> strokes;
  List<EraserStroke> eraserStrokes;
  StrokeOptions defaultOptions;
}

/// Stroke options (pressure sensitivity, smoothing, etc.)
class StrokeOptions {
  double size;
  double thinning;
  double smoothing;
  double streamline;
  double taperStart;
  double taperEnd;
  
  static const StrokeOptions ink;
  static const StrokeOptions sketch;
  static const StrokeOptions color;
}
```

See `SKETCHPAD_SPEC.md` for full details.

---

## Part 6: Event Patterns

Visual modules don't subscribe to streams. Instead:

### State Changes Flow Down

Main app passes updated data to modules via widget rebuilds:

```dart
// Main app widget
SpatialCanvas(
  dataSource: _taskSpatialSource,  // Provides current data
  entityBuilder: (entity, isSelected) => TaskCard(...),
)
```

When main app state changes (e.g., task completed), it rebuilds the widget tree with new data.

### User Actions Flow Up

Modules call DataSource methods when user interacts:

```dart
// Inside canvas module
void _onCardDragged(String id, Offset newPosition) {
  widget.dataSource.onEntityMoved(id, newPosition, _rotation);
}
```

### Events Visual Modules Should Handle

| Event | Source | Module Response |
|-------|--------|-----------------|
| Entity dragged | User gesture | Call `onEntityMoved()` |
| Entity tapped | User gesture | Call `onEntityTapped()` |
| Entity double-tapped | User gesture | Call `onEntityDoubleTapped()` |
| Canvas tapped | User gesture | Call `onCanvasTapped()` |
| Card flipped | User gesture | Internal state (optionally notify via callback) |
| Drawing changed | User gesture | Call `CardDrawingSource.saveDrawing()` |
| Page swiped | User gesture | Load new page via `getPage()` |
| Task tapped in journal | User gesture | Call `navigateToTask()` |

---

## Part 7: Mock Implementations

For dev harness and testing. See `ARCHITECTURE_AND_HARNESS.md` for full mock implementations.

### Minimal Mock Example

> **As-built note (2026-08-03):** the example below predates `SpatialDataSource` becoming a `ChangeNotifier` (see Part 1) and is stale in the same way `ARCHITECTURE_AND_HARNESS.md` Part 3's `MockSpatialDataSource` is — `implements` plus manual `print` callbacks, no `notifyListeners()`. Kept here for the shape of "what a minimal mock covers"; the real bundled example (`pin_and_paper_canvas/example/lib/mock_spatial_data_source.dart`) `extends SpatialDataSource` and calls `notifyListeners()` from `onEntityMoved`, which is what the canvas widget actually needs to pick up the change.

```dart
class MockSpatialDataSource implements SpatialDataSource {
  final List<MockTaskEntity> _tasks = [
    MockTaskEntity(id: '1', title: 'Brush Woolfie', position: Offset(100, 150)),
    MockTaskEntity(id: '2', title: 'Call mom', position: Offset(300, 200)),
  ];
  
  @override
  List<SpatialEntity> getVisibleEntities(Rect viewport) => _tasks;
  
  @override
  void onEntityMoved(String id, Offset position, double rotation) {
    final task = _tasks.firstWhere((t) => t.id == id);
    task.position = position;
    task.rotation = rotation;
  }
  
  @override
  void onEntityTapped(String id) => print('Tapped: $id');
  
  @override
  void onEntityDoubleTapped(String id) => print('Double-tapped: $id');
  
  @override
  void onCanvasTapped(Offset position) => print('Canvas tap: $position');
  
  @override
  void onSelectionChanged(Set<String> ids) => print('Selection: $ids');
}
```

---

## Summary

| Module | Receives | Calls Back |
|--------|----------|------------|
| **canvas** | `SpatialEntity` list | `SpatialDataSource` methods |
| **card_renderer** | `TaskCardData` | `CardDrawingSource` for drawings |
| **journal** | `JournalPage` | `JournalDataSource` methods |
| **sketchpad** | `LayerStack` | Direct modification (passed by reference) |

Module developers: Implement your UI against these interfaces. The main app will provide real implementations; the dev harness provides mocks.

---

*These contracts are stable. If they change, INTERFACE_CONTRACTS.md is updated and module teams are notified.*
