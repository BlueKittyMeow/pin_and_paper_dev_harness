# pin_and_paper_dev_harness
Dev harness and orchestrator for Pin and Paper modules

# Workflow

# Structure

pin_and_paper_dev_harness/
├── lib/
│   ├── main.dart                    # Harness app
│   ├── mocks/
│   │   ├── mock_spatial_source.dart
│   │   ├── mock_journal_source.dart
│   │   └── mock_data.dart
│   └── pages/
│       ├── sketchpad_page.dart
│       ├── canvas_page.dart
│       ├── card_page.dart
│       └── journal_page.dart
│
├── docs/
│   ├── ARCHITECTURE_AND_HARNESS.md  # Overall architecture
│   ├── INTERFACE_CONTRACTS.md       # What modules need to know (extracted)
│   │
│   └── module_specs/
│       ├── SKETCHPAD_SPEC.md        # Drawing layer spec
│       ├── SKETCHPAD_SHAPES.md      # Shape correction spec  
│       ├── CANVAS_SPEC.md           # To be written
│       ├── CARD_RENDERER_SPEC.md    # To be written
│       └── JOURNAL_SPEC.md          # Already written
│
└── pubspec.yaml
    dependencies:
      pin_and_paper_sketchpad:
        path: ../pin_and_paper_sketchpad
      pin_and_paper_canvas:
        path: ../pin_and_paper_canvas
       etc.

# Document Flow 

CORE_API.md (main app)
     │
     │ extract relevant parts
     ▼
INTERFACE_CONTRACTS.md (harness)
     │
     │ referenced by
     ▼
MODULE_SPECS/*.md (harness)
     │
     │ implemented by
     ▼
Module code (module repos)
