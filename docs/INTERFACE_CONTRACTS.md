# Interface Contracts

**Purpose:** This document defines the interfaces between the main Pin and Paper app and the visual modules (canvas, card_renderer, journal). Module developers only need this document — not the full CORE_API.md.

**Source:** Extracted from CORE_API.md (main app)
**Last Updated:** 2026-01-30

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
  
  /// Visual size of the entity
  Size get size;
  
  /// Z-order for layering (higher = on top)
  int get zIndex;
}
```

### SpatialDataSource

Canvas module calls these methods; main app implements.

```dart
abstract class SpatialDataSource {
  /// Get all entities that should render in the given viewport.
  /// 
  /// Implementation should filter to visible rect for performance.
  /// Called frequently during pan/zoom — keep it fast.
  List<SpatialEntity> getVisibleEntities(Rect viewport);
  
  /// Called when user drags or rotates an entity.
  /// 
  /// Implementation should:
  /// - Update the entity's stored position/rotation
  /// - Persist to database
  /// - NOT trigger full reload (entity already moved visually)
  void onEntityMoved(String id, Offset position, double rotation);
  
  /// Called when user taps an entity.
  /// 
  /// Implementation typically:
  /// - Selects the entity
  /// - Updates selection state
  void onEntityTapped(String id);
  
  /// Called when user double-taps an entity.
  /// 
  /// Implementation typically:
  /// - Opens detail/edit dialog
  /// - Or flips the card (if card_renderer supports it)
  void onEntityDoubleTapped(String id);
  
  /// Called when user taps empty canvas area.
  /// 
  /// Implementation might:
  /// - Clear selection
  /// - Create new task at that position (optional)
  void onCanvasTapped(Offset position);
  
  /// Called when selection changes.
  /// 
  /// Provides the full set of currently selected IDs.
  void onSelectionChanged(Set<String> selectedIds);
}
```

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
