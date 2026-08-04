# Research Brief: Perspective Canvas, Flat UI Chrome on Top

Legend:

- `Sourced fact:` directly supported by a linked source.
- `Inference:` my conclusion from sources, screenshots, or implementation implications.

## 1. Apps and systems that tilt the content plane while keeping UI flat

### Strong precedents

| Example | What is sourced | Perspective strength | Separation pattern |
| --- | --- | --- | --- |
| **Tabletop Simulator** | `Sourced fact:` Tabletop Simulator is a 3D tabletop simulation platform, has a top-down camera mode, and its patch notes explicitly say high-quality screenshots ignore the UI. Sources: [Steam store](https://store.steampowered.com/app/286160/Tabletop_Simulator/), [v8 patch notes](https://www.tabletopsimulator.com/news/patch-notes-archive/version-8). | `Inference:` Moderate to overt. Official screenshots and gameplay imagery show a true 3D table/camera, not a near-affine fake. | `Inference:` The world/table plane and the UI plane are separate. The screenshot note is especially telling: the game can render the table view without the UI layer. |
| **Balatro** | `Sourced fact:` The official press kit ships both general screenshots and specifically named `Balatro_ui_3840x2160_*` assets. Source: [Balatro press kit](https://www.playbalatro.com/press-kit/). | `Inference:` Overt but controlled. The table is clearly canted with visible vanishing, but the HUD, chips, and counters are screen-space. | `Inference:` This is a clean “perspective playfield + flat overlay UI” example. It is one of the closest visual precedents for Pin & Paper’s desired warmth. |
| **Hearthstone / Battlegrounds** | `Sourced fact:` Blizzard explicitly treats boards as a distinct visual surface in Battlegrounds (“Battlegrounds Boards”). Sources: [Battlegrounds boards patch notes](https://hearthstone.blizzard.com/en-us/news/23751629/22-0-patch-notes), [official news imagery](https://news.blizzard.com/en-us/article/24276666/celebrate-blizzcon-2026-with-the-hearthstone-blizzcon-bundle). | `Inference:` Overt. The board is a theatrical 3D stage with a strong camera angle. | `Inference:` Core counters, menus, and collection chrome are flat UI over a world board. This is standard “board as world, controls as HUD.” |
| **macOS Mission Control** | `Sourced fact:` Apple says Mission Control shows open windows “arranged in a single layer,” while Spaces thumbnails sit in a bar along the top edge. Source: [Apple Support](https://support.apple.com/en-ae/guide/mac-help/mh35798/mac). | `Inference:` Whisper-level. The effect is more depth-sorted than truly projective. | `Inference:` This is a subtle non-game example of content receding while top-level chrome remains screen-aligned. |
| **Finder / Safari Cover Flow era** | `Sourced fact:` Apple’s Quick Look guide refers to “Finder’s Cover Flow view,” and Apple shipped Cover Flow in Safari 4. Sources: [Quick Look guide archive](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/Quicklook_Programming_Guide/Articles/QLUserExperience.html), [Safari 4 tech specs](https://support.apple.com/en-by/112653). | `Inference:` Overt. Cover Flow uses a strong perspective carousel with obvious vanishing. | `Inference:` The content view is perspectival, but Finder/Safari chrome remains ordinary flat application chrome. |
| **Spline editor / exports** | `Sourced fact:` Spline supports both orthographic and perspective cameras, and its UI Scenes docs say 3D UI frames are spatial by default but a UI frame can be shown “overlaid on top of your scene in screen mode,” useful for menus or HUDs. Sources: [Working with Cameras](https://docs.spline.design/cameras/working-with-cameras), [UI Scenes](https://docs.spline.design/designing-in-3-d/ui-scenes). | `Sourced fact:` Can be either whisper or overt depending on camera/FOV. | `Sourced fact:` Spline names the split directly: spatial scene content vs screen-mode overlay UI. |

### Takeaway from precedents

- `Sourced fact:` Multiple shipped products separate a perspective-rendered content world from a flat overlay UI.
- `Inference:` This is not unusual or risky in itself. The risky part is not the layering rule; it is putting readable task text on the tilted plane.
- `Inference:` The closest visual precedents for Pin & Paper are Balatro and digital tabletop games, but those are entertainment interfaces with lower text-density expectations than a productivity canvas.

## 2. Text readability under small perspective or skew

### What the sources say

- `Sourced fact:` Human vision has an **oblique effect**: cardinal orientations are processed more accurately than oblique ones. Sources: [Perceptual asymmetries review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3019986/), [orientation anisotropy in writing systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC5887916/).
- `Sourced fact:` Reading horizontal text is materially faster than rotated text. One study reported horizontal reading speed was 81% faster than rotated text; another found vertical-rotated reading roughly doubled reading time. Sources: [Comparing Reading Speed for Horizontal and Vertical English Text](https://pmc.ncbi.nlm.nih.gov/articles/PMC2921212/), [How Does Vertical Reading Affect Reading Speed?](https://pmc.ncbi.nlm.nih.gov/articles/PMC7510370/).
- `Sourced fact:` Skia exposes LCD/subpixel text because it can improve glyph-edge precision. Source: [SkPaint reference](https://chromium.googlesource.com/skia/%2B/ab2621d3e2d2055096b9fbebf16ee443e4ea90fb/site/user/api/SkPaint_Reference.md).
- `Sourced fact:` WebKit/Skia historically disabled LCD text in some transparent or composited layer situations. Sources: [WebKit bug 64873](https://bugs.webkit.org/show_bug.cgi?id=64873), [WebKit bug 82777](https://bugs.webkit.org/show_bug.cgi?id=82777).
- `Sourced fact:` WebKit’s LayoutUnit notes say painting off pixel boundaries causes unwanted antialiasing, and text is a case where engines care about snapping. Source: [WebKit LayoutUnit wiki](https://trac.webkit.org/wiki/LayoutUnit).

### What I could not find

- `Inference:` I did **not** find a primary-source guideline that says “body text remains fine up to X degrees of projective skew.” The evidence is directional, not threshold-based.

### Practical interpretation for Pin & Paper

- `Inference:` Mild fixed perspective is less dangerous than rotation-heavy text studies imply, because Pin & Paper would use a small static keystone, not 90-degree rotation.
- `Inference:` Even so, the evidence points one way: **any** move away from axis-aligned, pixel-snapped text reduces the margin for comfortable reading.
- `Inference:` Short card titles can probably tolerate a whisper-level skew if the type is large, high-contrast, and not too light-weight.
- `Inference:` Dense body text, metadata, or small labels are where this becomes fragile first.
- `Inference:` On lower-density displays, GPU-rendered transformed text is more likely to look “soft” or slightly color-fringed than on Retina-class displays.

## 3. Input handling precedent: true projection math or cheating?

### What frameworks do

- `Sourced fact:` Flutter explicitly exposes hit-test decoupling on `Transform`: `transformHitTests` can be true or false. When false, hit tests ignore the transform even though coordinate conversion APIs still honor it. Sources: [Transform.transformHitTests](https://api.flutter.dev/flutter/widgets/Transform/transformHitTests.html), [RenderTransform.transformHitTests](https://api.flutter.dev/flutter/rendering/RenderTransform/transformHitTests.html).
- `Sourced fact:` Flutter also warns that transformed content can draw outside its original area but still not receive gestures outside the parent’s bounds. Sources: [Transform.transformHitTests](https://api.flutter.dev/flutter/widgets/Transform/transformHitTests.html), [InteractiveViewer](https://api.flutter.dev/flutter/widgets/InteractiveViewer-class.html).
- `Sourced fact:` Unity provides screen-to-plane utilities for world-space or camera-space UI: `ScreenPointToLocalPointInRectangle` maps a screen point onto a `RectTransform` plane, and `Screen Space - Overlay` uses no camera while world/camera-space UI does. Sources: [RectTransformUtility.ScreenPointToLocalPointInRectangle](https://docs.unity3d.com/jp/460/ScriptReference/RectTransformUtility.ScreenPointToLocalPointInRectangle.html), [Canvas manual](https://docs.unity3d.com/es/2018.3/Manual/UICanvas.html), [RenderMode](https://docs.unity3d.com/ja/6000.0/ScriptReference/RenderMode.html).
- `Sourced fact:` WPF exposes low-level hit testing and allows custom hit-testing behavior in the visual layer. Source: [WPF hit testing in the visual layer](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/graphics-multimedia/hit-testing-in-the-visual-layer).
- `Sourced fact:` Mapbox queries **rendered** features by screen coordinates. Sources: [Mapbox mobile apps guide](https://docs.mapbox.com/help/dive-deeper/mobile-apps/), [queryRenderedFeatures](https://docs.mapbox.com/android/maps/api/11.8.0/mapbox-maps-android/com.mapbox.maps/-mapbox-map/query-rendered-features.html).

### Interpretation

- `Inference:` There are two normal strategies:
  1. **True geometric mapping**: unproject/raycast or invert the transform so input matches the rendered plane.
  2. **Render cheat**: keep authoring and hit logic in flat space, then render with a transform, sometimes even letting hits ignore the transform.
- `Inference:` Framework precedent says both are legitimate. Flutter is unusually explicit about the choice.
- `Inference:` For a small fixed decorative skew, many apps can get away with “mostly flat logic, transformed paint.” For a stronger skew, the mismatch becomes noticeable and you need true transformed hit testing.

## 4. Pattern names for “world plane vs HUD plane”

### Terms I found

- `Sourced fact:` In browser terminology, **chrome** means the visible app shell outside the content. Source: [MDN glossary](https://developer.mozilla.org/en-US/docs/Glossary/Chrome).
- `Sourced fact:` Unity names **Screen Space - Overlay**, **Screen Space - Camera**, and **World Space** UI, and calls world-space UI a **diegetic interface**. Source: [Unity Canvas manual](https://docs.unity3d.com/es/2018.3/Manual/UICanvas.html).
- `Sourced fact:` Spline uses **Spatial Mode** vs **Screen Mode** for UI over 3D scenes. Source: [Spline UI Scenes](https://docs.spline.design/designing-in-3-d/ui-scenes).
- `Sourced fact:` Mapbox documents a **basemap-overlay** paradigm. Source: [Mapbox mobile apps guide](https://docs.mapbox.com/help/dive-deeper/mobile-apps/).

### Best naming fit for non-game app discussion

- `Inference:` Outside games there is no single dominant term as universal as “HUD.”
- `Inference:` The most understandable language for Pin & Paper is probably:
  - **desk/content plane** for the transformed world
  - **chrome/overlay plane** for menus, tabs, panels, and toolbars
- `Inference:` If you want more implementation-flavored terms, “world-space content + screen-space overlay” is already well established across engines and 3D tools.

## 5. What argues against perspective on a productivity canvas?

### Sourced risks

- `Sourced fact:` W3C accessibility guidance says non-essential motion can trigger dizziness, nausea, headaches, and distraction, with parallax-style depth motion called out as a known risk. Source: [WCAG 2.2 understanding: animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions).
- `Sourced fact:` Apple accessibility guidance recommends reducing distracting motion to improve legibility. Source: [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance?changes=_5).
- `Sourced fact:` Distorted/off-axis text is less favorable to the visual system than cardinal text, and transformed/composited rendering paths can reduce text crispness. Sources already cited in sections 2 and 3.

### What that means here

- `Inference:` A **fixed** perspective skew is much safer than animated parallax or camera drift. Static perspective is unlikely to cause motion sickness by itself for most users.
- `Inference:` The main downside for a productivity canvas is not nausea; it is ongoing low-grade text strain and loss of precision.
- `Inference:` I did not find strong primary-source evidence of major public backlash to mild fixed perspective in productivity apps specifically. That absence is not endorsement; it mostly suggests few productivity tools use this pattern for text-heavy work.
- `Inference:` Entertainment apps can spend readability budget on atmosphere. Productivity tools usually should not.

## Assessment for Pin & Paper

Assumption:

- `Inference:` The desk canvas is one transformed subtree, and screen-space chrome remains ordinary Flutter widgets above it in a `Stack` or `Overlay`.

### Option A: no perspective

- `Readability:` `Inference:` Best. Text stays crispest and easiest to scan.
- `Input mapping cost:` `Inference:` Lowest. Pan/zoom/hit logic stays affine and predictable.
- `Flat-chrome constraint:` `Inference:` Trivial to satisfy.
- `Overall:` `Inference:` Safest, but gives up the warmth the owner wants.

### Option B: whisper-level fixed skew

- `Readability:` `Inference:` Acceptable if limited to a very small keystone and tested on low/medium DPI screens. Card titles are plausible; small metadata is the danger zone.
- `Input mapping cost:` `Inference:` Moderate, not high. In Flutter this is manageable if the perspective is applied once at the desk-root and hit testing follows the visual transform.
- `Flat-chrome constraint:` `Inference:` Cleanly compatible. Keep all chrome outside the transformed subtree.
- `Overall:` `Inference:` This is the best prototype candidate. It buys atmosphere without fully turning the canvas into a theatrical stage.

### Option C: overt mockup-level skew

- `Readability:` `Inference:` Risky. This is where card titles start competing with the visual concept.
- `Input mapping cost:` `Inference:` Higher. Hit regions, clipping, tooltips, drag handles, and selection affordances become harder to trust.
- `Flat-chrome constraint:` `Inference:` Still solvable structurally, but the visual contrast between a dramatic desk and perfectly flat chrome may start to feel disjointed.
- `Overall:` `Inference:` Good for splash art, risky for a working productivity surface.

## Recommendation

- `Inference:` Prototype **Option B: whisper-level fixed skew**.
- `Inference:` Do **not** prototype overt skew first. It is the wrong place to spend iteration budget before you know whether transformed text stays comfortable.
- `Inference:` Keep the perspective **fixed** and subtle. Avoid any camera drift, parallax response, or perspective animation during pan/zoom.

## Implementation gotchas to watch in Flutter

- `Sourced fact:` Flutter allows transformed hit tests to be coupled or decoupled. Source: [RenderTransform.transformHitTests](https://api.flutter.dev/flutter/rendering/RenderTransform/transformHitTests.html).
  - `Inference:` For production behavior, prefer hit tests that match the rendered plane. A render-only cheat is useful only as an experiment.
- `Sourced fact:` Flutter transformed children may render outside their original bounds without receiving gestures there. Sources: [Transform.transformHitTests](https://api.flutter.dev/flutter/widgets/Transform/transformHitTests.html), [InteractiveViewer](https://api.flutter.dev/flutter/widgets/InteractiveViewer-class.html).
  - `Inference:` Expand the interactive bounds to the full visible desk, or you will create dead zones near transformed edges.
- `Inference:` Apply the perspective at the **desk root**, not per-card. Keep all internal authoring, layout, and selection logic in flat desk coordinates as long as possible.
- `Inference:` Keep chrome, context menus, inspectors, drag avatars, and temporary affordances in a separate screen-space overlay tree.
- `Inference:` Test transformed text on Windows-class non-Retina displays, not just high-density Macs and phones. That is where softness will show up first.
- `Inference:` If whisper-skew still softens titles too much, a fallback is to keep cards/shadows/paper edges in perspective while reducing or canceling the transform on small text inside the cards.

## Bottom line

- `Sourced fact:` The layering rule is well precedented. Many systems already do “perspective world, flat overlay.”
- `Inference:` The hard part is not compositing. The hard part is readable, trustworthy task text on the desk plane.
- `Inference:` Pin & Paper should prototype a **small, fixed, whisper-level desk skew** with flat chrome above it, and treat any stronger perspective as a likely aesthetic overshoot unless testing proves otherwise.

## Sources

1. Flutter `Transform.transformHitTests`: https://api.flutter.dev/flutter/widgets/Transform/transformHitTests.html
2. Flutter `RenderTransform.transformHitTests`: https://api.flutter.dev/flutter/rendering/RenderTransform/transformHitTests.html
3. Flutter `InteractiveViewer`: https://api.flutter.dev/flutter/widgets/InteractiveViewer-class.html
4. Flutter `Stack`: https://api.flutter.dev/flutter/widgets/Stack-class.html
5. Flutter `OverlayEntry`: https://api.flutter.dev/flutter/widgets/OverlayEntry-class.html
6. Tabletop Simulator Steam store: https://store.steampowered.com/app/286160/Tabletop_Simulator/
7. Tabletop Simulator patch notes v8: https://www.tabletopsimulator.com/news/patch-notes-archive/version-8
8. Tabletop Simulator press page: https://www.tabletopsimulator.com/contact/press
9. Balatro official site: https://www.playbalatro.com/
10. Balatro press kit: https://www.playbalatro.com/press-kit/
11. Hearthstone patch notes 22.0: https://hearthstone.blizzard.com/en-us/news/23751629/22-0-patch-notes
12. Hearthstone official news imagery example: https://news.blizzard.com/en-us/article/24276666/celebrate-blizzcon-2026-with-the-hearthstone-blizzcon-bundle
13. Apple Mission Control support page: https://support.apple.com/en-ae/guide/mac-help/mh35798/mac
14. Apple Quick Look guide archive: https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/Quicklook_Programming_Guide/Articles/QLUserExperience.html
15. Apple Safari 4 tech specs: https://support.apple.com/en-by/112653
16. Spline cameras: https://docs.spline.design/cameras/working-with-cameras
17. Spline UI Scenes: https://docs.spline.design/designing-in-3-d/ui-scenes
18. Unity `RenderMode`: https://docs.unity3d.com/ja/6000.0/ScriptReference/RenderMode.html
19. Unity Canvas manual: https://docs.unity3d.com/es/2018.3/Manual/UICanvas.html
20. Unity `RectTransformUtility.ScreenPointToLocalPointInRectangle`: https://docs.unity3d.com/jp/460/ScriptReference/RectTransformUtility.ScreenPointToLocalPointInRectangle.html
21. WPF hit testing in the visual layer: https://learn.microsoft.com/en-us/dotnet/desktop/wpf/graphics-multimedia/hit-testing-in-the-visual-layer
22. MDN browser chrome glossary: https://developer.mozilla.org/en-US/docs/Glossary/Chrome
23. Mapbox mobile apps guide: https://docs.mapbox.com/help/dive-deeper/mobile-apps/
24. Mapbox `queryRenderedFeatures`: https://docs.mapbox.com/android/maps/api/11.8.0/mapbox-maps-android/com.mapbox.maps/-mapbox-map/query-rendered-features.html
25. Skia `SkPaint` reference: https://chromium.googlesource.com/skia/%2B/ab2621d3e2d2055096b9fbebf16ee443e4ea90fb/site/user/api/SkPaint_Reference.md
26. WebKit bug 64873: https://bugs.webkit.org/show_bug.cgi?id=64873
27. WebKit bug 82777: https://bugs.webkit.org/show_bug.cgi?id=82777
28. WebKit LayoutUnit wiki: https://trac.webkit.org/wiki/LayoutUnit
29. Orientation anisotropy / writing systems: https://pmc.ncbi.nlm.nih.gov/articles/PMC5887916/
30. Perceptual asymmetries review: https://pmc.ncbi.nlm.nih.gov/articles/PMC3019986/
31. Comparing reading speed for horizontal and vertical English text: https://pmc.ncbi.nlm.nih.gov/articles/PMC2921212/
32. How Does Vertical Reading Affect Reading Speed?: https://pmc.ncbi.nlm.nih.gov/articles/PMC7510370/
33. WCAG 2.2 understanding, animation from interactions: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions
34. Apple accessible appearance: https://developer.apple.com/documentation/swiftui/accessible-appearance?changes=_5
