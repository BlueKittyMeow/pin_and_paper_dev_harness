# Module Phase Start Checklist

**Purpose:** Start a new subphase in any module
**Used by:** BlueKitty + Claude

---

## Trigger

"Let's start [module] Phase X.Y" (e.g., "Let's start canvas Phase 4.1")

---

## Checklist

### 1. Identify Module and Phase

**Module:** _________________ (sketchpad / canvas / card_renderer / journal)
**Phase:** _________________ (e.g., 4.1, 4.2)
**Spec location:** `docs/module_specs/[MODULE]_SPEC.md`

---

### 2. Review the Spec

**Read:**
- [ ] Module spec (`docs/module_specs/[MODULE]_SPEC.md`)
- [ ] Relevant phase section in the spec
- [ ] `INTERFACE_CONTRACTS.md` if this phase touches interfaces

**Extract:**
- What this phase builds
- Acceptance criteria / checklist items
- Dependencies on other modules (if any)

**Confirm:** "Phase X.Y scope understood"

---

### 3. Create Working Directory

```bash
mkdir -p docs/working/[module]-[phase]/
# Example: docs/working/canvas-4.1/
```

**Confirm:** "Created docs/working/[module]-[phase]/"

---

### 4. Decide: Agent Review Needed?

**Use agent review if:**
- [ ] Feature is complex (multiple files, new patterns)
- [ ] Touches shared interfaces
- [ ] First major feature in a new module
- [ ] You want a second opinion

**Skip agent review if:**
- [ ] Small feature or bug fix
- [ ] Well-understood code changes
- [ ] Quick iteration on existing feature

**If YES → create findings docs:**
```bash
cp docs/templates/module-findings-template.md docs/working/[module]-[phase]/codex-findings.md
cp docs/templates/module-findings-template.md docs/working/[module]-[phase]/gemini-findings.md
# Customize each with module/phase info
```

**If NO → proceed to implementation**

---

### 5. Optional: Create Plan Notes

For complex phases, create a quick plan:

**File:** `docs/working/[module]-[phase]/plan.md`

```markdown
# [Module] Phase X.Y Plan

**Goal:** [One sentence]

**Approach:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Files to create/modify:**
- `lib/src/foo.dart` - New file for X
- `lib/src/bar.dart` - Add Y method

**Open questions:**
- [Any uncertainties]
```

For simple phases, skip this and just work from the spec.

---

### 6. Prep AI Team Context

**For module AI team, gather:**
- [ ] Module spec (relevant section)
- [ ] `INTERFACE_CONTRACTS.md` (if relevant)
- [ ] Current module code (`lib/` folder)
- [ ] Findings doc (if created)

**Example prompt:**
> "We're implementing [module] Phase X.Y: [description].
> Here's the spec section and interface contracts.
> Let's start with [first task]."

---

## Start Checklist Summary

At the end of this checklist:

✅ Know what we're building (spec reviewed)
✅ Working directory created
✅ Findings docs created (if agent review needed)
✅ Context ready for AI team

**Ready to implement!**

---

## Quick Start (Minimal Version)

For simple phases, just:

```bash
# 1. Review spec section
cat docs/module_specs/[MODULE]_SPEC.md | grep -A 50 "Phase X.Y"

# 2. Create working dir
mkdir -p docs/working/[module]-[phase]/

# 3. Go implement in module repo
cd ../pin_and_paper_[module]
```

---

**Template Version:** 1.0
**Created:** 2026-01-30
