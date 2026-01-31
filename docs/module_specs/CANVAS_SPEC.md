# Canvas Module Spec

## Overview

The spatial canvas provides the foundation for Pin and Paper's "flatlay desk" view — a bounded, pannable, zoomable surface where task cards can be freely positioned and rotated.

**Module:** `pin_and_paper_canvas`
**Phase:** 4.1, 4.3
**Dependencies:** None (foundation module)
**Consumed by:** Main app (Spatial View)

---

## Philosophy

The canvas should feel like a physical desk surface:
- **Bounded** — There are edges, like a real desk
- **Tactile** — Drag and rotate feel direct, not floaty
- **Performant** — Smooth even with many cards
- **Invisible** — The canvas itself isn't the star; the cards are

---

## Core Features

### Viewport Management

| Feature | Description |
|---------|-------------|
| Pan | Two-finger drag moves the viewport |
| Zoom | Pinch gesture scales 50%–200% (configurable) |
| Bounds | Canvas has defined edges; viewport stops at bounds |
| Culling | Only render entities within visible rect |

### Entity Positioning

| Feature | Description |
|---------|-------------|
| Drag | Single-finger drag moves entity |
| Rotation | Two-finger twist rotates entity |
| Z-order | Tap brings entity to front; maintains layering |
| Snap (optional) | Grid snap or rotation snap to 45° increments |

### Selection

| Feature | Description |
|---------|-------------|
| Tap to select | Single tap selects entity |
| Tap canvas | Tap empty area deselects |
| Double-tap | Triggers callback (e.g., open detail view) |
| Multi-select | Future: drag-select or shift-tap |

---

## Subphases

### Phase 4.1: Canvas Foundation (Week 1)

**Goal:** Pan, zoom, and drag working with placeholder rectangles

- [ ] `SpatialCanvas` widget scaffold
- [ ] Viewport state (offset, scale)
- [ ] Pan gesture (two-finger)
- [ ] Zoom gesture (pinch) with min/max limits
- [ ] Bounded canvas (viewport clamps to edges)
- [ ] Entity rendering at position
- [ ] Entity drag gesture (single-finger)
- [ ] Hit testing (which entity at tap point?)
- [ ] Basic selection state (tap to select)
- [ ] Callback to DataSource on move

**Deliverable:** Demo in harness with colored rectangles you can drag around a bounded canvas

### Phase 4.3: Rotation + Selection Polish (Week 3)

**Goal:** Two-finger rotation, z-ordering, selection UX

- [ ] Two-finger rotation gesture
- [ ] Rotation state per entity
- [ ] Z-order management (tap brings to front)
- [ ] Visual selection indicator (glow, outline, or scale)
- [ ] Double-tap callback
- [ ] Canvas tap callback (for deselect or "create here")
- [ ] Optional: rotation snapping (0°, 45°, 90°)
- [ ] Optional: position grid snapping

**Deliverable:** Full spatial interaction in harness — drag, rotate, select, layer

---

## Technical Approach

### Widget Structure

```
SpatialCanvas (StatefulWidget)
├── GestureDetector (pan, zoom, tap)
└── CustomPaint / Stack
    └── Positioned widgets for each entity
        └── GestureDetector (drag, rotate per entity)
            └── entityBuilder(entity, isSelected)
```

### State

```dart
class SpatialCanvasState {
  Offset viewportOffset;      // Pan position
  double viewportScale;       // Zoom level (1.0 = 100%)
  Set<String> selectedIds;    // Currently selected
  Map<String, int> zOrder;    // Entity layering
}
```

### Coordinate Spaces

```
Screen coords → Viewport coords → Canvas coords

- Screen: Where finger touches
- Viewport: Adjusted for pan offset
- Canvas: Adjusted for zoom scale

Entity positions are stored in Canvas coords.
```

### Gesture Handling

| Gesture | Detected By | Action |
|---------|-------------|--------|
| Two-finger drag | `ScaleGestureRecognizer` | Pan viewport |
| Pinch | `ScaleGestureRecognizer` | Zoom viewport |
| Single-finger drag on entity | `GestureDetector` per entity | Move entity |
| Two-finger rotate on entity | `ScaleGestureRecognizer` | Rotate entity |
| Tap on entity | `GestureDetector` | Select entity |
| Tap on canvas | `GestureDetector` | Deselect / callback |
| Double-tap on entity | `GestureDetector` | Detail callback |

### Performance

- **Culling:** Only build widgets for entities intersecting visible rect
- **RepaintBoundary:** Wrap entities to isolate repaints
- **Lazy building:** Use builder pattern, not pre-built list
- **Throttle callbacks:** Don't spam `onEntityMoved` during drag; debounce or only fire on drag end

---

## Public API

```dart
/// Main canvas widget
class SpatialCanvas extends StatefulWidget {
  /// Provides entity data and receives callbacks
  final SpatialDataSource dataSource;
  
  /// Builds the visual for each entity
  final SpatialEntityBuilder entityBuilder;
  
  /// Canvas bounds (entities can't be dragged outside)
  final Size canvasSize;
  
  /// Optional controller for programmatic control
  final SpatialCanvasController? controller;
  
  /// Zoom limits
  final double minZoom; // default 0.5
  final double maxZoom; // default 2.0
  
  /// Optional: snap rotation to increments (null = no snap)
  final double? rotationSnapDegrees;
  
  /// Optional: snap position to grid (null = no snap)
  final double? positionSnapSize;
}

/// Controller for programmatic manipulation
class SpatialCanvasController extends ChangeNotifier {
  void panTo(Offset canvasPosition, {bool animate = true});
  void zoomTo(double scale, {bool animate = true});
  void focusOnEntity(String id, {bool animate = true});
  void selectEntity(String id);
  void clearSelection();
  
  Rect get visibleRect;
  double get currentZoom;
  Set<String> get selectedIds;
}

/// Builder for entity visuals
typedef SpatialEntityBuilder = Widget Function(
  SpatialEntity entity,
  bool isSelected,
);
```

See `INTERFACE_CONTRACTS.md` for `SpatialEntity` and `SpatialDataSource` definitions.

---

## Visual Design

The canvas itself is minimal:
- Background color matches desk surface (`#8B7355` warm wood or configurable)
- Optional subtle texture
- No grid lines by default (can be toggled for alignment)
- Bounds indicated by subtle shadow/vignette at edges (optional)

Selection indicator options:
- Subtle glow/shadow around selected entity
- Thin colored border
- Slight scale-up (1.02x)

---

## Testing Checklist

### Viewport
- [ ] Pan moves viewport smoothly
- [ ] Zoom scales around pinch center
- [ ] Viewport stops at canvas bounds
- [ ] Zoom clamps to min/max

### Entities
- [ ] Entities render at correct positions
- [ ] Drag moves entity
- [ ] Entity stops at canvas bounds
- [ ] Rotation works (Phase 4.3)
- [ ] Z-order updates on tap (Phase 4.3)

### Selection
- [ ] Tap selects entity
- [ ] Tap canvas deselects
- [ ] Double-tap triggers callback
- [ ] Visual indicator shows selection

### Performance
- [ ] Smooth with 10 entities
- [ ] Smooth with 50 entities
- [ ] Smooth with 100 entities
- [ ] No jank during rapid pan/zoom

### Callbacks
- [ ] `onEntityMoved` fires with correct position
- [ ] `onEntityTapped` fires on tap
- [ ] `onCanvasTapped` fires on empty area tap
- [ ] `onSelectionChanged` fires when selection changes

---

## Integration Notes

When integrating into main app:

1. Create `TaskSpatialEntity` implementing `SpatialEntity`
2. Create `TaskSpatialDataSource` implementing `SpatialDataSource`
3. Add `canvas_x`, `canvas_y`, `canvas_rotation`, `canvas_z` columns to tasks table (migration v12)
4. Wire up `entityBuilder` to render `TaskCard` widgets (from card_renderer)

---

## Future Enhancements

- [ ] Multi-select (drag box or modifier tap)
- [ ] Group selection (move multiple at once)
- [ ] Alignment guides (snap to other entities' edges)
- [ ] Minimap (overview of full canvas)
- [ ] Keyboard shortcuts (arrow keys to nudge, etc.)
- [ ] Undo/redo for position changes
- [ ] Animation when entities move programmatically

---

*The canvas is the stage. Keep it simple so the cards can shine.* 🎭
