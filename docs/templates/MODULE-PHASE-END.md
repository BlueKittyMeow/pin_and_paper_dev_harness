# Module Phase End Checklist

**Purpose:** Close out a completed module subphase
**Used by:** BlueKitty + Claude

---

## Trigger

"Phase X.Y is done" or "Let's close [module] Phase X.Y"

---

## Checklist

### 1. Verify Implementation Complete

**In module repo (`pin_and_paper_[module]/`):**

- [ ] Feature works as intended
- [ ] Code committed and pushed
- [ ] No obvious bugs or crashes

**Quick test:**
```bash
cd ../pin_and_paper_[module]
flutter pub get
flutter analyze
flutter test  # if tests exist
flutter run   # manual smoke test
```

**Confirm:** "Implementation complete and tested"

---

### 2. Update Spec Checkboxes

**File:** `docs/module_specs/[MODULE]_SPEC.md`

**Update:**
- [ ] Check off completed items in the phase section
- [ ] Add any notes about decisions made
- [ ] Note any deferred items with "→ Future" marker

**Example:**
```markdown
### Phase S4.1: Canvas Foundation

- [x] Basic widget structure
- [x] Viewport transform (pan/zoom matrix)
- [x] Two-finger pan gesture
- [x] Pinch-to-zoom gesture
- [x] Entity drag gesture
- [ ] Grid snapping → Future (not needed for MVP)

**Notes:** Used InteractiveViewer as base, extended for entity drag.
**Completed:** 2026-02-15
```

**Confirm:** "Spec updated with completion status"

---

### 3. Agent Review Complete? (If Applicable)

**If agent review was done:**

- [ ] Codex findings doc completed
- [ ] Gemini findings doc completed
- [ ] All CRITICAL/HIGH issues resolved
- [ ] Remaining issues documented as deferred

**If no agent review:** Skip to step 4.

---

### 4. Update Module README (If Needed)

**File:** `pin_and_paper_[module]/README.md`

**Update if:**
- Public API changed
- New features added that affect usage
- Dependencies changed

**Usually no update needed** for internal changes.

---

### 5. Archive Working Directory

```bash
# Create archive location
mkdir -p docs/archive/

# Move working dir to archive
mv docs/working/[module]-[phase]/ docs/archive/[module]-[phase]/

# Verify
ls docs/archive/[module]-[phase]/
```

**Confirm:** "Working directory archived"

---

### 6. Commit Harness Changes

```bash
cd pin_and_paper_dev_harness

git add docs/module_specs/[MODULE]_SPEC.md
git add docs/archive/[module]-[phase]/
git commit -m "docs: Complete [module] Phase X.Y

- Updated spec with completion status
- Archived working directory
- [Brief summary of what was built]"

git push
```

---

## End Checklist Summary

At the end of this checklist:

✅ Module code committed and tested
✅ Spec checkboxes updated
✅ Agent findings addressed (if applicable)
✅ Working directory archived
✅ Harness changes committed

**Phase X.Y complete! Ready for next phase.**

---

## Quick Close (Minimal Version)

For simple phases:

```bash
# 1. Update spec checkboxes (manually edit)
# 2. Archive working dir
mv docs/working/[module]-[phase]/ docs/archive/
# 3. Commit
git add -A && git commit -m "Complete [module] Phase X.Y"
```

---

## If Issues Were Deferred

Add deferred items to the spec's "Future Considerations" or create a note:

**In spec:**
```markdown
## Future Considerations

- [ ] Grid snapping (deferred from S4.1)
- [ ] Multi-select (deferred from S4.3)
```

**Or in archive:**
Create `docs/archive/[module]-[phase]/deferred.md` listing what was skipped and why.

---

## Transitioning to Main App Integration

When a module is complete enough to integrate:

1. **This is a main app task, not a module task**
2. Use main app's `phase-start-checklist.md`
3. Integration gets its own phase (e.g., "Phase S4.4: Canvas Integration")
4. Full agent review of integration code

The module subphases are done; integration is a new chapter.

---

**Template Version:** 1.0
**Created:** 2026-01-30
