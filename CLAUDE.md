# Pin & Paper Dev Harness - Shared Architecture Context

This file is loaded by all module repos via `additionalDirectories`. It provides canonical architecture rules and spec locations.

## 🏗️ Module Architecture

```
pin_and_paper (main app)
    ├── pin_and_paper_canvas (spatial task management)
    │   └── pin_and_paper_sketchpad (drawing/ink engine)
    ├── pin_and_paper_card_renderer (task card widgets)
    └── pin_and_paper_journal (Phase 6 - future)
```

**Dependency Rule**: Modules depend DOWN only. Never create circular dependencies.
- App can depend on all modules
- Canvas depends on Sketchpad
- Card Renderer is standalone
- Journal will depend on Sketchpad

## 📋 Spec Locations

| Phase | Spec File | Status |
|-------|-----------|--------|
| 4.1 Canvas MVP | `specs/phase-4.1-canvas-mvp/canvas-mvp-spec.md` | Ready |
| 4.2 Card Renderer | `specs/phase-4.2-card-renderer-mvp/card-renderer-spec.md` | Ready |
| 4.3 Integration | `specs/phase-4.3-integration/integration-spec.md` | Ready |
| 5 Polish | `specs/phase-5-spatial-polish/spatial-polish-spec.md` | Ready |
| 6 Journal | `specs/phase-6-journal/journal-spec.md` | Ready |

**Always read the relevant spec before implementing features.**

## 🔧 Module Paths (Local Development)

```
~/Documents/Git/pin-and-paper/                    # Main app
~/Documents/Git/pin_and_paper_sketchpad/          # Drawing engine
~/Documents/Git/pin_and_paper_canvas/             # Spatial canvas
~/Documents/Git/pin_and_paper_card_renderer/      # Card widgets
~/Documents/Git/pin_and_paper_journal/            # Journal (Phase 6)
~/Documents/Git/pin_and_paper_dev_harness/        # This repo - specs & integration
```

## 🎯 Key Architecture Decisions

### State Ownership
- **Task data**: Lives in main app's SQLite via TaskService
- **Spatial positions**: Lives in main app (canvas just displays)
- **Drawing strokes**: Live in Sketchpad's StrokeController
- **Card rendering**: Stateless - receives TaskCardData, renders widget

### Data Flow for Spatial Tasks
```
User creates task → TaskService.createTask() → SQLite
                                             ↓
UI refresh → Spatial Canvas gets tasks → transforms to TaskCardData
                                             ↓
                          CardRenderer displays → User sees card
```

### Module Communication
- Modules expose **callbacks** for events (onTaskTap, onStrokeComplete)
- Modules receive **data** and **configuration**, not services
- Main app orchestrates - modules are dumb renderers

## 🧪 Testing Strategy

- **Unit tests**: In each module repo (`flutter test`)
- **Integration tests**: In this harness (`integration_test/`)
- **Visual verification**: Run module's `example/` app

## 📝 Commit Message Convention

```
type(scope): description

Types: feat, fix, refactor, docs, test, chore
Scopes: canvas, card, sketchpad, journal, harness, app
```

## ⚠️ Safety Reminders

All repos have `.claude/hooks/safety-guard.py` that blocks:
- `rm -rf .git`
- `git push --force` to main/master
- `git reflog expire`

**Always commit before major refactors.**
