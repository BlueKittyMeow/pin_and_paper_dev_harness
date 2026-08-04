# Defaults to revisit before general users

Running registry of design choices where LARA'S BUILD gets one setting
but the general-user default is deliberately undecided until we've lived
with it. Started 2026-08-04 (owner request). Add an entry whenever we
ship a preference tuned to the owner rather than reasoned for strangers.

| # | Setting | Lara's build | General-user question | Evidence to gather |
|---|---|---|---|---|
| 1 | Z-order "last-touched comes to front" toggle | **ON** (physical-desk feel; owner decision 2026-08-04) | Research says comparable canvas apps default OFF (spatial memory, touch misfire risk) — see ZORDER_RESEARCH.md | How often does Lara hit accidental reshuffles on Android/finger vs desktop? Does she ever turn it off? |
| 2 | Drawing editor input policy | Stylus-only default, toggle available (owner L6) | Finger-first users (phone, no stylus) need the opposite default — possibly per-device detection | Friction reports from Lara's tablet vs phone use |
| 3 | Done-pile size | 10 most recent | Is 10 right for heavy completers? Configurable count vs fixed? | Does Lara's pile feel like glanceable history or clutter at 10? |
| 4 | Card-back fields | Global six-switch defaults (notes/tags/due/status on; created/id off) | Are these the right out-of-box switches? Notes per-card toggle default? | Which switches Lara actually changes |
| 5 | Marquee selection semantics (when built) | Intersection-based (catches touched cards) | Research recommends intersection for v1; containment-as-modifier on desktop later | Whether dense desks make intersection feel grabby |

## Adopted-direction notes (not defaults, but locked design)

- **tldraw-style overlap-aware reorder** for Bring Forward / Send
  Backward (owner 2026-08-04: emphatic yes): forward/back move relative
  to items actually overlapping, not a global list. Bring to Front /
  Send to Back stay global. See ZORDER_RESEARCH.md policy H.
- Z-order controls: toggle + all four explicit commands + a small
  animation in settings demonstrating the behaviors.
