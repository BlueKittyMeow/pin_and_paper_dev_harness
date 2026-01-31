# Card Renderer Module Spec

## Overview

The card renderer creates the visual appearance of task cards — torn paper edges, paper textures, shadows, flip animations, and drawing integration. It transforms simple data into tactile, delightful widgets.

**Module:** `pin_and_paper_card_renderer`
**Phase:** 4.2, 4.5, 5.x
**Dependencies:** `pin_and_paper_sketchpad` (for drawing on cards)
**Consumed by:** Main app (via canvas `entityBuilder`)

---

## Philosophy

Cards should feel like real paper artifacts:
- **Tactile** — Textures you can almost feel
- **Imperfect** — Torn edges, slight variations
- **Warm** — Cream paper, soft shadows, not sterile white
- **Personal** — Space for doodles and personality

---

## Card Styles

### Index Card (default)
Classic 3x5 ruled index card with lines, optional red/blue rule.
```
    📌
┌─────────────────────────┐
│ ══════════════════════  │  ← Top rule (red)
│ Call mom tomorrow       │  ← Title
│ ──────────────────────  │  ← Lines (blue, faint)
│ [family]                │  ← Tags
│                    2pm  │  ← Due time
└─────────────────────────┘
       ░░░░░░░░░░░░         ← Shadow
```

### Torn Paper
Irregular hand-torn edges, kraft or cream paper.
```
    📌
╭┄┄┄╮┄┄┄┄┄┄┄┄┄┄┄┄┄┄╭┄┄╮
┊                      ┊
┊  Ship Phase 4        ┊
┊  [work]              ┊
┊                      ┊
╰┄┄┄┄┄╮┄┄┄┄┄┄┄┄╭┄┄┄┄┄╯
```

### Sticky Note (stretch goal)
Square, solid color, slight curl at corner.

---

## Card States

| State | Visual Treatment |
|-------|------------------|
| **Normal** | Standard appearance |
| **Selected** | Subtle glow (lavender), slight lift |
| **Completed** | Muted colors, strikethrough title, ✓ mark |
| **Overdue** | Red accent border or corner flag |
| **Dragging** | Larger shadow, slight scale-up (1.02x) |

---

## Subphases

### Phase 4.2: Static Card Rendering (Week 2)

**Goal:** Beautiful cards with no interaction

- [ ] `TaskCard` widget scaffold
- [ ] Index card style (ruled lines, paper texture)
- [ ] Torn paper style (procedural or PNG edges)
- [ ] Paper textures (cream, kraft)
- [ ] Static drop shadow (`BoxShadow`)
- [ ] Title + tags + due date layout
- [ ] Visual states (normal, selected, completed, overdue)
- [ ] Pushpin decoration widget
- [ ] `TaskCardData` model

**Deliverable:** Cards look beautiful in harness, shown at various states

### Phase 4.5: Flip + Drawing (Week 5)

**Goal:** Cards are interactive objects

- [ ] Flip animation (front ↔ back, 3D Y-axis rotation)
- [ ] Card back design (metadata, kraft texture)
- [ ] `CardFlipController`
- [ ] Sketchpad embedding on front
- [ ] Sketchpad embedding on back
- [ ] Drawing persistence callbacks
- [ ] Toggle drawing mode

**Deliverable:** Can flip cards, draw on front and back, drawings persist

### Phase 5.x: Advanced Visuals (Future)

- [ ] Dynamic shadows (angle based on time of day)
- [ ] Lighting overlay (warm morning, cool evening)
- [ ] Shadow casts onto "desk" surface
- [ ] Conspiracy strings (connections between cards)
- [ ] Paper grain animation (subtle)

---

## Technical Approach

### Card Structure

```dart
class TaskCard extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _flipController,
      builder: (context, child) {
        final angle = _flipController.value * pi;
        final showFront = angle <= pi / 2;
        
        return Transform(
          transform: Matrix4.identity()
            ..setEntry(3, 2, 0.001)  // Perspective
            ..rotateY(angle),
          alignment: Alignment.center,
          child: showFront
            ? _buildFront()
            : Transform(
                transform: Matrix4.rotationY(pi),  // Un-mirror the back
                child: _buildBack(),
              ),
        );
      },
    );
  }
}
```

### Torn Edge Generation

```dart
Path generateTornEdge(double length, {required int seed}) {
  final random = Random(seed);
  final path = Path();
  
  double x = 0;
  path.moveTo(x, 0);
  
  while (x < length) {
    final segmentLength = 4 + random.nextDouble() * 8;
    final yOffset = random.nextDouble() * 4 - 2;  // ±2 pixels
    x += segmentLength;
    path.lineTo(min(x, length), yOffset);
  }
  
  return path;
}
```

### Shadow Rendering

Phase 4.2 (static):
```dart
BoxDecoration(
  boxShadow: [
    BoxShadow(
      color: PinAndPaperColors.shadow.withOpacity(0.25),
      blurRadius: 8,
      offset: Offset(2, 4),
    ),
  ],
)
```

Phase 5 (dynamic, based on time):
```dart
BoxShadow dynamicShadow(TimeOfDay time) {
  final hour = time.hour;
  final angle = (hour - 12) * (pi / 12);  // -π to π over 24h
  final length = (6 - (hour - 12).abs() / 2).clamp(2.0, 8.0);
  
  return BoxShadow(
    color: PinAndPaperColors.shadow.withOpacity(0.2),
    blurRadius: 6 + length,
    offset: Offset(cos(angle) * length, sin(angle).abs() * length + 2),
  );
}
```

---

## Public API

```dart
/// Main card widget
class TaskCard extends StatefulWidget {
  final TaskCardData data;
  final CardStyle style;
  final Size size;
  final bool isSelected;
  final bool showBack;
  final bool drawingEnabled;
  final LayerStack? frontDrawing;
  final LayerStack? backDrawing;
  final CardFlipController? flipController;
  
  final VoidCallback? onTap;
  final VoidCallback? onDoubleTap;
  final VoidCallback? onFlip;
  final void Function(LayerStack, CardSide)? onDrawingChanged;
}

/// Visual style options
enum CardStyle { indexCard, tornPaper, stickyNote }

/// Simplified task data for rendering
class TaskCardData {
  final String id;
  final String title;
  final List<TagChip> tags;
  final DateTime? dueDate;
  final bool isCompleted;
  final bool isOverdue;
  final String? notes;
  final DateTime? createdAt;
  final DateTime? completedAt;
}

/// Flip controller
class CardFlipController extends ChangeNotifier {
  void flipToFront({bool animate = true});
  void flipToBack({bool animate = true});
  void toggle();
  bool get isShowingFront;
  bool get isAnimating;
}

/// Side enum for drawings
enum CardSide { front, back }
```

See `INTERFACE_CONTRACTS.md` for `TagChip` and `CardDrawingSource` definitions.

---

## Assets Required

### Textures (`assets/textures/`)

| Asset | Description | Specs |
|-------|-------------|-------|
| `cream_paper.png` | Light cream paper | 512x512, seamless tile |
| `kraft_paper.png` | Brown kraft paper | 512x512, seamless tile |
| `vintage_paper.png` | Aged/stained paper | 512x512, seamless tile |
| `lined_overlay.png` | Ruled lines (optional) | 512x512, transparent |
| `dot_grid.png` | Dot grid (optional) | 512x512, transparent |

### Pins (`assets/pins/`)

| Asset | Description | Specs |
|-------|-------------|-------|
| `pushpin_red.png` | Red pushpin | 128x128, transparent |
| `pushpin_gold.png` | Brass/gold pushpin | 128x128, transparent |
| `thumbtack.png` | Simple thumbtack | 64x64, transparent |

### Notes on Assets

- Textures should be seamless/tileable
- Can use your existing scanned paper textures from sketchpad
- Pins can be simple illustrations or photos
- Keep file sizes reasonable (<100KB each)

---

## Color Palette

```dart
class CardColors {
  // Paper surfaces
  static const cream = Color(0xFFF5F1E8);
  static const kraft = Color(0xFFD4B896);
  
  // Shadows
  static const shadow = Color(0xFF4A3F35);
  
  // Card lines (index card)
  static const blueRule = Color(0xFFB8D4E8);
  static const redRule = Color(0xFFE8B8B8);
  
  // States
  static const overdue = Color(0xFFC75B4A);
  static const completed = Color(0xFF5B8C7A);
  static const selectedGlow = Color(0xFF9B8FA5);
  
  // Text
  static const inkBlack = Color(0xFF2D2D2D);
}
```

---

## Testing Checklist

### Rendering
- [ ] Index card style looks correct
- [ ] Torn paper edges look natural (not too regular)
- [ ] Paper textures tile without visible seams
- [ ] Pushpin positioned correctly
- [ ] Tags render with correct colors (WCAG compliant)
- [ ] Due date formatted correctly
- [ ] Shadow looks grounded, not floating

### States
- [ ] Normal state is default, clean
- [ ] Selected state clearly indicated
- [ ] Completed state muted, has checkmark
- [ ] Overdue state shows urgency

### Flip Animation
- [ ] Animation is smooth (60fps)
- [ ] Front/back swap at 90° (edge-on)
- [ ] No visual glitches mid-flip
- [ ] Shadow changes appropriately during flip

### Drawing Integration
- [ ] Sketchpad embeds without layout issues
- [ ] Drawing doesn't obscure title/tags badly
- [ ] Front and back drawings are independent
- [ ] `onDrawingChanged` callback fires
- [ ] Drawing mode can be toggled

### Performance
- [ ] Single card renders fast (<16ms)
- [ ] 20 cards on screen smooth
- [ ] Shadow blur doesn't cause jank
- [ ] Texture loading doesn't hitch

---

## File Structure

```
pin_and_paper_card_renderer/
├── lib/
│   ├── card_renderer.dart         # Public API exports
│   ├── src/
│   │   ├── task_card.dart         # Main widget
│   │   ├── card_front.dart        # Front side layout
│   │   ├── card_back.dart         # Back side layout
│   │   ├── flip_animation.dart    # Flip controller + transform
│   │   ├── torn_edge.dart         # Procedural torn edges
│   │   ├── card_shadow.dart       # Shadow generation
│   │   ├── pushpin.dart           # Pin widget
│   │   └── styles/
│   │       ├── index_card_style.dart
│   │       └── torn_paper_style.dart
│   └── models/
│       └── task_card_data.dart
├── assets/
│   ├── textures/
│   │   └── .gitkeep
│   └── pins/
│       └── .gitkeep
├── pubspec.yaml
└── README.md
```

---

## Integration Notes

The card renderer is used via the canvas `entityBuilder`:

```dart
SpatialCanvas(
  dataSource: myDataSource,
  entityBuilder: (entity, isSelected) {
    final task = entity as TaskSpatialEntity;
    return TaskCard(
      data: task.cardData,
      style: CardStyle.indexCard,
      isSelected: isSelected,
      size: entity.size,
      frontDrawing: task.frontDrawing,
      onDrawingChanged: (layers, side) => _saveDrawing(task.id, side, layers),
    );
  },
)
```

---

*The card renderer is where craft meets code. Every torn edge, every shadow, every texture — that's what makes it feel like paper instead of pixels.* 🍂📌
