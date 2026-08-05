# Desk aspect ratio and viewport strategy

Research date: 2026-08-04

## Decision summary

Keep one canonical **2000 × 1500 (4:3) desk** and adapt the camera, not the
world. Store card and object positions only in that desk coordinate system.
On a fresh view, show the whole desk only when it fits at a readable working
scale; otherwise open at the working scale on a content-bearing part of the
desk. After the user moves the camera, restore that camera on return.

The current `0.5` minimum is serving two different purposes and should be
split:

- **Working floor:** `0.5` initially, validated on the smallest supported
  phone. This is a readability detent and the minimum automatic entry zoom.
- **Overview floor:** a dynamic, lower hard minimum that allows the complete
  desk to fit. It is for orientation, not reading or editing.

The camera should be saved as **desk-space center + zoom**, locally and per
form-factor/orientation bucket. Do not sync one raw pan matrix between phone
and desktop. Add an explicit whole-desk overview action, a compact minimap or
overview scrubber, and soft resistance at desk edges.

This is the strongest synthesis of the precedents:

- FigJam explicitly uses fit-to-content on a first open; Miro and tldraw keep
  personal/per-page cameras and provide fit/selection navigation.
- Freeform keeps the same boundless board across devices and reframes saved
  scenes for the viewer's aspect ratio rather than moving content.
- Zinnia, Goodnotes, and Notability preserve canonical pages. They accept
  panning/zooming rather than silently reflowing authored marks.
- Papers, Please only made phone work by replacing its freeform desk with a
  carousel and rack. That is a separate interaction mode, not a differently
  sized version of the same desk.
- Solitaire can re-layout safely because the program, not the player, owns
  every pile position.

## Evidence and confidence

`Documented` means the behavior is stated by the maker or in primary
documentation. `Observed/reported` means it comes from current product media,
a staff/community answer, or hands-on reporting; camera defaults are often not
public API. `Inference` marks the product lesson drawn from those facts. Exact
behavior can change between releases.

## Survey table

| Product | World model | First open / return | Form-factor strategy | Zoom and edges | Pin & Paper lesson |
| --- | --- | --- | --- | --- | --- |
| **Zinnia** | Page-based journals; default “Zinnia Standard” is 10.37 × 7.78, almost exactly 4:3, with portrait/landscape and spread choices | Exact camera default is not documented. The editor presents a discrete page/spread over a background; recent pages are first-class return targets. | Same journal pages on iPhone, iPad, and Mac. Pages do not reflow for phone. An App Store reviewer reports small text and “lots of zooming and panning” on iPhone; Pixite replied that it was working on iPhone usability. | Bounded page; pinch/rotate/move the page. Older reporting notes raster ink limited useful deep zoom, though Zinnia shipped a higher-resolution brush engine in 2025. | A lovely 4:3 authored surface can still fail on phone if “same page, only smaller” is the whole adaptation strategy. Preserve the world, but provide a useful phone camera/focus workflow. |
| **Apple Freeform** | Infinite/boundless board | A new board is blank, so there is no content extent to fit. Exact reopen-camera persistence is not documented. Explicit **Zoom to Fit Content**, **Zoom to Selection**, and saved **Scenes** provide recovery and authored framing. | Same board and coordinates across iPhone, iPad, and Mac; chrome and capabilities adapt. Apple warns that a saved scene can frame differently on another device/orientation. | No meaningful world edge; navigation relies on content fit, selection fit, scenes, pinch, and pan. | Saved views should be semantic world regions, not screenshots or raw screen rectangles. Reframe them for the current viewport. |
| **Milanote** | Marketed as an infinite canvas, but effectively content-expanding: staff answers say blank panning is restricted and the board grows as content is moved outward | Exact first/reopen policy is not documented. `Z` fits all content; zoom returns to 100%. | Same boards on desktop, phone, and tablet, with reduced mobile capabilities. Milanote also promotes quick capture on phone and visual organization on a larger screen. | Current help documents pinch/controls; a Milanote staff answer describes a 25% zoom floor and content-bounded panning to prevent getting lost. | Content bounds can prevent “lost in space” better than mathematical infinity. A bounded desk is an asset if its overview and edges are pleasant. |
| **Miro** | Infinite board | A new board establishes its origin from the initial viewport. A community moderator reports the last zoom/view is retained per user; the first visit can use a set start view. Embeds officially support board, item, or custom start areas. | Same coordinates on desktop/tablet/phone. Mobile opens in view-only mode by default so panning is safe; editing is an explicit action. | Fit to screen, zoom to selection, 100%, frames, and a minimap. No board edge. | Remember a personal camera, expose recovery tools, and consider navigation-safe phone entry so a one-finger gesture does not accidentally move a card. |
| **FigJam** | Infinite board (and multiple infinite pages on paid tiers) | **Documented: first open defaults to Zoom to fit.** Deep links to a layer fit that layer. | Same board on desktop and iPad; iPad swaps in touch/stylus gestures and has capability differences. Phone is principally a viewing companion. | Pan/pinch, exact percent, fit, and fit selection; no edge clamp. | “First open = meaningful extent” is better than 100% at an arbitrary origin. Keep explicit fit and selection-fit commands after camera restoration begins. |
| **tldraw** | Infinite by default, but its SDK also supports fully bounded cameras | Camera state is per page and restored when switching pages. Persistence separates document state from per-user session state. | One scene graph; UI can detect coarse pointers. Following another user reframes their viewport to contain it while respecting the follower's aspect ratio. | Configurable zoom steps set min/max. Bounded modes include fixed, contain, inside, and outside; initial zoom can be fit-x/y/min/max, optionally capped at 100%. Fit content, bounds, and selection are built in. | This is nearly the required camera vocabulary. In particular, `contain` plus `fit-max-100` is a direct implementation precedent for a fixed desk that must work in arbitrary viewports. |
| **Goodnotes** | Page-based notebooks/PDFs; it now also has whiteboards | Opens a document/page, not an arbitrary canvas corner. Exact zoom restoration is not documented in current help. | Page size/orientation is authored; the same page is shown on every platform. Users choose vertical or horizontal page navigation. | Pinch, double-tap in/out, pan while enlarged; a separate writing Zoom Window and auto-advance preserve precise input without shrinking the page model. Whiteboards add a minimap. | Keep authored geometry stable. Solve small-screen detail with focus/inspect modes rather than rescaling stored positions. Double-tap-to-toggle zoom is well established. |
| **Notability** | Page-based notes/PDFs | Returns to a note/page; exact zoom persistence is not documented. | Same pages across iPad/iPhone/Mac/web. Users choose seamless vertical or single-page horizontal viewing rather than per-device page reflow. | Pinch plus a separate Zoom View with auto-scroll and line return. Page boundaries are clear. | Page apps separate “overview/navigation” from “detail work.” Pin & Paper can similarly distinguish desk overview from card reading/editing. |
| **Papers, Please** | Fixed, authored desk/game composition on desktop (570 × 320, 16:9) | Fixed scene framing rather than a user camera | Desktop, tablet, and phone have **three distinct interface modes**. For phone portrait, the author removed the freeform desk and replaced it with a full-size snap carousel plus document rack so no squinting or precision zoom was required. | Desktop preserves a static aspect. Phone adjusts within a range, then scales to fill; individual oversized elements get alternate layouts/scales. | The strongest warning against “fit everything on a phone.” If the Spatial View must be a primary phone workflow and camera adaptation is insufficient, add a phone focus mode—not a second set of card coordinates. |
| **Stardew Valley** | Large tiled world viewed by a camera; not a bounded one-screen desk | Camera follows player/game state | World scale and HUD scale are separate. Mobile adds different controls, toolbar orientation/size, padding, date-box size, and pinch game scaling while saves transfer from PC. | World camera zoom is adjustable; screen chrome has independent sizing and safe-area controls. | Keep flat chrome and world camera independent. Safe-area/padding issues belong to chrome, not desk coordinates. |
| **Solitaire apps** | Bounded logical playfield with program-owned piles | New deal is always fully framed | Common mobile implementations change card size/spacing and sometimes pile placement for portrait vs landscape; some recommend landscape for legibility. | Usually fit-only rather than a freely navigable camera; no “lost” state. | Re-layout works because pile positions are derived. Pin & Paper positions are authored spatial memory, so copying this strategy would make the desk move under the user. |
| **Flutter canvas ecosystem** | `InteractiveViewer` supports a bounded child; packages such as fldraw/Fluera/infinity_view use infinite scenes; scribe_canvas uses fixed pages | Application-defined. A `TransformationController` makes camera save/restore and desk-space hit conversion explicit. | Same render tree across Flutter targets; pointer policy and chrome must be adapted by the app. | `InteractiveViewer` defaults to 0.8–2.5 and zero boundary margin; docs warn that zoom below 1 often requires boundary margin. Flutter infinite-canvas packages commonly add custom camera physics; several expose minimap/fit affordances. | The stock widget is a primitive, not a viewport policy. Dynamic minimum zoom, centering on underflow axes, saved semantic camera state, and elastic edges should live in Pin & Paper's canvas layer. |

## Per-app notes

### Zinnia: closest aesthetic comparison, cautionary viewport comparison

Zinnia is not one persistent desk world. It is a journal made of discrete,
authored pages. Its current page-creation flow defaults to a 10.37 × 7.78
landscape surface (1.333:1), offers portrait orientation, and can make a
spread. The page is itself a manipulable object over the app background. That
produces the physical-paper feeling without making the journal an infinite
tabletop. Sources: [Pixite: Add a New Page](https://support.pixiteapps.com/hc/en-us/articles/51076554334355-Add-a-New-Page),
[Zinnia App Store listing](https://apps.apple.com/us/app/planner-journal-zinnia/id1485310935),
and [Paperless X review](https://beingpaperless.com/zinnia-planner-journal-for-ipad-complete-review-2023/).

The important negative evidence is phone use. A highlighted App Store review
says existing planner templates are not optimized for iPhone, leaving very
small fonts and much zooming/panning. Pixite's response says it is working on
improving iPhone usability. Zinnia subsequently added Recently Edited Pages,
which improves return/navigation but does not change the canonical page.

**Inference for Pin & Paper:** Zinnia supports keeping a tactile authored
surface, but does not support assuming full-surface fit is an adequate phone
working view. Pin & Paper needs a legible phone entry camera and probably a
fast way to move between cards without repeatedly navigating the whole desk.

### Freeform: same world, viewer-relative framing

Apple describes Freeform as a canvas that expands with content and has no page
formatting limits. On Mac it exposes Zoom to Fit Content and Zoom to Selection.
Its newer Scenes feature saves labeled board views; Apple explicitly notes
that a scene captured on Mac may be framed differently on an iPhone in
portrait. That is the correct behavior when the *region of interest* is stable
but the viewport aspect is not. Sources: [create a board](https://support.apple.com/en-gb/guide/freeform/frfm9474646a9/mac),
[view and zoom](https://support.apple.com/en-ph/guide/freeform/frfm000074a4e/mac),
and [navigate/present scenes](https://support.apple.com/en-ph/guide/iphone/iphbe64aa259/ios).

Freeform also permits a large locked rectangle when users want a bounded area
inside the boundless board. This is indirect validation that an intentional
world edge can aid organization; infinity is not automatically better.

### Milanote: “infinite” with content-aware guardrails

Milanote's product pages call its visual board an infinite canvas and its help
offers `Z` to fit all content. In practice, Milanote staff responses explain
that the pannable range follows the content, the board expands when a card is
moved outward, and zoom bottoms out around 25%. The stated purpose is avoiding
aimless scrolling and loss of orientation. Sources: [Milanote visual notes](https://milanote.com/product/note-taking),
[zoom help](https://help.milanote.com/en/articles/1721940-zoom-in-out), and
[staff explanation of content bounds](https://www.reddit.com/r/Milanote/comments/1rkf5bu/milanote_i_cant_move/).

Milanote's mobile positioning is also instructive: its official listing still
frames phone as a good capture surface and desktop as the place to organize
visually, even though mobile can open/edit boards. Source: [Milanote App Store](https://apps.apple.com/us/app/milanote/id1433852790?ls=1).

**Inference:** edge constraints can be reassuring. Pin & Paper should make its
desk boundary feel intentional, while its existing List View can remain the
fast compact-device workflow rather than forcing every task through a tiny
desk overview.

### Miro, FigJam, and tldraw: recovery beats a magic default

All three treat the camera as personal navigation state, separate from shared
content.

- Miro officially exposes fit, 100%, selection fit, frames, and a minimap; its
  embed API can set a start board/item/area. A Miro community moderator reports
  that subsequent visits retain each user's last zoom/view. On mobile the
  board opens view-only, making pan the safe default. Sources: [navigation and minimap](https://help.miro.com/hc/en-us/articles/360017731053-Using-Miro-with-a-mouse-trackpad-or-touchscreen),
  [mobile app](https://help.miro.com/hc/en-us/articles/360017572834-Mobile-app),
  [board coordinates and initial origin](https://developers.miro.com/docs/boards),
  [embed start view](https://help.miro.com/hc/en-us/articles/360016335640--GitHub-Embed-a-Miro-board),
  and [camera retention answer](https://community.miro.com/ask-the-community-45/how-to-set-the-default-zoom-on-board-5485).
- FigJam documents a first-open default of Zoom to fit, plus fit-selection and
  exact zoom percentages. Its iPad version keeps the same board but changes
  gestures/capabilities. Sources: [FigJam pan and zoom](https://help.figma.com/hc/en-us/articles/1500004414582-Pan-and-zoom-in-FigJam),
  [infinite board](https://help.figma.com/hc/en-us/articles/15300412458647-Explore-FigJam-files),
  and [FigJam for iPad](https://help.figma.com/hc/en-us/articles/4502073572247-FigJam-for-iPad).
- tldraw formalizes the pattern: every page has its own camera, persistence
  separates document and session snapshots, zoom steps define hard bounds, and
  constrained cameras offer initial `fit-*` modes plus `contain`/`inside`/
  `outside` edge behavior. Sources: [pages and camera restore](https://tldraw.dev/sdk-features/pages),
  [persistence](https://tldraw.dev/sdk-features/persistence),
  [camera constraints](https://tldraw.dev/reference/editor/TLCameraConstraints),
  and [bounded camera example](https://tldraw.dev/examples/camera-options).

Their common lesson is not “use an infinite canvas.” It is “make the camera
recoverable.” Remember where the user was, and always offer fit world/content/
selection when that remembered location is no longer useful.

### Goodnotes and Notability: fixed pages plus a detail instrument

Both products retain page geometry, offer vertical continuous versus
horizontal/single-page navigation, and use pinch/double-tap for the ordinary
page camera. Both also provide a separate magnified writing window with
auto-advance instead of making the underlying page responsive. Sources:
[Goodnotes zoom and scroll](https://support.goodnotes.com/hc/en-us/articles/6554036735631-How-to-zoom-and-scroll-through-pages),
[Goodnotes Zoom Window](https://support.goodnotes.com/hc/en-us/articles/7353756826383-Write-with-the-Zoom-Window),
[Notability view settings](https://support.gingerlabs.com/hc/en-us/articles/5955187356442-Note-View-Settings),
and [Notability Zoom View](https://support.gingerlabs.com/hc/en-us/articles/206058497-Zoom-View).

Pin & Paper already follows this principle when card drawing opens a large
modal editor. The same logic argues for opening a card detail/folder at a
readable size instead of expecting the desk camera to make dense card content
comfortable on phone.

### Digital desks and tables: when layouts may change

The Papers, Please port is unusually well documented by its author. Desktop's
570 × 320 interface always shows checkpoint, booth, and desk. Tablet stacks
and scrolls those regions. On phone portrait, Lucas Pope rejected a scaled
desk because documents were too small and crowded; the shipped interface uses
a full-size snap carousel and a rack, while temporary modal desks preserve
the few interactions that truly require a surface. The app contains desktop,
tablet, and phone interface modes over the same game state. Source: [Lucas Pope, “Cramming Papers, Please Onto Phones”](https://dukope.com/devlogs/papers-please/mobile/).

Stardew Valley keeps world camera and HUD separate. Its mobile version adds
mobile-specific control schemes and adjustable toolbar/menu/date-box sizes and
padding; desktop offers separate world zoom and UI scale. Sources: [official mobile announcement](https://www.stardewvalley.net/android-version-coming-soon/),
[options](https://stardewvalleywiki.com/Options), and [mobile version history](https://stardewvalleywiki.com/Mobile_Version_History).

Solitaire commonly goes further and automatically adjusts card sizes and
layout for portrait/landscape. That works because a deal's spatial layout is
computed, not authored. Examples: [CWI FreeCell](https://www.cwigames.com/freecell-solitaire/)
and [MobilityWare legibility guidance](https://mobilityware.helpshift.com/hc/en/10-solitaire/faq/1497-how-do-i-make-the-game-larger-and-easier-to-see/).

**Inference:** Pin & Paper belongs with Freeform/tldraw/page apps for its world
model, and with Papers, Please only if it later adds an explicit phone-focused
card navigator. It does not belong with solitaire's orientation re-layout.

### Flutter-specific implications

Flutter's `InteractiveViewer` supplies pan/zoom mechanics, not product policy.
Its defaults are 0.8–2.5; the documentation notes that a zero boundary margin
often prevents scaling below 1.0. `TransformationController.toScene` converts
a viewport point to child/desk coordinates. Sources: [`InteractiveViewer`](https://api.flutter.dev/flutter/widgets/InteractiveViewer-class.html),
[`minScale`](https://api.flutter.dev/flutter/widgets/InteractiveViewer/minScale.html),
and [`toScene`](https://api.flutter.dev/flutter/widgets/TransformationController/toScene.html).

The Flutter package ecosystem divides along the same product lines as shipped
apps: fldraw and Fluera expose infinite cameras, while scribe_canvas uses
multiple fixed pages with dynamic constraints. A drawing-board package ships
a very broad 0.2–20 range, illustrating why framework defaults are not useful
readability policy. Sources: [fldraw](https://pub.dev/packages/fldraw),
[Fluera Canvas](https://pub.dev/packages/fluera_canvas),
[scribe_canvas](https://pub.dev/packages/scribe_canvas), and
[flutter_drawing_board](https://github.com/fluttercandies/flutter_drawing_board).

I did not find a shipped Flutter product that publicly documents its
first-open camera and cross-form-factor restoration policy well enough to use
as stronger evidence than these APIs and packages.

For Pin & Paper, fit/clamp math should remain in flat desk space. With the
planned perspective variant, compute visible bounds from the **projected desk
quadrilateral**, but persist the same semantic desk-space center and zoom for
both A/B variants. Chrome remains outside that transformed subtree.

## The geometry of the current desk

For a usable viewport `V` and screen-space padding `p`, whole-desk fit is:

```text
zFitDesk = min((V.width - 2p) / 2000, (V.height - 2p) / 1500)
```

Representative usable viewports (after chrome/safe areas, with `p = 0` here to
isolate the aspect-ratio constraint) show why one fixed minimum cannot also be
a fit policy:

| Usable viewport | Approx. `zFitDesk` | 220 × 140 card at fit | Meaning |
| --- | ---: | ---: | --- |
| Phone portrait, 360 × 720 | 0.18 | 40 × 25 px | Orientation thumbnail only |
| Phone landscape, 780 × 360 | 0.24 | 53 × 34 px | Orientation thumbnail only |
| Tablet portrait, 820 × 1050 | 0.41 | 90 × 57 px | Most card text likely too small |
| Tablet landscape, 1180 × 760 | 0.51 | 111 × 71 px | Current working floor; plausible overview/work crossover |
| Desktop content area, 1360 × 760 | 0.51 | 111 × 71 px | Whole desk can just fit at the current floor |
| Large desktop, 1880 × 1000 | 0.67 | 147 × 94 px | Whole desk can be both legible and contextual |

These are logical screen pixels, not device pixels, and are deliberately
approximate. They demonstrate the policy boundary; device testing must set the
actual readability floor.

## Ranked recommendations

### 1. Keep one 2000 × 1500 desk; make the camera responsive

**Recommendation:** keep the fixed 4:3 world for v1. Do not create portrait,
landscape, phone, or desktop desk dimensions.

**Rationale:** users author spatial memory: “this card is beside the notebook,”
not “this card is at 38% width on the current screen.” One canonical world
gives stable placement, sync, collision bounds, selection, desk-object scale,
and perspective behavior. A 4:3 surface is also a good neutral middle ground:
it fits tablets naturally and is neither extremely tall nor wide.

Changing desk dimensions per device would force one of four bad storage
models:

- Keep absolute `(x,y)`: content can become out of bounds or expose new blank
  regions.
- Normalize to `(x/W,y/H)`: every switch stretches spatial relationships and
  makes physical props change apparent spacing.
- Rotate coordinates: orientation changes the user's mental map and complicates
  asymmetric card/object sizes.
- Store independent layouts: edits diverge and syncing becomes a merge problem.

If the fixed desk proves too small as card counts grow, make resizing or a
second desk an **explicit user action with a migration**, not an automatic
property of the viewer.

### 2. Separate readable work zoom from whole-desk overview zoom

Use two values:

```text
workingFloor = 0.5 initially
hardMin = min(workingFloor, zFitDesk)
hardMax = 2.0
```

`0.5` remains a strong detent and the lowest zoom chosen automatically for
work. The user may pinch through it to `hardMin` to see the entire desk. At
that point cards are landmarks, not readable controls. Label this state
“Overview” in the zoom UI rather than pretending it is an ordinary working
percentage.

Keep `2.0` for now. It renders a card at 440 × 280 logical pixels, enough for
inspection while leaving true detail editing to the card/folder modal. Raise
it only if drawing or selection handles demonstrate a real need; larger ranges
make accidental zoom and navigation recovery worse.

Validate the working floor using a typical two-line title, tag row, and due
state on the smallest supported phone. If `0.5` fails, use a compact-device
working floor of `0.6` or `0.65` without changing `hardMin`.

### 3. First-open policy: fit when readable, otherwise focus content

Use the **usable viewport after app bar, drawer/tab, and safe areas**.

| Form factor | No saved camera | Saved camera |
| --- | --- | --- |
| Phone portrait | Open at `workingFloor` on the most relevant active-card cluster. Priority: explicit/deep-linked card, most recently touched active card, then the canonical home cluster. Never auto-fit the full desk. | Restore the phone-portrait camera; preserve desk center, re-clamp, and repair if it now shows no active content. |
| Phone landscape | Same semantic center as the phone-portrait home target, normally at `workingFloor`; fit desk only through Overview because typical `zFitDesk` is far below readable. | Restore a separate phone-landscape camera so rotation does not destroy the portrait view. |
| Tablet portrait / small window | If `zFitDesk < workingFloor`, use the phone rule. If the active-card bounds fit at or above the floor, frame those bounds rather than an empty desk center. | Restore the medium camera and keep its desk-space center through resize. |
| Tablet landscape / normal desktop | If `zFitDesk >= workingFloor`, center and fit the entire desk with 24–48 px padding, capped at 100% so a huge window does not make the desk comically large. Otherwise use content focus at the floor. | Restore the expanded camera. Provide one-click Overview to recover. |
| Empty desk | Center the whole desk at `min(1.0, max(zFitDesk, workingFloor))`; on compact screens this is a centered crop, never a corner. | Restore unless it is invalid. |

For content focus, ignore purely decorative knick-knacks. First try to fit the
active task-card bounds at a zoom between `workingFloor` and `1.0`. If that
would require going below the floor, center on the explicit/recent card plus
nearby cards. A simple spatial-grid “densest occupied cell” heuristic is enough
for v1; it does not require semantic AI.

### 4. Remember camera state, but keep it personal and viewport-aware

Persist `{centerX, centerY, zoom}` after gesture/animation end. Do not persist
the raw translation matrix: a translation that was correct for 390 px width is
wrong for a 1400 px window.

Recommended key:

```text
deskId + cameraBucket

cameraBucket = compactPortrait | compactLandscape | medium | expanded
```

Keep this state local/per user; do not sync it as shared desk content. On
window resize, preserve the desk point under the viewport center and clamp only
as necessary. On reopen, validate that the visible rect intersects the desk
and, when active cards exist, that it is not an entirely blank stale view.
Repair invalid cameras with a short, interruptible animation to the nearest
active content.

An explicit “open/focus this card” action should override the remembered
camera for that navigation only. Returning later resumes the newly chosen
camera because it is now the user's latest view.

### 5. Make bounds tactile, not punitive

- When the scaled desk is smaller than the viewport on an axis, **center and
  lock it on that axis**. Never pin it to the top-left.
- Distinguish the space outside the desk with a quiet neutral/felt surround and
  desk shadow. Do not stretch the wood/felt texture to fill arbitrary windows;
  that visually denies the fixed world.
- Allow roughly 48–72 screen pixels of resisted overscroll during a gesture,
  then spring back. The limit should be in screen space so it feels the same at
  every zoom.
- Keep a sliver of desk visible while panning near an edge. Hard instantaneous
  clamps feel broken when a focal-point zoom also needs translation correction.
- At perspective A/B fit, include every projected desk corner plus padding;
  switching variants should keep the same desk-space center and re-clamp.

Milanote's guardrail rationale and tldraw's `contain` camera are better models
than either an immovable brick wall or unlimited empty panning.

### 6. Add recovery and focus affordances before a permanent minimap

Ship in this order:

1. **Overview / Fit Desk** button: whole 4:3 desk, with viewport rectangle if
   displayed as a transient miniature.
2. **Fit Selection / Focus Card**: center a selected card with enough nearby
   context; never zoom past 100% automatically.
3. **Double-tap empty desk** toggles working view ↔ whole-desk overview.
   Double-tap on a card remains card detail, preserving the current spec.
4. Desktop shortcuts: `0` or Cmd/Ctrl+`0` for 100%; `Shift+1`/`F` for desk;
   `Shift+2` for selection. Keep existing scroll-pan and Cmd/Ctrl-scroll zoom.
5. If testing still finds users lost, add a minimap: always available on
   desktop, collapsed/transient on phone, with active cards as dots and a
   draggable viewport rect.

Also steal focal-point pinch zoom, interruptible 180–250 ms camera animations,
and subtle detents at fit, `0.5`, `1.0`, and `2.0`. Do not auto-snap after every
pinch; resistance or a small haptic at the detent is enough.

### 7. If phone still fails, add a focus mode—not another desk

Papers, Please shows the honest fallback. A compact card strip, search result,
or “next nearby task” focus mode could navigate the same cards while the desk
remains underneath. Opening or dismissing focus mode maps to the canonical
card position and camera. This preserves cross-device spatial memory while
giving phone users a legible task workflow.

Do not build this before testing the camera policy above. Pin & Paper already
has List View and a planned large card/folder workspace, so it may already have
the necessary compact alternatives.

## Owner decisions and open questions

1. **What must be readable at the working floor?** Is a card landmark/title
   enough, or must tags, due date, and drawing controls remain usable? This
   determines whether compact `workingFloor` stays `0.5` or rises to
   `0.6–0.65`.
2. **What is “home” on a populated desk?** Recommended default is the most
   recently touched active card plus neighbors, falling back to the densest
   active-card cluster. A fixed top-left “inbox zone” would be simpler but must
   become a real product concept, not an implementation accident.
3. **Is phone Spatial View for editing or mainly checking/focusing?** If it
   must support long organization sessions, budget for the Papers,
   Please-style focus navigator. If List View is the normal phone workflow,
   the desk can prioritize recognition and light movement.
4. **Should camera state survive indefinitely?** Recommendation: yes, unless
   it has become invalid/blank. A “Reset View” command removes only the current
   bucket's camera.
5. **How visible should the outside-of-desk surround be?** This needs a visual
   choice before edge resistance can feel finished, especially in large
   desktop windows and the perspective experiment.
6. **Minimap or transient overview?** Start with transient Overview. Add a
   persistent minimap only if device tests show repeated disorientation.
7. **What happens as the desk fills?** Decide the card-count/congestion signal
   that prompts archiving, a second desk, or explicit desk enlargement. Do not
   silently resize the world.
8. **Does perspective change the apparent fit enough to need separate tuning?**
   Store one semantic camera, but test both A/B projected quadrilaterals on
   narrow portrait and ultrawide desktop windows.

## Recommended acceptance tests

- Fresh phone portrait with cards only in the current top-left grid opens on
  cards, not desk center or an arbitrary corner.
- Fresh tablet landscape/desktop that can fit at `>= 0.5` shows the entire
  centered desk and all four edges.
- Overview works below `0.5` on phones and returns to the prior working camera.
- Rotate phone twice: portrait and landscape each return to their last camera.
- Resize a desktop window across the fit threshold: the same desk-space center
  remains under the viewport center; there is no jump to a corner.
- Complete/move every card visible in a saved camera, reopen, and verify the
  stale blank camera repairs to active content.
- At every zoom, overscroll distance feels constant in screen pixels and
  springs back without a focal-point jump.
- At projected and flat A/B variants, Fit Desk includes all four visual desk
  corners; chrome does not transform.
- At the chosen working floor on the smallest supported phone, the agreed card
  information passes Lara's readability check.
