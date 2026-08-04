# Z-order Policies in Canvas/Board Apps
As of **August 4, 2026**, the evidence still points to a simple baseline: **explicit-only stacking is the default in most canvas/note/whiteboard apps**, while **window managers** remain the clearest precedent for automatic raise behavior and user-visible toggles.

## 1. Policy inventory and real examples

| Policy | What it means | Source-backed examples | Fit / tradeoff |
|---|---|---|---|
| **A. Explicit-only** | Stacking changes only when the user invokes arrange/layer commands. | [Freeform](https://support.apple.com/en-ie/guide/freeform/frfm6cb2dcdd/mac), [Miro](https://help.miro.com/hc/en-us/articles/360017730953-Working-with-objects), [PowerPoint](https://support.microsoft.com/en-us/powerpoint/training/layer-objects-on-slides), [Keynote](https://support.apple.com/en-lamr/guide/keynote/tan003ee8980/mac), [OneNote for Mac](https://support.microsoft.com/en-us/onenote/onenote-for-mac-help-and-learning/insert-and-format-pictures-in-onenote-for-mac), [Xournal++](https://github.com/xournalpp/xournalpp/blob/master/CHANGELOG.md) | Best for spatial memory and predictability; slower when buried objects need rescue. |
| **B. Auto-raise on select/tap/focus** | Selecting/focusing an item raises it immediately and persistently. | Desktop window managers are the canonical case: [KWin](https://docs.kde.org/trunk_kf6/en/kwin/kcontrol/windowbehaviour/index.html), [Xfwm4](https://docs.xfce.org/xfce/xfwm4/preferences). Windows also supports hover activation/raise variants: [Activate on hover](https://www.elevenforum.com/t/turn-on-or-off-activate-window-by-hovering-over-with-mouse-pointer-in-windows-11.6104/) | Fast access, but weak for piles and overlapping layouts; highest accidental reshuffle risk on touch. |
| **C. Auto-raise on drag, restore on drop** | Item is temporarily lifted while moving, then returns to prior order. | I **did not find strong public-doc evidence** for mainstream apps that document this as a durable policy. It appears more as transient drag feedback than a documented stacking model. | Good visibility during move, but snap-back can feel wrong if users expected a “desk” model. |
| **D. Auto-raise on drag, persists after drop** | Dragging/manipulating an item brings it forward and keeps it there. | Window managers effectively behave this way once a window is activated/dragged to front under click-to-focus/raise policies: [KWin](https://docs.kde.org/trunk_kf6/en/kwin/kcontrol/windowbehaviour/index.html), [Xfwm4](https://docs.xfce.org/xfce/xfwm4/preferences) | Strong physical-desk feel; weakest spatial stability. |
| **E. Creation-on-top only** | New items appear on top, but later selection/drag does not auto-reorder. | [Illustrator](https://helpx.adobe.com/illustrator/using/stacking-objects.html), [Microsoft Office layering model](https://support.microsoft.com/en-us/office/manipulate-objects-in-layers-e6eb6147-ecfc-455b-914d-77dbff3a476f) | Simple, common baseline; imports/new cards can unexpectedly occlude older work. |
| **F. Tier/layer bands** | Some content lives in protected bands or semantic layers. | [Concepts automatic/manual layers](https://tophatch.helpshift.com/hc/en/3-concepts/faq/18-how-does-concepts-decide-which-layer-to-draw-to/?contact=1%2F&p=winpc), [Miro frames always behind board objects](https://help.miro.com/hc/en-us/articles/360017730953-Working-with-objects), [OneNote “Set Picture as Background”](https://support.microsoft.com/en-us/onenote/onenote-for-mac-help-and-learning/insert-and-format-pictures-in-onenote-for-mac), [Unity UI sibling/tree order](https://docs.unity3d.com/ja/current/Manual/UIE-draw-order.html) | Best when background/reference objects should stay put; adds exceptions users must learn. |
| **G. User-configurable** | User can toggle between stacking/raising behaviors. | [KWin](https://docs.kde.org/trunk_kf6/en/kwin/kcontrol/windowbehaviour/index.html), [Xfwm4](https://docs.xfce.org/xfce/xfwm4/preferences), Windows 11 hover/raise options ([activate](https://www.elevenforum.com/t/turn-on-or-off-activate-window-by-hovering-over-with-mouse-pointer-in-windows-11.6104/), [move to top](https://www.elevenforum.com/t/turn-on-or-off-move-windows-to-top-when-activating-for-mouse-hover-in-windows-11.35570/)), [Figma auto-layout canvas stacking](https://help.figma.com/hc/en-us/articles/31289464393751-Use-the-horizontal-and-vertical-flows-in-auto-layout) | Strong precedent exists, but mostly in window managers and constrained contexts. |
| **H. Overlap-aware local reorder** | Forward/back acts relative to overlapping items, not the full global list. | [tldraw](https://tldraw.dev/examples/z-order) | Especially good in dense canvases; behavior is smart but less obvious unless explained. |

## 2. Cross-app takeaways

- **Slide/layout editors**: PowerPoint, Keynote, Illustrator, Premiere Elements all expose explicit arrange controls and treat z-order as a deliberate edit, not a side effect.
- **Whiteboards/canvas apps**: Freeform, Miro, Goodnotes, Concepts, and likely much of the broader category still lean explicit or layer-based.
- **Minimal subsets exist**: [Goodnotes](https://support.goodnotes.com/hc/en-us/articles/14141163656335-Working-with-Objects) and [Zinnia](https://play.google.com/store/apps/details?id=com.pixite.zinnia) surface **Front/Back only**. Mature editors usually ship **all four**.
- **Miro is a useful precedent**: it long had front/back, then added forward/backward later in 2024 after demand ([community announcement](https://community.miro.com/ideas/add-push-backwards-bring-forwards-option-to-objects-selections-2464)).

## 3. Pros/cons by user concern

- **Spatial memory**: strongest with explicit-only and tiered systems; weakest with persistent auto-raise.
- **Predictability**: strongest with explicit-only; next best is overlap-aware reorder like tldraw because it still requires an explicit command.
- **Dense overlaps**: full four commands or a layers/object list matter a lot; front/back-only becomes tedious.
- **Accidental reshuffling**: touch/stylus makes auto-raise materially riskier than mouse.
- **Touch vs mouse**: auto-raise is far more acceptable in windowed mouse environments than in finger/stylus canvases.

## 4. Toggle precedent and how it is explained

- **KWin** separates **focus** from **raising**, then offers “Raise on hover, delayed by…”. Good precedent for explaining the behavior in plain interaction terms.
- **Xfwm4** exposes **Focus model**, **Raise on focus**, and **Raise on click** as separate checkboxes.
- **Windows 11** now exposes **Activate on hover** and **Move window to top when activating for mouse hover**. That is a direct precedent for splitting “select/focus” from “also raise”.
- **Figma** exposes **Canvas stacking: First on top / Last on top** for overlapping auto-layout stacks, and explicitly says the layer list stays the same while canvas stacking changes.

## 5. How explicit commands are exposed

- **Context menu**: Miro, OneNote, Goodnotes, Premiere Elements.
- **Toolbar / ribbon / inspector**: PowerPoint Arrange, Keynote Arrange tab, Goodnotes object menu.
- **Keyboard shortcuts**: Miro, Keynote, Premiere.
- **Layers/object list/pane**: PowerPoint Selection Pane, Keynote object list, Figma Layers panel, Illustrator Layers panel, Concepts Layers.

For a minimal v1, **Front/Back only** is defensible. For a pile-heavy desk UI, the evidence favors **all four**.

## Assessment for Pin & Paper

The owner’s proposal is **directionally good**: a **toggle plus explicit commands** is well supported by precedent. The evidence does **not** support making persistent auto-front the universal default for a touch-capable canvas.

**Recommended default:** **Off**  
Keep stacking fixed unless the user explicitly reorders. Reasons:
- It matches the dominant behavior in comparable canvas/note apps.
- It preserves intentional piles and spatial memory.
- It is safer on Android finger/stylus input.

**Recommended option design:**
- Keep the toggle.
- Keep all four explicit commands.
- Use plain language, not z-order jargon.
- The settings animation is a good idea; it matches how the best precedents explain interaction policy visually.

**Important pitfall:** if this is a true **user preference**, but z-order is persisted into the document, the preference changes shared data rules. That is fine for a personal app, but awkward for future collaboration. Decide early whether the behavior is:
- per-user interaction policy over shared persistent z-order, or
- per-board policy.

**Implementation risks to flag**
- Persist z-order deterministically; plan for renumber/compaction.
- Preserve relative order for multi-select reorder.
- Define whether forward/backward is global or overlap-aware.
- Exclude future pinned/background/locked objects from auto-front.
- Define group semantics now: group-local order vs global order.

## What I could not verify cleanly

- A strong, public, mainstream precedent for **“raise while dragging, then restore on drop”** as a documented product policy.
- Public docs for **Mural**, **Milanote freeform overlap behavior**, and **Excalidraw** that clearly state their non-command stacking behavior.
- An official Microsoft Support page for the newer Windows 11 “move to top on hover activation” checkbox; the cited Windows 11 Forum tutorials appear to reflect the shipping UI.

## Key sources

- Apple Freeform: https://support.apple.com/en-ie/guide/freeform/frfm6cb2dcdd/mac
- Miro objects + shortcuts: https://help.miro.com/hc/en-us/articles/360017730953-Working-with-objects , https://help.miro.com/hc/en-us/articles/360017731033-Shortcuts-and-hotkeys
- Miro forward/backward addition: https://community.miro.com/ideas/add-push-backwards-bring-forwards-option-to-objects-selections-2464
- tldraw z-order: https://tldraw.dev/examples/z-order
- PowerPoint layering / Selection Pane: https://support.microsoft.com/en-us/powerpoint/training/layer-objects-on-slides , https://support.microsoft.com/en-us/powerpoint/use-the-selection-pane-to-manage-objects-in-documents
- Keynote layering: https://support.apple.com/en-lamr/guide/keynote/tan003ee8980/mac
- OneNote ordering/background: https://support.microsoft.com/en-us/onenote/onenote-for-mac-help-and-learning/insert-and-format-pictures-in-onenote-for-mac
- Goodnotes objects: https://support.goodnotes.com/hc/en-us/articles/14141163656335-Working-with-Objects
- Concepts layers: https://tophatch.helpshift.com/hc/en/3-concepts/faq/18-how-does-concepts-decide-which-layer-to-draw-to/?contact=1%2F&p=winpc
- Illustrator stacking: https://helpx.adobe.com/illustrator/using/stacking-objects.html
- Xournal++ changelog: https://github.com/xournalpp/xournalpp/blob/master/CHANGELOG.md
- KWin / Xfwm4: https://docs.kde.org/trunk_kf6/en/kwin/kcontrol/windowbehaviour/index.html , https://docs.xfce.org/xfce/xfwm4/preferences
- Figma auto-layout canvas stacking: https://help.figma.com/hc/en-us/articles/31289464393751-Use-the-horizontal-and-vertical-flows-in-auto-layout
- Zinnia listing: https://play.google.com/store/apps/details?id=com.pixite.zinnia
