# MASTER_PLAN.md — Doctor Strange Portal

**Purpose of this document:** the single source of truth for where the project is, where it's going, and in what order. Every other document (SDD, sprint files, API spec) hangs off this one. If a Codex/Claude Code session is starting cold, read this file first.

---

## 1. The Chain

```
Vision (SDD §1)
   ↓
Requirements (SDD §2–3)
   ↓
Architecture (SDD §4–7, API_SPEC.md)
   ↓
Sprint 00 — Repo scaffold, config, no CV yet
   ↓
Sprint 01 — Camera + Hand Tracking          → Prototype v0.1
   ↓
Sprint 02 — Gesture Detection                → Prototype v0.2
   ↓
Sprint 03 — Portal Rendering                 → Prototype v0.3
   ↓
Sprint 04 — Portal Animation                 → Prototype v0.4
   ↓
Sprint 05 — Body Detection                   → Prototype v0.5
   ↓
Sprint 06 — Disappearance Effect             → Prototype v0.6
   ↓
Sprint 07 — Integration + Polish             → Release v1.0
```

Each arrow is a **gate**: don't start the next sprint until the current prototype's acceptance criteria (defined in that sprint's file) are met and manually verified against a live webcam.

### The Per-Sprint Loop

Every single arrow above actually expands to this cycle — it's not implicit, it's the required sequence for every sprint:

```
Read MASTER_PLAN.md + this sprint's file
        ↓
Codex implements the sprint
        ↓
Human review (does it match Acceptance Criteria?)
        ↓
Run the prototype live (webcam), fix issues
        ↓
Git commit (message references the sprint, CODEX_GUIDELINES.md §7)
        ↓
Update CHANGELOG.md
        ↓
Update ARCHITECTURE_DECISIONS.md (only if a real design decision was made/changed)
        ↓
Update this file's Current Status table
        ↓
Next sprint
```

Documentation evolves with the code, one sprint at a time — it does not get written once up front and left static. Skipping the CHANGELOG/status update step is how `MASTER_PLAN.md` silently goes stale, which defeats its purpose as the single reorientation point for a new session.

## 2. Current Status

| Field | Value |
|---|---|
| Current Sprint | Sprint 00 (not yet started) |
| Current Prototype | none |
| Blocking Issues | none |
| Last Updated | 2026-07-07 |

*(Update this table at the end of every sprint — it's the fastest way for a new Codex session to reorient.)*

## 3. Document Map

| Document | Role |
|---|---|
| `SDD.md` | Full architecture, algorithms, module responsibilities — the "why" |
| `API_SPEC.md` | Exact class/method signatures per module — the "what" |
| `CONFIG_SPEC.md` | Every tunable constant, defaults, valid ranges (`config/config.yaml` + `config/logging.yaml`) |
| `CODING_STANDARDS.md` | Style, structure, and quality rules |
| `CODEX_GUIDELINES.md` | Rules of engagement specifically for AI coding sessions |
| `ARCHITECTURE_DECISIONS.md` | Running ADR log — why each non-obvious design choice was made, and what would change the answer |
| `CHANGELOG.md` | Plain record of what shipped each sprint |
| `ASSET_GUIDE.md` | Asset folder conventions, naming, required formats |
| `sprints/SPRINT_00.md` … `SPRINT_07.md` | The "how, in what order" — one prompt-sized unit of work each |
| `MASTER_PLAN.md` (this file) | Ties all of the above together, tracks current status |

Project structure was right-sized in ADR-006 (see `ARCHITECTURE_DECISIONS.md`): `config/` is now a top-level split (`config.yaml` for tunables, `logging.yaml` for logging setup), and `tests/` splits into `unit/`, `integration/`, and `data/` (fixtures). Full rationale and the complete tree are in `SDD.md` §6.

## 4. Working Agreement for AI-Assisted Sessions

1. Always start a session by reading `MASTER_PLAN.md` → the current sprint file → `API_SPEC.md` for any module being touched.
2. A sprint is not "done" until its Acceptance Criteria are checked off **and** the Current Status table above is updated.
3. Architecture changes (folder structure, module boundaries) require a corresponding edit to `SDD.md`, `API_SPEC.md`, **and** a new entry in `ARCHITECTURE_DECISIONS.md` in the *same* change — never let code and docs drift, and never let a non-obvious decision go unrecorded.
4. See `CODEX_GUIDELINES.md` for the full rules of engagement.

## 5. Versioning

- `v0.1` – `v0.6`: internal prototypes, one per sprint, not tagged in git beyond a commit message.
- `v1.0`: first fully integrated, polished, demo-ready release — tagged in git, README finalized, demo video recorded.
- Anything after `v1.0` (stretch goals from `SDD.md` §17) is `v1.x` and gets its own sprint file created on demand, following the same template as Sprints 00–07.
