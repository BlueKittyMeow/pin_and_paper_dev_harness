# pin_and_paper_dev_harness

This repo is the **specs/docs home** for the Pin and Paper module family
(`pin_and_paper_canvas`, `pin_and_paper_card_renderer`, `pin_and_paper_sketchpad`,
`pin_and_paper_journal`) — architecture decisions, interface contracts, and
per-module specs live here.

The harness *app* itself (a 4-tab Flutter shell for exercising modules
against mocks) is **not yet built**. It's deferred until multi-module
integration testing is actually needed — see "After the POC" in
`docs/prototype.md`.

## Current focus

The active effort is the drag-and-drop spatial canvas POC, tracked in
[`docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md`](docs/working/DRAG_DROP_CANVAS_MVP_PLAN.md)
(the approved plan of record). It builds the canvas module + a card renderer
slice + main-app persistence directly — no harness app required.

## Key docs

- [`docs/prototype.md`](docs/prototype.md) — current plan-of-record framing:
  the POC path and what's deferred until after it.
- [`docs/fable-integration-review.md`](docs/fable-integration-review.md) —
  the longer-term wiring plan (spatial data storage, drawing persistence,
  interface contract fixes) for everything after the POC.
- [`docs/module_specs/`](docs/module_specs/) — per-module specs (canvas,
  card renderer, sketchpad, journal).
- [`docs/INTERFACE_CONTRACTS.md`](docs/INTERFACE_CONTRACTS.md) — the
  cross-module interfaces (`SpatialEntity`, `SpatialDataSource`,
  `TaskCardData`, etc.) extracted from the main app's `CORE_API.md`.
