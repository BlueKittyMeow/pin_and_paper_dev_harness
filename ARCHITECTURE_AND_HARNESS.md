# Pin and Paper — Complete Architecture & Dev Harness Plan

## Executive Summary

Pin and Paper is being restructured into modular components to enable:
- Parallel development across AI assistants
- Context-window-friendly chunks
- Independent testing of visual modules
- Clean separation between data/logic and UI

This document defines the module structure, interfaces, and a dev harness for testing visual modules against mock data.

---

# Part 1: Module Architecture

## Module Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WORKSPACE STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  pin_and_paper/                    ← Main App (data, logic, list UI)    │
│  pin_and_paper_sketchpad/          ← Drawing system                      │
│  pin_and_paper_canvas/             ← Spatial positioning                 │
│  pin_and_paper_card_renderer/      ← Card visuals                        │
│  pin_and_paper_journal/            ← Daybook/planner                     │
│  pin_and_paper_dev_harness/        ← Test orchestrator                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Details

### 1. pin_and_paper/ (Main App)

**Role:** Data layer, business logic, list-based UI, orchestration

**Contains:**
- SQLite database + migrations (currently v11)
- Task, Tag, and related data models
- TaskService, TagService, NotificationService, etc.
- Claude AI integration (brain dump, suggestions)
- User preferences and onboarding
- List View UI (current working interface)
- State management (Provider → Riverpod)

**Status:** ~16k lines, Phase 3.9 complete

**Provides to other modules:**
- Data source implementations
- Task/Tag models
- User preferences
- Event streams (task completed, etc.)

---

### 2. pin_and_paper_sketchpad/

**Role:** Pressure-sensitive drawing with layer system

**Contains:**
- Stroke capture (S-Pen pressure via PointerEvent)
- Stroke rendering (perfect_freehand)
- Three-layer system (Color → Sketch → Ink)
- Blend modes (Multiply, Normal)
- Per-layer eraser (hard/soft, constant/tapered)
- Stroke options presets
- Undo/redo

**Public API:**
```dart
// Main widget
class Sketchpad extends StatefulWidget {
  final LayerStack layerStack;
  final Color currentColor;
  final StrokeOptions strokeOptions;
  final ImageProvider? backgroundImage;
  final bool debugPressure;
  final VoidCallback? onChanged;
}

// Data models
class LayerStack { ... }
class DrawingLayer { ... }
class Stroke { ... }
class StrokePoint { ... }
class StrokeOptions { ... }
class EraserOptions { ... }
```

**Dependencies:** None (foundation module)

**Consumed by:** card_renderer, journal

**Status:** Prototype in progress

**Specs:**
- DRAWING_LAYER_SPEC.md
- SHAPE_CORRECTION_SPEC.md (Phase 5+)

---

### 3. pin_and_paper_canvas/

**Role:** Spatial positioning, viewport management, gestures

**Contains:**
- Bounded canvas with configurable limits
- Viewport (pan, zoom, current visible rect)
- Entity positioning (drag to move)
- Entity rotation (two-finger gesture)
- Z-ordering / layering
- Hit testing (which entity at point?)
- Selection state management
- Viewport culling (render only visible)

**Public API:**
```dart
// Main widget
class SpatialCanvas extends StatefulWidget {
  final SpatialDataSource dataSource;
  final SpatialEntityBuilder entityBuilder;
  final Rect bounds;
  final SpatialCanvasController? controller;
  final void Function(Offset)? onCanvasTap;
}

// Controller for programmatic control
class SpatialCanvasController {
  void panTo(Offset position);
  void zoomTo(double scale);
  void selectEntity(String id);
  void clearSelection();
  Rect get visibleRect;
}

// Interface: What the canvas needs from entities
abstract class SpatialEntity {
  String get id;
  Offset get position;
  double get rotation;
  Size get size;
  int get zIndex;
}

// Interface: Canvas calls back to data layer
abstract class SpatialDataSource {
  List<SpatialEntity> getVisibleEntities(Rect viewport);
  void onEntityMoved(String id, Offset position, double rotation);
  void onEntityTapped(String id);
  void onEntityDoubleTapped(String id);
  void onCanvasTapped(Offset position);
  void onSelectionChanged(Set<String> selectedIds);
}

// Builder for rendering entities
typedef SpatialEntityBuilder = Widget Function(
  SpatialEntity entity,
  bool isSelected,
);
```

**Dependencies:** None

**Consumed by:** Main app (Spatial View)

**Status:** Not started (Phase 4.1)

---

### 4. pin_and_paper_card_renderer/

**Role:** Visual appearance of task cards

**Contains:**
- Torn paper edge rendering
- Index card styling (cream, kraft)
- Card shadows (static → dynamic in Phase 5)
- Pushpin/tack graphics
- Card states (normal, selected, completed, overdue)
- Card flip animation (3D transform, front ↔ back)
- Paper textures (shared asset)
- Time-based lighting (Phase 5)

**Public API:**
```dart
// Main widget
class TaskCard extends StatefulWidget {
  final TaskCardData data;
  final CardStyle style;
  final bool isSelected;
  final bool showBack;
  final Widget? frontDrawing;   // Sketchpad overlay
  final Widget? backDrawing;    // Sketchpad overlay
  final VoidCallback? onTap;
  final VoidCallback? onDoubleTap;
  final VoidCallback? onFlip;
}

// Data for rendering (not the full Task model)
class TaskCardData {
  final String id;
  final String title;
  final List<TagChip> tags;
  final DateTime? dueDate;
  final bool isCompleted;
  final bool isOverdue;
}

class TagChip {
  final String name;
  final Color color;
}

enum CardStyle { 
  indexCard,      // Classic ruled card
  tornPaper,      // Torn strip
  stickyNote,     // Post-it style
}

// Shared textures
class PaperTextures {
  static ImageProvider get cream;
  static ImageProvider get kraft;
  static ImageProvider get dotGrid;
  static ImageProvider get lined;
}

// Card flip controller
class CardFlipController {
  void flipToFront();
  void flipToBack();
  void toggle();
  bool get isShowingFront;
}
```

**Dependencies:** 
- pin_and_paper_sketchpad (for drawing on cards)

**Consumed by:** Main app (Spatial View)

**Status:** Not started (Phase 4.2)

---

### 5. pin_and_paper_journal/

**Role:** Hobonichi-style daily planner/journal

**Contains:**
- Pull-up sheet UI
- Journal page data model
- Page layout (date header, task list, drawing area)
- Page flip animation (3D with shadows)
- Date navigation (swipe, bookmark, picker)
- Page templates (daily, weekly, blank)
- Paper textures
- Per-page drawing persistence

**Public API:**
```dart
// Main widget (pull-up sheet)
class JournalSheet extends StatefulWidget {
  final JournalDataSource dataSource;
  final JournalController? controller;
  final double initialHeight;
}

// Controller
class JournalController {
  void open();
  void close();
  void goToDate(DateTime date);
  void goToToday();
  bool get isOpen;
  DateTime get currentDate;
}

// Page view (can be used standalone)
class JournalPageView extends StatefulWidget {
  final JournalPage page;
  final bool allowDrawing;
  final bool allowEditing;
}

// Interface: Journal calls back to data layer
abstract class JournalDataSource {
  Future<List<CompletedTaskEntry>> getCompletedTasks(DateTime date);
  Future<JournalPage> getPage(DateTime date);
  Future<void> savePage(JournalPage page);
  void navigateToTask(String taskId);
  Future<DateTimeRange> getActivityRange();
}

// Data models
class JournalPage {
  final DateTime date;
  final List<CompletedTaskEntry> tasks;
  final LayerStack? drawings;
  final String? userNotes;
  final PageTemplate template;
  final PaperTexture texture;
}

class CompletedTaskEntry {
  final String taskId;
  final String title;
  final DateTime completedAt;
  final List<TagChip> tags;
}

enum PageTemplate { daily, weeklySpread, blank }
enum PaperTexture { cream, kraft, dotGrid, lined, graph }
```

**Dependencies:**
- pin_and_paper_sketchpad (for drawing on pages)

**Consumed by:** Main app

**Status:** Not started (Phase 6)

**Specs:**
- PHASE_6_JOURNAL_SPEC.md

---

## Dependency Graph

```
                         ┌──────────────────────┐
                         │                      │
                         │   pin_and_paper      │
                         │   (Main App)         │
                         │                      │
                         └──────────┬───────────┘
                                    │
                                    │ implements interfaces,
                                    │ provides data sources
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  canvas         │      │  card_renderer  │      │  journal        │
│                 │      │                 │      │                 │
│  - positioning  │      │  - visuals      │      │  - daybook      │
│  - gestures     │      │  - flip anim    │      │  - page flip    │
│  - viewport     │      │  - shadows      │      │  - templates    │
│                 │      │                 │      │                 │
└─────────────────┘      └────────┬────────┘      └────────┬────────┘
                                  │                        │
                                  │   depends on           │
                                  │                        │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                   ┌─────────────────┐
                                   │                 │
                                   │   sketchpad     │
                                   │                 │
                                   │  - drawing      │
                                   │  - layers       │
                                   │  - eraser       │
                                   │                 │
                                   └─────────────────┘
```

---

# Part 2: Interface Contracts

These interfaces define the communication between modules. The main app implements these; visual modules consume them.

## SpatialEntity Interface

```dart
/// Anything that can be positioned on the spatial canvas.
/// Main app implements this for Task objects.
abstract class SpatialEntity {
  /// Unique identifier
  String get id;
  
  /// Position on canvas (top-left of entity)
  Offset get position;
  
  /// Rotation in degrees
  double get rotation;
  
  /// Size of the entity
  Size get size;
  
  /// Z-order (higher = on top)
  int get zIndex;
}
```

## SpatialDataSource Interface

```dart
/// Canvas module calls these methods.
/// Main app provides implementation with real data.
abstract class SpatialDataSource {
  /// Get all entities that should render in the given viewport.
  /// Implementation should handle culling for performance.
  List<SpatialEntity> getVisibleEntities(Rect viewport);
  
  /// Called when user drags/rotates an entity.
  /// Implementation should persist the new position.
  void onEntityMoved(String id, Offset position, double rotation);
  
  /// Called when user taps an entity.
  /// Implementation typically selects it.
  void onEntityTapped(String id);
  
  /// Called when user double-taps an entity.
  /// Implementation typically opens detail/edit view.
  void onEntityDoubleTapped(String id);
  
  /// Called when user taps empty canvas area.
  /// Implementation might deselect, or create new task at location.
  void onCanvasTapped(Offset position);
  
  /// Called when selection changes.
  void onSelectionChanged(Set<String> selectedIds);
}
```

## JournalDataSource Interface

```dart
/// Journal module calls these methods.
/// Main app provides implementation with real data.
abstract class JournalDataSource {
  /// Get all tasks completed on a specific date.
  Future<List<CompletedTaskEntry>> getCompletedTasks(DateTime date);
  
  /// Load journal page data (drawings, notes, template).
  /// Creates empty page if none exists.
  Future<JournalPage> getPage(DateTime date);
  
  /// Save journal page data.
  Future<void> savePage(JournalPage page);
  
  /// User tapped a task in the journal; navigate to it in list/spatial view.
  void navigateToTask(String taskId);
  
  /// Get the date range containing any completed tasks.
  /// Used for navigation hints (which dates have content).
  Future<DateTimeRange> getActivityRange();
}
```

## CardDrawingSource Interface

```dart
/// Card renderer calls these for drawing data persistence.
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

---

# Part 3: Dev Harness

## Purpose

The dev harness allows visual modules to be developed and tested independently from the main app's 16k+ line codebase. It provides:

1. **Mock data sources** that implement the interfaces
2. **Tabbed UI** to test each module
3. **Dev controls** to simulate events and states
4. **No SQLite dependency** — all in-memory

## Structure

```
pin_and_paper_dev_harness/
├── lib/
│   ├── main.dart                     # App entry, tab navigation
│   │
│   ├── mocks/
│   │   ├── mock_spatial_source.dart  # Fake tasks for canvas
│   │   ├── mock_journal_source.dart  # Fake completions for journal
│   │   ├── mock_drawing_source.dart  # In-memory drawing storage
│   │   └── mock_data.dart            # Shared fake data
│   │
│   ├── pages/
│   │   ├── sketchpad_test_page.dart  # Sketchpad in isolation
│   │   ├── canvas_test_page.dart     # Canvas with mock entities
│   │   ├── card_test_page.dart       # Card renderer showcase
│   │   └── journal_test_page.dart    # Journal with mock data
│   │
│   └── widgets/
│       ├── dev_controls_drawer.dart  # Simulation controls
│       └── debug_overlay.dart        # State inspection
│
├── pubspec.yaml
│   dependencies:
│     pin_and_paper_sketchpad:
│       path: ../pin_and_paper_sketchpad
│     pin_and_paper_canvas:
│       path: ../pin_and_paper_canvas
│     pin_and_paper_card_renderer:
│       path: ../pin_and_paper_card_renderer
│     pin_and_paper_journal:
│       path: ../pin_and_paper_journal
│
└── README.md
```

## Mock Implementations

### MockSpatialDataSource

```dart
class MockSpatialDataSource implements SpatialDataSource {
  final List<MockTaskEntity> _tasks = [];
  final Set<String> _selectedIds = {};
  final void Function()? onDataChanged;
  
  MockSpatialDataSource({this.onDataChanged}) {
    // Initialize with sample tasks
    _tasks.addAll([
      MockTaskEntity(
        id: '1',
        title: 'Brush Woolfie',
        position: Offset(100, 150),
        rotation: 5,
        tags: [MockTag('pet', Colors.amber)],
      ),
      MockTaskEntity(
        id: '2', 
        title: 'Call mom',
        position: Offset(300, 200),
        rotation: -3,
        tags: [MockTag('family', Colors.pink)],
      ),
      MockTaskEntity(
        id: '3',
        title: 'Ship Phase 4',
        position: Offset(200, 400),
        rotation: 0,
        tags: [MockTag('work', Colors.blue)],
        isOverdue: true,
      ),
    ]);
  }
  
  @override
  List<SpatialEntity> getVisibleEntities(Rect viewport) {
    // Simple implementation - return all (real impl would cull)
    return _tasks;
  }
  
  @override
  void onEntityMoved(String id, Offset position, double rotation) {
    final task = _tasks.firstWhere((t) => t.id == id);
    task.position = position;
    task.rotation = rotation;
    onDataChanged?.call();
  }
  
  @override
  void onEntityTapped(String id) {
    _selectedIds.clear();
    _selectedIds.add(id);
    onDataChanged?.call();
  }
  
  // ... etc
  
  // === Dev harness extras ===
  
  void addRandomTask() {
    _tasks.add(MockTaskEntity.random());
    onDataChanged?.call();
  }
  
  void simulateManyTasks(int count) {
    for (var i = 0; i < count; i++) {
      _tasks.add(MockTaskEntity.random());
    }
    onDataChanged?.call();
  }
  
  void resetPositions() {
    // Arrange in grid
    for (var i = 0; i < _tasks.length; i++) {
      _tasks[i].position = Offset(
        100 + (i % 4) * 200,
        100 + (i ~/ 4) * 150,
      );
      _tasks[i].rotation = 0;
    }
    onDataChanged?.call();
  }
}
```

### MockJournalDataSource

```dart
class MockJournalDataSource implements JournalDataSource {
  final Map<DateTime, JournalPage> _pages = {};
  
  @override
  Future<List<CompletedTaskEntry>> getCompletedTasks(DateTime date) async {
    // Generate plausible fake completions for any date
    final random = Random(date.millisecondsSinceEpoch);
    final count = random.nextInt(6); // 0-5 tasks per day
    
    return List.generate(count, (i) => CompletedTaskEntry(
      taskId: 'mock_${date.day}_$i',
      title: _randomTaskTitles[random.nextInt(_randomTaskTitles.length)],
      completedAt: date.add(Duration(hours: 8 + random.nextInt(12))),
      tags: _randomTags(random),
    ));
  }
  
  @override
  Future<JournalPage> getPage(DateTime date) async {
    final normalized = DateTime(date.year, date.month, date.day);
    return _pages[normalized] ?? JournalPage(
      date: normalized,
      tasks: await getCompletedTasks(date),
      drawings: null,
      userNotes: null,
      template: PageTemplate.daily,
      texture: PaperTexture.cream,
    );
  }
  
  @override
  Future<void> savePage(JournalPage page) async {
    final normalized = DateTime(page.date.year, page.date.month, page.date.day);
    _pages[normalized] = page;
  }
  
  @override
  void navigateToTask(String taskId) {
    print('Mock: Would navigate to task $taskId');
  }
  
  @override
  Future<DateTimeRange> getActivityRange() async {
    return DateTimeRange(
      start: DateTime.now().subtract(Duration(days: 60)),
      end: DateTime.now(),
    );
  }
  
  static const _randomTaskTitles = [
    'Brush Woolfie',
    'Take meds',
    'Call mom',
    'Buy groceries',
    'Ship feature',
    'Review PRs',
    'Water plants',
    'Laundry',
    'Meal prep',
    'Exercise',
  ];
}
```

## Dev Harness UI

### Main App

```dart
class DevHarnessApp extends StatefulWidget {
  @override
  State<DevHarnessApp> createState() => _DevHarnessAppState();
}

class _DevHarnessAppState extends State<DevHarnessApp> {
  late MockSpatialDataSource _spatialSource;
  late MockJournalDataSource _journalSource;
  late MockDrawingSource _drawingSource;
  
  bool _nightMode = false;
  
  @override
  void initState() {
    super.initState();
    _spatialSource = MockSpatialDataSource(onDataChanged: () => setState(() {}));
    _journalSource = MockJournalDataSource();
    _drawingSource = MockDrawingSource();
  }
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pin & Paper Dev Harness',
      theme: _nightMode ? _nightTheme : _dayTheme,
      home: DefaultTabController(
        length: 4,
        child: Scaffold(
          appBar: AppBar(
            title: Text('Dev Harness'),
            bottom: TabBar(
              tabs: [
                Tab(icon: Icon(Icons.brush), text: 'Sketchpad'),
                Tab(icon: Icon(Icons.grid_view), text: 'Canvas'),
                Tab(icon: Icon(Icons.sticky_note_2), text: 'Cards'),
                Tab(icon: Icon(Icons.book), text: 'Journal'),
              ],
            ),
            actions: [
              IconButton(
                icon: Icon(_nightMode ? Icons.light_mode : Icons.dark_mode),
                onPressed: () => setState(() => _nightMode = !_nightMode),
              ),
            ],
          ),
          body: TabBarView(
            children: [
              SketchpadTestPage(),
              CanvasTestPage(dataSource: _spatialSource),
              CardTestPage(drawingSource: _drawingSource),
              JournalTestPage(dataSource: _journalSource),
            ],
          ),
          endDrawer: DevControlsDrawer(
            spatialSource: _spatialSource,
            journalSource: _journalSource,
            onNightModeChanged: (v) => setState(() => _nightMode = v),
          ),
        ),
      ),
    );
  }
}
```

### Dev Controls Drawer

```dart
class DevControlsDrawer extends StatelessWidget {
  final MockSpatialDataSource spatialSource;
  final MockJournalDataSource journalSource;
  final ValueChanged<bool> onNightModeChanged;
  
  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Text('DEV CONTROLS', style: Theme.of(context).textTheme.titleLarge),
          Divider(),
          
          Text('Spatial Canvas', style: Theme.of(context).textTheme.titleMedium),
          ListTile(
            leading: Icon(Icons.add),
            title: Text('Add mock task'),
            onTap: () => spatialSource.addRandomTask(),
          ),
          ListTile(
            leading: Icon(Icons.grid_on),
            title: Text('Simulate 50 tasks'),
            onTap: () => spatialSource.simulateManyTasks(50),
          ),
          ListTile(
            leading: Icon(Icons.restart_alt),
            title: Text('Reset positions'),
            onTap: () => spatialSource.resetPositions(),
          ),
          
          Divider(),
          
          Text('Journal', style: Theme.of(context).textTheme.titleMedium),
          ListTile(
            leading: Icon(Icons.calendar_today),
            title: Text('Jump to random date'),
            onTap: () {
              final random = Random();
              final days = random.nextInt(60);
              // Would need controller access
            },
          ),
          
          Divider(),
          
          Text('Display', style: Theme.of(context).textTheme.titleMedium),
          SwitchListTile(
            title: Text('Night mode'),
            subtitle: Text('Test time-based lighting'),
            value: false, // Would be stateful
            onChanged: onNightModeChanged,
          ),
          
          Divider(),
          
          Text('Performance', style: Theme.of(context).textTheme.titleMedium),
          ListTile(
            leading: Icon(Icons.speed),
            title: Text('Simulate 100 tasks'),
            subtitle: Text('Test rendering performance'),
            onTap: () => spatialSource.simulateManyTasks(100),
          ),
          ListTile(
            leading: Icon(Icons.bug_report),
            title: Text('Show debug overlay'),
            onTap: () {
              // Toggle overlay
            },
          ),
        ],
      ),
    );
  }
}
```

---

# Part 4: Development Workflow

## For AI Assistants

When working on a specific module, the AI needs:

| Working On | Provide |
|------------|---------|
| sketchpad | DRAWING_LAYER_SPEC.md only |
| canvas | Interface contracts (SpatialEntity, SpatialDataSource) |
| card_renderer | Interface contracts + sketchpad public API |
| journal | PHASE_6_JOURNAL_SPEC.md + interface contracts + sketchpad public API |
| integration | CORE_API.md from main app |

**Do NOT provide:**
- Full main app source code
- SQLite migration details
- Other modules' implementations

## Workflow Steps

1. **Develop module** against dev harness with mocks
2. **Test visually** in the harness (all modules side by side)
3. **Performance test** using "simulate 100 tasks" etc.
4. **Integration test** by implementing real data sources in main app
5. **Ship** when stable

## Integration Checklist

When integrating a module into the main app:

- [ ] Create real data source implementing the interface
- [ ] Add module as dependency in pubspec.yaml
- [ ] Wire up navigation (tab, button, etc.)
- [ ] Add persistence for module-specific data (e.g., card positions)
- [ ] Test with real data
- [ ] Performance test with real data volume

---

# Part 5: Phase Mapping

| Phase | Module(s) | Deliverable |
|-------|-----------|-------------|
| 4.1 | canvas | Pan/zoom/drag with rectangles in harness |
| 4.2 | card_renderer | Beautiful cards (static) in harness |
| 4.3 | canvas | Rotation + selection in harness |
| 4.4 | main app | Integration, persistence, view toggle |
| 4.5 | card_renderer + sketchpad | Drawing on cards, flip animation |
| 5.x | card_renderer | Dynamic lighting, conspiracy strings |
| 6.1 | journal | Pull-up sheet, basic layout in harness |
| 6.2 | journal | Page flip animation |
| 6.3 | journal + sketchpad | Drawing on pages |
| 6.4 | journal | Templates, textures |
| 6.5 | journal | Navigation polish |
| 6.6 | main app | Journal integration |

---

# Part 6: File Checklist

## Specs to Write

- [x] DRAWING_LAYER_SPEC.md
- [x] SHAPE_CORRECTION_SPEC.md
- [x] PHASE_6_JOURNAL_SPEC.md
- [x] MODULE_ARCHITECTURE.md (this document)
- [ ] CORE_API.md (from main app team)
- [ ] CANVAS_SPEC.md
- [ ] CARD_RENDERER_SPEC.md

## Repos to Create

- [x] pin_and_paper_sketchpad/
- [ ] pin_and_paper_canvas/
- [ ] pin_and_paper_card_renderer/
- [ ] pin_and_paper_journal/
- [ ] pin_and_paper_dev_harness/

---

# Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Main App (pin_and_paper/)                                         │
│  ├── Owns: Data, Logic, List UI                                    │
│  ├── Implements: All DataSource interfaces                         │
│  └── Consumes: All visual modules                                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Dev Harness (pin_and_paper_dev_harness/)                          │
│  ├── Mock implementations of all interfaces                        │
│  ├── Tabbed UI for testing each module                             │
│  └── Dev controls for simulation                                   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Visual Modules                                                     │
│  ├── sketchpad   → drawing system (foundation)                     │
│  ├── canvas      → spatial positioning                             │
│  ├── card_renderer → card visuals (depends on sketchpad)           │
│  └── journal     → daybook (depends on sketchpad)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**The key insight:** Visual modules don't know about Tasks, SQLite, or Provider. They only know about their interfaces. This keeps them small, testable, and AI-context-friendly.

---

*Modularity isn't just architecture — it's how you scale a one-person-plus-AI team.* 🐕✨📌
