# 3D-ish Desk Objects on a 2D Spatial Canvas
_As of August 4, 2026._

**Label key:** `[Source]` directly stated in a cited source. `[Inference]` inferred from official screenshots/store media on the cited page. `[Analysis]` my geometry/engineering judgment.

## A. Prior Art

Short answer: **yes, but it splits into two camps**. Flat composition apps keep everything flat and allow free 2D rotation; true 3D arrangers use a coherent 3D camera and either discrete yaw or full 3D manipulation. **Your current hybrid is unusual.**

| Hit | Objects | Surface/camera | Rotation | How “resting on surface” is sold |
|---|---|---|---|---|
| [Grimoire Virtual Altar](https://getgrimoire.app/features/virtual-altar) | Flat illustrated altar items `[Source]` | Flat 2D scene backgrounds `[Source]` | Free 2D rotate/resize/layer `[Source]` | Overlap, layering, background art; not true grounding `[Analysis]` |
| [Zinnia](https://apps.apple.com/us/app/zinnia-digital-planner/id1485310935) | Flat stickers/photos/page objects `[Source]` | Flat page `[Source]` | Free 2D rotation; 45° snap in updates `[Source]` | Page metaphor + layer order; no 3D contact `[Analysis]` |
| [Beautiful Tarot](https://beautifultarot.com/) and [The Fool’s Dog](https://www.foolsdog.com/) | Flat cards `[Source]` | Flat table/background `[Source]` | Flip, shuffle, scale, arrange freely `[Source]` | Card borders/backs/table texture; essentially tabletop collage `[Analysis]` |
| [Tabletop Simulator](https://www.tabletopsimulator.com/about) + [controls](https://kb.tabletopsimulator.com/player-guides/basic-controls/) | Real 3D models with physics `[Source]` | Free 3D table camera; first-person mode `[Source]` | Pick up, rotate, flip, precise gizmo rotation `[Source]` | Actual collision, lighting, shadows, table plane `[Source]` |
| [Animal Crossing: New Horizons / HHP](https://animalcrossing.nintendo.com/new-horizons/create/) + [designer controls](https://nookipedia.com/wiki/Lighting) | Real-time 3D stylized furniture `[Inference/Source]` | Fixed 3/4 room/world camera `[Inference]` | Discrete furniture rotation in design UI `[Source]` | Grid/floor categories, matching camera, cast shadows `[Inference]` |
| [Unpacking](https://store.steampowered.com/app/1135690/Unpacking/) | 2D/isometric-feeling painted or sprite objects `[Inference]` | Isometric room view; Steam tags it “Isometric” and “2D” `[Source/Inference]` | No free 3D manipulation surfaced on official page `[Source gap]` | Surface slots, occlusion, tiny shadows, object-specific orientations `[Inference]` |
| [My Dream Setup](https://store.steampowered.com/app/2200780/my_dream_setup?l=english) + [update note](https://store.steampowered.com/news/posts/?enddate=1697445754&feed=steam_community_announcements) | Real 3D room props `[Source/Inference]` | Perspective/isometric room builder `[Inference]` | No-grid placement; snap to nearest 45° `[Source]` | Full 3D room, lighting, and floor contact `[Inference]` |
| [Getty Life of Art](https://www.getty.edu/mobile/loa_app/) / [Mobile Museum](https://www.mobilemuseum.app/) | Isolated 3D object viewers `[Source]` | Turntable/AR, not arranged surface `[Source]` | Rotate/zoom/inspect `[Source]` | Museums usually choose **inspection**, not desktop arrangement `[Analysis]` |

**Takeaway:**  
- Flat journaling/altar/tarot apps treat the surface like a **page**.  
- Decorator/tabletop apps treat the surface like a **world**.  
- Pin & Paper is trying to make a page behave a little like a world. That is doable, but the camera and shadow rules must be strict.

## B. Projection Coherence

### What makes the current hybrid read well
`[Analysis]` This is the classic **3/4 cheat**: the ground stays legible like a map/page, while objects show side/top information and the **shadow does the grounding**. Related art references: [OpenGameArt perspective guide](https://opengameart.org/node/5491), [SLYNYRD top-down objects](https://raymond-schlitter.squarespace.com/blog/2019/9/18/pixelblog-21-top-down-objects).

Best practices for your current approach:
- Keep one global light direction and one shadow language.
- Give every tchotchke a stable **footprint/contact patch** independent of its painted silhouette.
- Let objects yaw; avoid arbitrary pitch/roll unless the asset has authored side poses.
- Use a dense contact shadow plus a softer cast shadow.
- Keep cards visually “paper-flat” and tchotchkes visually “upright”; make the distinction intentional.

### What breaks if you tilt the desk toward true isometric/dimetric
- **Cards stop being believable** if they remain plain screen rectangles. If they lie on the desk plane, they should foreshorten with that plane. `[Analysis]`
- Text/edit affordances on cards get harder to read as soon as the card is no longer front-facing. `[Analysis]`
- Z-order is no longer “screen Y plus stack order”; height starts projecting into screen space, so sorting gets trickier. `[Analysis]`
- Drag math changes:
  - Axonometric tilt is still basically an **affine** mapping. Easier.
  - True perspective tilt becomes a **projective** mapping. Harder for drag/hit reasoning. `[Analysis]`
- If objects live in a tilted world but cards stay flat UI, the scene splits into two incompatible spaces.

### Best-fit projections for mixed paper + objects
Using standard projection definitions from [Onshape](https://cad.onshape.com/help/Content/View/isometric_dimetric_trimetric_projections.htm?Highlight=use) and [CSUS axonometric notes](https://athena.ecs.csus.edu/~ysuh/EGTextbook/Ch5-Axonometric-Projection.html):

- **Pure top-down:** best for paper, weakest for standing figurines.
- **3/4 cheat:** best compromise for a paper-first canvas with decorative upright objects.
- **30° dimetric/isometric:** good if the whole desk becomes a world; requires cards to become plane-aware art, not plain widgets.
- **Trimetric/perspective:** most naturalistic, least compatible with current flat-card interaction model.

**Conclusion:** for Pin & Paper’s current priorities, **3/4 cheat beats true isometric**.

## C. Flutter Feasibility (2026)

### 1. `flutter_scene` / Flutter GPU / Impeller
- Flutter’s own docs say **Impeller is default on iOS and Android API 29+**; web still uses Skia; macOS is opt-in as of July 23, 2026. `[Source: https://docs.flutter.dev/perf/impeller]`
- Flutter’s official Flutter GPU writeup still calls **Flutter GPU and Flutter Scene preview / main-channel work**. `[Source: https://flutter.dev/blog/getting-started-with-flutter-gpu]`
- `flutter_scene` itself says it is **pre-1.0**, evolving quickly, and currently wants **Flutter master** because Flutter GPU is not yet stable. `[Source: https://pub.dev/packages/flutter_scene]`

**Assessment:** promising, but **too bleeding-edge for “next 2–3 tchotchkes” in a stable solo-dev app**.

### 2. `flutter_gl` / `three_dart`
- `flutter_gl` latest pub release shown is **0.0.21**, published **3 years ago**. `[Source: https://pub.dev/packages/flutter_gl/versions]`
- `three_dart` latest pub release shown is **0.0.16**, also **3 years old**. `[Source: https://pub.dev/packages/three_dart/versions]`

**Assessment:** technically possible, but the package freshness signals **maintenance risk**.

### 3. Embedding a game engine view
- Flutter Platform Views on Android have explicit composition/performance tradeoffs; hybrid composition can reduce Flutter FPS, texture composition can jank on fast updates. `[Source: https://docs.flutter.dev/platform-integration/android/platform-views]`
- Unity as a Library supports Android/iOS/Windows, but Unity documents important limits, including **fullscreen-only on Android/iOS** and retained memory after unload. `[Source: https://docs.unity3d.com/cn/6000.0/Manual/UnityasaLibrary.html]`
- Godot documents Android embedding as a library/view, but warns about **single engine instance per process** and resize/orientation caveats. `[Source: https://docs.godotengine.org/en/stable/tutorials/platform/android/android_library.html]`

**Assessment:** viable for a dedicated 3D app surface, **not a clean fit for “objects are widgets on a pannable Flutter canvas.”**

### 4. Offline prerendered sprite sets
`[Analysis]` This is the lowest-risk option:
- sculpt/model once,
- render 24–48 yaw frames,
- optionally author 2–3 pose variants,
- render separate contact/cast shadow layers,
- use ordinary Flutter widgets/images/CustomPainter.

**Performance on mid Android:** excellent relative to live 3D, because runtime cost is mostly texture draw + transform.  
**Coexistence with current canvas:** excellent.

## D. Asset Pipeline From Real Objects

### What the current tools can do
- [RealityScan Mobile](https://www.realityscan.com/mobile): iOS + Android object capture, real-time feedback, masks, export. `[Source]`
- [Polycam Object Mode](https://learn.poly.cam/hc/en-us/articles/34419168797972-Which-Devices-Are-Supported-by-Polycam): photogrammetry and Gaussian splats; Android support is more limited than iOS for some modes. `[Source]`
- [Scaniverse](https://api-staging-isolated.scaniverse.com/) + [support](https://scaniverse.com/support?trk=public_post-text): phone-based meshes/splats with export. `[Source]`
- [KIRI Engine](https://play.google.com/store/apps/details?id=com.kiriengine.app): markets photogrammetry, NSR/NeRF-like shiny-object workflows, Gaussian splats, retopo. `[Source]`
- [Meshroom](https://meshroom.readthedocs.io/en/stable/index.html): free/open desktop photogrammetry. `[Source]`
- [Apple Object Capture](https://developer.apple.com/documentation/realitykit/realitykit-object-capture?changes=_5): official photogrammetry API on Apple platforms. `[Source]`

### The glass/amber toad problem
This is the bad case for classic photogrammetry.
- RealityScan docs say smooth/reflective surfaces are problematic and **glass may fail entirely**. `[Source: https://dev.epicgames.com/documentation/realityscan-mobile/photogrammetry-objects-and-backgrounds?lang=en-US]`
- Polycam says reflective/transparent surfaces are difficult, suggests matte spray / paper markers, and says Gaussian splats can cope better visually. `[Source: https://learn.poly.cam/hc/en-us/articles/48538689020692-Preparing-to-Scan]`

### Practical workarounds
- Use photos/scan as **reference only**, then hand-model.
- If safe for the object, use removable matte scan spray or temporary markers for a geometry pass, then recreate the glass look manually.
- Use Gaussian splats for reference or marketing renders, **not as a clean runtime mesh pipeline**. `[Analysis]`

### Best pipeline for your aesthetic
- **Hand-painted 2.5D:** cheapest, most coherent with the amethyst, least technical risk.
- **Photo-derived 3D:** highest realism, highest mismatch risk, worst fit for amber glass.
- **Stylized hand-modeled 3D rendered to sprites:** strongest middle path.

**My recommendation:** for the marble dog and amber toad, **use real-object photos as reference, optionally scan for proportions, then render to authored 2.5D sprite sets.**

## E. Rotation & Pose UX

What ships today:
- Flat composition apps: **free 2D rotation** ([Grimoire](https://getgrimoire.app/features/virtual-altar), [Zinnia](https://apps.apple.com/us/app/zinnia-digital-planner/id1485310935), tarot apps). `[Source]`
- Room decorators: **discrete yaw / snap rotation** ([Animal Crossing](https://nookipedia.com/wiki/Lighting), [My Dream Setup](https://store.steampowered.com/news/posts/?enddate=1697445754&feed=steam_community_announcements)). `[Source]`
- Physics sandboxes: **free 3D rotation/flip** ([Tabletop Simulator](https://kb.tabletopsimulator.com/player-guides/basic-controls/)). `[Source]`

**Best fit for a desk metaphor:**  
- Cards: keep free in-plane 2D rotation.  
- Standing tchotchkes: **yaw-only turntable** by default.  
- Rare exceptions: authored **snap poses** like `upright`, `on-side`, `upside-down` when the object meaningfully supports them.

**Not recommended:** unconstrained free 3D rotation for ordinary desk tchotchkes. It reads like a 3D editor, not a desk.

## F. Extra Question You Should Ask

**How will assets from different pipelines stay in the same world?**

Answer: create a tiny **desk object style bible**. `[Analysis]`
- One light direction.
- One shadow recipe.
- One scale convention.
- One allowed camera cheat.
- One rule for footprints/hitboxes.
- One maximum apparent height range for “small desk objects.”

Without that, a hand-painted crystal, a scanned glass toad, and a modeled marble dog will look like they came from three different apps.

## Assessment for Pin & Paper

For the **next two or three tchotchkes**, I would **not invest in live 3D**.

Use this path instead:
- **Camera convention:** keep the desk visually flat/paper-first; continue the current **3/4 cheat** for tchotchkes rather than tilting the whole desk.
- **Rendering tech:** authored 2.5D or prerendered sprite atlases, with yaw frames and authored shadow layers, inside the existing widget/CustomPainter canvas.
- **Asset pipeline:** photograph real objects; optionally run a scan for proportion/reference; then hand-paint or hand-model and prerender. For the amber glass toad, assume photogrammetry will be unreliable unless you use temporary matte treatment.
- **Rotation model:** cards rotate freely in-plane; tchotchkes get yaw-only rotation, plus a few explicit pose variants if needed.

**Why this is the coherent solo-dev choice:** it preserves card readability, keeps your current interaction model, avoids Flutter 3D maturity risk, avoids platform-view/engine embedding pain, and still lets the object roster grow.

**When 3D becomes worth it:** only if you decide tchotchkes are becoming a real system of their own: many more objects, shared reusable materials/lighting, true occlusion needs, animation, or a dedicated 3D inspect/place mode. For the next 2–3 objects, **keep-current-2.5D wins.**
