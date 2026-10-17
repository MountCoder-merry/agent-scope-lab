# AgentScope Autonomous Engineering Rules

This file defines **project-scoped** behavior. It does not override operating-system, provider, authentication, or GitHub security controls.

## Read first

1. `AgentScope_全自主开发计划书.md` — scope, architecture, acceptance gates, and preauthorized actions.
2. `CODEX_MASTER_PROMPT.md` — current unattended execution mandate.
3. `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/AUTONOMOUS_STATE.json` when present.
4. Original user workflow: `references/Codex开发流程规范.md` when present.

If the plan conflicts with the original workflow only in its approval cadence, use this plan's **bounded autopilot** policy. All security principles remain mandatory.

## Product boundaries

- Build a visual, local-first, open-source AI Agent trace debugging, recorded replay, and controlled failure simulation workbench.
- Static public Demo: synthetic fixtures; no accounts; no API keys; no paid LLM calls; no actual arbitrary tool execution.
- Differentiate workflow templates, recorded execution spans/events, deterministic recorded playback, mock execution, and real agent resumption.
- Deliver end-to-end vertical slices, not fake mock-only pages presented as production features.
- Use `agent-scope-lab` as a working repository identifier, subject to name-conflict review.

## Engineering principles

- Prefer React + strict TypeScript + Vite / FastAPI + Pydantic + SQLAlchemy for the respective components.
- Use `@xyflow/react` for graphs and React Flow layouts backed by validated data.
- Keep TraceDataSource abstracted so static fixtures and live API share the same UI contracts.
- Follow stable event order, strong IDs, explicit schema versions, and clear error semantics.
- Validate all imports; limit payload size/depth/count; do not render unsafe HTML or run text as commands.
- Persist testable schema/API contracts, ADRs, and genuine fixtures.
- Do not build auth, billing, microservices, generic tool execution, or production LLM orchestration into public Demo.

## Continue without asking at each milestone

- Within the bounded, preauthorized project scope, proceed M0 → M9 continuously.
- At each milestone: write a short plan, implement, test, inspect diff, repair, update docs, then continue.
- Never pause for cosmetic choices, package patch selection, internal architecture alternatives, or tests you can run.
- Choose a simple defensible approach; write significant choices to `docs/decisions/`.
- Automatically fix reproducible failures with a regression test first; stop after 3 materially different failed attempts on the same blocker.
- Record `docs/AUTONOMOUS_STATE.json` and `docs/WORKLOG.md` after each milestone, with the next actionable task.
- Emit truthful updates in log files; do not call a milestone complete until its acceptance checks pass.

## Security and explicit scope

**Allowed only in this newly dedicated project workspace:** create/edit/delete project files, install project dependencies, run tests, launch local servers, create project-specific Docker resources, use Git branches and local commits, generate CI/Pages config.

**Allowed if GitHub authentication and narrowly scoped rights already exist:** create or push to a *new dedicated repository* for this project and publish a synthetic static Demo using that repository's GitHub Pages. Never alter pre-existing repositories or the GitHub profile.

**Not authorized:** spend money, purchase a domain, provision billable cloud services, read or modify other projects, delete user data, modify system security/network settings, circumvent MFA/approval, create or expose secrets, disable CI/protection gates, run arbitrary uploaded code, deploy an unprotected public agent-runner API, delete hosted production data or run destructive migrations.

When external permission is missing, do not weaken safety or request repeated manual feedback. Finish independent safe work, mark the specific item `blocked`, write concrete next steps in `docs/BLOCKERS.md`, and exit gracefully if no work remains.

## Verification and quality bar

- Run actual lint, typecheck, unit, integration, E2E and build checks as appropriate; report exact commands and exit codes.
- Never remove tests, change tests to vacuous checks, disable lint, hardcode success metrics, or fabricate screenshots, release URLs, CI passes, coverage or reviews.
- Screenshot the running UI at desktop viewport; verify real interaction paths with Playwright.
- Ensure stable replay, malformed import behavior, no external tool side effects, correct routing on GitHub Pages.
- Before publishing: inspect for leaks, unsafe HTML, exposed secrets, dangerous imports, broken assets and failing builds.
- Public release **must** include independently verified URL and HTTP/browser smoke results.
- Label partial production backend deployment accurately as `self-host-ready`, not `live`.

## Status schema

File: `docs/AUTONOMOUS_STATE.json`

- `overall_status`: `in_progress` | `blocked` | `completed`
- `phase`: `M0` through `M9`
- `last_completed_milestone`: string or null
- `public_demo_url`: link or null
- `verified_demo_url`: link or null
- `quality_gates_passed`: boolean
- `blockers`: array of strings
- `next_action`: string
- `updated_at`: ISO8601 UTC

Set `completed` only when required gates are genuinely met. Keep `in_progress` if useful safe tasks remain. All project logs are .gitignored when potentially sensitive.

## Final handoff

Deliver changed files, features, test commands/results, release URL if verified, blockers, risk assessment, next actions, and instructions for resuming. If an action cannot be completed because of access, state it as blocked; never simulate success.
