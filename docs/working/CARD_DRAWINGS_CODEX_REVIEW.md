# Sketchpad Review

`pin_and_paper_sketchpad` is a working drawing prototype, not yet an integration-ready package. The code proves out pressure-aware freehand rendering and layered compositing, but the current input model, persistence story, and repaint path would all break or drag down the planned per-card Spatial View use case.

I could not run `flutter test` or `flutter analyze` here because the local Flutter SDK attempted to write to `/home/bluekitty/flutter/bin/cache/engine.stamp`, which is read-only in this environment.

## Highest-priority findings

1. **The input model is incompatible with card drag/pan/zoom integration.** [`DrawingCanvas`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:7>) captures raw pointer events with a [`Listener`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:112>) and always inks on pointer down/move/up. There is no draw-mode gate, stylus-only mode, or gesture-arena coordination, so a card drag or viewport pan would also create strokes.

2. **There is no persistence or serialized document model.** [`Stroke`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/stroke.dart:15>), [`DrawingLayer`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:5>), and [`LayerStack`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:65>) are mutable runtime objects only. No `toJson`, `fromJson`, schema versioning, IDs for strokes, or export helpers exist.

3. **Rendering cost is too high for many zoomable cards.** [`_DrawingPainter.paint`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:188>) recomputes `perfect_freehand` outlines for every stored stroke on every repaint, and [`shouldRepaint`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:289>) always returns `true`. That is acceptable for a single full-screen editor, not for a desk of cards.

4. **The core model still bakes in prototype assumptions.** [`LayerStack`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:69>) hardcodes `_activeLayerIndex = 2`, which crashes for custom layer lists. [`DrawingToolbar`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/toolbar.dart:89>) hardcodes the three default layer indices `[1, 2, 0]`. This is a fixed demo stack, not a generic document model.

5. **Input correctness is incomplete even before integration.** [`DrawingCanvas`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:55>) does not track pointer IDs, so multi-touch/stylus-plus-finger input can corrupt a stroke. There is no `onPointerCancel`, and `_normalizePressure()` maps exact `1.0` pressure to `0.5`, which can flatten real max-pressure stylus samples ([`drawing_canvas.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:97>)).

## 1. State assessment

**What works today**
- Interactive drawing with pressure-fed points into `perfect_freehand` via [`DrawingCanvas`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/drawing_canvas.dart:7>).
- Three-layer compositing with visibility, opacity, blend mode, and eraser-as-stroke semantics via [`DrawingLayer`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:5>) and [`LayerStack`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:65>).
- Demo controls for color/tool/layer switching in [`DrawingToolbar`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/toolbar.dart:5>).
- A runnable prototype app in [`lib/main.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/main.dart:7>) with texture background and pressure debug overlay.

**Prototype-only or missing**
- Persistence/serialization: missing.
- Undo/redo history across edits: missing; only `undoOnActiveLayer()` exists ([`layer.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/models/layer.dart:92>)).
- Read-only renderer/thumbnail/export API: missing.
- Gesture coexistence with drag/pan/zoom/double-tap: missing.
- Package hygiene: the public library exports demo UI via [`sketchpad.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/sketchpad.dart:41>), and the only test imports the demo app, not the package API ([`test/widget_test.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/test/widget_test.dart:3>)).

## 2. Top improvements before integrating

1. **Introduce an immutable serialized document model and editing controller** — `M`
   - Replace ad hoc mutation on `LayerStack` with a `SketchDocument` value object plus `SketchpadController`.
   - This is the prerequisite for SQLite persistence, undo/redo, change notifications, and safe read-only rendering.

2. **Separate editor input from read-only rendering** — `M`
   - Keep one interactive widget for modal editing, and a lightweight painter/view for cards.
   - Do not render stored card doodles with the live editor widget.

3. **Fix gesture/input policy** — `M`
   - Add `enabled`, `inputPolicy` (`drawMode`, `stylusOnly`, `disabled`), pointer-ID tracking, and cancel handling.
   - Without this, Spatial View gestures and drawing will interfere.

4. **Cache committed stroke rendering** — `M/L`
   - Rebuild a cached `Picture` or `Image` on stroke commit; only paint the in-progress stroke each frame.
   - For card thumbnails/desk view, prefer cached raster overlays.

5. **Make the core model generic, not “always 3 art layers”** — `S/M`
   - Remove fixed indices from `LayerStack` and UI.
   - Card drawing likely starts as a single ink layer plus whole-overlay show/hide.

6. **Add real package tests** — `S`
   - Constructor edge cases, serialization round-trip, undo/redo ordering, pointer ownership, cancel behavior, and read-only rendering output.

## 3. Gaps blocking the card-drawing use case

- **Serialization format:** none exists. For SQLite, I would store one JSON `TEXT` blob per card drawing plus an optional cached preview `BLOB` or filesystem PNG. JSON is easier to evolve than a normalized stroke table for this scale.
- **Recommended schema:** `{"v":1,"size":[220,140],"layers":[...],"activeLayerId":"..."}`
- **Stroke payload:** store points as `[x, y, p]` triples in card-local logical coordinates, rounded to 2 decimals. Include `color`, `isEraser`, and stroke options.
- **Coordinate space:** the current use of `event.localPosition` is acceptable if the editor widget itself is laid out at the card’s logical size and only the parent canvas applies transforms. Persist those card-local coordinates and include `size:[220,140]` in the document.
- **Whole-card show/hide:** current layer visibility can hide individual layers, but there is no first-class “drawing overlay enabled/disabled for this card” concept.
- **Export/thumbnail rendering:** completely missing. There is no offscreen renderer, no `ui.Image` export, and no thumbnail path.
- **Undo/redo:** current undo is active-layer-only and will feel wrong after layer switches or clears.
- **Bounds/clipping:** `DrawingCanvas` does not clip painting to card bounds. Thick edge strokes can bleed visually unless the parent clips.

## 4. API recommendation

The smallest public surface I would integrate is:

```dart
class SketchDocument {
  final Size logicalSize; // 220x140
  final List<SketchLayer> layers;
  Map<String, dynamic> toJson();
  factory SketchDocument.fromJson(Map<String, dynamic> json);
}

class SketchpadController extends ChangeNotifier {
  SketchDocument get document;
  bool get canUndo;
  bool get canRedo;
  void replaceDocument(SketchDocument document);
  void setLayerVisibility(String layerId, bool visible);
  void undo();
  void redo();
  Future<ui.Image> renderImage({double pixelRatio = 2.0});
}

class Sketchpad extends StatelessWidget {
  final SketchpadController controller;
  final SketchTool tool;
  final SketchInputPolicy inputPolicy;
  final VoidCallback? onChanged;
}
```

For `pin_and_paper_card_renderer`, do not pass sketchpad types into that module. Give the renderer a generic `Widget? overlay` or `CustomPainter? overlayPainter` slot; the main app can build that overlay from `SketchDocument` using sketchpad code outside the renderer package.

## 5. What I would delete or simplify now

- Move [`lib/main.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/main.dart:7>) and [`DrawingToolbar`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/widgets/toolbar.dart:5>) into `example/`. They are demo harness code, not package surface.
- Stop exporting [`toolbar.dart`](</home/bluekitty/Documents/Git/pin_and_paper_sketchpad/lib/sketchpad.dart:42>) publicly.
- Remove fixed three-layer assumptions from the model. Keep a convenience factory for the sketch/ink/color stack if you still want it for a standalone editor.
- Consider starting card integration with a **single ink layer** and eraser only. The three-layer art workflow is extra complexity for 220x140 task cards unless you know users need it.
