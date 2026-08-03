# Phase S4 MVP Roadmap (spatial)

**Goal:** Validate the spatial architecture with a working vertical slice.

**Success criteria:** "I can see task cards on a canvas and drag them around."

---

## Philosophy

Build "good enough" versions of each piece, then wire them together early. Polish later.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Sketchpad ✓        Canvas MVP        Card Renderer MVP    │
│   (done)             (pan/drag)        (static display)     │
│                                                             │
│                            ↓                                │
│                                                             │
│                   Integration MVP                           │
│                   (wire together)                           │
│                                                             │
│                            ↓                                │
│                                                             │
│                   Polish Each Piece                         │
│                   (rotation, flip, eraser, etc.)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Current Status

| Module | Status | MVP Ready? |
|--------|--------|------------|
| Sketchpad | Prototype working, eraser done! | ✅ Yes |
| Canvas | Stub only | ❌ Not started |
| Card Renderer | Stub only | ❌ Not started |
| Integration | N/A | ❌ Waiting on above |

---

## Phase S4.1-MVP: Canvas Foundation

**Duration:** 1-2 weeks
**Goal:** Pan, zoom, and drag rectangles on a bounded canvas

### What to Build

- [ ] `SpatialCanvas` widget
- [ ] Viewport state (offset + scale)
- [ ] Two-finger pan gesture
- [ ] Pinch-to-zoom gesture
- [ ] Render entities at positions
- [ ] Single-finger drag to move entity
- [ ] Basic hit testing (which entity was tapped?)
- [ ] Canvas bounds (can't drag off edge)

### What to Skip (for now)

- ❌ Rotation gesture
- ❌ Selection state / glow
- ❌ Z-ordering management
- ❌ Grid snapping
- ❌ Double-tap handling
- ❌ Multi-select

### Interface Contract Needed

From `INTERFACE_CONTRACTS.md`, you need:

**Part 1: SpatialEntity**
```dart
abstract class SpatialEntity {
  String get id;
  Offset get position;
  double get rotation;  // Can ignore for MVP
  Size get size;
  int get zIndex;       // Can ignore for MVP
}
```

**Part 1: SpatialDataSource**
```dart
abstract class SpatialDataSource {
  List<SpatialEntity> getVisibleEntities(Rect viewport);
  void onEntityMoved(String id, Offset position, double rotation);
  void onEntityTapped(String id);          // Basic impl okay
  void onCanvasTapped(Offset position);    // Basic impl okay
  // Skip: onEntityDoubleTapped, onSelectionChanged
}
```

### Deliverable

A demo where you can:
1. See colored rectangles on a canvas
2. Pan the canvas with two fingers
3. Zoom with pinch
4. Drag a rectangle with one finger
5. Rectangle stays where you put it

### Test With

Hardcoded mock entities:
```dart
final mockEntities = [
  MockEntity(id: '1', position: Offset(100, 100), size: Size(200, 120)),
  MockEntity(id: '2', position: Offset(350, 200), size: Size(200, 120)),
  MockEntity(id: '3', position: Offset(200, 400), size: Size(200, 120)),
];
```

---

## Phase S4.2-MVP: Card Renderer Foundation

**Duration:** 1-2 weeks
**Goal:** A static card widget that looks like an index card

### What to Build

- [ ] `TaskCard` widget
- [ ] Index card style (cream background, ruled lines)
- [ ] Title display
- [ ] Tag chips display
- [ ] Due date display (formatted nicely)
- [ ] Basic drop shadow
- [ ] Visual states: normal, completed (muted + strikethrough)

### What to Skip (for now)

- ❌ Torn paper edges
- ❌ Flip animation
- ❌ Card back
- ❌ Drawing integration
- ❌ Pushpins
- ❌ Overdue state styling
- ❌ Selection glow
- ❌ Multiple card styles

### Interface Contract Needed

From `INTERFACE_CONTRACTS.md`, you need:

**Part 2: TaskCardData**
```dart
class TaskCardData {
  final String id;
  final String title;
  final List<TagChip> tags;
  final DateTime? dueDate;
  final bool isCompleted;
  final bool isOverdue;     // Can ignore for MVP
  final String? notes;      // Can ignore for MVP
}
```

**Part 2: TagChip**
```dart
class TagChip {
  final String id;
  final String name;
  final Color color;
  final Color textColor;
}
```

### Deliverable

A widget that displays:
```
┌─────────────────────────────────┐
│ ══════════════════════════════  │  ← Ruled line
│ Call mom tomorrow               │  ← Title
│ ──────────────────────────────  │
│ [family] [weekly]               │  ← Tag chips
│                                 │
│                     2:00 PM 📅  │  ← Due date
└─────────────────────────────────┘
       ░░░░░░░░░░░░░░░░░           ← Shadow
```

### Test With

Hardcoded mock card data:
```dart
final mockCard = TaskCardData(
  id: '1',
  title: 'Call mom tomorrow',
  tags: [
    TagChip(id: 't1', name: 'family', color: Colors.pink, textColor: Colors.white),
    TagChip(id: 't2', name: 'weekly', color: Colors.blue, textColor: Colors.white),
  ],
  dueDate: DateTime.now().add(Duration(days: 1)),
  isCompleted: false,
);
```

---

## Phase S4.4-MVP: Integration

**Duration:** 1 week
**Goal:** Wire canvas + card_renderer together with real tasks

### What to Build

- [ ] Add canvas and card_renderer as dependencies to main app
- [ ] Create `TaskSpatialEntity` implementing `SpatialEntity`
- [ ] Create `TaskSpatialDataSource` implementing `SpatialDataSource`
- [ ] Create `Task` → `TaskCardData` transformer
- [ ] Add spatial columns to database (migration v12):
  - `canvas_x` REAL
  - `canvas_y` REAL
  - `canvas_rotation` REAL (for later, default 0)
  - `canvas_z` INTEGER (for later, default 0)
- [ ] Basic layout algorithm (position tasks in grid initially)
- [ ] Add "Spatial View" toggle/button somewhere

### What to Skip (for now)

- ❌ Smooth view transitions
- ❌ Persisting zoom/pan state
- ❌ Complex layout algorithms
- ❌ Drawing on cards

### The Transform

```dart
// In main app
TaskCardData taskToCardData(Task task, List<Tag> tags) {
  return TaskCardData(
    id: task.id,
    title: task.title,
    tags: tags.map((t) => TagChip(
      id: t.id,
      name: t.name,
      color: hexToColor(t.color ?? '#2196F3'),
      textColor: getTextColor(t.color),
    )).toList(),
    dueDate: task.dueDate,
    isCompleted: task.completed,
    isOverdue: task.dueDate != null && 
               task.dueDate!.isBefore(DateTime.now()) && 
               !task.completed,
  );
}
```

### Deliverable

In the main app:
1. Button/toggle to enter "Spatial View"
2. See your actual tasks as cards on a canvas
3. Drag cards around
4. Positions persist (saved to DB)
5. Switch back to list view

---

## After MVP: Polish Phases

Once the vertical slice works, go back and add features:

### Canvas Polish (S4.3+)
- Two-finger rotation
- Selection state + glow
- Z-ordering (tap brings to front)
- Double-tap to open detail
- Grid snapping (optional)

### Card Renderer Polish (S4.5+)
- Torn paper edges
- Flip animation
- Card back design
- Drawing integration (sketchpad on cards)
- Multiple card styles
- Pushpin decorations
- Overdue styling

### Sketchpad Polish (ongoing)
- ✅ Eraser (done!)
- Shape correction
- More brush presets
- Undo/redo

### Advanced (Phase 5+)
- Dynamic shadows (time-based)
- Lighting effects
- Conspiracy strings between cards
- Performance optimization for 100+ cards

---

## Working With AI Teams

### For Canvas S4.1-MVP

**Give the AI:**
1. This section of this doc (Phase S4.1-MVP)
2. The `SpatialEntity` and `SpatialDataSource` interfaces from INTERFACE_CONTRACTS.md
3. Current canvas repo code (empty/stub)

**Prompt:**
> "We're building Canvas S4.1-MVP: pan, zoom, and drag. Here's the scope and interfaces. Let's start with the basic SpatialCanvas widget structure."

### For Card Renderer S4.2-MVP

**Give the AI:**
1. This section of this doc (Phase S4.2-MVP)
2. The `TaskCardData` and `TagChip` types from INTERFACE_CONTRACTS.md
3. Current card_renderer repo code (empty/stub)

**Prompt:**
> "We're building Card Renderer S4.2-MVP: a static index card display. Here's the scope and data types. Let's start with the TaskCard widget."

### For Integration S4.4-MVP

**Give the AI:**
1. This section of this doc (Phase S4.4-MVP)
2. Both interfaces (SpatialDataSource + TaskCardData)
3. The main app's Task model (from CORE_API.md)

**Prompt:**
> "We're integrating canvas and card_renderer into the main app. Here's the scope. Let's start with the database migration for spatial columns."

---

## Claude Code Filesystem Tip

To let Claude Code access multiple repos (so it can read specs from harness while coding in a module), try adding to `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(~/Documents/Git/pin_and_paper_dev_harness/**)",
      "Read(~/Documents/Git/pin_and_paper_canvas/**)",
      "Write(~/Documents/Git/pin_and_paper_canvas/**)"
    ]
  }
}
```

Or set the project root to `~/Documents/Git/` to access everything.

Check Claude Code docs for exact syntax — this would let AI read specs from harness while implementing in module repos.

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| MVP before polish | Validate architecture early |
| Skip rotation for MVP | Core mechanic is drag; rotation is refinement |
| Skip flip for MVP | Core display works without it |
| Integrate in main app (not harness) | Real data validates better than mocks |
| Single card style for MVP | Index card is the default; others are variants |

---

## Success Checklist

At end of Phase S4 MVP:

- [ ] Can open spatial view in main app
- [ ] See real tasks as cards
- [ ] Drag cards around
- [ ] Pan and zoom the canvas
- [ ] Positions persist across app restarts
- [ ] Can switch between list and spatial views
- [ ] No crashes on 20+ tasks

**If all checked:** Architecture validated! Proceed to polish phases.

**If issues:** Adjust interfaces and approach before building more.

---

*Build the skateboard before the car. You need to know wheels work.* 🛹
