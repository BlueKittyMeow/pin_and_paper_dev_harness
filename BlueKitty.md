# BlueKitty's Cheat Sheet 🐱

*A reassuring guide to managing the Pin and Paper module system.*

---

## Your Repos At a Glance

| Repo | What It Is | Status |
|------|------------|--------|
| `pin-and-paper` | Main app (16k lines, the big one) | ✅ Working, Phase 3.9 |
| `pin_and_paper_sketchpad` | Drawing module | 🔨 Prototype working |
| `pin_and_paper_canvas` | Spatial positioning | 📋 Stub ready |
| `pin_and_paper_card_renderer` | Card visuals | 📋 Stub ready |
| `pin_and_paper_journal` | Future daybook | 📋 Not created yet |
| `pin_and_paper_dev_harness` | **Command center** | 📋 Docs ready |

---

## The Golden Rule

> **Specs and docs live in `dev_harness`. Code lives in module repos.**

Don't put specs in module repos. Don't put code in dev_harness (yet).

---

## Where Everything Lives

### In `pin_and_paper_dev_harness/`

```
docs/
├── ARCHITECTURE_AND_HARNESS.md   ← Big picture, how it all fits
├── INTERFACE_CONTRACTS.md        ← What modules need to know about each other
└── module_specs/
    ├── SKETCHPAD_SPEC.md         ← Drawing module spec
    ├── CANVAS_SPEC.md            ← Spatial canvas spec
    ├── CARD_RENDERER_SPEC.md     ← Card visuals spec
    └── JOURNAL_SPEC.md           ← Journal/daybook spec
```

### In module repos (sketchpad, canvas, card_renderer)

```
lib/               ← Code only
assets/            ← Images, textures (if needed)
pubspec.yaml
README.md          ← Brief, points to harness for specs
```

### In main app (`pin-and-paper/`)

```
docs/
└── CORE_API.md    ← Full API reference (source of truth)
lib/               ← The big codebase
```

---

## Working With AI Teams

### Starting work on a module

**Give the AI:**
1. The module's current code (if any)
2. The module's spec from `dev_harness/docs/module_specs/`
3. `INTERFACE_CONTRACTS.md` from `dev_harness/docs/`
4. Optionally: `ARCHITECTURE_AND_HARNESS.md` for context

**Don't give:**
- Full CORE_API.md (too much noise)
- Other module code
- Main app code

### Example prompt for canvas work:

> "Here's the canvas module spec and interface contracts. Let's implement Phase 4.1 — pan, zoom, and drag with placeholder rectangles."
> 
> [attach: CANVAS_SPEC.md]
> [attach: INTERFACE_CONTRACTS.md]
> [attach: current canvas lib/ folder if any]

### Example prompt for sketchpad work:

> "Here's the sketchpad spec. We need to add the eraser feature per the spec."
>
> [attach: SKETCHPAD_SPEC.md]
> [attach: current sketchpad lib/ folder]

---

## The Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. PLAN                                                │
│     Update spec in dev_harness/docs/module_specs/       │
│     (What are we building? What's the approach?)        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. BUILD                                               │
│     Work in the module repo with AI team                │
│     Give them: spec + interface contracts               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. TEST                                                │
│     (Eventually) Test in dev_harness with mocks         │
│     For now: test module in isolation                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. INTEGRATE                                           │
│     Wire module into main app                           │
│     Implement real DataSource interfaces                │
└─────────────────────────────────────────────────────────┘
```

---

## Phase Roadmap

| Phase | Module | What You're Building |
|-------|--------|---------------------|
| **Current** | sketchpad | Pressure drawing, eraser |
| 4.1 | canvas | Pan, zoom, drag rectangles |
| 4.2 | card_renderer | Beautiful static cards |
| 4.3 | canvas | Rotation, selection |
| 4.4 | main app | Wire it all together |
| 4.5 | card_renderer | Drawing on cards, flip |
| 5.x | card_renderer | Dynamic lighting |
| 6.x | journal | Daybook feature |

---

## Quick Reference: Which Doc for What?

| I need to... | Look at... |
|--------------|------------|
| Understand the whole system | `ARCHITECTURE_AND_HARNESS.md` |
| Know how modules talk to each other | `INTERFACE_CONTRACTS.md` |
| See the MVP plan for Phase 4 | `PHASE_4_MVP_ROADMAP.md` |
| Build/modify the sketchpad | `module_specs/SKETCHPAD_SPEC.md` |
| Build/modify the canvas | `module_specs/CANVAS_SPEC.md` |
| Build/modify the card renderer | `module_specs/CARD_RENDERER_SPEC.md` |
| Build/modify the journal | `module_specs/JOURNAL_SPEC.md` |
| Understand main app internals | Main app's `CORE_API.md` |

---

## When Things Feel Overwhelming

1. **You don't need to understand everything at once.** Each module is isolated for a reason.

2. **Start with one module, one phase.** Right now that's probably finishing sketchpad.

3. **The specs are your source of truth.** If you're not sure what to build, read the spec.

4. **It's okay to update specs.** They're living documents. If something doesn't make sense, change it.

5. **You're the conductor, not the orchestra.** You provide vision and taste. The AI team handles implementation details.

---

## Workflow Templates

Simplified templates for module work live in `docs/templates/`:

| Template | When to Use |
|----------|-------------|
| `WORKFLOW.md` | Reference guide for the whole process |
| `MODULE-PHASE-START.md` | Starting a new subphase |
| `MODULE-PHASE-END.md` | Closing a completed subphase |
| `module-findings-template.md` | Agent code review |

**Working directory:** `docs/working/[module]-[phase]/`
**Archive:** `docs/archive/[module]-[phase]/`

### Quick Start a Phase
```bash
# 1. Create working dir
mkdir -p docs/working/canvas-4.1/

# 2. Copy findings template if needed
cp docs/templates/module-findings-template.md docs/working/canvas-4.1/codex-findings.md

# 3. Review spec
cat docs/module_specs/CANVAS_SPEC.md

# 4. Go implement!
cd ../pin_and_paper_canvas
```

### Quick Close a Phase
```bash
# 1. Update spec checkboxes
# 2. Archive working dir
mv docs/working/canvas-4.1/ docs/archive/
# 3. Commit
git add -A && git commit -m "Complete canvas Phase 4.1"
```

---

## Updating Docs

### When to update INTERFACE_CONTRACTS.md:
- Main app API changes (new fields, new methods)
- You discover modules need something new from each other

### When to update a module spec:
- Scope changes (adding/removing features)
- Approach changes (technical decisions)
- After completing a phase (check off boxes, add learnings)

### When to update ARCHITECTURE_AND_HARNESS.md:
- Adding a new module
- Changing how modules relate
- Major structural decisions

---

## Checklist: Before Starting a Phase

- [ ] Spec exists for this phase's module
- [ ] Phase section in spec has clear checklist
- [ ] I know which repo I'm working in
- [ ] I have the right docs ready for the AI team

---

## Checklist: After Completing a Phase

- [ ] Code committed and pushed to module repo
- [ ] Spec updated (checkboxes marked, notes added)
- [ ] README in module repo still accurate
- [ ] Tested the feature works

---

## You've Got This 🐕

This is a well-structured system. The modules are isolated. The specs are clear. The interfaces are defined.

When you feel lost, come back to this doc. Read the relevant spec. Take it one phase at a time.

Woolfie believes in you. So does the AI team. 

---

*"Modularity isn't just architecture — it's how you ship complex software with a distributed AI team."*
