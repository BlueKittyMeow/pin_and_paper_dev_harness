# Phase 6: Journal / Daybook Module Spec

## Overview

A Hobonichi-inspired daily planner that serves as a **temporal record of existence**. The journal auto-populates with completed tasks and provides space for doodling, notes, and reflection. It's both functional (review what you did) and therapeutic (proof you existed and accomplished things).

**Priority:** Phase 6 (after Spatial Workspace complete)
**Complexity:** High
**Dependencies:** Sketchpad module, Card Renderer (paper textures), Task data layer

---

## Philosophy

> "Temporal proof of existence — see your accomplishments, know you persisted."

For ADHD brains, the past can feel fuzzy or lost. Days blur together. The journal provides:
- **Concrete evidence** of what you did (auto-populated tasks)
- **Creative expression** space (doodling, notes)
- **Ritual/grounding** through the physical planner metaphor
- **Time navigation** that feels tangible (page flips, not infinite scroll)

---

## Core Features

### Auto-Population
Each day's page automatically shows:
- Date header (with day of week, maybe moon phase for witchy vibes 🌙)
- Completed tasks from that day
- Time completed (optional, toggleable)
- Task tags as small color chips

User doesn't have to do anything — the journal writes itself.

### Drawing / Doodling
Full sketchpad capabilities on each page:
- Sketch, ink, color layers
- Draw alongside, around, or over task entries
- Doodles persist per page

### Navigation
Physical book metaphor:
- Swipe to turn pages
- Animated page flip with curl/shadow
- Jump to today (ribbon bookmark)
- Date picker for distant dates

### Customization
- Page templates (daily, weekly spread, blank)
- Paper textures (cream, dot grid, lined, graph)
- User notes/text areas
- Stickers/stamps (future)

---

## Entry Points

The journal is accessible from multiple places:

| Entry Point | Behavior |
|-------------|----------|
| **Pull-up sheet** | Swipe up from bottom edge of any screen → journal opens to today |
| **Tab/mode toggle** | List View / Spatial View / Journal View in nav |
| **From completed task** | Tap completed task → "View in Journal" → opens to that day, scrolls to task |
| **From notification** | "You completed 5 tasks today!" → tap → journal for today |

The pull-up is the primary/always-available method. Others are shortcuts.

---

## Visual Design

### Book Metaphor
- Visible spine on left edge when open
- Two-page spread option (landscape/tablet) or single page (phone)
- Page edges visible (that riffly paper edge look)
- Ribbon bookmark dangling from spine

### Page Layout
```
┌─────────────────────────────────────────┐
│ ☽ Wednesday, January 29, 2025          │  ← Date header
├─────────────────────────────────────────┤
│                                         │
│  ✓ Brush Woolfie              2:30 PM  │  ← Auto-populated tasks
│    [pet] [self-care]                    │     with tags
│                                         │
│  ✓ Submit project proposal    4:15 PM  │
│    [work] [important]                   │
│                                         │
│  ✓ Call mom                   6:00 PM  │
│    [family]                             │
│                                         │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │  ← Soft divider
│                                         │
│  [User doodles / notes area]           │
│                                         │
│        🐕 ~little woolfie~              │  ← User's drawing
│                                         │
│  "Good day today. Tired but okay."     │  ← User's note
│                                         │
└─────────────────────────────────────────┘
         │ 29 │                              ← Page number/date
```

### Paper Textures
Reuse from card renderer:
- Cream (`#F5F1E8`)
- Kraft (`#D4B896`)
- Options: blank, lined, dot grid, graph

### Lighting
If Phase 5 dynamic lighting is implemented, journal pages respond too:
- Morning: warm sunlight on pages
- Evening: lamp glow, warmer shadows

---

## Page Flip Animation

### Basic Flip
- Swipe left → next day (page turns right-to-left)
- Swipe right → previous day (page turns left-to-right)
- Page rotates on Y-axis with perspective
- Shadow cast on underlying page during flip
- ~300ms duration, ease-out curve

### Page Curl (Stretch Goal)
- Corner follows finger during drag
- Page actually curls/bends, not just rotates
- Reveals next page underneath
- This is complex — many apps skip it. Evaluate after basic flip works.

### Performance
- Preload adjacent pages (yesterday, tomorrow)
- Lazy-load drawings (load strokes when page is approached)
- Virtualize distant pages (don't keep 365 pages in memory)

---

## Data Model

### JournalPage
```dart
class JournalPage {
  final DateTime date;
  final List<CompletedTaskEntry> tasks;    // Auto-populated
  final List<DrawingLayer> drawings;        // User doodles
  final String? userNotes;                  // Text note area
  final PageTemplate template;
  final PaperTexture texture;
  
  bool get isEmpty => tasks.isEmpty && drawings.isEmpty && userNotes == null;
  bool get hasUserContent => drawings.isNotEmpty || userNotes != null;
}

class CompletedTaskEntry {
  final String taskId;
  final String title;
  final DateTime completedAt;
  final List<Tag> tags;
  final Offset? customPosition;            // If user drags it around
}

enum PageTemplate { daily, weeklySpread, blank, custom }
enum PaperTexture { cream, kraft, dotGrid, lined, graph }
```

### Storage

**Option A: SQLite tables**
```sql
journal_pages (
  date DATE PRIMARY KEY,
  template TEXT,
  texture TEXT,
  user_notes TEXT,
  drawings BLOB,                -- JSON or binary stroke data
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**Option B: File-based per page**
```
/journal/
  /2025-01-29/
    page.json         -- metadata, notes, template
    drawings.json     -- stroke data
  /2025-01-30/
    ...
```

File-based might be cleaner for large drawing data. Evaluate based on performance.

---

## Module Structure

```
pin_and_paper_journal/
├── lib/
│   ├── models/
│   │   ├── journal_page.dart
│   │   ├── completed_task_entry.dart
│   │   └── page_template.dart
│   ├── widgets/
│   │   ├── journal_sheet.dart          # Pull-up container
│   │   ├── journal_page_view.dart      # Single page renderer
│   │   ├── page_flip_view.dart         # Page turn container + animation
│   │   ├── page_flip_animation.dart    # The actual flip math
│   │   ├── task_entry_widget.dart      # Completed task display
│   │   ├── date_header.dart            # Date + moon phase + vibes
│   │   └── ribbon_bookmark.dart        # Jump to today
│   ├── services/
│   │   ├── journal_service.dart        # Load/save pages
│   │   └── task_aggregator.dart        # Query completed tasks by date
│   └── journal.dart                    # Public API
├── pubspec.yaml
│   dependencies:
│     pin_and_paper_sketchpad:
│       path: ../pin_and_paper_sketchpad
└── README.md
```

---

## Integration Points

### With Main App
```dart
/// Main app provides this to journal module
abstract class JournalDataSource {
  /// Get all tasks completed on a specific date
  Future<List<CompletedTaskEntry>> getCompletedTasks(DateTime date);
  
  /// Navigate to task in list/spatial view
  void navigateToTask(String taskId);
  
  /// Get date range with any completed tasks (for calendar/nav)
  Future<DateRange> getActivityRange();
}
```

### With Sketchpad Module
Journal embeds sketchpad directly:
```dart
JournalPageView(
  page: page,
  child: Sketchpad(
    layerStack: page.drawingLayers,
    // ... 
  ),
)
```

### With Card Renderer
Reuse paper textures and shadow rendering.

---

## Subphases

### Phase 6.1: Foundation (1-2 weeks)
- Pull-up sheet UI (`DraggableScrollableSheet` or custom)
- `JournalPage` data model
- Basic page layout (date header + task list)
- Query completed tasks by date
- Navigate by date (arrows/buttons, no animation yet)
- Persist page data (SQLite or file)

**Deliverable:** Can open journal, see today's completed tasks, navigate to other days

### Phase 6.2: Page Flip Animation (1-2 weeks)
- Horizontal swipe detection
- Basic page turn animation (3D rotate on Y-axis)
- Shadow during flip
- Preload adjacent pages
- Gesture → animation feels natural (velocity-based)

**Deliverable:** Can swipe between days with satisfying page flip

### Phase 6.3: Drawing Integration (1 week)
- Embed sketchpad in page
- Per-page drawing layer storage
- Drawings persist and reload
- Drawing works alongside task entries

**Deliverable:** Can doodle on journal pages, comes back when you return

### Phase 6.4: Templates & Textures (1 week)
- Page template options (daily, weekly, blank)
- Paper texture options
- User notes text area
- Template picker in page settings

**Deliverable:** Pages can look different, user can customize

### Phase 6.5: Navigation Polish (1 week)
- Ribbon bookmark (jump to today)
- Date picker for distant dates
- "View in Journal" from completed task
- Activity indicators (dots on dates that have content)

**Deliverable:** Navigation feels complete and intuitive

### Phase 6.6: Advanced Polish (stretch)
- Page curl animation (if basic flip isn't satisfying enough)
- Moon phases in date header 🌙
- Weekly spread layout (two pages side by side)
- Stickers/stamps library
- Export page as image/PDF

---

## Open Questions

1. **Weekly spread:** Is this portrait-two-pages or landscape-single-view? Tablet vs phone?
2. **Tasks layout:** Strict list, or can user drag tasks around the page?
3. **Handwriting vs typed notes:** Just drawing, or actual text input too?
4. **Search:** Can you search journal pages? By date, by task, by tag?
5. **Sharing:** Export/share a page image? "Look what I accomplished!"

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Page flip performance | Janky animation kills the vibe | Preload, virtualize, test early on low-end device |
| Drawing data size | Many pages × many strokes = storage bloat | Compress strokes, lazy load, consider file-based storage |
| Scope creep | "Just one more feature" delays forever | Strict subphases, ship 6.1-6.3 before polish |
| Complexity | Journal + spatial + drawing = a lot | Module boundaries, clean interfaces, reuse ruthlessly |

---

## Dependencies Summary

| Dependency | Status | Blocker? |
|------------|--------|----------|
| Sketchpad module | In progress | Yes — need drawing for 6.3 |
| Card renderer (textures) | Phase S4.2 | No — can use solid colors initially |
| Completed task timestamps | Exists ✓ | No |
| SQLite migrations | Exists ✓ | No |

---

## Success Criteria

The journal is successful if:
- [ ] Opening it feels like opening a real planner (satisfying)
- [ ] Page flips feel physical, not digital
- [ ] Seeing past completed tasks triggers positive feelings
- [ ] Drawing on pages is joyful, not frustrating
- [ ] Performance is smooth even with months of history
- [ ] Users actually open it (engagement metric)

---

## References

- **Hobonichi Techo** — The gold standard for daily planners
- **Hobonichi app** — Their digital version (Japan only, but screenshots exist)
- **Day One app** — Journal with auto-population from calendar/photos
- **GoodNotes / Notability** — Page flip implementations
- **Apple Books** — Page curl animation reference

---

*"From chaos to clarity, one index card at a time — and one page at a time."* 🍂✨📌
