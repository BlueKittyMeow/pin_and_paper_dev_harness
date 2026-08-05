# Desk Objects — tchotchke roster & design notes

Owner-driven wishlist and design thinking for Spatial View desk objects
(knick-knacks). Started 2026-08-04. Related: the queued **object drawer**
feature (ghosted-if-placed, full-opacity-if-available — owner, 2026-08-03),
post-it notes as objects, and sketch+object grouping (see HANDOFF +
CARD_DRAWINGS_PLAN owner answers L7/L9).

## Modeled/shipped

| Object | Status | Notes |
|---|---|---|
| Amethyst chunk | SHIPPED (2026-08-03) | 2.5D painted CustomPainter, yaw rotation, grounding shadow ("shadow saga" — chimera of Gemini base + Claude contact line/caustics). Resize chips. zIndex 1<<20 paperweight. Now removable via the drawer (2026-08-04); legacy prefs position migrates to desk_objects on first write. |
| Citrine / Rose Quartz / Fluorite chunks | SHIPPED (2026-08-04, drawer test roster) | Hue-rotated variants of the amethyst painter (`hueShift`: +134 golden, +68 pink, −130 green; shadows stay neutral). Same resize rules as the stone; unique zIndexes; start in the drawer. |
| Marble longhaired dachshund | SHIPPED IN APP (2026-08-04) | `dachshund-v1-approved` sprite bundle as `DachshundFigurine` in the canvas module (768px color + 256px shadow layers ×7 stops, shadows composited at 40% per the rig). Double-tap cycles the 7 rotation stops. Default 128px = manifest true scale (`ppm_multiplier: 2`); resize chips clamp 64–384. zIndex amethyst+1. |

## Tab drawer (SHIPPED 2026-08-04)

Form chosen by owner 2026-08-04: **side tab panel, right edge** — slim
gold-accented tab (chevron + drawer glyph), slides out a dark
chip-styled panel. Screen-space chrome in a Stack OVER the canvas —
satisfies the world-vs-chrome perspective constraint by construction.
Behavior: tiles ghosted at 35% if placed / full opacity if available
(owner spec); tap available → lands centered in the current view
(clamped to canvas) + selected; tap ghosted → canvas pans to it
(find-my-figurine); put-away lives on the selected object as a third
chip under the resize pair. Persistence: DB v15 `desk_objects` table
(id/placed/x/y/width/variant, sync-silent like task_drawings); variant
holds the dachshund's rotation stop. Tap-to-place, not drag-out — the
canvas's raw-Listener pointer tracking makes cross-boundary drags
fragile; drag-out can layer on later if wanted.

## Wishlist (owner)

| Object | Notes |
|---|---|
| ~~Marble longhaired dachshund figurine~~ SHIPPED — see Modeled/shipped | v1 accepted + in app 2026-08-04. V2 realism branch still mid-flight in the workshop (bandsaw-driven). |
| Glass amber toad/frog | Owner HAS reference images (2026-08-04) — to be filed in docs/working/reference/ when she shares them |
| Post-it notes | Functional object (writeable?), also drawer item |
| Snowflake obsidian hunk | Owner request 2026-08-05 — black conchoidal glass, grey cristobalite "snowflake" rosettes. In the gem-habits workshop round. |

## Gem habit round (owner direction 2026-08-05, in flight)

Modeled gemchunk v1 (one cluster mesh, 4 material variants) is
approved-but-superseded as a direction: owner wants **each mineral to
grow like its real self** — amethyst + citrine as DIFFERENTLY-arranged
prismatic clusters, rose quartz as a massive/anhedral rounded chunk
(keeping the approved milky/waxy material), fluorite as interpenetrating
CUBES, plus the new snowflake obsidian. Also: internal seams / cloudy
occlusions inside translucent crystals + per-face color variation
(her rose-quartz note). Workshop agent iterates to a 5-mineral review
strip (`assets/gemchunk/renders/habit_strip_v1.png`) — owner approves
looks BEFORE full bundles render.

## Reference mockups (owner-made, 2026-08-04, filed in reference/)

`desk_mockup_cards_flat.png` + `desk_mockup_cards_skewed.png`: two
degrees of card perspective on the same 3/4-cheat desk. Both prove the
cheat — flat/near-flat cards + side-view objects + top-right light +
cast shadows read as one desk. The dog rotation strip at the bottom of
each is effectively the SPRITE-SET + CAMERA-RIG SPEC: preset stops at
Top-Down 0°, Front 90°, 3/4 L/R ±45°, Front L/R ±60°, Back 180°.
(Biplane/globe/succulent are mood, not roster.)

**OPEN QUESTION (owner, discuss before deciding): card perspective.**
Even the "flat" mockup carries subtle perspective skew, and the owner
suspects some small degree of it may be wanted. Tension: the tech spec
and research favor exact top-down rectangles (text readability, affine
drag/hit math, plain widget rendering). Candidate middle paths, to
prototype rather than argue: (a) truly flat cards, objects carry all
depth; (b) a tiny FIXED global perspective term on the viewport
transform (uniform for everything — Flutter Matrix4 supports it; hit
testing inverts the matrix, needs verification); (c) cosmetic-only skew
(shadows/edges suggest perspective, text stays screen-aligned). Plan
APPROVED by owner 2026-08-04: cheap throwaway A/B on device once the
drawing wave lands, owner picks by eye.
**HARD CONSTRAINT (owner):** any perspective applies to the desk plane
and its contents ONLY — screen-space UI chrome (menu tabs, panels,
anything sitting over the table) stays perfectly flat. World plane vs
chrome plane, strictly separated. Codex research on how other apps
handle this split → PERSPECTIVE_UI_RESEARCH.md when filed.

## Phase 1 log (GO given 2026-08-04)

- **Pre-flight done:** no prior Blender on MysteryOfGlass; Python 3.12
  satisfies MCP's 3.11+; blender-ai-mcp cloned to
  ~/Documents/Git/blender-ai-mcp (Apache-2.0; tested on Blender 5.0,
  addon min 4.0; Blender 5.0.1 portable downloading to
  ~/tools/blender-5.0.1-linux-x64/).
- **Setup shape verified from its README:** Blender-side addon (build
  zip via scripts/build_addon.py, enable → RPC server on :8765) + MCP
  server process (Docker OR local Python env; NO docker on this box →
  local env via uv; deps are heavy — sentence-transformers/torch/
  lancedb, ~2GB venv; /home has 13G, acceptable). Server profile:
  ROUTER_ENABLED=true, MCP_SURFACE_PROFILE=llm-guided, stdio transport
  for Claude Code.
- **Next:** build+install addon headless → uv env + server smoke test →
  create agentic-blender-props workspace (trimmed §13 contract from
  BLENDER_AGENTIC_MODELING_BRIEF.md) with .mcp.json → NOTE: new MCP
  servers load at session start, so first real Blender driving happens
  in a fresh session → pilot asset: notebook WITH ribbon bookmark;
  camera rig = the mockups' 7 rotation stops.

## Blender pilot notes (owner round, 2026-08-04)
- **License concern dissolved:** blend-ai's AGPL is irrelevant — it's a
  build-time asset tool, never part of the shipped app (owner call,
  correct reading). Toolchain choice is now purely "best for loop-based
  work": blender-ai-mcp primary, blend-ai as A/B candidate, ahujasid
  blender-mcp fallback (Claude's pick, owner delegated).
- **Pilot asset 1: notebook — WITH A RIBBON BOOKMARK (owner request).**
  Design note: the ribbon is genuinely useful, not just charming — a
  thin draped curve is a gentle first test of the organic/drape
  geometry the dachshund's long coat will demand at full strength.

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

## Stretch goal: time-dynamic window light (owner vision, 2026-08-04)

**Mood reference images (owner, 2026-08-04): COMPLETE SET.**
`reference/lighting_mood_01.png` … `lighting_mood_04.png` — golden-hour
dappled leaf-light (fern gobo) across leather desk surfaces with aged
paper cards; range spans bright dapple to deep amber evening. Owner's
caveats: clutter level NOT canon, card styles NOT canon — these are for
the LIGHT and the desk-top surface/texture only. Primary references for
the gobo/time-of-day lighting system and desk textures.

The desk is lit by one conceptual **window, top-right** (consistent with
the existing down-left shadow convention — light from top-right casts
down-left). Owner's ideal:
- **Early morning:** gentle light filtered through mottled tree leaves —
  dappled but clear, mellow yellow.
- **Evening:** more golden, more diffuse.
- **Night:** cool moonlight.
- **Stretch-stretch:** subtle MOVEMENT — the way leaves or a lace
  curtain make sunlight dance rather than sit as a static beam.
- **Configurable interrupt pattern** (the thing between window and desk):
  potted monstera leaf vs gentle tree leaves vs winter stick trees.

**Feasibility (Claude assessment): yes, genuinely plausible.** This is a
"gobo"/"cookie" in stage-lighting terms — a patterned mask between light
and surface. Flutter implementation: a fragment-shader or blended-image
overlay layer above the desk background (below cards? above all with low
opacity? — design call), tinted by a time-of-day color ramp, with the
pattern texture slowly warped/translated by an animation for the dance.
Fragment shaders are well-supported in Flutter (FragmentProgram);
animated dappled light is cheap on GPU. Swappable gobo = swappable mask
texture — the monstera/tree/winter-sticks configurability falls out for
free. Battery: idle animation should pause when the app is backgrounded
and possibly offer a reduce-motion setting (→ DEFAULTS_TO_REVISIT).

**Style-bible implications (why this matters NOW, before modeling):**
1. Object sprites must be lit NEUTRALLY and tinted globally at runtime —
   baked-in warm/cool lighting would fight the time-of-day ramp.
2. Shadow layers must be SEPARATE from object sprites (already the
   3D-research recommendation) so shadow color/softness can follow the
   time of day (hard-edged noon vs soft golden evening vs cool night).
3. One light direction (top-right window) stays fixed across all times —
   only color, softness, and the gobo pattern change. This keeps every
   prerendered yaw frame valid all day.

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
