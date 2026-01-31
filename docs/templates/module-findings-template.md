# Module Findings - [MODULE] Phase [X.Y]

**⚠️ TEMPLATE USAGE**
Copy this file, don't edit directly:
```bash
cp docs/templates/module-findings-template.md docs/working/[module]-[phase]/[agent]-findings.md
# Example: docs/working/canvas-4.1/codex-findings.md
```

---

**Module:** [sketchpad / canvas / card_renderer / journal]
**Phase:** [X.Y - Brief Description]
**Reviewer:** [Codex / Gemini / Other]
**Date:** [YYYY-MM-DD]
**Status:** ⏳ Pending Review

---

## Context

**What was built:**
[Brief description of what this phase implemented]

**Spec reference:**
`docs/module_specs/[MODULE]_SPEC.md` — Phase X.Y section

**Files to review:**
```
pin_and_paper_[module]/lib/
├── [list key files]
├── [...]
└── [...]
```

---

## Instructions

**🚫 DO NOT modify code** — document findings only, Claude will fix.

**🚫 DO NOT simulate other agents** — this is YOUR findings doc only.

**Review focus:**
1. Code correctness (does it do what the spec says?)
2. Edge cases (what could break?)
3. Performance (obvious inefficiencies?)
4. Code quality (readability, patterns)

---

## Review Commands

```bash
# Navigate to module
cd pin_and_paper_[module]

# Static analysis
flutter analyze

# Run tests (if any)
flutter test

# Search for patterns
grep -r "[pattern]" lib/

# Check for TODOs
grep -r "TODO\|FIXME" lib/
```

---

## Findings

### Issue Format

```markdown
### Issue #[N]: [Title]

**File:** `lib/path/to/file.dart:line`
**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]
**Type:** [Bug / Performance / Code Quality / Missing Feature]

**Description:**
[What's wrong]

**Code:**
\`\`\`dart
[Problematic code]
\`\`\`

**Suggested Fix:**
[How to fix it]

---
```

---

## [Document findings here]

_Add issues using the format above._

---

## Build/Analyze Results

**flutter analyze:**
```
[Output or "✅ Clean"]
```

**flutter test:**
```
[Output or "No tests yet" or "✅ All passing"]
```

---

## Summary

**Total issues:** [X]

| Severity | Count |
|----------|-------|
| CRITICAL | [X] |
| HIGH | [X] |
| MEDIUM | [X] |
| LOW | [X] |

**Must fix:** [List CRITICAL/HIGH issue numbers]

**Can defer:** [List LOW issue numbers]

---

## Notes for Claude

[Any additional context to help with fixes]

---

**Review complete:** [YES / NO]
**Time spent:** [X minutes]
