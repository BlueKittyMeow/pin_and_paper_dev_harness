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

The `specs/phase-*` paths below used to appear here but exist in no repo.
The real specs are all under `docs/module_specs/` in this repo:

| Phase | Spec File | Status |
|-------|-----------|--------|
| S4.1 Canvas MVP | `docs/module_specs/CANVAS_SPEC.md` | Ready |
| S4.2 Card Renderer | `docs/module_specs/CARD_RENDERER_SPEC.md` | Ready |
| — Sketchpad | `docs/module_specs/SKETCHPAD_SPEC.md` | Prototype working |
| 6 Journal | `docs/module_specs/JOURNAL_SPEC.md` | Placeholder screen only |

**Always read the relevant spec before implementing features.**

**Plan of record vs. roadmap:**
- `docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md` is the **approved POC plan**
  currently being executed (branch `claude/drag-drop-canvas-mvp-cu6uoy`) —
  read this before touching canvas, card_renderer, or main-app spatial code.
- `docs/prototype.md` is the roadmap: what the POC covers, what's deferred
  until after it (harness app, sync, polish, journal).

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
