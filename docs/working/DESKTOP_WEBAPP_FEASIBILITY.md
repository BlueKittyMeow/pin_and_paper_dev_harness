# Desktop webapp feasibility — porting Pin & Paper to Flutter web

Research date: 2026-08-16

Question: how hard would it be to ship the current stack as a webapp
for general desktop use?

**Analysis is STATIC ONLY** — read from the five repo checkouts, no
Flutter toolchain in the research container, so nothing here was
compiled or run. Every estimate below is unverified until the spike
(bottom of this doc) actually runs.

## Verdict

The port is much easier than expected; "general desktop use" is the
part with real work in it. Those are two different projects and should
be scoped separately.

The native surface area is **3 files out of 101** in
`pin_and_paper/lib` (~29k LOC): `main.dart`, `services/auth_service.dart`,
`services/notification_service.dart`. Those are the only files that
touch `dart:io`. Everything else is already portable.

## Owner direction (2026-08-16, capture-not-decision)

- **Notifications are "whatever"** — not a blocker, staged delivery is
  fine. Nuance accepted: tab-open notifications are trivial, closed-
  browser scheduled reminders need Web Push.
- **Calendar integration raised as an alternative** to notifications
  entirely. Worth pursuing — see Open questions.
- **API keys are per-user and BYO.** Each user brings their own key;
  some users won't have one at all and simply won't use the AI
  features. This materially downgrades blocker 4 (below).
- **Auth approach accepted** as described.
- **Layout framing corrected by owner:** desktop Linux window resizing
  is already smooth in practice. The gap is REORG/REFLOW at
  breakpoints, not elasticity. Confirmed in code — see below.

## What already works in our favor

- **Flutter web is a first-class target.** `web/` scaffolds already
  exist in `pin_and_paper/` and `pin_and_paper_sketchpad/`.
- **All three modules compile to web as-is.** canvas, card_renderer,
  and sketchpad have zero platform plugins (only `perfect_freehand`,
  pure Dart), zero `dart:io`, no platform channels. The path deps in
  `pubspec.yaml` need no changes.
- **The canvas was already built desktop-aware.**
  `pin_and_paper_canvas/lib/src/spatial_canvas.dart:326-330` handles
  `PointerSignalEvent`/`PointerScrollEvent` for mouse-wheel zoom, and
  `:440-450` deliberately reasons about trackpad vs mouse vs stylus in
  `supportedDevices`. This is normally the painful part of putting a
  spatial UI on desktop and it is done.
- **Supabase sync is better on web than anywhere else.**
- **Partial web work already exists:** `kIsWeb` guards in
  `services/date_parsing_service.dart:73,117` and
  `widgets/highlighted_text_editing_controller.dart:36`.

## Blockers

### 1. SQLite / persistence — biggest, but mechanical

`services/database_service.dart:41` calls
`getApplicationDocumentsDirectory()` then `openDatabase(path)`. Neither
exists on web.

**Fix:** `sqflite_common_ffi_web` (sqlite3 WASM over IndexedDB/OPFS).
Swap `databaseFactory` in `main.dart:27-30`, run the package's setup
step to place `sqlite3.wasm` + `sqflite_sw.js` into `web/`, and pass a
bare database name instead of a filesystem path. The other ~1420 lines
of `database_service.dart` — schema, migrations, all queries — are
untouched.

**The real catch is durability, not code.** IndexedDB/OPFS can be
evicted under browser storage pressure and is destroyed when a user
clears site data. Our "local-first, sync optional" posture becomes
"sync is load-bearing" on web. Worth an explicit decision.

### 2. Notifications — no direct web equivalent

`flutter_local_notifications` has no web support; 8 files reference
`NotificationService`/`ReminderService`. Split by when the code runs:

- **Tab open or backgrounded:** the Web Notifications API gives a
  proper OS-level popup once permission is granted. This is the
  mechanism Claude's own web UI uses. ~1 day.
- **Browser fully closed, "remind me at 9am tomorrow":** no browser API
  can do this. There is no local scheduler. Requires Web Push — VAPID
  keys plus something server-side firing on time (Supabase edge
  function). A real project.

Our due-date reminders are the second case. Staged delivery is fine per
owner direction; see Open questions for the calendar alternative, which
may sidestep this entirely.

### 3. Auth — small

`services/auth_service.dart:52` binds `HttpServer` on localhost:54321
to catch the desktop OAuth callback. On web the redirect is simply the
page URL — simpler, but it becomes a third branch alongside the mobile
deep-link and desktop-server paths.

### 4. Claude API — downgraded by BYO-key posture

`services/claude_service.dart:33` posts directly to
`api.anthropic.com` with a key read from `flutter_secure_storage`.

Two web-specific problems: browsers block cross-origin API calls unless
the server opts in (Anthropic's opt-in header is literally named
`anthropic-dangerous-direct-browser-access`), and
`flutter_secure_storage` on web is WebCrypto over localStorage —
obfuscation, not a keystore.

**But per owner direction, keys are per-user BYO.** Each user exposes
only their own key to their own browser, and the AI features are
already optional for users without keys. That makes the direct-browser
path defensible for a personal/BYO build, with a clear warning in
settings. A Supabase edge function proxy only becomes necessary if we
ever ship a shared/quota'd key. **Not a blocker for the spike.**

### Bonus: flutter_js is already stubbed off on web

`date_parsing_service.dart:73` skips the QuickJS runtime on web, so
natural-language date parsing silently does nothing there. This is the
easiest thing on the list to FIX rather than work around — chrono.js
runs natively in the browser via `dart:js_interop`, no QuickJS needed.
Roughly half a day, and it restores a feature.

## Second tier — desktop polish

- **Layout: reflow works, reorg doesn't.** Corrected from an initial
  bad read. `home_screen.dart` and `canvas_screen.dart` are built on
  `Expanded`/`Flexible`, and there is exactly ONE hardcoded pixel width
  in the entire `screens/` + `widgets/` tree
  (`settings_screen.dart:1486`). The app is elastic and stretches
  correctly at any size — confirmed by owner's Linux desktop use. What
  it does not do is REORGANIZE at width: at 2560px you get a correct
  layout whose rows are ~2500px of mostly whitespace. Fix is largely
  `ConstrainedBox(maxWidth: ~900)` centering plus selective two-pane
  treatment. Days, not weeks.
- **Assets: ~91 MB across the repos.** 27 MB badges, 9.3 MB quiz, an
  18 MB `VintagePaper8.png` in sketchpad, 17 MB canvas sprite bundle.
  Flutter web fetches assets on demand rather than all upfront, so this
  is not a 91 MB cold start — but opening the desk pulls the sprite
  bundle. A WebP/AVIF + responsive-sizes pass is the highest-leverage
  perf item and helps mobile too.
- **Keyboard/mouse affordances are thin.** Only
  `widgets/tag_filter_dialog.dart` and `widgets/search_dialog.dart` use
  shortcuts. No right-click menus, no Esc/Del/Cmd-K. Desktop users
  notice immediately.
- **Renderer: take the CanvasKit default and stop thinking about it.**
  Correct for our CustomPainter-heavy canvas and sketchpad; ~1.5 MB
  cached after first load. `flutter build web --wasm` (skwasm) is
  faster but wants COOP/COEP cross-origin-isolation headers on the
  host — only chase it if the spike shows we need it. The renderer that
  would have hurt us (the old HTML renderer) is already removed from
  Flutter.
- **Text input friction expected.** The `kIsWeb` guard at
  `highlighted_text_editing_controller.dart:36` is a tell — Flutter
  web's IME/composition handling fights custom text controllers. Brain
  dump is text-heavy.
- **Stylus pressure should survive.** Browsers expose pressure via
  PointerEvent and Flutter forwards it, so a Surface/Wacom works. But
  `sketchpad/lib/widgets/drawing_canvas.dart` `_normalizePressure` was
  tuned against native; expect recalibration.

## Web-only configuration — the one trap

Three mechanisms, and picking wrong is the classic web-port mistake:

- `kIsWeb` — runtime branch, for behavior differences.
- **Conditional imports** — `import 'x_stub.dart' if (dart.library.io)
  'x_io.dart';` — compile-time.
- `--dart-define` — build-time constants.

**`kIsWeb` does NOT save you from `dart:io`.** Wrapping the call site
in `if (!kIsWeb)` does not help, because the IMPORT STATEMENT itself
fails to compile on web — the branch never runs. So
`notification_service.dart` and `auth_service.dart` need conditional
imports or split files, not runtime checks. This is why the 3-file
count matters so much: only three files need this treatment.

## The spike (do this first — 1–2 days, timeboxed, throwaway)

Purpose: buy ONE piece of information — **does the desk canvas perform
acceptably in a browser?** That is the only item on this list that
could kill the idea outright, and it cannot be predicted by reading
code. Hardcode freely, no tests, throw it away after.

1. Add `sqflite_common_ffi_web`; run its setup to populate `web/`.
2. In `main.dart:27`, branch the factory on `kIsWeb` before the
   existing `Platform.isLinux || ...` check (which itself must move
   behind a conditional import).
3. Conditional-import stub `notification_service.dart` — no-op every
   method on web.
4. Conditional-import stub the `HttpServer` branch in
   `auth_service.dart`; hardcode the page URL as the redirect.
5. `flutter build web` → serve → open Spatial View, drag a card, draw
   on one, zoom with the wheel.

Success = the desk is usable at desktop resolution. Everything else on
this page is negotiable; that is not.

## Rough sizing

Calendar time for owner working WITH Claude, not solo human days.

| Goal | Estimate |
|---|---|
| Spike — compiles and runs on web | 1–2 days |
| Feature-complete web build | ~1 week |
| Polished desktop webapp | ~2 weeks |

Splits very unevenly by task type:

- **Fast with Claude:** db factory swap, conditional imports, auth
  branch, chrono via JS interop, bulk asset conversion. Mechanical and
  well-specified.
- **Slow regardless:** anything needing the owner to look at the
  running app and say "that feels wrong." CanvasKit perf tuning,
  whether the desk feels right with a mouse, taste calls on wide
  layouts. Most of the remaining time lives here.

## Open questions

- **Calendar integration instead of notifications** (owner idea, worth
  real consideration). Writing due dates to the user's calendar — via
  Google Calendar API, or a subscribable/exportable `.ics` — offloads
  notification DELIVERY to the calendar app, which already notifies on
  every device the user owns. This sidesteps Web Push entirely, and
  OAuth for it is easiest on web of all platforms. Possibly a better
  answer than local notifications on EVERY platform, not just web.
  Needs its own research pass.
- **Storage durability decision** (blocker 1): is OPFS-backed local
  data acceptable given sync exists, or does web need a different
  local-first story?
- **Deployment target** unexamined — hosting, custom domain, whether
  this is a PWA with an install prompt or a plain tab.
- **Does web get Spatial View at all in v1?** It is the heaviest thing
  to port and the most likely to disappoint. A list-only web build is
  a legitimate smaller first target if the spike disappoints.
