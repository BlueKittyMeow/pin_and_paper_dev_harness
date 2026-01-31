# Module Workflow Guide

**Purpose:** How to manage development across the Pin and Paper module system.
**Scope:** All modules (sketchpad, canvas, card_renderer, journal)
**For:** BlueKitty + AI Team

---

## Key Differences from Main App

| Main App | Modules |
|----------|---------|
| 16k+ lines, complex | Small, focused (<2k lines each) |
| Heavy process needed | Lighter process okay |
| Specs live in `docs/` | Specs live in **harness** |
| One repo | Multiple repos |
| Database migrations | No database (usually) |

**Result:** Module workflow is simpler but still structured.

---

## Where Things Live

```
pin_and_paper_dev_harness/          ← Command Center
├── docs/
│   ├── module_specs/               ← All specs here
│   │   ├── SKETCHPAD_SPEC.md
│   │   ├── CANVAS_SPEC.md
│   │   ├── CARD_RENDERER_SPEC.md
│   │   └── JOURNAL_SPEC.md
│   ├── INTERFACE_CONTRACTS.md      ← Shared interfaces
│   └── templates/                  ← These templates
│       ├── WORKFLOW.md (this file)
│       ├── MODULE-PHASE-START.md
│       ├── MODULE-PHASE-END.md
│       └── module-findings-template.md
└── BlueKitty.md                    ← Your cheat sheet

pin_and_paper_[module]/             ← Code only
├── lib/
├── README.md                       ← Brief, points to harness
└── pubspec.yaml
```

---

## The Module Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│  1. PREP (in harness)                                   │
│     - Update/create spec in module_specs/               │
│     - Define what this subphase builds                  │
│     - Create working directory in harness               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. BUILD (in module repo)                              │
│     - Give AI team: spec + contracts                    │
│     - Implement the feature                             │
│     - Commit frequently                                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. REVIEW (agent findings)                             │
│     - Create findings docs in harness working dir       │
│     - Codex/Gemini review the module code               │
│     - Fix issues found                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. CLOSE                                               │
│     - Update spec checkboxes                            │
│     - Archive working dir                               │
│     - Update module README if needed                    │
└─────────────────────────────────────────────────────────┘
```

---

## When to Use Full Process vs. Light Process

### Full Process (use templates)
- Major features (e.g., "implement eraser system")
- Anything touching multiple files
- Features that need agent review
- Phase milestones (4.1, 4.2, etc.)

### Light Process (just commit and go)
- Bug fixes
- Small tweaks
- Documentation updates
- Refactoring within a file

**Rule of thumb:** If it takes more than an hour, use the full process.

---

## Working Directory Structure

During active work on a module subphase:

```
pin_and_paper_dev_harness/
├── docs/
│   └── working/                    ← Active work (not archived yet)
│       └── [module]-[phase]/       ← e.g., sketchpad-eraser/
│           ├── plan.md             ← What we're building (optional)
│           ├── codex-findings.md   ← Codex review
│           ├── gemini-findings.md  ← Gemini review
│           └── notes.md            ← Your notes (optional)
```

After completion, move to archive:

```
pin_and_paper_dev_harness/
├── docs/
│   └── archive/
│       └── [module]-[phase]/       ← Completed work
```

---

## Quick Reference: Which Template When

| I'm doing... | Use... |
|--------------|--------|
| Starting a new subphase | `MODULE-PHASE-START.md` |
| Closing a completed subphase | `MODULE-PHASE-END.md` |
| Agent review | `module-findings-template.md` |
| Quick fix or tweak | No template, just commit |

---

## Agent Coordination

### For Module Work

**Give agents:**
1. The module spec (from `module_specs/`)
2. `INTERFACE_CONTRACTS.md`
3. The module's current code
4. Their findings doc (from template)

**Don't give:**
- Full main app code
- Other module implementations
- CORE_API.md (too much noise)

### Findings Docs

- One per agent per subphase
- Lives in `docs/working/[module]-[phase]/`
- Simplified version of main app template
- Archive when subphase complete

---

## Spec Updates

### During Development
- Check off completed items in the spec
- Add notes about decisions made
- Update "Future Considerations" if scope changes

### After Subphase Complete
- Mark phase section as done
- Add any lessons learned
- Update testing checklist results

### Example:
```markdown
## Phase 4.1: Canvas Foundation

- [x] Basic widget structure
- [x] Viewport transform (pan/zoom matrix)
- [x] Two-finger pan gesture
- [ ] Pinch-to-zoom gesture        ← Still working on this
```

---

## Integration with Main App

When a module is ready to integrate:

1. **In main app repo:**
   - Add module as dependency in `pubspec.yaml`
   - Implement real DataSource interfaces
   - Wire up navigation

2. **Follow main app's full process:**
   - Use main app templates (phase-start, phase-end)
   - Agent review of integration code
   - Full validation cycle

The module itself is done; integration is a main app task.

---

## Tips

1. **Don't over-process small modules.** A 200-line canvas module doesn't need the same rigor as a 16k-line main app.

2. **Specs are living docs.** Update them as you learn. They're not contracts, they're guides.

3. **Archive liberally.** When a subphase is done, move the working dir to archive. Clean workspace = clear mind.

4. **Test in harness (eventually).** Once harness has mocks, test modules there before integrating.

5. **One module at a time.** Finish sketchpad before starting canvas. Context switching kills momentum.

---

## Checklist: Module Subphase

Quick version of the full process:

**Start:**
- [ ] Create working dir: `docs/working/[module]-[phase]/`
- [ ] Review spec for this phase
- [ ] Create findings docs from template (if agent review needed)

**Build:**
- [ ] Implement in module repo
- [ ] Commit frequently with clear messages
- [ ] Update spec checkboxes as you go

**Review (if needed):**
- [ ] Codex reviews code
- [ ] Gemini runs build/analyze
- [ ] Fix issues found
- [ ] Verify fixes

**Close:**
- [ ] All spec checkboxes for this phase checked
- [ ] Module builds and runs
- [ ] Archive working dir
- [ ] Update module README if needed

---

**Template Version:** 1.0
**Created:** 2026-01-30
**For:** Pin and Paper module system
