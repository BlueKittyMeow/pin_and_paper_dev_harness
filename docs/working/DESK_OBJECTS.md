# Desk Objects — tchotchke roster & design notes

Owner-driven wishlist and design thinking for Spatial View desk objects
(knick-knacks). Started 2026-08-04. Related: the queued **object drawer**
feature (ghosted-if-placed, full-opacity-if-available — owner, 2026-08-03),
post-it notes as objects, and sketch+object grouping (see HANDOFF +
CARD_DRAWINGS_PLAN owner answers L7/L9).

## Modeled/shipped

| Object | Status | Notes |
|---|---|---|
| Amethyst chunk | SHIPPED (2026-08-03) | 2.5D painted CustomPainter, yaw rotation, grounding shadow ("shadow saga" — chimera of Gemini base + Claude contact line/caustics). Resize chips. zIndex 1<<20 paperweight. |

## Wishlist (owner)

| Object | Notes |
|---|---|
| Marble scottie OR longhaired dachshund figurine | "slightly roughly cut" marble — carved-not-polished look |
| Glass amber toad | Owner has the real one — she'll photograph it for reference (multiple angles useful if we try photo-derived modeling) |
| Post-it notes | Functional object (writeable?), also drawer item |

## Open design question: 2.5D vs 3D, and the desk's camera

Owner framing (2026-08-04): if objects are actually modeled (3D), they
could plant their "feet" flat on the surface and be rendered that way —
which suggests a slightly **isometric/tilted view of the desk itself** —
OR users could rotate objects freely and rest them on their sides.
Current state: desk is rendered flat/top-down-ish; the amethyst is a
painted 2.5D illusion with its own baked perspective and a
down-left-sun shadow convention (kDeskLightAzimuth).

Codex research LANDED → `DESK_OBJECTS_3D_RESEARCH.md` (2026-08-04).
Recommended path for the next 2-3 tchotchkes (pending owner read):
- **Keep the 3/4 cheat; do NOT tilt the desk.** Paper-first surface,
  upright objects, shadows do the grounding — the established convention
  (Stardew/JRPG lineage). True isometric would force foreshortened cards
  and projective drag math for little gain.
- **No live 3D yet.** flutter_scene is pre-1.0/master-only; flutter_gl
  and three_dart are 3 years stale; engine embedding fights the widget
  canvas. Revisit only if tchotchkes become a real system (many objects,
  occlusion, animation, inspect mode).
- **Rendering: prerendered sprite sets** — model/paint once, render
  24-48 yaw frames + separate contact/cast shadow layers, ship as
  ordinary widgets. Excellent mid-Android perf; drop-in with the canvas.
- **Toad confirmed photogrammetry-hostile** (RealityScan: "glass may
  fail entirely"; Polycam: matte-spray workaround). Photos as REFERENCE,
  model by eye — which is exactly the Blender-agent pipeline below.
- **Rotation: yaw-only turntable** for tchotchkes (matches amethyst),
  authored snap poses (upright/on-side) only where meaningful; free 2D
  in-plane rotation stays for cards. No free 3D rotation — "reads like
  a 3D editor, not a desk."
- **TODO before the next tchotchke: author a desk-object STYLE BIBLE**
  (codex's added question, and the best catch in the report): one light
  direction, one shadow recipe, one scale convention, one camera cheat,
  one footprint/hitbox rule, one apparent-height range — so a painted
  crystal, a modeled marble dog, and a glass toad read as one desk.

## Asset-creation option: agent-driven Blender (owner note 2026-08-04)

Blender MCP integrations exist for both Claude and codex; the owner has
seen strong results from pure agent loops (model → screenshot → adjust),
including fully articulated/rigged mechanisms. Potential pipeline for
tchotchkes: agent models the object in Blender from reference photos →
decimate/simplify the mesh → either export for real-3D rendering or
prerender to per-yaw sprite sets (whichever the 3D research recommends).
This sidesteps photogrammetry's glass problem for the amber toad —
model it by eye from photos instead of scanning it. Evaluate alongside
the codex 3D research when it lands; if adopted, the Blender MCP setup
gets its own session (install, connect, test loop on a simple object).
