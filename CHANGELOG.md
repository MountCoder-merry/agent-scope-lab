# Changelog

All notable changes to AgentScope are recorded here. The project is pre-1.0 and interfaces may evolve between milestones.

## [Unreleased]

### Added

- CI workflow for Web lint, TypeScript, unit tests, Vite build, FastAPI checks, and browser smoke.
- GitHub Pages Actions workflow that publishes the static Web artifact only.
- Docker Compose definition for Web + API, with an optional PostgreSQL profile and named data volumes.
- Self-hosting environment template, Nginx SPA fallback, health checks, and security headers.
- Chinese README, security review checklist, and release evidence template.

### Security

- Documented the no-key, synthetic-data boundary for the public demo.
- Documented JSON import limits, secret handling, dependency audit expectations, and Docker verification blockers.

## [0.1.0] - 2026-10-17

### Added

- React + TypeScript + Vite trace workbench.
- Three synthetic trace fixtures with graph, span inspector, event replay, and deterministic Failure Lab.
- FastAPI health and trace-list skeleton.
- Zod validation for imported trace JSON.

