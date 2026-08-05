# DESK 3D BRIEF — model the desk itself in Blender

**Status:** SCOPED 2026-08-05 (late session, owner + Claude "uña y carne").
**Runs in its own fresh session** — this is a deliberately big lift with
big payoff; expect heavy agent/token spend, planned for.
**Prerequisite sequence (owner):** finish the gem HABIT round first
(review strip → owner approval → farm-render full gem bundles), THEN
clear context and kick this off.

## Why (the payoff list, owner's own)

The current desk is a warped photo (`desk_executive.webp`, pipeline at
`reference/desk_assets/regenerate_desk_asset.py`). It works, but it has
**baked lighting** — which violates the workshop style bible (neutral-lit
assets + separate shadow layers, app owns light) and caps half the
roadmap. A modeled desk unlocks:

1. **Reskins** — "cottage-core distressed paint desk" = a material
   definition + a farm re-render. Economics already PROVEN by the
   gemchunk (one mesh, four materials, ~6 min farm time).
2. **Rigged, usable drawers** — renderable open/closed states; endgame:
   the desk's real drawer becomes the desk-objects drawer UI (tap the
   drawer front, it opens, tchotchkes inside).
3. **Lighting** — re-render under any sun, or ship neutral + runtime
   tint/gobo per the time-of-day plan. The desk joins the same lighting
   system as every prop.
4. **Parametric width** — owner's "this desk could be a bit wider"
   becomes a build-script argument.
5. **Panel rect BY CONSTRUCTION** — no more photo warping and groove
   archaeology; the camera is authored so the usable surface renders as
   an exact rectangle at known pixel coords.

## Architecture: the HINGED DESK (owner's cheat — the "bent set")

The desk's app look is an impossible projection: true top-down surface
+ visible drawer fronts. Instead of faking it with warps or composites:

- **Model the desk normally**, then **hinge the top surface at the
  front edge** (where top meets frame) and lift it from the back until
  it hangs perpendicular to the camera. (Owner's invention; it is the
  classic theater/matte-painting "bent set" trick.)
- **Orthographic camera** (house standard). The lifted surface renders
  as a mathematically exact rectangle; drawer fronts render face-on
  below it; the hinge line gives GEOMETRIC continuity — no compositing
  seam, ever, in any light or drawer state.
- **Single render pass** → shadows/lighting agree globally across
  surface + drawers (critical for gobo relighting later).
- **Watch-item:** the lifted surface is lit as if vertical; the light
  rig may need per-zone tuning so the surface reads "flat desk under
  window light," not "wall." It's a bake — author until it reads right.
- **Fallback if bent-geometry lighting fights us:** two-camera
  composite (ortho straight-down pass for the surface + front-elevation
  pass for the drawer band, blended at the lip like the photo pipeline
  effectively is). Keep in reserve; hinge is primary.

## Specs / contract with the app

- App contract (already shipped, keep it): canvas = inner bevel panel,
  currently **1823×1264 logical px**, canvas origin = panel top-left;
  desk image positioned by a fixed offset; drawers/rim overflow as
  decoration (Stacks are Clip.none). A modeled desk may CHANGE panel
  dims (esp. if width goes parametric) — that's fine; update
  `kCanvasScreenSize` + `kDeskImageOffset/Size` together, and remember
  the stored-positions migration quirk (cards outside new bounds are
  strandable — see "recall all cards" backlog item).
- Desk mats: full-canvas art dropped in the panel — modeled desk should
  keep a crisp bevel/groove so mats read as sitting IN it.
- Scale: desk is NOT a tiny prop — global 3000 px/m policy at 1:1... in
  practice author the render so panel px ≈ canvas logical px (≈2000 px
  wide master); follow world-scale policy discussion in
  MCP_PILOT_NOTES; frame padding lesson applies (measure shadow
  extents; contact vs cast — measure, don't assume).
- Render deliverables per skin:
  - color layer, NEUTRAL light (style bible), full desk incl. drawers
  - separate cast + contact shadow layers (desk onto floor)
  - drawer states: v1 minimum = all-closed; stretch = per-drawer open
  - v1 skins: (a) match the beloved executive-desk look (the current
    photo is the reference), (b) ONE proof-of-economics variant (owner
    suggested cottage-core distressed paint)
- Workshop process: agentic-blender-props conventions (CLAUDE.md house
  rules: checkpoints, ≤6 correction rounds, codex critic, literal
  measurements, plateau rule, MarshLair farm, keep meshes AND sprites).
  Furniture is boxy — geometry is notebook-tier, not dachshund-tier;
  expect the iterations to go into WOOD MATERIALS and light tuning.

## Open questions for the owner (answer before/at kickoff)

1. v1 skin: faithful recreation of the current executive desk? (Bar =
   "as good as the photo she already loves.")
2. Drawer roster: how many drawers rigged, which get open-state renders
   in v1?
3. Parametric width in v1, or fixed-first-then-parametric?
4. Does the floor backdrop stay a photo, or eventually get modeled into
   the same scene for coherent desk-on-floor shadows?

## Session-1 kickoff shape (suggested)

1. Read this brief + workshop CLAUDE.md + MCP_PILOT_NOTES +
   RETROSPECTIVE + desk_assets pipeline docstring.
2. Blockout: desk geometry from the DESK.png reference proportions;
   hinge rig; ortho camera; verify panel-rect-by-construction with a
   measured render.
3. First wood material pass against the photo reference; codex critic
   loop; owner eyeballs a comparison (photo desk vs modeled desk, same
   framing) BEFORE polish continues.
